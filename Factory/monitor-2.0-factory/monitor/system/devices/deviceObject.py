#! /usr/bin/python

import threading
import datetime
from collections import OrderedDict

from deviceConstants import *

import logsystem
log = logsystem.getLogger()

import dbUtils
import auditTrail
import utilities



class DeviceObject:
  def __init__(self, deviceManager, name, description, deviceType, deviceTypeName, executionType, executionTypeName, image ):
    self.lock = threading.RLock()
    self.deviceManager = deviceManager
    self.name = name
    self.description = description
    self.deviceType = deviceType
    self.deviceTypeName = deviceTypeName
    self.executionType = executionType
    self.executionTypeName = executionTypeName
    self.image = image

    self._valueDescriptions = OrderedDict()
    self._alarmDescriptions = OrderedDict()

    self._values = OrderedDict()
    self._values1 = OrderedDict()
    self._alarms = OrderedDict()
    self._dynamicImages = OrderedDict()

    self._alarm = False
    self._logReady = False
    self.i = 0
    self._connectedInputValues = OrderedDict()     # list of external input keys - use s.discard(x)

  def getDeviceManager(self):
    return self.deviceManager

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

  def getDeviceType(self):
    return self.deviceType

  def getDeviceTypeName(self):
    return self.deviceTypeName

  def getExecutionType(self):
    return self.executionType

  def getExecutionTypeName(self):
    return self.executionTypeName

  def getImage(self):
    return self.image

  def isNetworkDevice(self):
    return False

  def isVirtualDevice(self):
    return False

  def _getValueType(self, key):
    if key in self._valueDescriptions:
      return self._valueDescriptions[key]["valueType"]
    return None

  def _getDataType(self, key):
    if key in self._valueDescriptions:
      return self._valueDescriptions[key]["dataType"]
    return None

  def checkSetToDefaultLogging(self):
    # See if we need to initialize the logging to default logging.
    valuesToLog = self.deviceManager.directory.getLoggingManager().getLoggedValuesForDevice(self.name)
    if "LEO-NEED-DEFAULTS" in valuesToLog :  # Set when device is added in device list.
      newValuesToLog = []
      for key in self._valueDescriptions:
        if "defaultLog" in self._valueDescriptions[key]:
          newValuesToLog.append( key )
      self.deviceManager.directory.getLoggingManager().setLoggedValuesForDevice(self.name, newValuesToLog )

  def _initValuesFromDescription(self, values):
    for key in self._valueDescriptions.keys():
      valueDesc = self._valueDescriptions[key]
      values[key] = valueDesc["default"] if "default" in valueDesc else None

  def _loadValuesFromDatabase(self, values):
    with self.lock:
      self._initValuesFromDescription(values)

      conn = dbUtils.getDeviceDatabaseConnection()
      cur = conn.cursor()
      cur.execute('select valueName, value from configs where deviceName=?', (self.name,))
      for valueInfo in cur.fetchall():
        key = valueInfo["valueName"]
        dt = self._getDataType(key)
        try:
          if dt == dataTypeBool:
            values[key] = (valueInfo["value"] == "True")
          elif dt == dataTypeFloat:
            values[key] = float(valueInfo["value"])
          elif dt == dataTypeInt or dt == dataTypeList:
            values[key] = int(valueInfo["value"])
          else:
            values[key] = valueInfo["value"]
        except:
          pass
      conn.commit()
      conn.close()

  def _loadConstantValuesFromDatabase(self, values):
    with self.lock:
      self._initValuesFromDescription(values)

      conn = dbUtils.getDeviceDatabaseConnection()
      cur = conn.cursor()
      cur.execute('select valueName, value from idealConfigs where deviceName=?', (self.name,))
      for valueInfo in cur.fetchall():
        key = valueInfo["valueName"]
        dt = self._getDataType(key)
        try:
          if dt == dataTypeBool:
            values[key] = (valueInfo["value"] == "True")
          elif dt == dataTypeFloat:
            values[key] = float(valueInfo["value"])
          elif dt == dataTypeInt or dt == dataTypeList:
            values[key] = int(valueInfo["value"])
          else:
            values[key] = valueInfo["value"]
        except:
          pass
      conn.commit()
      conn.close()

  def loadValuesFromDatabase(self):
    dbvalues = OrderedDict()
    self._loadValuesFromDatabase(dbvalues)
    with self.lock:
      self._values = dbvalues

  def loadConstantValuesFromDatabase(self):
    dbvalues1 = OrderedDict()
    #log.debug("loadConstantValuesFomDatabase called")
    self._loadConstantValuesFromDatabase(dbvalues1)
    with self.lock:
      self._values1 = dbvalues1
      #log.debug(dbvalues1)


  def loadConstantConfigVals(self):
    #print "Entered LoadConstantConfigVals"
    dbvalues1 = OrderedDict()
    retval = OrderedDict()
    # log.debug("loadConstantValuesFomDatabase called")
    self._loadConstantValuesFromDatabase(dbvalues1)
    with self.lock:
      self._ConstVal = dbvalues1
      for key in self._ConstVal.keys():
        if self._getValueType(key) == valueTypeConfig:
          retval[key] = self._ConstVal[key]
          # log.debug(dbvalues1)
    return retval

  def saveValuesToDatabase(self):
    #log.debug(self.name)
    dbvalues = OrderedDict()
    dbvalues1 = OrderedDict()
    deviceNames = []
    i=0
    self._loadValuesFromDatabase(dbvalues)
    self._loadConstantValuesFromDatabase(dbvalues1)
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    cur.execute('select DISTINCT(valueName) as Valkeys from idealConfigs where deviceName=?',(self.name,))
    devNames = cur.fetchall()
    for device in devNames:
      #log.debug(device["Valkeys"])
      deviceNames.append(str(device["Valkeys"]))

    with self.lock:
      #log.debug(self._values.keys())
      for key in self._values.keys():

        if self._getValueType(key) == valueTypeConfig:
          if key not in deviceNames:
            value = str(self._values[key])
            cur.execute('INSERT INTO idealConfigs VALUES (?, ?, ?)', (self.name, key, value))
            conn.commit()
          if dbvalues[key] != self._values[key]:
            cur.execute('DELETE FROM configs WHERE deviceName=? AND valueName=?', (self.name, key))
            value = str(self._values[key])
            cur.execute('INSERT INTO configs VALUES (?, ?, ?)', (self.name, key, value))
            #cur.execute('INSERT INTO idealConfigs VALUES (?, ?, ?)', (self.name, key, value))
            #log.debug("Value of i",self.i)
    self.i= self.i+1
    #log.debug(self.i)
    conn.commit()
    conn.close()


  def saveConstantValuesToDatabase(self):
    dbvalues1 = OrderedDict()
    self._loadConstantValuesFromDatabase(dbvalues1)
    #log.debug(dbvalues1)
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()

    with self.lock:
      for key in self._values1.keys():
        if self._getValueType(key) == valueTypeConfig:
          if dbvalues1[key] != self._values1[key]:
            cur.execute('DELETE FROM idealConfigs WHERE deviceName=? AND valueName=?', (self.name, key))
            value = str(self._values1[key])
            cur.execute('INSERT INTO idealConfigs VALUES (?, ?, ?)', (self.name, key, value))
            #cur.execute('INSERT INTO idealConfigs VALUES (?, ?, ?)', (self.name, key, value))
            #log.debug("Value Changed")
            #log.debug(key)
    conn.commit()
    conn.close()



  # def _loadDistinctDeviceNames(self, deviceNames):
    # conn = dbUtils.getDeviceDatabaseConnection()
    # cur = conn.cursor()


  def setSyncDaily(self, configBit, devName):
    log.debug("setSyncDaily is called")
    log.debug(self.name)
    deviceN = devName
    configBit1 = configBit
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    cur.execute('delete from syncVal where deviceName =?', (self.name,))
    cur.execute('INSERT INTO syncVal VALUES (?, ?)', (self.name, configBit1))
    # data1= OrderedDict()
    # data1 = cur.fetchall()
    # log.debug(data1)
    # for row in data1:
      # print row[0]
      # if row[0] == self.name:
        # print "entered"
        # cur.execute('DELETE FROM syncVal WHERE deviceName=?', (devicename,))
        # # #conn.commit()
        # cur.execute('INSERT INTO syncVal VALUES (?, ?)', (self.name, configBit1))
        # #strSQL = 'UPDATE syncVal SET enableBit="{0}" where deviceName="{1}"'.format(configBit1,self.name)
        # cur.execute(strSQL)
        # conn.commit()
      # else:
        # cur.execute('DELETE FROM syncVal WHERE deviceName=?', (devicename,))
        # cur.execute('INSERT INTO syncVal VALUES (?, ?)', (self.name, configBit1))
    # #log.debug("Value changed")
    conn.commit()
    conn.close()

  def _loadSyncBitValuesFromDatabase(self,data1):
    #log.debug("Load Sync called")
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select * from syncVal")
    data1 = cur.fetchall()
    self.retVal1 = data1

  def getSyncDaily(self):
    #log.debug("get Sync bit called")
    #log.debug(self.name)
    data1 = OrderedDict()
    configBit1 = OrderedDict()
    #checkBackupSync()
    #self._loadSyncBitValuesFromDatabase(data1)
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    cur.execute('select * from syncVal')
    devNames = cur.fetchall()
    conn.close()
    #log.debug(devNames)
    i =0
    for device in devNames:
      configBit1[i] = {"deviceName":device[0],"enableBit":device[1]}
      #log.debug(configBit1[i])
      i = i+1
    #checkBackupSync(configBit1)
    #log.debug(configBit1)
    return configBit1#configBit

  def checkBackupSync(self):
    date_time = datetime.datetime.now()
    time = date_time.time()
    log.debug(time.hour)
    log.debug(time.minute)
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    cur.execute('select * from syncVal')
    devNames = cur.fetchall()
    conn.close()
    #log.debug(devNames)
    i =0
    for device in devNames:
      configBit1[i] = {"deviceName":device[0],"enableBit":device[1]}
      #log.debug(configBit1[i])
      i = i+1
    for row in configBit1:
      if confiBit1[row]["enableBit"] == 1:
        if time.hour == 11 and time.minute == 24 and time.second <30:
          name = confiBit1[row]["deviceName"]
          self.getDeviceObject(name).loadConstantValuesFromDatabase()
          log.debug(dbvalues1)


  # ##############################################################
  # Logging
  ##############################################################
  # tells the device that logging is to take place
  def updateLoggedValues(self, valuesToLog):
    with self.lock:
      self._logReady = True

  # the device tells the system that the latest values exist and it should log - virtual devices can be logged anytime
  def areLoggedValuesReady(self):
    with self.lock:
      retval = self._logReady
    return retval

  def clearLoggedValuesReady(self):
    with self.lock:
      self._logReady = False

  ##############################################################
  # Advisories
  ##############################################################
  def _initAlarmsFromDescription(self):
    for key in self._alarmDescriptions.keys():
      self._alarms[key] = False

  def loadAdvisoriesFromDatabase(self):
    with self.lock:
      self._initAlarmsFromDescription()
      
      if self.deviceType == "E2":
        activeAlarmList = dbUtils.getAlarmEntries(dbUtils.GETE2DEVICEACTIVEALARMS, { "deviceName":self.name } )
      elif self.deviceType == "SiteSupervisor":
        activeAlarmList = dbUtils.getAlarmEntries(dbUtils.GETSITESUPERVISORDEVICEACTIVEALARMS, { "deviceName":self.name } )
      else:
        activeAlarmList = dbUtils.getAlarmEntries(dbUtils.GETDEVICEACTIVEALARMS, { "deviceName":self.name } )

      for alarmInfo in activeAlarmList:
        self._alarms[alarmInfo["alarm"]] = True
        # If the device is a network failure, update the alarmDescription with the alarm description from the alarm entry.
        if alarmInfo["alarm"] == networkFailureKey:
          self._alarmDescriptions[networkFailureKey]["description"] = alarmInfo['description']

  def _addAdvisoryEntry(self, action, alarm, description ):
    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()
    try:
      UTCnow = utilities.getUTCnowFormatted()

      if self.deviceType == "E2":
        strE2ControllerName = self.name
        strE2timestamp = "01-01-16 00:00"
      elif self.deviceType == "SiteSupervisor":
        strE2ControllerName = self.name
        strE2timestamp = "01-01-16 00:00"
      else:
        strE2ControllerName = ""
        strE2timestamp = ""
      E2advid = -1

      strSQL = 'INSERT INTO devicealarms (date,action,name,alarm,description,E2advid,E2timestamp,E2ControllerName,EBrecId) ' \
                  'VALUES ("{0}","{1}","{2}","{3}","{4}",{5},"{6}","{7}",{8})'.format( UTCnow,
                              action, self.name, alarm, description, E2advid, strE2timestamp, strE2ControllerName, -1)
      cur.execute( strSQL )
    except Exception, e:
      strExcept = "Error Updating Database: {0}".format( e )
      log.exception(strExcept)
      auditTrail.AuditTrailAddEntry(strExcept)

    conn.commit()
    conn.close()

  def _updateAdvisoryEntry(self, strSQL ):
    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()
    try:
      cur.execute( strSQL )
    except Exception, e:
      strExcept = "Error Updating Database: {0}".format( e )
      log.exception(strExcept)
      auditTrail.AuditTrailAddEntry(strExcept)

    conn.commit()
    conn.close()

  def newAdvisory(self, alarm, description):
    self._addAdvisoryEntry("NEW", alarm, description)

  def rtnAdvisory(self, alarm, description):
    strSQL = 'UPDATE devicealarms SET action="RTN", rtntimestamp="{0}" where action<>"RTN" and alarm="{1}" ' \
             'and description="{2}" and name="{3}"'.format(utilities.getUTCnowFormatted(), alarm, description, self.name )
    self._updateAdvisoryEntry( strSQL )

  def ackAdvisory(self, alarm, description):
    strSQL = 'UPDATE devicealarms SET action="ACK" where action<>"RTN" and alarm="{0}" ' \
             'and description="{1}" and name="{2}"'.format(alarm, description, self.name )
    self._updateAdvisoryEntry( strSQL )

  def checkBooleanAdvisory(self, alarm, value):
    if alarm in self._alarms:
      if value != self._alarms[alarm]:
        desc = self._alarmDescriptions[alarm]
        if value:
          self.newAdvisory(alarm, desc["description"])
        else:
          self.rtnAdvisory(alarm, desc["description"])
        self._alarms[alarm] = value

  ###################################################
  # JSON helpers
  ###################################################

  def getDeviceAlarms(self, strAlarmType):
      # returns all alarms for a given device name
      # If an E2 device, query differently because the "name" field is E2 name.
      if self.deviceType == "E2" :
        if strAlarmType == "Active":
          typeOfAlarms = dbUtils.GETE2DEVICEACTIVEALARMS
        else :
          typeOfAlarms = dbUtils.GETE2DEVICEHISTORYALARMS
      elif self.deviceType == "AKSC255" :
        if strAlarmType == "Active":
          typeOfAlarms = dbUtils.GETAKSC255DEVICEACTIVEALARMS
        else :
          typeOfAlarms = dbUtils.GETAKSC255DEVICEHISTORYALARMS
      elif self.deviceType == "SiteSupervisor" :
        if strAlarmType == "Active":
          typeOfAlarms = dbUtils.GETSITESUPERVISORDEVICEACTIVEALARMS
        else :
          typeOfAlarms = dbUtils.GETSITESUPERVISORDEVICEHISTORYALARMS
      else: # non-E2 device
        if strAlarmType == "Active":
          typeOfAlarms = dbUtils.GETDEVICEACTIVEALARMS
        else :
          typeOfAlarms = dbUtils.GETDEVICEHISTORYALARMS
          
      dictAlarmList = dbUtils.getAlarmEntries( typeOfAlarms, {"deviceName": self.name} )
      return dictAlarmList

  def getDeviceInformation(self):
    return { "description": self.description, "deviceType": self.deviceType, "deviceTypeName": self.deviceTypeName, "alarm": self._alarm, "executionType": self.executionType, "image": self.image }

  def getValueDescriptions(self):
    with self.lock:
      return self._valueDescriptions;

  def getValueDescriptionByKey(self,key):
    with self.lock:
      if key in self._valueDescriptions:
        return self._valueDescriptions[key];
      else :
        return None

  def getDynamicImagesByKey(self,key):
    with self.lock:
      retval = OrderedDict()
      for key in self._dynamicImages:
        retval[key] = self._dynamicImages[key]
      return retval

  def getValues(self):
    with self.lock:
      retval = OrderedDict()
      for key in self._values:
        retval[key] = self.connectedValues[key] if key in self._connectedInputValues.keys() else self._values[key]
      return retval

  def getInAlarm(self):
    return self._alarm

  ###################################################
  # Help methods for concise information transfer
  ###################################################

  # get values for the general list
  def getListedValues(self, listedKeys):
    with self.lock:
      retval = OrderedDict()
      for key in listedKeys:
        if key in self._values:
          retval[key] = self.connectedValues[key] if key in self._connectedInputValues.keys() else self._values[key]
      return retval

  # TODO: work on configurable values
  def getAllConfigurableValues(self):
    with self.lock:
      retval = self.getConfigValues().copy()
      #retval.update(self.getConfigValues())
      return retval

  def getDataValues(self):
    with self.lock:
      retval = self.getInputValues().copy()
      retval.update(self.getOutputValues())
      return retval

  ###################################################
  # Inputs
  ###################################################

  def getInputValues(self):
    with self.lock:
      retval = OrderedDict()
      for key in self._values.keys():
        if self._getValueType(key) == valueTypeInput:
          if key in self._connectedInputValues.keys():
            retval[key] = self.connectedValues[key]
          else:
            retval[key] = self._values[key]
    return retval

  # This is setting configuration
  def setInputValues(self, values):
    with self.lock:
      for key in values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeInput:
          self._values[key] = values[key]
          # TODO: write to the database

  # RUNTIME!!!!  This should be called prior to execute on a virtual device
  def setConnectedInputValues(self, values):
    with self.lock:
      self._connectedInputValues.clear()
      for key in values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeInput:
          self._connectedInputValues[key] = values[key]
          # We will not write these to the database

  ###################################################
  # Outputs
  ###################################################
  def getOutputValues(self):
    with self.lock:
      retval = OrderedDict()
      for key in self._values.keys():
        if self._getValueType(key) == valueTypeOutput:
          retval[key] = self._values[key]
    return retval

  # this is an internal convenience method
  def _setOutputValues(self, values):
    with self.lock:
      for key in values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeOutput:
          self._values[key] = values[key]

  def _nullOutputValues(self):
    with self.lock:
      for key in self._values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeOutput:
          self._values[key] = None


  ###################################################
  # Configs
  ###################################################
  def getConfigValues(self):
    with self.lock:
      retval = OrderedDict()
      for key in self._values.keys():
        if self._getValueType(key) == valueTypeConfig:
          retval[key] = self._values[key]
    return retval

  def getConstantConfigValues(self):
    with self.lock:
      retval = OrderedDict()
      self.loadConstantValuesFromDatabase()
      for key in self._values1.keys():
        if self._getValueType(key) == valueTypeConfig:
          retval[key] = self._values1[key]
    #log.debug("getConstantConfigValues retval Called")
    #log.debug(retval)
    return retval

  def setConfigValues(self, values):
    #log.debug("Set Config Values Called")
    with self.lock:
      for key in values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeConfig:
          self._values[key] = values[key]
    self.saveValuesToDatabase()
    #NetworkDeviceObject._prepareActionTransactions(self)


  def setConstantConfigValues(self, values):
    log.debug("Device Configuration is being save to LEO Backup Database")
    with self.lock:
      for key in values.keys():
        valueType = self._getValueType(key)
        if valueType == valueTypeConfig:
          self._values1[key] = values[key]
    self.i =0;
    self.saveConstantValuesToDatabase()


  ###################################################
  # User Action - meant to be derived
  ###################################################
  def performUserAction(self, data):
    return None


##########################################
# NETWORK DEVICE OBJECT
##########################################
class NetworkDeviceObject(DeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image ):
    DeviceObject.__init__(self, deviceManager, name, description, deviceType, deviceTypeName, deviceNetworkExecution, deviceNetworkExecutionText, image )
    self.network = network
    self.networkAddress = networkAddress

    self.online = False

    self._valuesToLog = None
    self._logMessagesCount = 0

    self._newDeviceConfigurationValues = None
    self._setDeviceConfiguration = False
    # self._setDeviceConstantConfiguration = False

    self._updateDeviceConfiguration = True
    self._updateStatus = False
    self._updateAlarms = False

  def getNetwork(self):
    return self.network

  def getNetworkAddress(self):
    return self.networkAddress

  def isNetworkDevice(self):
    return True;

  def getDeviceInformation(self):
    retval = DeviceObject.getDeviceInformation(self)
    retval["online"] = self.online
    retval["network"] = self.network
    # When we return the network address, we need to peel off the port information.
    if self.networkAddress.find(":") >= 0 :
      # Remove colon and everything after.
      filteredNetworkAddress = self.networkAddress[:self.networkAddress.find(":")]
    else :
      filteredNetworkAddress = self.networkAddress
    retval["networkAddress"] = filteredNetworkAddress
    return retval

  # this is overridden in the derived to add network failure
  def _initAlarmsFromDescription(self):
    self._alarmDescriptions[networkFailureKey] = {"description": "" }
    DeviceObject._initAlarmsFromDescription(self)

  # tells the device that logging is to take place
  def updateLoggedValues(self, valuesToLog):
    with self.lock:
      self._valuesToLog = valuesToLog
      self._logMessagesCount = 0


  def setConfigValues(self, values):
    log.debug("LEO sent Backup database configuration to Device or user set configuration from LEO UI for " +self.name)
    DeviceObject.setConfigValues(self, values)
    with self.lock:
      self._newDeviceConfigurationValues = values
      self._setDeviceConfiguration = True

  # def setConstantConfigValues(self, values):
    # DeviceObject.setConstantConfigValues(self, values)
    # with self.lock:
      # self._newDeviceConfigurationValues = values
      # self._setDeviceConstantConfiguration = True

  def updateDeviceConfiguration(self):
    with self.lock:
      self._updateDeviceConfiguration = True

  def updateStatus(self):
    with self.lock:
      self._updateStatus = True

  def updateAlarms(self):
    with self.lock:
      self._updateAlarms = True


  def getNetworkTransactions(self):
    # print "getNetworkTransactions->Update Status =", self._updateStatus
    networkTrans = None
    with self.lock:
      networkTrans = self._prepareActionTransactions()
      if networkTrans is not None and len(networkTrans) > 0:
        for tran in networkTrans:
          tran.priority = 1

      elif self._valuesToLog is not None:
        networkTrans = self._prepareLoggingTransactions(self._valuesToLog)
        for tran in networkTrans:
          tran.priority = 2
          tran.forLogging = True
        self._valuesToLog = None

        if self._logMessagesCount == 0:
          self._logMessagesCount = len(networkTrans)

      elif self._updateAlarms:
        networkTrans = self._prepareUpdateAlarmsTransactions()
        for tran in networkTrans:
          tran.priority = 2
        self._updateAlarms = False

      elif self._setDeviceConfiguration:
        networkTrans = self._prepareSetDeviceConfigurationTransactions()
        for tran in networkTrans:
          tran.priority = 2
        self._setDeviceConfiguration = False
        self._newDeviceConfigurationValues = None

      # elif self._setDeviceConstantConfiguration:
        # networkTrans = self._prepareSetDeviceConfigurationTransactions()
        # for tran in networkTrans:
          # tran.priority = 2
        # self._setDeviceConstantConfiguration = False
        # self._newDeviceConfigurationValues = None

      elif self._updateDeviceConfiguration:
        networkTrans = self._prepareUpdateDeviceConfigurationTransactions()
        for tran in networkTrans:
          tran.priority = 3
        self._updateDeviceConfiguration = False
      elif self._updateStatus:
        networkTrans = self._prepareUpdateStatusTransactions()
        for tran in networkTrans:
          tran.priority = 4
        self._updateStatus = False


    if networkTrans is not None:
      for tran in networkTrans:
        tran.name = self.name
        tran.network = self.network
        tran.networkAddress = self.networkAddress
    return networkTrans

  def putNetworkTransaction(self, networkTrans):
    retval = self._executeTransaction(networkTrans)
    if retval is None:
      self._setOnlineStatus(networkTrans.online, networkTrans.offlineMessage)
    else:
      self._setOnlineStatus(retval["online"], retval["message"])

    with self.lock:
      if networkTrans.forLogging:
        self._logMessagesCount = self._logMessagesCount - 1
        if self._logMessagesCount <= 0:
          self._logReady = True

  def _setOnlineStatus(self, online, msg):
    with self.lock:
      self.online = online
      self.msg = msg

      if not online:
        # If the reason for offline has changed...
        if self._alarmDescriptions[networkFailureKey]["description"] != msg:
          # Clear the alarm.
          self.checkBooleanAdvisory(networkFailureKey, False)
        # Update the description for the new active alarm
        self._alarmDescriptions[networkFailureKey]["description"] = msg
        self._alarm = True

      self.checkBooleanAdvisory(networkFailureKey, not online)

  def _prepareActionTransactions(self):
    return []

  def _prepareLoggingTransactions(self, valueToLog):
    raise NotImplementedError

  def _prepareSetDeviceConfigurationTransactions(self):
    raise NotImplementedError

  def _prepareUpdateDeviceConfigurationTransactions(self):
    raise NotImplementedError

  def _prepareUpdateStatusTransactions(self):
    raise NotImplementedError

  def _prepareUpdateAlarmsTransactions(self):
    raise NotImplementedError

  def _executeTransaction(self, networkTrans):
    raise NotImplementedError



##########################################
# VIRTUAL DEVICE OBJECT
##########################################
class VirtualDeviceObject(DeviceObject):
  def __init__(self, deviceManager, name, description, deviceType, deviceTypeName, image, devOptions):
    DeviceObject.__init__(self, deviceManager, name, description, deviceType, deviceTypeName, deviceVirtualExecution, deviceVirtualExecutionText, image, devOptions)

  def executeVirtualDevice(self):
    with self.lock:
      inputValues = self.getInputValues()
      outputValues = self.getOutputValues()
      configValues = self.getConfigValues()
      outputValues = self._execute(inputValues, outputValues, configValues)
      self._setOutputValues(outputValues)

  def _execute(self, inputValues, outputValues, configValues):
    raise NotImplementedError


