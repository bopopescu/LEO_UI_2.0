#! /usr/bin/python

import threading
import sqlite3

import objectDirectory
import dbUtils
import plugins
import utilities
from collections import OrderedDict
import auditTrail
import httplib
import json
import systemConstants
from xml.etree import ElementTree

from devices import deviceConstants

import logsystem
log = logsystem.getLogger()

class DeviceManager:
  def __init__(self, directory):
    self.lock = threading.RLock()
    self.directory = directory
    self.dummyDevice = []
    self.plugins = {}

    i = 0
    pluginsList = plugins.getPlugins("system/devices")
    strDevTypeNames = "Loading {0} Device Type Plugins: ".format( len( pluginsList) )
    while i < len( pluginsList ) :
      strDevTypeNames = "{0}{1}, ".format( strDevTypeNames, pluginsList[i]['name'] )
      i = i + 1
    log.info( strDevTypeNames )

    # Add new supported devices as they come
    for plugin in plugins.getPlugins("system/devices"):
      try:
        loadedPlugin = plugins.loadPlugin(plugin)
        self.plugins[loadedPlugin.deviceType] = plugin
        self.directory.addDeviceObjectType(loadedPlugin.deviceType, loadedPlugin.deviceTypeName)

      except Exception, e:
        log.exception("Loading device namespace from directory: " + plugin["name"] + " failed: " + str(e))

    self.loadDevices()

  # This method is called after the networks, devices, alarm and logging subsystems are "going".
  def afterInitializeObjectsInit(self):
    # We need to loop through the device objects and see if anybody needs their logs set to default logging.
    with self.lock:
      keys = self.directory.getDeviceObjectKeys()
      retval = OrderedDict()
      for key in keys:
        deviceObj = self.directory.getDeviceObject(key)
        if deviceObj is not None:
          deviceObj.checkSetToDefaultLogging()

  def _deviceFactory(self, deviceType, name, description, network, networkAddress, image ):
    try:
      loadedPlugin = plugins.loadPlugin(self.plugins[deviceType])
      log.info( "Creating Device Type: {0}, Name:{1}, Address:{2}".format( loadedPlugin.executionType, name, networkAddress  ) )
      if loadedPlugin.executionType == deviceConstants.deviceNetworkExecution or loadedPlugin.executionType == deviceConstants.deviceE2Execution :
        setValue = 0
        method = "rebootMethod"
        return loadedPlugin.Device(self, name, description, network, networkAddress, image, method)
      elif loadedPlugin.executionType == deviceConstants.deviceAKSC255Execution:
        setValue = 0
        method = "rebootMethod"
        return loadedPlugin.Device(self, name, description, network, networkAddress, image, method)
      elif loadedPlugin.executionType == deviceConstants.deviceSiteExecution:
        setValue = 0
        method = "rebootMethod"
        return loadedPlugin.Device(self, name, description, network, networkAddress, image, method)
      elif loadedPlugin.executionType == deviceConstants.deviceVirtualExecution:
        return loadedPlugin.Device(self, name, description, image )
    except Exception, e:
      log.exception("Create instance of type " + deviceType + " failed: " + str(e))
    return None


  def loadDevices(self):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select * from devices")
    for deviceInfo in cur.fetchall():
      device = self._deviceFactory(deviceInfo["deviceType"], deviceInfo["name"], deviceInfo["description"], deviceInfo["network"], deviceInfo["networkAddress"], deviceInfo["image"] )
      log.debug(device)
      if device is not None:
        self.directory.addDeviceObject(device.getName(), device)
    conn.close()

  def getDeviceTypes(self):
    return self.directory.getDeviceObjectTypes()

  def getDeviceStatus(self):
    with self.lock:
      keys = self.directory.getDeviceObjectKeys()
      retval = OrderedDict()
      for key in keys:
        device = self.directory.getDeviceObject(key)
        if device is not None:
          retval[key] = device.getDeviceInformation()
      return retval

  def getDevices(self):
    with self.lock:
      keys = self.directory.getDeviceObjectKeys()
      retval = OrderedDict()
      for key in keys:
        device = self.directory.getDeviceObject(key)
        if device is not None:
          if device.executionType == deviceConstants.deviceNetworkExecution or device.executionType == deviceConstants.deviceE2Execution :
            retval[key] = { "deviceTypeName": device.getDeviceTypeName(),
                            "name": device.getName(),
                            "description": device.getDescription(),
                            "network": device.getNetwork(),
                            "networkAddress": device.getNetworkAddress(),
                            "image": device.getImage() }
          elif device.executionType == deviceConstants.deviceAKSC255Execution :
            retval[key] = { "deviceTypeName": device.getDeviceTypeName(),
                            "name": device.getName(),
                            "description": device.getDescription(),
                            "network": device.getNetwork(),
                            "networkAddress": device.getNetworkAddress(),
                            "image": device.getImage() }
            log.debug(retval[key])
          elif device.executionType == deviceConstants.deviceSiteExecution :
            retval[key] = { "deviceTypeName": device.getDeviceTypeName(),
                            "name": device.getName(),
                            "description": device.getDescription(),
                            "network": device.getNetwork(),
                            "networkAddress": device.getNetworkAddress(),
                            "image": device.getImage() }
            log.debug(retval[key])
          elif device.executionType == deviceConstants.deviceVirtualExecution:
            retval[key] = { "deviceTypeName": device.getDeviceTypeName(),
                            "name": device.getName(),
                            "description": device.getDescription(),
                            "image": device.getImage() }
      return retval



  def GetE2NameFromIPAddress( self, E2IPAddress ) :
    retE2Name = ""
#    print "GetE2NameFromIPAddress IP=", E2IPAddress

    # Yes, this is a hack. Let's quickly send a message to the IP address and see if we can get the controller name.
    try:
      E2Connection = httplib.HTTPConnection(E2IPAddress, timeout=10)
    except Exception, e:
      E2Connection = None

    if E2Connection is not None:
      try:
        jsonRequest = json.dumps( {'id': 'E2IP Network', 'method': 'E2.GetThisControllerName', 'params': '[[]]'} )
        E2Connection.request('POST', '/JSON-RPC', jsonRequest, headers={"Content-type": "application/json"})
        jsonResponse = E2Connection.getresponse()
        jsonData = jsonResponse.read()
        jsonReturn = json.loads(jsonData)
      except Exception, e:
        strExcept = "Could not get controller name: {}".format(str(e))
        log.exception( strExcept )
        # Remove the port information...
        ipOnlyAddr = E2IPAddress[:E2IPAddress.find(":")]
        strBuf = "E2 Device Did Not Respond at {}".format( ipOnlyAddr )
        jsonReturn = { 'result' : strBuf }

      E2Connection.close()

      if len(jsonReturn) > 0:
          retE2Name = jsonReturn['result']

    return retE2Name

  def GetSiteNameFromIPAddress(self, SiteIPAddress):
    retSiteName = ""
    #    print "GetSiteNameFromIPAddress IP=", E2IPAddress

    # Yes, this is a hack. Let's quickly send a message to the IP address and see if we can get the controller name.
    try:
      print(SiteIPAddress)
      SiteConnection = httplib.HTTPConnection(SiteIPAddress, timeout=20)
      print(SiteConnection)
    except Exception, e:
      E2Connection = None
      print("Error")

    if SiteConnection is not None:
      try:
        jsonRequest = {"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}
        SiteConnection.request("GET",
                               'http://' + SiteIPAddress + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":"1"}')
        # print(SiteConnection.request('GET', '/cgi-bin/mgw.cgi?m={"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}',headers={""}))
        # SiteConnection.request("http://10.1.10.59/cgi-bin/mgw.cgi?m={%22jsonrpc%22:%222.0%22,%22method%22:%22GetSessionID%22,%22id%22:%221%22}")
        jsonResponse = SiteConnection.getresponse()
        jsonData = jsonResponse.read()
        log.debug(jsonData)
        jsonReturn = json.loads(jsonData)
        sessionID = str(jsonReturn["result"]["sid"])
        log.debug(sessionID)
        # jsonRequest = '{"jsonrpc": "2.0", "method":"GetSystemInventory", ' \
        #               '"params":{"sid":"' + sessionID+'"}, "id": "8"}'

        SiteConnection.request("GET",
                               'http://' + SiteIPAddress + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSystemInventory","id":"1"}')

        # SiteConnection.request("GET", "http://" + SiteIPAddress +
        #                        "/cgi-bin/mgw.cgi?m={'jsonrpc':'2.0','method':'GetSystemInventory','params':{'sid':'" + sessionID + "'}, 'id':'1'}")

        # print('http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m='+ jsonRequest)
        # requestURL = 'http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m=' + jsonRequest
        # SiteConnection.request('GET', str(requestURL))
        jsonResponse = SiteConnection.getresponse()
        jsonData = jsonResponse.read()
        print jsonData
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["aps"]
        for i in dataValues:
          if (i["apptype"] == "SystemSettings"):
            iid = i["iid"]
            break
        log.debug(iid)
        # jsonRequest = '{"jsonrpc": "2.0", "method": "GetPointValues", "params": {"sid":"'+ sessionID+'","points": [{"ptr":"'+ iid +':SiteName"},{"ptr":"'+ iid +':UnitName"},{"ptr":"'+iid +':UnitNumber"}]},"id": "178"}'
        jsonRequest = '{"jsonrpc":"2.0","method":"GetPointValues","params":{"sid":"' + sessionID + '","points":[{"ptr":"' + iid + ':SiteName"},{"ptr":"' + iid + ':UnitName"},{"ptr":"' + iid + ':UnitNumber"}]},"id":"178"}'

        SiteConnection.request('GET', 'http://' + SiteIPAddress + '/cgi-bin/mgw.cgi?m=' + jsonRequest)
        jsonResponse = SiteConnection.getresponse()
        jsonData = jsonResponse.read()
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["points"]
        ptrVal = iid + ":UnitName"
        for i in dataValues:
          if (i["ptr"] == ptrVal):
            deviceName = i["val"]
            log.debug("Site Supervisor Name")
            log.debug(deviceName)
            jsonReturn["result"] = deviceName
            break

      except Exception, e:
        strExcept = "Could not get controller name: {}".format(str(e))
        print(strExcept)
        # Remove the port information...
        ipOnlyAddr = SiteIPAddress[:SiteIPAddress.find(":")]
        strBuf = "Site Supervisor Device Did Not Respond at {}".format(ipOnlyAddr)
        jsonReturn = {'result': strBuf}

      SiteConnection.close()

      if len(jsonReturn) > 0:
        retSiteName = jsonReturn['result']

    return retSiteName

  # This method is only used when a new AKSC255 device is added to the system to ensure that the ip address is correct and communicating.
  def GetAKSC255NameFromIPAddress(self, AKSC255IPAddress):
    AKSC255Name = ""
    
    try:
      AKSC255Connection = httplib.HTTPConnection(AKSC255IPAddress, timeout=10)
    except Exception, e:
      AKSC255Connection = None

    if AKSC255Connection is not None:
      try:
        AKSC255Connection.request('POST', '/html/xml.cgi', '<cmd action="read_units">',
                           headers={"Content-type": "application/x-www-form-urlencoded"})
        response = AKSC255Connection.getresponse()
        XMLdata = response.read()
        XMLroot = ElementTree.fromstring(XMLdata)
        AKSC255Name = XMLroot.find('unit_name').text

      except Exception, e:
        strExcept = "Could not get controller name: {}".format(str(e))
        log.exception(strExcept)
        strBuf = "E2 Device Did Not Respond at {}".format(AKSC255IPAddress)
        jsonReturn = {'result': strBuf}

      AKSC255Connection.close()
  
    return AKSC255Name

  def setDevices(self, newDevices):

    # we are looking for unit devices to remove from alarming or logging
    delimiter = '*&^%$#@!'

    existingSet = []
    newSet = []

    # Before we get too far, we want to do some data E2 information validation.
    # We need to translate IP addresses into controller names if necessary before saving.
#    print "newDevices = ", newDevices
    for device in newDevices:
      # We have an IP, but not name. Go get it from the controller.
      if device["deviceTypeName"] == deviceConstants.deviceE2ExecutionText and device["name"] == "<auto-detect>" :
        # Let's make sure the IP address for the E2 is properly formatted with the Port number
        if device["networkAddress"].find(":") >= 0 :
          ipAddr = device["networkAddress"]
        else :
          ipAddr = "{}:{}".format( device["networkAddress"], deviceConstants.E2_JSON_INTERFACE_PORT )

        E2Name = self.GetE2NameFromIPAddress( ipAddr  )
        if E2Name.find("Did Not Respond") >= 0 :
          # print "ERROR in GetE2NameFromIPAddress", E2Name
          return( E2Name ) # This contains the error message.
        elif len( E2Name ) > 0 :
          device["name"] = E2Name
      elif device["deviceTypeName"] == deviceConstants.deviceAKSC255ExecutionText and device["name"] == "<auto-detect>":
        AKSC255Name = self.GetAKSC255NameFromIPAddress(device["networkAddress"])
        if AKSC255Name.find("Did Not Respond") >= 0:
          print "ERROR in GetAKSC255NameFromIPAddress", AKSC255Name
          return (AKSC255Name)  # This contains the error message.
        elif len(AKSC255Name) > 0:
          device["name"] = AKSC255Name
      elif device["deviceTypeName"] == deviceConstants.deviceSiteExecutionText and device["name"] == "<auto-detect>":
        SiteName = self.GetSiteNameFromIPAddress(device["networkAddress"])
        if SiteName.find("Did Not Respond") >= 0:
          print "ERROR in GetSiteNameFromIPAddress", SiteName
          return (SiteName)  # This contains the error message.
        elif len(SiteName) > 0:
          device["name"] = SiteName
    #log.debug( "newDevices UPDATED ", newDevices)

    keys = self.directory.getDeviceObjectKeys()
    for key in keys:
      device = self.directory.getDeviceObject(key)
      existingSet.append(device.getDeviceTypeName() + delimiter + device.getName())

    for device in newDevices:
      newSet.append(device["deviceTypeName"] + delimiter + device["name"])

    #find the differences from compound keys
    addlist, dellist, samelist = utilities.compareLists(existingSet, newSet)

    # call alarm and device managers and delete old devices
    for deviceKey in dellist:
      deviceName = deviceKey.split(delimiter)[1]
#      print "REMOVING ", deviceName
      log.info('Removing alarms, logging, and configuration for:' + deviceName)
      self.directory.getAlarmManager().deleteAlarmsForDevice(deviceName)
      self.directory.getLoggingManager().deleteLogsForDevice(deviceName)
      self._deleteDeviceConfiguration(deviceName)
      devObject = self.getDeviceObjectByName(deviceName)

      # If an E2 device
      if devObject.deviceTypeName.find( deviceConstants.deviceE2ExecutionText ) == 0 :
        devObject.deleteE2DeviceInformation(deviceName)
      elif devObject.deviceTypeName.find(deviceConstants.deviceAKSC255ExecutionText) == 0:
        devObject.deleteAKSC255DeviceInformation( devObject,deviceName )
      elif devObject.deviceTypeName.find(deviceConstants.deviceSiteExecutionText) == 0:
        devObject.deleteSiteDeviceInformation( devObject,deviceName )

    # Let's create a list of added app names only from addlist
    addDeviceNameList = []
    for addDeviceMung in addlist:
      # Syntax of addlist = ['<deviceType>*&^%$#@!<deviceName>',...] - Remove everythign up to device name.
      addDeviceNameList.append( addDeviceMung.split(delimiter)[1] )

    # Adding of device information will be done in the device file - since the actual object is not
    # yet created at this time. System will restart the network manager and the objects will be created then.

    uniqueNames = []

#    print "----- Rebuilding device list -----"
    # update system configuration database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select name from devices")
      oldDevices = cur.fetchall()

      for i in oldDevices:
        abc = i["name"]
        self.dummyDevice.append(abc)
      log.debug(self.dummyDevice)
      systemConstants.OLD_DEVICES = self.dummyDevice
      cur.execute("delete from devices")

      for device in newDevices:

        # guarantee name uniqueness
        if device["name"] in uniqueNames:
          continue
        uniqueNames.append(device["name"])

        deviceTypes = self.directory.getDeviceObjectTypes()
        deviceType = ""
        for key in deviceTypes.keys():
          #log.debug("Update SYSTEM Configuration-->", key, device["name"], device["deviceTypeName"])
          if deviceTypes[key] == device["deviceTypeName"]:
            deviceType = key
            break
        cur.execute("INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?)", (deviceType, device["name"], device["network"], device["networkAddress"], device["description"], device["image"] ))
        if device["name"] in addDeviceNameList:
          # If this is a new name in the list, indicate a neeed to reset the logging to default logging.
          cur.execute("DELETE FROM logging WHERE deviceName = ?", (device["name"],))
          cur.execute("INSERT INTO logging VALUES (?, ?)", (device["name"], "LEO-NEED-DEFAULTS"))
          if deviceType != "E2 Device" or deviceType != "AKSC255" or deviceType != "SiteSupervisor":
            self.createDefaultSyncBit(device["name"])
      conn.commit()

      self.directory.getSystemObject().reinitialize() # restarts the network manager
      return "+++++ Re-Init System Objects +++++"

    except Exception, e:
      strBuf = "**** Error in setDevices - updating database **** - {0} ({1})".format(e, device["name"])
      log.exception(strBuf)

    finally:
      conn.close()

    return ""

  def oldDevices1(self):
    abc = set(self.dummyDevice)
    log.debug(abc)
    return abc

  def _deleteDeviceConfiguration(self, device):
    log.info('Deleting configuration for device ' + device)
    conn = dbUtils.getDeviceDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute('delete from configs where deviceName=?', (device,))
      cur.execute('delete from idealConfigs where deviceName=?', (device,))
      cur.execute('delete from syncVal where deviceName=?', (device,))
      conn.commit()
      conn.close()

      dbUtils.vacuumDatabase( dbUtils.deviceDatabasePath ) # Compress database
      strAudit = 'Delete device configuration for {0}'.format( device )
      auditTrail.AuditTrailAddEntry( strAudit )
    except:
      log.exception("Error in _deleteDeviceConfiguration")

  def createDefaultSyncBit(self, device):
    log.info('Adding Default syncVal enableBit for device ' + device)
    conn = dbUtils.getDeviceDatabaseConnection()
    #configBit1 = OrderedDict()
    cur = conn.cursor()
    #configBit1 = self.directory.getDeviceObject().getSyncDaily()
    cur.execute("select * from syncVal where deviceName = ?", (device,))
    row = cur.fetchone()
    if row == None:
      try:
        cur.execute("insert into syncVal VALUES (?, ?)", (device, 0))
        conn.commit()
        conn.close()
      except:
        log.exception("Error in createDefaultSyncBit")

  def getDeviceObjectByName(self, key):
    return self.directory.getDeviceObject(key)

  def getNetworkObjectByName(self, key):
    return self.directory.getNetworkObject(key)

  ###########################################
  # Device Database Blue-R
  def setDeviceDatabaseToFactorySettings(self) :
    conn = dbUtils.getDeviceDatabaseConnection()
    cur = conn.cursor()
    # Clear all user records.
    cur.execute('delete from configs')
    cur.execute('delete from idealConfigs')
    cur.execute('delete from syncVal')
    conn.commit()
    conn.close()
    dbUtils.vacuumDatabase( dbUtils.deviceDatabasePath ) # Compress database


