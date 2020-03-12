#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys

sys.path.append('system/devices')
sys.path.append('system/utils')

from deviceConstants import *
from networkConstants import *

import deviceObject
import deviceManager
import httplib
import json

import elapsedTimer
import time

import os
import csv

import sqlite3
import dbUtils
import auditTrail
import utilities
import copy
import systemConstants

from collections import OrderedDict
from collections import Counter

import logsystem

sys.path.insert(1, os.path.join(sys.path[0], 'system/devices/E2 Device'))
log = logsystem.getLogger()

import datetime
import pytz
from pytz import timezone
from datetime import datetime

deviceType = "E2"
deviceTypeName = deviceE2ExecutionText
executionType = deviceNetworkExecution
#deviceTypeName = deviceE2ExecutionText
#executionType = deviceE2Execution
# executionTypeName = deviceE2ExecutionText

E2_COMM_FAIL_ALM = 'E2 COMM FAILURE'
E2_STATUS_UPDATE_FILTER_SECS = (10) # 10 seconds is the most often an E2 status will be updated. We know it takes may take about 2-4 seocnds to get all the points -
                                   # and for a typical device updateStatus() gets called about once a second while on the device status page

GETALMDBFIELD_NAMES = 1
GETALMDBFIELD_TYPES = 2

UTC_TO_E2LOCAL_TIMESTAMP = 1
E2LOCAL_TO_UTC_TIMESTAMP = 2

# CREATING/ENCODING THE DYNAMIC E2 STATUS SCREEN LAYOUT IN LEO
APP_HEADER = 1
APP_TYPE = 2
SGL_STATUS = 3
DBL_STATUS = 4
SECT_HEADER = 5
STAGES_STATUS = 6
COMMENT_LINE = 7
MULTI_HEADER = 8
MULTI_VALUE = 9
MULTI_VALUE_STAR = 10

# For the E2 status screen commands.
# Ordered by what I beleve will be the ones seen most
dictStatusLineCmds = {'SglStatus': SGL_STATUS, 'DblStatus': DBL_STATUS, 'AppHeader': APP_HEADER,
                      'AppType': APP_TYPE, 'MultiTitle': MULTI_HEADER, 'MultiValue': MULTI_VALUE,
                      'MultiValueStar': MULTI_VALUE_STAR,
                      'StagesStatus': STAGES_STATUS, 'SectHeader': SECT_HEADER, '#': COMMENT_LINE}

#################################################################
# E2 Device
#################################################################

valueDescriptions = OrderedDict()
alarmDescriptions = OrderedDict()

# For E2 Device, the valueDescription list/dict variables will be created dynamically - currently based upon the status screen "dictionary"
# For alarms, this module will simply get the E2 alarm log and sychronize it with the Leo alarm database for the specific e2 device.
valueDescriptions["IncorrectType"] = {"dataType":dataTypeBool,"valueType":valueTypeOutput,"displayName":"Incorrect Type"}
alarmDescriptions[networkFailureKey] = {"description":""}

valueTypeInput = "input"
valueTypeOutput = "output"
valueTypeConfig = "config"


class Device(deviceObject.NetworkDeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, image,  method="",setValue=1):
    deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image)
    self.setValue = setValue
    self.method = method
   # log.debug(self.method)
    self.blStopE2Device = False
    # log.info( "Starting E2 Device:{0}, Network Address:{1}".format( name, networkAddress ) )

    # store the network address.
    self.E2ControllerName = name
    self.E2ControllerNameRcvd = self.E2ControllerName # initliaze to match until actually received from E2

    # We need to help the address...If there is no port number, add it.
    if networkAddress.find(":") >= 0 :
      self.networkAddress = networkAddress
    else:
      self.networkAddress = "{}:{}".format( networkAddress, E2_JSON_INTERFACE_PORT )

    # Create timer for limiting status updates for E2
    self.E2StatusUpdateFilter = elapsedTimer.Interval(E2_STATUS_UPDATE_FILTER_SECS)
    self.E2StatusUpdateFilter.elapse()

    # Get E2 init related information from databases
    self.InitE2TimeZones() # Read timezones table from database
    self.InitE2Device()
    self.InitE2DeviceSettings() # Read E2 Settings from database
    
    self.blInitE2Device = True
    self.userAction = None

    self._E2AppInfo = {}
    self._E2celltypes  = {}


  ###########################################################################################
  # The purpose of this method is to initialize the LEO E2 offline state based upon LEO generated alarms.
  ############################################################################################
  def initLeoAlarmDatabase( self, deviceName ) :

    # Init device object information
    self._alarmDescriptions = alarmDescriptions

    self.UpdateE2AlarmState()

    # Check for specific alarms in the list and initalize as appropriate.
    if networkFailureKey in self._alarms :
      # E2 Device has offline alarm.
      self.online = False
      self._alarms[networkFailureKey] = True
      self.E2CommState = "Offline"
      self.E2CommStateToOfflineTimer.elapse()
    else :
      self.online = True
      self._alarms[networkFailureKey] = False
      self.E2CommState = "Online"
      self.E2CommStateToOnlineTimer.elapse()

    self.RTOnline = self.online
    self.RTMsg = self.msg

    # print "*** initLeoAlarmDatabase ***: Online at init from leo alarm log:{0}, Messasge:{1}".format( self.online, self.msg )

  #################################################################
  # This function sets the device alarm state based upon a query of the LEO alarms database (for E2 alarms)
  # or a _alarms property in the case of device offline (even though the query should find this)
  #################################################################
  def UpdateE2AlarmState(self):
    try:
      # Let's determine if there are any active LEO alarms for this device.
      dictDBActiveAlmList = dbUtils.getAlarmEntries(dbUtils.GETE2DEVICEACTIVEALARMS, {'deviceName': self.E2ControllerName} )
    
      strNetworkFailDesc = ""
      alarmCount = 0
    
      # First, loop through the known alarms and make sure they are in the _alarms dict.
      activeAlarmList = []
      for alarmInfo in dictDBActiveAlmList:  # For each alarm record, see update _alarms
        alarmCount = alarmCount + 1
        activeAlarmList.append(alarmInfo['alarm'])
        self._alarms[alarmInfo['alarm']] = True
        if alarmInfo['alarm'] == networkFailureKey:  # Device offline alarm
          strNetworkFailDesc = alarmInfo['description']
    
      # Next, loop through all the _alarms entries. IF there is no matching alarm, clear the _alarms state.
      for currAlarm in self._alarms:  # For each alarm record, update _alarms
        if not currAlarm in activeAlarmList:
          self._alarms[currAlarm] = False  # Clear the alarm condition.
    
      # Set overall device alarm state based upon number of alarms.
      if alarmCount == 0:
        self._alarm = False
      else:
        self._alarm = True
    
      self.msg = strNetworkFailDesc
      self._alarmDescriptions[networkFailureKey]['description'] = strNetworkFailDesc
  
    except Exception, e:
      strExcept = "Error in setE2AlarmState: {0}".format(e)
      log.exception(strExcept)

  ###########################################################################################
  # The purpose of this method is to initialize the E2 device settings from the databases
  ############################################################################################
  def InitE2Device(self):
#    print "InitE2Device"
    self.InitE2DeviceSettings() # Make sure these settings are up to date from the database.

    # Determine current state of communications from looking for an active alarm in the database.
    if self.E2ControllerName is not None :
      self.InitE2AlarmDatabases( self.E2ControllerName ) # Setup database information
      self.initLeoAlarmDatabase( self.E2ControllerName ) # Ensure E2 specifc database records are initialized

      # setup informatioon for updating status screen data
      self.E2StatusScreenData = {}
      self.initE2CellTypeInfo()
      return True
    return False

  def E2AlarmDateToUTC( self, strAlarmDate ) :
    # Let's check for an "default" empty rtntimestamp. If no rtntimestamp, set to defualt.
    strReturn = ""
    if strAlarmDate.lstrip()  == "0:00" :
      strReturn = "2000-01-01 00:00:00"   # Virtually NONE. Need to filter at UI.
    else:
      # Good E2 timestamp; turn into proper formatted SQLite UTC format
      params = strAlarmDate.split(" ")  # params[0] = Date, if no leading zero, then params[1] = "" and params[2] = time ELSE params[1] = time
      if len(params) == 3 : # Need leading zero.
        strTime = "0" + params[2]
      else :
        strTime = params[1]
      # Parse the date into the proper UTC format
      dateFlds = params[0].split("-")
      strReturn = "20{}-{}-{} {}:00".format(dateFlds[2], dateFlds[0], dateFlds[1], strTime )
    return strReturn
  
  def InitE2AlarmDatabases(self, deviceName):
#    print "InitE2AlarmDatabases"
    self.alarmRecTableKey = ['advid']
    self.JSONBooleanFieldNames = ["reset", "notice", "unacked", "alarm", "rtn", "acked", "fail"]

    self.E2alarmRecTableName = 'E2AlarmEntryTable'
    self.E2RealTimeTableName = 'E2RealTimeInfo'  ### Stores last update time for alarms and status

    self.LEOalarmRecTableName = 'devicealarms'

    if len(self.alarmRecTableKey) > 1:
        self.strAlarmRecTableKey = ",".join(self.alarmRecTableKey)
    else:
        self.strAlarmRecTableKey = self.alarmRecTableKey

    conn = dbUtils.getE2AlarmDatabaseConnection()
    self.E2dbFieldNames = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_NAMES, self.E2alarmRecTableName)
    self.E2dbFieldTypes = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_TYPES, self.E2alarmRecTableName)

    # Let's make sure there is an entry in the alarm timestamp database for this E2Controller
    cur = conn.cursor()
    strSQL = 'SELECT COUNT(*) FROM {0} where controllerName="{1}"'.format(self.E2RealTimeTableName,
                                                                           deviceName )
    cur.execute(strSQL)
    numRecords = cur.fetchone()[0]

    if numRecords == 0 :
      try:
        strSQL = 'INSERT INTO ' + self.E2RealTimeTableName + ' (controllerName, LastUpdateTime, LastAlarmUpdateTime, LastStatusUpdateTime) VALUES ("' + deviceName + '", 0, 0, 0)'
        cur.execute(strSQL)
        conn.commit()
      except Exception, e:
        strBuf = "Error Creating Realtime Table Information - {} {}".format(e , deviceName )
        log.exception(strBuf)
    
    # We need to make sure all E2 alarms have their timestamps converted into UTC.
    # We didn't re-architect the database due to the extensive re-testing and validation required (e.g. not enough time)
    try:
      cur = conn.cursor()
      strSQL = 'SELECT dbTimestamp, rtntimestamp, advid, UTCdbTimestamp from E2AlarmEntryTable where advid > 0 and UTCdbTimestamp is null'
      cur.execute(strSQL)
      # Convert E2 Timestamp to UTC formatted timestamp - because sqlite cannot sort E2 timestamp.
      for alarmRec in cur.fetchall():
        alarm = dbUtils.dictFromRow(alarmRec)
        # E2 Alarm = 01-03-18  8:05, Need to convert to 2018-01-03 08:05:00 and add to newly created columns
        UTCdbTimestamp = self.E2AlarmDateToUTC( alarm['dbTimestamp'] )
        UTCrtntimestamp = self.E2AlarmDateToUTC( alarm['rtntimestamp'] )
        strSQL = 'update E2AlarmEntryTable set UTCdbTimestamp="{}", UTCrtntimestamp="{}" where advid = {}'.format( UTCdbTimestamp, UTCrtntimestamp, alarm['advid'] )
        cur.execute(strSQL)
      conn.commit()
    except Exception, e:
      strBuf = "Error Updating UTC date fields {} for ({})".format(e , deviceName )
      log.exception(strBuf)

    conn.close()

    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()
    self.LEOdbFieldNames = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_NAMES, self.LEOalarmRecTableName)
    self.LEOdbFieldTypes = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_TYPES, self.LEOalarmRecTableName)
   
    conn.close()


  def openE2Connection(self):
      # Let's make sure we have a connection
      if self.E2Connection is None:
          try:
              self.E2Connection = httplib.HTTPConnection(self.networkAddress, timeout=self.IPConnectionTimeout)
          except Exception, e:
              strBuf = "Error Opening HTTP Connection to {0}. Err:{1}".format(self.networkAddress, e)
              log.exception(strBuf)
              self.E2Connection = None

  def _adjustDisplayNames(self):
    # Nothing special to do here for the E2 devices
#    log.debug( "Do I need to adjust display names for E2?" )
    dummy = 1

  def setConfigValues(self, values):
    deviceObject.DeviceObject.setConfigValues(self, values)

  def _prepareJsonRequest(self, tag, method, params = ['']):
    self.jsonId = tag
    request = {'id': tag, 'method': method, 'params': params, 'addr':self.networkAddress }
    nm = NetworkMessage(request, tag)
#    strInfo = "_prepareJsonRequest: {0}, Req:{1}".format( nm, request)
#    log.info( strInfo )
    return nm

  def _addStatusToNetworkTransaction(self, networkTrans):
    if hasattr( self, '_listAppPathNameQueryProps') is True :
      for appPath in self._listAppPathNameQueryProps :
        i = 0
        while i < len( self._listAppPathNameQueryProps[appPath] ) :
          params2Send = self._listAppPathNameQueryProps[appPath][i]
          i = i + 1
          networkTrans.transactions.append(self._prepareJsonRequest('GetMultiExpandedStatus', 'E2.GetMultiExpandedStatus', [params2Send]))

  def _addGetE2InfoToNetworkTransaction(self, networkTrans ) :
    networkTrans.transactions.append(self._prepareJsonRequest('GetThisControllerName', 'E2.GetThisControllerName', '[[]]'))
    networkTrans.transactions.append(self._prepareJsonRequest('GetConfigValues', 'E2.GetConfigValues', [[self.E2ControllerName + ':' + 'TIME SERVICES:Time Zone']] ))
    networkTrans.transactions.append(self._prepareJsonRequest('GetCellList', 'E2.GetCellList', [self.E2ControllerName] ))

  def _getE2ControllerName(self):
    return self.E2ControllerName

  # This method is required to sit on top of the NetworkTransaction instantiation
  # because E2 transations need the IP address to be part of the networkTransaction message
  def InitE2NetworkTransaction(self, tag):
    networkTrans = NetworkTransaction(tag)
    networkTrans.networkAddress = self.networkAddress
    return networkTrans

  def _prepareLoggingTransactions(self, valueToLog):
    networkTrans = self.InitE2NetworkTransaction("Logging")
    self._addStatusToNetworkTransaction(networkTrans)
    return [networkTrans]

  def _prepareSetDeviceConfigurationTransactions(self):
#    log.debug( "Do Nothing" )
    return []

  def _prepareUpdateDeviceConfigurationTransactions(self):
#    log.debug( "Do Nothing" )
    return []

  # We have to filter how often we create all the E2 get values messages - since it can be lengthy to get this information.
  # We will not allow a device to update in less than X seconds - in case this method is being call too often.
  def _prepareUpdateStatusTransactions(self):
    networkTrans = self.InitE2NetworkTransaction("Status")
    if self.E2StatusUpdateFilter.hasElapsed() is True:
      self.E2StatusUpdateFilter.reset()           # Reset the timer
      self._addStatusToNetworkTransaction(networkTrans)
#    else:
#      log.debug( "+++ _prepareUpdateStatusTransactions FILTERED +++" )
#    strDebug = "--- Added Status - {0} Transactions".format( len( networkTrans.transactions ) )
#    log.info( strDebug )
    return [networkTrans]

  def _prepareUpdateAlarmsTransactions(self):
    networkTrans = self.InitE2NetworkTransaction("Alarms")
    # Refresh E2celltypes and timezone at a periodic interval.
    self._addGetE2InfoToNetworkTransaction(networkTrans)
    paramStr = '["{0}", {1}]'.format(self.E2ControllerName, self.blE2GetAdvisoryOrAnnunciatorLog )
    networkTrans.transactions.append(self._prepareJsonRequest('GetAlarmList', 'E2.GetAlarmList', paramStr ))
#    strInfo = "networkTrans:{0}, Len:{1}".format( networkTrans, len(networkTrans.transactions) )
#    log.info( strInfo )

    return [networkTrans]

  def _logdebug(msg):
    log.debug(msg)

  def _setOutputValue(self, key, value, engunit, dataType, unitType ):

    try:
      if value == 'NONE':
        value = None
        self._values[key] = value
        return
  
      if dataType == 2:
        splitUnits = engunit.split('/')
        value = True if splitUnits[0] == value else False
  
      valueDesc = self._valueDescriptions[key]
  
      if valueDesc["dataType"] == dataTypeFloat:
        value = float(value)
  
        if engunit == 'DF':
          value = self._convertF2C(value)
        elif engunit == 'DDF':
          value = self._convertDeltaF2C(value)
        elif engunit == 'PSI' : # Convert to pascals
          value = self._convertPSI2PA(value)
        elif engunit == 'KPA' : # Need everything in PA (Pascal for precision)
          value = self._convertKPA2PA(value)
        elif engunit == 'PPM' : # No translation needed.
          notneeded = 1

        self._values[key] = round( value, int(valueDesc["significantDigits"]) )
  
      elif valueDesc["dataType"] == dataTypeBool:
        if valueDesc["unitType"] == "OnOff":
          if value == "OFF":
            self._values[key] = "Off"
          elif value == "ON":
            self._values[key] = "On"
          else:
            self._values[key] = "NA"
        elif valueDesc["unitType"] == "ActiveInactive":
          if value == "ACTIVE":
            self._values[key] = "Active"
          elif value == "INACTV":
            self._values[key] = "Inactive"
          else:
            self._values[key] = "NA"
        elif valueDesc["unitType"] == "LossOk":
          if value == "LOSS":
            self._values[key] = "Loss"
          elif value == "OK":
            self._values[key] = "Ok"
          else:
            self._values[key] = "NA"
        else:
          self._values[key] = False if value == 0 else True
      elif valueDesc["dataType"] == dataTypeInt:
        self._values[key] = int(value)
      elif valueDesc["dataType"] == dataTypeList:
        self._values[key] = int(value)
      else:
        self._values[key] = value

    except Exception, e:
      strBuf = "_setOutputValue exception - {0} ({1})-PropInformation:{2}, {3}, {4}, {5}".format(e, self.E2ControllerName, key, value, engunit, dataType)
      log.exception(strBuf)

  def _executeTransaction(self, networkTrans):

    # print "*** Execute Transactions for E2. networkTrans.online-->", networkTrans.online
      # Default to current filter online status and msg as well as real-time online status and msg
    online = self.online
    currMsg = self.msg

    RTOnline = self.RTOnline
    RTMsg = self.RTMsg
    numMessages = 0

    try:
      if not networkTrans.online:
        self._nullOutputValues()
        RTOnline = False
        RTMsg = networkTrans.offlineMessage
      else:
        numMessages = len(networkTrans.transactions)
#        strInfo = "Number of Messages To Receive:{0}".format( numMessages )
#        log.debug( strInfo )

        # if there are messages to prcoess
        if numMessages > 0 :
          # Messages were sent, loop through the transactions and responses
          for transaction in networkTrans.transactions:
            with self.lock:
              response = transaction.response

              if response is not None :
                # Let's update the E2ControllerNameRcvd variable if the message is a GetControllerName. Otherwise, we won't update E2ControllerNameRcvd.
                if transaction.tag == 'GetThisControllerName':
                  self.E2ControllerNameRcvd = transaction.response['result']
                  
              # Message sent with no response OR the initailized E2 controller name does NOT match the name recevied in the response.
              if response is None or self.E2ControllerName != self.E2ControllerNameRcvd :
                iDummy = 1
                RTOnline = False
                RTMsg = networkFailureKey
  #              strInfo = "RECEIVE IS NONE. THIS IS VERY, VERY BAD. Trans:{0}, Request:{1}".format( transaction, transaction.request )
  #              log.info( strInfo )
              else :
                if transaction.tag == 'GetMultiExpandedStatus' : # Let's abbreviate multiexpandedstatusmessages...
                  iDummy = 2
#                  strInfo = "E2 RECEIVE-->Trans:{0}, GetMultiExpandedStatus Len:{1}".format(transaction,len(response))
#                  log.info( strInfo )
                else:
                  iDummy = 3
#                  strInfo = "E2 RECEIVE-->Trans:{0}, Request:{1}, Len:{2}".format( transaction, transaction.request, len( response ) )
#                  log.info( strInfo )

                if response.has_key('error') and 'RSP_INVALID_NAME' in response['error']['msg']:
                  self._nullOutputValues()
                  RTOnline = False
                  RTMsg = "E2 controller or application does not exist - Confirm consistent naming with E2"
                else:
                  if len( response ) > 0 :
                    RTOnline = True     # We get a message. We are talking. Move towards online...
                    result = response['result']
                    # print "E2 _executeTransactions result = ", result

                    if transaction.tag == 'GetMultiExpandedStatus' :
                      data = result['data']
                      self.ProcessE2GetMultiExpandedStatus( data )

                    elif transaction.tag == 'GetConfigValues':
                      # print 'ConfigValues = ', result['data']
                      data = result['data']
                      if len(data) > 0 :
                        self.ProcessE2GetConfigValues( data )


                    elif transaction.tag == 'GetCellList':
                      # print "celltypes = ", result['data']
                      data = result['data']
                      if len( data ) > 0 :
                        self.ProcessE2GetCellList( data )

                    elif transaction.tag == 'GetThisControllerName':
                      self.E2ControllerNameRcvd = result

                    elif transaction.tag == 'GetAlarmList':
                      # print "Process E2GetAlarmList"
                      # log.info( "Proocess E2GetAlarmList" )
                      data = result['data']
                      if len( data ) > 0 :
                        self.ProcessE2GetAlarmList( data )

                    else :
                      print "***** UNPROCESSED TRANSACTION.TAG *****-->", transaction.tag
#                  else:
#                    print "***** ERROR No response to -->", transaction.request
        else:
          iDummy = 4
          # There were no messages to process. No changes to the states

        # update the alarm status.
        self.UpdateE2AlarmState()

    except Exception, e:
      strBuf = "exception - {0} ({1})".format(e, self.E2ControllerName )
      log.exception(strBuf)

    # For E2, we are going to add some filtering here to avoid nuisance alarms caused by periodic "hiccups"
    # RTOnline will be the "raw" communications state of messages sent.
    # self.E2CommState will represent the current communications state machine that represents either online or offline or the a transition state.
    # online will be the filtered boolean online (True) or offline (False) translated from the E2CommState Online or Offline
    # Therefore, the return value "online" will be the "filtered" online state for the E2.

    # We will only transition comm state if there were messages sent/processed OR the network is offline.
    if numMessages > 0 or networkTrans.online is False :
      # log.debug( "+++ Processing Transition - RTOnline:{0}, CommState:{1}, Num Msgs:{2}, ToOnlineTimer:{3}, ToOfflineTmer:{4}".format ( RTOnline, self.E2CommState,
      #               numMessages, self.E2CommStateToOnlineTimer.getTimeRemainingSecs(), self.E2CommStateToOfflineTimer.getTimeRemainingSecs() ) )
      if RTOnline is True : # GOOD MESSAGE PROCESSED
        if self.E2CommState == "Online" : # All good. Update filtered state
          online = True
          currMsg = ""
        elif self.E2CommState == "Offline" : # Good message, but current state is offline; restart to online timer
          self.E2CommState = "ToOnline"
          self.E2CommStateToOnlineTimer.setTimeout( (self.E2DevOfflineRTNDelay * 60) - 2 )
          self.E2CommStateToOnlineTimer.reset()
        elif self.E2CommState == "ToOnline" : # Comm is good but are still considered offline until timer elapses.
          if self.E2CommStateToOnlineTimer.hasElapsed() :
            self.E2CommState = "Online"
            online = True
            currMsg = ""
        elif self.E2CommState == "ToOffline":  # Comm is now good, but was heading offline. Reset and move toward online
          self.E2CommStateToOnlineTimer.setTimeout( (self.E2DevOfflineRTNDelay * 60) - 2  )
          self.E2CommStateToOnlineTimer.reset()
          self.E2CommState = "ToOnline"
      elif RTOnline is False : # bad communications.
        if self.E2CommState == "Offline" : # Offline and still no good messages.
          online = False
          currMsg = "LEO is unable to communicate with E2"
        elif self.E2CommState == "Online" : # current state is online; restart timer to transition to offline
          # We are "considered" online and have problems, start the transition to offline.
          self.E2CommState = "ToOffline"
          self.E2CommStateToOfflineTimer.setTimeout( (self.E2DevOfflineAlmDelay * 60) - 2  )
          self.E2CommStateToOfflineTimer.reset()
        elif self.E2CommState == "ToOffline" : # Comm is bad and heading to offline.
          if self.E2CommStateToOfflineTimer.hasElapsed() :
            self.E2CommState = "Offline"
            online = False
            currMsg = "LEO is unable to communicate with E2"
        elif self.E2CommState == "ToOnline":  # Was trying to go online, but got bad message. Start Transition back to offline
          self.E2CommStateToOfflineTimer.setTimeout( (self.E2DevOfflineAlmDelay * 60) - 2 )
          self.E2CommStateToOfflineTimer.reset()
          self.E2CommState = "ToOffline"
    else:
      nothingToDoHere = 1
      # log.debug( "NO TRANSITION CHANGE: {0}, numMessages:{1}, networkTrans.online:{2}, RTOnline:{3}".format( self.E2CommState, numMessages, networkTrans.online, RTOnline ) )

    if RTOnline is True:
      breakMe = 1
    else:
      breakMe = 2
      
    # log.debug("----- executeXaction - name:{}, self.online->{}, numMessages:{} -----".format( self.name, self.online, numMessages ))
    # log.debug(" self.E2CommState:{}, RTOnline:{}, online:{} ".format( self.E2CommState, RTOnline, online ))
    # log.debug(" RTMsg:{}, currMsg:{}".format( RTMsg, currMsg ))
    # log.debug(" ToOnlineTimer Secs Remaining:{}, ToOFFLINETimer Secs Remaining:{}".format(
    #    self.E2CommStateToOnlineTimer.getTimeRemainingSecs(), self.E2CommStateToOfflineTimer.getTimeRemainingSecs() ))
    
    return {'online': online, 'message': currMsg }


  def ProcessE2GetMultiExpandedStatus( self, data ) :
    if len( data ) > 0 :
      # Read the response and update the status values in memory
      for propertyStatus in data:
        #log.debug(propertyStatus)
        params = propertyStatus['prop'].split( ":" ) # Param[0] = controller, Param[1] = appName, Param[2] = property
        controller = params[0]
        appName = params[1]
        appName = appName.replace('"','')
        prop = params[2]
        appNameProp = '{0}:{1}'.format( appName, prop )
        #log.debug(self._valueDescriptions[appNameProp])
        dataType = self._valueDescriptions[appNameProp]['dataType']
        unitType = self._valueDescriptions[appNameProp]['unitType']
        # if appName == "RLDS001":
          # print "Got Value for :", appNameProp, propertyStatus['value'], dataType, unitType
        self._setOutputValue( appNameProp, propertyStatus['value'], propertyStatus['engUnits'], dataType, unitType)
        #strDebug = "_setOutputValue: key:{0}, value:{1}, engunit:{2}, dataType:{3}, unitType:{4} - Values:{5}".format( key, value, engunit, dataType, unitType, self._values[key] )
        #log.debug( strDebug )

  def ProcessE2GetConfigValues( self, data ) :
    # Let's look specifically to process the time zone get config request
    if data[0]['prop'].find("Time Zone") >= 0 :
      E2temp = data[0]['value'] # Get Timezone
      E2temp = E2temp.split(' ')      # First part is the +x:xx offset. We don't need this.
      strE2TimeZone = E2temp[1]
      if strE2TimeZone != self.E2TimeZone :
        self.E2TimeZone = strE2TimeZone
        try:
          self.E2PythonTimeZone = self.e2TimeZoneNameDict[ self.E2TimeZone ]['pyTimeZone']
        except Exception, e:
          strExcept = "Error in Converting Timezone: {0}".format( e )
          log.exception(strExcept)

  def ProcessE2GetCellList( self, celltypes ) :

    # If there are no changes in the cell list, we dont need to anything.
    if self._E2celltypes != celltypes:

      self._E2celltypes = celltypes

      self._E2AppInfo['controllerName'] = self.E2ControllerName
      self._E2AppInfo['cellTypeAppList'] = {}

      # Let's create "empty" sets of ALL celltypes from the E2 app init file. This is so that
      # EVERY cell type possible (regardless whether it is in the E2 cell list) can be checked for length
      # to determine if there are apps for a certain cell type.
      # So, loop through all cell types found in the device csv file and add an entry in E2AppInfo for that app type.
      for cellTypeNum in self._E2CellTypeInfo['numList'] :
        self._E2AppInfo['cellTypeAppList'][str(cellTypeNum)] = []

      # Now, run through the celltype list and load up the cell type properties in the _E2AppInfo dict.
      for celltype in celltypes:
        strCellTypeNum = str(celltype['celltype'])
        # IF this celltype is something we are interested in, then add it to the E2AppInfo cellTypeAppList
        if strCellTypeNum in self._E2CellTypeInfo['numList'] :
          if strCellTypeNum not in self._E2AppInfo['cellTypeAppList'] :
            self._E2AppInfo['cellTypeAppList'][strCellTypeNum] = []
          #celltype['cellname'] = celltype['cellname'].replace('"','')
          self._E2AppInfo['cellTypeAppList'][strCellTypeNum].append( celltype['cellname'] )
          self._E2AppInfo[celltype['cellname']] = { 'cellTypeNum' : strCellTypeNum }
          self._E2AppInfo[celltype['cellname']] = { 'cellTypeName' : self._E2CellTypeInfo[strCellTypeNum] }

      # Last, create the list of properties that are needed to get the current values.
      self._createE2AppQueryProps()

      # Elapse the timer so that we can send messages to get status values
      self.E2StatusUpdateFilter.elapse()

      # initiate a status update.
      self.updateStatus()

      blPrintResults = False
      if blPrintResults is True :
        print "self._E2celltypes->", self._E2celltypes
        print "self._listAppPathNameQueryProps->", self._listAppPathNameQueryProps
        print "self.E2AppInfo-->", self.E2AppInfo

  def ProcessE2GetAlarmList( self, data ) :

    self.E2JSONAlmList = data

    if len(self.E2JSONAlmList) > 0 :               # E2 Alarm and LEO Database Synchronization operations

      # Before we process the alarms, we need to handle some issues we have found in the syntax of the alarm list
      # as sent by E2
      # 1. the ackuser and other E2 strings cannot contain a ' (single quote) -- this does really bad things.
      # 2. E2 can be put into AM/PM mode - instead of 24 hours. So we have to strip off the A or P and
      # update the time and dates to military times.
      # For the sake of SQLite, we also need to make sure that none of the strings have a single quote as part of the string. We will simply remove these.
      for E2AlmRec in self.E2JSONAlmList :

        # First, check to make sure no ' in fields where there "might" be single quotes.
        listStrChkKeys = [ "ackuser", "source", "text" ]
        for strChkKey in listStrChkKeys :
          singleQuoteLoc = E2AlmRec[strChkKey].find("'")

          # Remove all single quotes from the string
          while singleQuoteLoc >= 0:
            if singleQuoteLoc == 0:
              E2AlmRec[strChkKey] = ' '
            else:
              E2AlmRec[strChkKey] = E2AlmRec[strChkKey][0:singleQuoteLoc] + " " + E2AlmRec[strChkKey][singleQuoteLoc + 1:]
            singleQuoteLoc = E2AlmRec[strChkKey].find("'")

        # Second, make sure we fix up 12 hour times to military times.
        listTimeKeys = [ "timestamp", "acktimestamp", "rtntimestamp" ]
        for timeKey in listTimeKeys :
          if E2AlmRec[timeKey].rfind("A") >= 0 :
            ltrLoc = len( E2AlmRec[timeKey] )
            E2AlmRec[timeKey] = E2AlmRec[timeKey][:ltrLoc-1]
          elif E2AlmRec[timeKey].rfind("P") >= 0 :
            ltrLoc = len( E2AlmRec[timeKey] )
            E2AlmRec[timeKey] = E2AlmRec[timeKey][:ltrLoc-1]
            # Convert time
            # Add 12 hours
            
            
      # We will only synchornize when we get the E2 alarm log
      # The E2 Synchornization makes sure that what is in the E2 (and only alarms for "this controller")
      # is an exact copy in LEO's E2 Alarm Log (NOT in the LEO alarm log)
      self._E2AlarmRecordTableSynchronize(self.E2JSONAlmList)

      # Now we want to clear out entries that are meant to be filtered based upon E2Settings
      # (e.g. filter notice, alarm, fail, etc)
      # We will remove all of these E2 alarm entries that do not pass the filter settings.
      self.E2JSONAlmListFiltered = []
      for E2AlmRec in self.E2JSONAlmList :
        # Check to see if record can pass through the filter
        # This is the E2 alarm filter.
        blKeep = self._CheckE2AlmRecWithFilters( E2AlmRec )
        if blKeep == True :
            self.E2JSONAlmListFiltered.append( E2AlmRec )

#                print "E2FilteredAlarmList-->", self.E2JSONAlmListFiltered
      self._LEOToE2DBAlarmRecordTableSynchronize(self.E2JSONAlmListFiltered)

    else :
      # We will NOT synchornize when we don't get the E2 alarm log
      self.E2JSONAlmList = {}

  def performUserAction(self, data):
    self.userAction = data
    return data

  def _prepareActionTransactions(self):
    retval = []
    if self.userAction is not None:

      self.userAction = None
    return retval

  def _convertF2C(self, value):
    if value is None: return None
    return (value - 32) / 1.8

  def _convertC2F(self, value):
    if value is None: return None
    return (value * 1.8) + 32

  def _convertDeltaF2C(self, value):
    if value is None: return None
    return value / 1.8

  def _convertDeltaC2F(self, value):
    if value is None: return None
    return value * 1.8

  # Convert to pascals
  def _convertPSI2PA(self, value):
    if value is None: return None
    return value * 6894.7

  # Convert to pascals
  def _convertKPA2PA(self, value):
    if value is None: return None
    return value * 1000

  ######################################################################
  # E2 Alarm Handling functions
  #
  # The following are functions for managing and obtaining
  # the alarm records from the E2 and mapping to the LEO alarm database
  ######################################################################

  # This method simply returns the E2 "static" datastructures which are the following:
  def GetE2DataStructs(self, strDataStruct ) :
    retDict = {}

    if strDataStruct == "E2CellTypeInfo" :
      retDict['E2CellTypeInfo'] = self._E2CellTypeInfo
    elif strDataStruct == "E2AppInfo" :
      retDict['E2AppInfo'] = self._E2AppInfo

    return retDict

  # This method is called from a JSON/POST call to get the latest values for the E2
  def getE2StatusScreenData(self) :
    # Whenever we get this call, increase the refresh rate. We will
    # change the interval timer back if we do not hit this refresh for 15 seconds
    print "***** IS THIS BEING CALLED???  getE2StatusScreenData CALLED. Online= ", self.online
    if self.online == True :
      try:
          self.E2StatusScreenData['E2CellTypeInfo'] = self._E2CellTypeInfo
          self.E2StatusScreenData['E2AppInfo'] = self._E2AppInfo
          self.E2StatusScreenData['online'] = self.online
          return self.E2StatusScreenData
      except Exception, e:
        strExcept = "Exception: {0}".format( e )
        log.exception(strExcept)
        return None

    else :
#          print "GetE2DataStructs Returned NONE"
        return None

  def getE2ControllerName(self):
    return self.E2ControllerName

  def getE2celltypes(self):
    return self._E2celltypes

  def newLeoAdvisory(self, alarm, description):
    self.newAdvisory( alarm, description )

  def rtnLeoAdvisory(self, alarm, description):
    self.rtnAdvisory( alarm, description )

  def _execute(self, inputValues, outputValues, configValues ): # Currently runs once a second.
#    print "E2 Device: _execute called for ", self.E2ControllerName

    if self.blStopE2Device is True:
#      print "_execute() for ", self.E2ControllerName, "has been STOPPED"
      return

  # This will compare an E2 Alarm JSON record against the user defined filter options
  # The function returns True if the record is supposed to be kept (placed into LEO Alarm Log)
  def _CheckE2AlmRecWithFilters( self, E2AlmRec ):
    blKeepRecord = True

    # The first thing we will do is filter out alarms that are not part of this controller.
    # If the controller name IS NOT in the alarm name, we filter it out. We only want only alarms
    # for "this controller"
    if E2AlmRec['source'].find( self.E2ControllerName ) != 0 :
      blKeepRecord = False
    if E2AlmRec['rtn'] == True and self.blE2AlarmFilterRTN > 0 :
      blKeepRecord = False
    elif E2AlmRec['fail'] == True and self.blE2AlarmFilterFail > 0 :
      blKeepRecord = False
    elif E2AlmRec['notice'] == True and self.blE2AlarmFilterNotice > 0 :
      blKeepRecord = False
    elif E2AlmRec['alarm'] == True and self.blE2AlarmFilterAlarm > 0 :
      blKeepRecord = False
    elif E2AlmRec['priority'] > self.iE2AlarmPriorityFilter :
      blKeepRecord = False

    return blKeepRecord


  @staticmethod
  def _E2AlarmDictFromRow(row):  # row = cur.fetchone()
      return OrderedDict(zip(row.keys(), row))

  @staticmethod
  def _GetAlmDbFieldInfo(conn, iTypeOfInfo, alarmRecTableName):

      retdbFieldInfo = ""

      cur = conn.cursor()

      # result [x][0] = RowId, [x][1] = Field Name, [x][2] = Field Data Type, [x][3] = Field Required,
      # [x][4] = Field Default Value, [x][5] = Primary Key Indicator
      sqlQuery = 'PRAGMA table_info({0})'.format(alarmRecTableName)
      try:
          cur.execute(sqlQuery)
          result = cur.fetchall()

          if iTypeOfInfo == GETALMDBFIELD_NAMES:
              retdbFieldInfo = ([[x][0][1] for x in result])
          elif iTypeOfInfo == GETALMDBFIELD_TYPES:
              retdbFieldInfo = ([[x][0][2] for x in result])
      except:
          log.exception("Exception")

      return retdbFieldInfo

  def _E2CompareAlarmRecordTableEntry(self, JSONE2AlmRec, orderedDictDBAlmRec):
      # This function compares an orderedDict alarm record (from the database) with the JSON Alarm record obtained
      # (from the E2)

      # First go through all boolean fields and change them from 0/1 to False/True
      for field in self.JSONBooleanFieldNames:
          if orderedDictDBAlmRec[field] == 0:
              orderedDictDBAlmRec[field] = False
          else:
              orderedDictDBAlmRec[field] = True

      blMatch = True
      for field in JSONE2AlmRec.keys():  # E2 Alarm record is subset of database fields...
          # Now loop through all the properties and verify they match
          if field.find('state') == 0:
              if orderedDictDBAlmRec['dbState'] != JSONE2AlmRec[field]:
                  xStr = "*** No Match - |{0}|: |{1}| != |{2}|".format(field, orderedDictDBAlmRec[field],
                                                                       JSONE2AlmRec[field])
#                  log.debug( xStr )
                  blMatch = False
                  break
          elif field.find('timestamp') == 0:  # make sure it is not rtntimestamp
              if orderedDictDBAlmRec['dbTimestamp'] != JSONE2AlmRec[field]:
                  xStr = "*** No Match - |{0}|: |{1}| != |{2}|".format(field, orderedDictDBAlmRec[field],
JSONE2AlmRec[field])
#                  log.debug( xStr )
                  blMatch = False
                  break
          elif field.find('limit') == 0:
              if orderedDictDBAlmRec['dbLimit'] != JSONE2AlmRec[field]:
                  xStr = "*** No Match - |{0}|: |{1}| != |{2}|".format(field, orderedDictDBAlmRec[field],
                                                                       JSONE2AlmRec[field])
#                  log.debug( xStr )
                  blMatch = False
                  break
          else:
              if orderedDictDBAlmRec[field] != JSONE2AlmRec[field]:
                  xStr = "*** No Match - |{0}|: |{1}| != |{2}| (AdvID:{3})".format(field, orderedDictDBAlmRec[field],
                                                                       JSONE2AlmRec[field], JSONE2AlmRec['advid'])
#                  log.debug( xStr )
                  blMatch = False
                  break

      return blMatch

  def _E2DeleteAlarmRecordTableEntry(self, conn, advid, dbTimeStamp):
    cur = conn.cursor()

    try:
      if dbTimeStamp == None:
        strSQL = 'Delete FROM {0} WHERE advid={1} and controllerName="{2}"'.format(self.E2alarmRecTableName, advid, self.E2ControllerName )
      else:
        strSQL = 'Delete FROM {0} WHERE advid={1} and dbTimeStamp="{2}" and controllerName="{3}"'.format(self.E2alarmRecTableName, advid,
                                                                                  dbTimeStamp, self.E2ControllerName )
      cur.execute(strSQL)
      recResult = cur.fetchone()
      conn.commit()
    except:
      log.exception("Exception")

  # JSONAlmRec is a single records with the same advid AND CONTROLLER NAME that needs to be added or updated in the database.
  # This method will make sure that there are entries in the E2 database for the entries in the JSONAlmRec
  def _E2UpdateAlarmRecordTableEntry(self, conn, JSONAlmRec, blForceInsert):
    cur = conn.cursor()

    if blForceInsert is True :
        # Caller knows this record needs to be inserted
        blInsertRecord = True
    else :
        # Caller is not sure if this record needs to be inserted. Look for matching record in database
        # Get the database records for this advid and timestamp
        strSQL = 'SELECT * FROM {0} WHERE advid={1} AND dbTimeStamp="{2}" and controllerName="{3}"'.format(self.E2alarmRecTableName,
                                                                                  JSONAlmRec['advid'], JSONAlmRec['timestamp'], self.E2ControllerName )
        cur.execute(strSQL)
        DBadvidRecs = cur.fetchone()

        # If there are no records for the advid in the database, we simply need to add the new records.
        if DBadvidRecs == None :
            blInsertRecord = True
        else:
            # there are record(s) for the advid in the database. Now we need to match the advid and dbTimestamp with the JSONAlmRecs.
            # This could mean adding or deleting records.
            blInsertRecord = False


    # First, let's create a copy of the JSONAlmRec that we will match more closely to a database record.
    # change all True and False strings to 1 and 0, rename some fields and add controller name
    tmpJSONAlmRec = copy.deepcopy(JSONAlmRec)
    for key in tmpJSONAlmRec:
        if tmpJSONAlmRec[key] == False:
            tmpJSONAlmRec[key] = 0
        if tmpJSONAlmRec[key] == True:
            tmpJSONAlmRec[key] = 1

    # Next replace the some record names with their appropriate DB field names
    tmpJSONAlmRec['dbState'] = tmpJSONAlmRec['state']
    tmpJSONAlmRec.pop('state', None)
    tmpJSONAlmRec['dbLimit'] = tmpJSONAlmRec['limit']
    tmpJSONAlmRec.pop('limit', None)
    tmpJSONAlmRec['dbTimestamp'] = tmpJSONAlmRec['timestamp']
    tmpJSONAlmRec.pop('timestamp', None)
    tmpJSONAlmRec['UTCdbTimestamp'] = self.E2AlarmDateToUTC( tmpJSONAlmRec['dbTimestamp'] )
    tmpJSONAlmRec['UTCrtntimestamp'] = self.E2AlarmDateToUTC( tmpJSONAlmRec['rtntimestamp'] )
    
    # Add additional DB record information
    tmpJSONAlmRec['controllerName'] = self.E2ControllerName

    # Let's add or update the record in the database
    if blInsertRecord == True:  # We need to insert the record
        # Format the SQL statement
        columns = ', '.join(tmpJSONAlmRec.keys())
        placeholders = ':'+', :'.join(tmpJSONAlmRec.keys())
        strSQL = 'INSERT INTO ' + self.E2alarmRecTableName + '(%s) VALUES (%s)' % (columns, placeholders)
#          print strSQL
        cur.execute(strSQL, tmpJSONAlmRec)
    else:
        # Record found in database. Update the record's values. Let's format the SQL Statement to update database.

        # Add database fields not found in the JSONAlmRec
        strFieldUpdates = "controllername='{0}',".format( self.E2ControllerName )

        for almKey in tmpJSONAlmRec.keys():
            if type(tmpJSONAlmRec[almKey]) is int :
                strFieldUpdates = "{0} {1}={2},".format(strFieldUpdates, almKey, tmpJSONAlmRec[almKey])
            else :
                strFieldUpdates = "{0} {1}='{2}',".format(strFieldUpdates, almKey, tmpJSONAlmRec[almKey])

        # Remove last comma
        strFieldUpdates = strFieldUpdates[0:strFieldUpdates.rfind(",")]

        strSQL2 = "UPDATE {0} SET {1} where advid={2} and dbTimeStamp='{3}' and controllerName='{4}'".format(self.E2alarmRecTableName,
                                                       strFieldUpdates, tmpJSONAlmRec['advid'], tmpJSONAlmRec['dbTimestamp'], self.E2ControllerName )
#          print "update advid={0}, {1}".format( JSONAlmRec['advid'], strSQL2)
        try:
          cur.execute(strSQL2)
          conn.commit()
        except sqlite3.OperationalError, e:
          strExcept = "SQL Operational Error Exception: {0} - s:{1}, r:{2}".format( str(e), strSQL2, tmpJSONAlmRec )
          print strExcept
          log.exception( strExcept )
        except Exception, e:
          strExcept = "Exception: {0}, s:{1}, r:{2}".format( str(e), strSQL2, tmpJSONAlmRec )
          log.exception( strExcept )


  # This function will simply confirm that the database is consistent between the JSON received from the E2
  # and the LEO E2 alarm database.

  # log.debug('Start _E2AlarmRecordTableSynchronize')
  def _E2AlarmRecordTableSynchronize(self, JSONE2AlmList):

      numDBAlarmList = 0
      dbAdvid = []

      # Now we want to go through the database and ensure it is in synch between the JSON and individual fields stored
      # First, let's count the number of records.
      conn = dbUtils.getE2AlarmDatabaseConnection()
      cur = conn.cursor()

      # Get the number of records
      try:
          strSQL = 'SELECT Count(*) FROM {0} where controllerName="{1}"'.format(self.E2alarmRecTableName, self.E2ControllerName)
          cur.execute(strSQL)
          numDBAlarmList = cur.fetchone()[0]
      except Exception, e:
        strExcept = "Exception: ".format( str(e) )
        log.exception( strExcept )

      numJSONAlmList = len(JSONE2AlmList)
#      print "E2 ALM SYNC: DB Count:", numDBAlarmList, "JSON Count:", numJSONAlmList

      # We need to confirm that the advIDs are the same.
      JSONE2AlmAdvidList = [x['advid'] for x in JSONE2AlmList]
      JSONE2AlmAdvidList.sort()

      try:
        strSQL = 'SELECT advid FROM {0} where controllerName="{1}"'.format(self.E2alarmRecTableName, self.E2ControllerName)
        cur.execute(strSQL)
        dbAdvidList = [x[0] for x in cur.fetchall()]
        dbAdvidList.sort()
      except Exception, e:
        strExcept = "Exception: ".format( str(e) )
        log.exception( strExcept )

      # Counter creates a dict for each advid which is indexed (key) by advid and the value is the number of instances in the advid list.
      # This is how we manage duplicate advids in the list.
      counterdbAdvid = Counter(dbAdvidList)

      counterJSONE2Advid = Counter(JSONE2AlmAdvidList)

      # Let's see what are the differences in the alarm ids list
      # We use a counter python data structure because there could be two or more advisory
      # entries with the same advid. It also allows us to compare to make sure both the
      # JSON and the database have all the same advIDs.
      dictAddedIds = counterJSONE2Advid - counterdbAdvid
      dictRemovedIds = counterdbAdvid - counterJSONE2Advid
      if len(dictAddedIds) == 0 and len(dictRemovedIds) == 0:
          outStr = "No E2 Records Added or Deleted"
#          print outStr
#            log.debug(outStr)
      else:
#         outStr = "Adding:{0}, Deleting:{1}".format( dictAddedIds, dictRemovedIds )
#         print outStr
#            log.debug(outStr)
          # We have to add or remove records from the database
          # The goal is simply to make sure that for each advid changed, the proper number of records match between the
          # JSON and database.
          # Once we have the proper records in the database that match the JSON, THEN we will make sure there are no changes
          # in the individual fields.

          # First, let's remove the removed IDs from the database
          for advid in dictRemovedIds:
              numDBRecsForAdvid = counterdbAdvid[advid]
              numDBRecsToDelete = counterdbAdvid[advid] - counterJSONE2Advid[advid]
              # If there is only one record for the advid or all the records for the ID are deleted, then
              # just kill the record for this advid.(No timestamp needed)
              if numDBRecsForAdvid == 1 or numDBRecsToDelete == counterJSONE2Advid[advid] :
                  self._E2DeleteAlarmRecordTableEntry(conn, advid, None)
              else:
                  # A bit more complicated because there are multiple records for the same advid, but not all are deleted.
                  # Make sure we delete the right one...We do this by only deleting records that do not match the JSON timestamp
                  # We have to get the database records for this advid and determine which one(s) to delete.

                  # Get all Database records for advid
                  strSQL = 'SELECT * FROM {0} WHERE advid={1} and controllerName="{2}"'.format(self.E2alarmRecTableName, advid, self.E2ControllerName)
                  cur.execute(strSQL)
                  DBRecsForAdvid = cur.fetchall()
                  numDBRecsforAvid = len(DBRecsForAdvid)

                  # Get JSON records for advid
                  JSONRecsForAdvid = []
                  for JSONrec in JSONE2AlmList:
                      if JSONrec['advid'] == advid:
                          JSONRecsForAdvid.append(JSONrec)

                  # Loop through database records. Delete if they don't match timestamp.
                  for DBrec in DBRecsForAdvid:
                      JSONrecFound = False  # Default not found
                      for JSONrec in JSONRecsForAdvid:
                          if JSONrec['timestamp'] == DBrec['dbTimestamp'] :
                              JSONrecFound = True
                      if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                          self._E2DeleteAlarmRecordTableEntry(conn, advid, DBrec['dbTimestamp'])


          for advid in dictAddedIds:

              # Get list of JSON records for advid
              JSONRecsForAdvid = []
              for JSONrec in JSONE2AlmList:
                  if JSONrec['advid'] == advid:
                      JSONRecsForAdvid.append(JSONrec)

              # Get all Database records for advid
              strSQL = 'SELECT * FROM {0} WHERE advid={1} and controllerName="{2}"'.format(self.E2alarmRecTableName, advid, self.E2ControllerName)
              cur.execute(strSQL)
              DBRecsForAdvid = cur.fetchall()
              numDBRecs = len(DBRecsForAdvid)

              for JSONrec in JSONRecsForAdvid:
                  if numDBRecs == 0: # There are no database records. Add the record.
                      JSONrecFound = False
                  else :
                      JSONrecFound = False  # Default to we found it...
                      for DBrec in DBRecsForAdvid:
                          if JSONrec['timestamp'] == DBrec['dbTimestamp'] :
                              JSONrecFound = True

                  if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                      self._E2UpdateAlarmRecordTableEntry(conn, JSONrec, True)

          # For testing, Let's make sure the number of records between JSON and DB match...
          # Get the matching database record
          strSQL = 'SELECT COUNT(*) FROM {0} where controllerName="{1}"'.format(self.E2alarmRecTableName, self.E2ControllerName )
          try:
            cur.execute(strSQL)
            newNumDBAlarmList = cur.fetchone()[0]
#                strBuf = "Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, numJSONAlmList)
#                log.debug(strBuf)
          except Exception, e:
            strExcept = "Exception: ".format( str(e) )
            log.exception( strExcept )

      # Now the number of records should all be in synch.

      # Next we loop through each record ensuring the fields match the latest JSON Listing
      # We do this by reading each advId from the database, create a memory record and comparing it to
      # a "memory" record that we create from the E2 Alarm List.
      for JSONE2AlmRec in JSONE2AlmList:

        # Get the matching database record
        strSQL = 'SELECT * FROM {0} where advid={1} and dbTimestamp="{2}" and controllerName="{3}"'.format(self.E2alarmRecTableName, JSONE2AlmRec['advid'], JSONE2AlmRec['timestamp'], self.E2ControllerName )
        try:
          cur.execute(strSQL)
          result = cur.fetchone()
          if result == None: # If we get no results, we know we need to add this record.
            self._E2UpdateAlarmRecordTableEntry(conn, JSONE2AlmRec, False)
          else : # Compare currrent record with database record to determine changes
            OrderedDBAlmRec = OrderedDict(zip(self.E2dbFieldNames, result))

            # compare database record and E2 JSON alarm record
            # If the Database record does not match the current E2 Alarm list, update the database.
            if self._E2CompareAlarmRecordTableEntry(JSONE2AlmRec, OrderedDBAlmRec) != True:
#              print "_E2AlarmRecordTableSynchronize: Records Do NOT Match - Curr", JSONE2AlmRec
#              print "_E2AlarmRecordTableSynchronize: Records Do NOT Match - DB", OrderedDBAlmRec
              self._E2UpdateAlarmRecordTableEntry(conn, JSONE2AlmRec, False)

        except Exception, e:
          strExcept = "Exception: ".format( str(e) )
          log.exception( strExcept )

      strSQL = 'SELECT COUNT(*) FROM {0} where controllerName="{1}"'.format(self.E2alarmRecTableName, self.E2ControllerName )
      try:
        cur.execute(strSQL)
        newNumDBAlarmList = cur.fetchone()[0]
#        if newNumDBAlarmList != numJSONAlmList :
#          strBuf = "At End of Sychronize - Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, numJSONAlmList)
#          log.debug(strBuf)
      except:
        log.exception("Error DEBUG in _E2AlarmRecordTableSynchronize")

      # If we made it here, we have successfully updated the E2 alarms database. Timestamp it.
      # We need to add UTC after the timestamp so we can properly convert it in the javascript
      strUpdateTimestamp = utilities.getUTCnowFormatted()
#      print "Updated E2 Alarms Timestamp-->", strUpdateTimestamp, "Controller:", self.E2ControllerName

      try:
        strSQL = "UPDATE {0} set LastAlarmUpdateTime='{1}' where controllerName='{2}'".format( self.E2RealTimeTableName, strUpdateTimestamp, self.E2ControllerName )
        cur.execute(strSQL)
        conn.commit()
      except Exception, e:
        strBuf = "Error Timestamping E2 Alarm Database Update - {0} ({1})".format(e, self.E2ControllerName)
        log.exception(strBuf)

      conn.close()

  ####################################################
  # external methods for the E2DeviceObject
  ####################################################
  # This method will provide the deletion of "other" information that is specific to the E2 device (e.g. not part of the DeviceObject data management)
  def deleteE2DeviceInformation( self, deviceName ) :
#    print "CALLED deleteE2DeviceInformation"
    self.blStopE2Device = True # Don't allow _execute loop to run anymore. (System manager restart will stop)

    # Clean out E2 database records
    conn = dbUtils.getE2AlarmDatabaseConnection()
    cur = conn.cursor()

    try:
#      print "Clear out E2 database Records for ", deviceName
      # Clear out the E2 alarm database records for the specific device.
      strSQL = 'delete from {0} where controllerName="{1}"'.format( self.E2alarmRecTableName, deviceName )
#      print strSQL
      cur.execute( strSQL )
    except Exception, e:
      strExcept = "Exception: ".format( str(e) )
      log.exception( strExcept )

    try:
#      print "Clear out Realtime database Records for ", deviceName
      # Clear out the REALTIME status information.
      strSQL = 'DELETE FROM {0} where controllerName="{1}"'.format( self.E2RealTimeTableName, deviceName )
#      print strSQL
      cur.execute(strSQL)
    except Exception, e:
      strExcept = "Exception: ".format( str(e) )
      log.exception( strExcept )

    conn.commit()
    conn.close()

    # Open system (LEO) alarm database.
    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()
    try:
#      print "Clear out E2 database Records in LEO ALARM LOG for ", deviceName
      # Clear out the E2 alarm database records for the specific device.
      strSQL = 'delete from {0} where E2ControllerName="{1}"'.format( self.LEOalarmRecTableName, deviceName )
#      print strSQL
      cur.execute( strSQL )
    except Exception, e:
      strExcept = "Exception: ".format( str(e) )
      log.exception( strExcept )
    conn.commit()
    conn.close()



  # Deletes all alarms based upon self.E2ControllerName
  def deleteAllE2Alarms(self):
#        print 'Deleting ALL E2 alarms from E2 Database'
    conn = dbUtils.getE2AlarmDatabaseConnection()
    try:
      cur = conn.cursor()
      # Clear Entire E2AlarmEntryTable
      strSQL = 'delete from {0} where controllerName="{1}"'.format( self.E2alarmRecTableName, self.E2ControllerName )
      cur.execute(strSQL)
      conn.commit()
      dbUtils.vacuumDatabase( dbUtils.E2AlarmDatabasePath ) # Compress database
#        auditTrail.AuditTrailAddEntry( 'Deleted All E2 Alarms' )
    except:
      print("Error in deleteAllE2AlarmsFromE2Database")
    conn.close()

    return {}

  # Get ALL E2 alarms for this controller. If you want ALL e2 Alarms from ALL devices, a method should be created at the Network object level
  def getE2AllAlarms(self):
    conn = dbUtils.getE2AlarmDatabaseConnection()
    try:
        retVal = {}
        cur = conn.cursor()
        strSQL = 'select lastAlarmUpdateTime from {0} where controllerName="{1}"'.format( self.E2RealTimeTableName, self.E2ControllerName )
        cur.execute( strSQL )
        retVal['lastAlarmUpdateTime'] = cur.fetchone()[0]
#          print retVal['lastAlarmUpdateTime']

        retVal['online'] = self.online

        # The format of the dbTimestamp is verbatim of what is in the E2 - for exact matching purposes. UTCdbTimeStamp is what is used to sort the E2 database alarm records.
        strSQL = 'select UTCdbTimestamp, dbTimestamp, dbState, source, text, reportvalue, priority,' \
                 'rtntimestamp, acked, acktimestamp from {} where controllerName="{}" order by UTCdbTimestamp DESC'.format( self.E2alarmRecTableName, self.E2ControllerName )
        cur.execute( strSQL )
        retAlarms = []
        for alarm in cur.fetchall():
            dict = dbUtils.dictFromRow(alarm)
            retAlarms.append(dict)
        retVal['alarms'] = retAlarms
        return retVal
    except Exception, e:
      strBuf = "**** Error in GetE2Alarms - updating database **** - {0} ({1})".format(e, self.E2ControllerName )
      log.exception(strBuf)
    finally:
        conn.close()

  ########################################################################################
  # The following method is responsible for obtaining the filtering parameters from the E2
  # database. The filter settings are used to determine what advisories get into the LEO
  # database from the E2 advisory log.
  ########################################################################

  def InitE2DeviceSettings(self) :

    # We need to read the E2 settings from the database to ensure the device object properties are up to date.
    conn = dbUtils.getE2AlarmDatabaseConnection()
    cur = conn.cursor()

    self.E2Settings = 'E2Settings'
    self.E2AlarmFilters = 'E2AlarmFilters'

    # result [x][0][0] = RowId, [x][0][1] = Field Name, [x][0][2] = Field Data Type, [x][0][3] = Field Required,
    # [x][0][4] = Field Default Value, [x][0][5] = Primary Key Indicator
    strSQL = 'PRAGMA table_info({0})'.format(self.E2Settings)
    try:
        cur.execute(strSQL)
        result = cur.fetchall()
        dbFieldNames = ([[x][0][1] for x in result])
    except:
        log.exception("Error in GetAlmDbFieldInfo")

    try:
      strSQL = 'SELECT * FROM {0}'.format(self.E2Settings)
      cur.execute(strSQL)
      result = cur.fetchone()
      OrderedDictE2Settings = OrderedDict(zip(dbFieldNames, result))

      if OrderedDictE2Settings["E2GetAlarms"] > 0 :
        self.blE2GetAlarms = True
      else :
        self.blE2GetAlarms = False

      # This is commented out until we want to do futher filtering in the LEO alarm log...
      doThis = 0
      if doThis == 0 :
          self.blE2AlarmFilterRTN = 0
          self.blE2GetAdvisoryOrAnnunciatorLog = 0
          self.blE2AlarmFilterNotice = 0
          self.blE2AlarmFilterFail = 0
          self.blE2AlarmFilterAlarm = 0
      else :
        if OrderedDictE2Settings["E2AlarmFilterRTN"] > 0 :
          self.blE2AlarmFilterRTN = 1
        else :
          self.blE2AlarmFilterRTN = 0
        if OrderedDictE2Settings["E2GetAdvisoryOrAnnunciatorLog"] > 0 :
          self.blE2GetAdvisoryOrAnnunciatorLog = 1
        else :
          self.blE2GetAdvisoryOrAnnunciatorLog = 0
        if OrderedDictE2Settings["E2AlarmFilterNotice"] > 0 :
          self.blE2AlarmFilterNotice = 1
        else :
          self.blE2AlarmFilterNotice = 0
        if OrderedDictE2Settings["E2AlarmFilterFail"] > 0 :
          self.blE2AlarmFilterFail = 1
        else :
          self.blE2AlarmFilterFail = 0
        if OrderedDictE2Settings["E2AlarmFilterAlarm"] > 0 :
          self.blE2AlarmFilterAlarm = 1
        else :
          self.blE2AlarmFilterAlarm = 0

      self.iE2AlarmPriorityFilter = OrderedDictE2Settings["E2AlarmPriorityFilter"]
      self.E2GetAlarmInterval = OrderedDictE2Settings["E2alarmCycleTime"] # Setting is in seconds
      self.E2DevOfflineRTNDelay = OrderedDictE2Settings["E2DevOfflineRTNDelay"]
      self.E2DevOfflineAlmDelay = OrderedDictE2Settings["E2DevOfflineAlmDelay"]
      self.E2MaxValsPerMsg = OrderedDictE2Settings["E2MaxValsPerMsg"]
      self.E2DelayBetweenMsgsMS = OrderedDictE2Settings["E2DelayBetweenMsgsMS"]

      # Create timer for determining offline/online state. We have to subtract 1 second from the delay
      # because of the "polling rate". The executeTransactions method gets called every 30 seconds.
      # If the user sets the delay to 1 minute, due to the fact that the timer was restarted within
      # the 30 second window, it would actually take 3 intervals (90 seconds) to generate the alarm.
      # To ensure that the alarm is initiated within 2 intervals, we simply subtract 1 from the alarm delay below.
      self.E2CommStateToOfflineTimer = elapsedTimer.Timeout()
      self.E2CommStateToOfflineTimer.elapse()
  
      self.E2CommStateToOnlineTimer = elapsedTimer.Timeout()
      self.E2CommStateToOnlineTimer.elapse()

    except:
        log.exception("Error in InitE2DeviceSettings")

    conn.close()

  ########################################################################
  # The following are E2 Timezone related functions for converting
  # the E2 time zone name into appropriate UTC time zone name for proper
  # Python time zone conversions. No conversion is needed
  # for the E2 Alarm database
  ########################################################################

  def InitE2TimeZones(self) :

    self.E2TimeZone = ''         # Current E2 time zone setting received from the E2
    self.E2PythonTimeZone = ''   # Based upon the current E2 time zone, the corresponding Python time zone for converting
    self.e2TimeZoneNameDict = {} # In memory dict copy of timezones from the database.
    self.E2TimeZonesTableName = 'E2TimeZonesTable'

    # Get the time zones from the E2 database table and store in memory for efficiency
    conn = dbUtils.getE2AlarmDatabaseConnection()
    cur = conn.cursor()

    strSQL = 'SELECT * FROM {0}'.format(self.E2TimeZonesTableName)
    try:
      cur.execute(strSQL)
      result = cur.fetchall()
      for x in result :
        self.e2TimeZoneNameDict[x[0]] = { 'GMToffset':x[1], 'pyTimeZone':x[2] }
        pyTimeZoneName = x[2]
    except:
        log.exception("Error in E2TimeZonesInit")
#     print self.e2TimeZoneNameDict

    conn.close()


  ######################################################################
  # The following functions are for synchronizing with the LEO Alarm Log
  ######################################################################
  def _LEOTranslateTimeStamp(self, strTimestamp, translateDirection):

    retStrTimestamp = ""
    
    if strTimestamp != "  0:00" :     # Default un-initialized time in E2

      # E2 Timestamp is: "06-20-16 17:07", LEO Timestamp is: "2016-04-22 10:12:05.536618" AND UTC
      strTimestamp = strTimestamp.replace('  ', ' ')  # We do this in case the hour is less than 10
  
      strTimestampParams = strTimestamp.split(' ')  # param[0] = date, param[1] = time
      strDate = strTimestampParams[0].split('-')
      strTime = strTimestampParams[1].split(':')
  
      if translateDirection == E2LOCAL_TO_UTC_TIMESTAMP:
          # Expand E2 Time To Leo Format. We also need to convert it to UTC.
          iYear = int(strDate[2]) + 2000
          curE2PyTzObj = timezone( self.E2PythonTimeZone )
          utcPyTzObj = pytz.utc
  
          loc_dt = curE2PyTzObj.localize(datetime(iYear, int(strDate[0]), int(strDate[1]), int(strTime[0]), int(strTime[1]), 0))
          utc_dt = loc_dt.astimezone(utcPyTzObj)
  
          # Adjust the utc_dt string to fill in record for LEO database entry - We have to cut off the UTC offset.
          utc_dt = loc_dt.astimezone(utcPyTzObj)
          utc_dt_str = str(utc_dt)
  
          # Adjust the utc_dt string to fill in record for LEO database entry - We have to cut off the UTC offset.
          utcOffsetLoc = utc_dt_str.rfind('+')
          if  utcOffsetLoc >= 0 :
            utc_dt_str = utc_dt_str[0:utcOffsetLoc]
          else :
            utcOffsetLoc = utc_dt_str.rfind( '-' )
            if utcOffsetLoc >= 0:
              utc_dt_str = utc_dt_str[0:utcOffsetLoc]
  
          retStrTimestamp = utc_dt_str

    return retStrTimestamp

  ###########################################################################################
  # This function will map the state of the E2 alarm to the proper state in the Leo alarm log
  ###########################################################################################
  def _determineLEOAlmAction( self, JSONE2AlmRec ) :

    almState = JSONE2AlmRec['state']

    if almState.find( "N-ALM" ) >= 0 or almState.find( "N-FL" ) >= 0 or almState.find( "N-NTC" ) >= 0 :
      LEOaction = 'RTN'
    if almState.find( "R-ALM" ) >= 0 or almState.find( "R-FL" ) >= 0 or almState.find( "R-NTC" ) >= 0 :
      LEOaction = 'RST'
    elif almState.find( "ALARM*" ) >= 0 or almState.find( "FAIL*" ) >= 0 or almState.find("NOTCE*") >= 0 :
      LEOaction = 'NEW'
    elif almState.find( "ALARM-" ) >= 0 or almState.find( "FAIL-" ) >= 0 or almState.find("NOTCE-") >= 0 :
      LEOaction = 'ACK'

    return LEOaction

 # Removed function to figure out alarm states from E2 properties. Comment here is simply for documenting - in case
 # we need this in the future.
 # 'reset' == 1 : Alarm Reset
 # 'acked' == 1 and 'reset' == 0 : Alarm Acknowledged
 # 'rtn' == 1 : Alarm RTN

  ######################################################################################
  # This function will update the LEO alarm log based upon converting an E2 alarm entry
  ######################################################################################
  def _LEOupdateE2AlarmEntry(self, conn, E2JSONAlmRec, blForceInsert ):

    # We will convert the record based upon the alarm state string. We do this because
    # the various properties in the alarm record are rather "screwed up". Converting the
    # alarm state to the proper LEO action is the most reliable way to do this.

    LEOaction = self._determineLEOAlmAction( E2JSONAlmRec )

    # Convert LEO Timestamp to E2 timestamp
    date = self._LEOTranslateTimeStamp(E2JSONAlmRec['timestamp'], E2LOCAL_TO_UTC_TIMESTAMP)
    rtntimestamp = self._LEOTranslateTimeStamp(E2JSONAlmRec['rtntimestamp'], E2LOCAL_TO_UTC_TIMESTAMP)

    name = E2JSONAlmRec['source']
    alarm = E2JSONAlmRec['text']
    description = "E2 Alarm"
    E2advid = E2JSONAlmRec['advid']
    E2timestamp = E2JSONAlmRec['timestamp']

    # See if the record is currently in the database...
    # Get the database records for this advid and timestamp
    cur = conn.cursor()
    strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2timestamp="{2}" and E2ControllerName="{3}"'.format(self.LEOalarmRecTableName,
                                                                                E2JSONAlmRec['advid'], E2JSONAlmRec['timestamp'], self.E2ControllerName )
    cur.execute(strSQL)
    DBAdvidRecs = cur.fetchone()
    # If there are no records for the advid in the database, we simply need to add the new records.
    if DBAdvidRecs == None or blForceInsert == True :
        blInsertRecord = True
    else:
        # there are record(s) for the advid in the database. Now we need to match the advid and dbTimestamp with the JSONAlmRecs.
        # This could mean adding or deleting records.
        blInsertRecord = False

    if blInsertRecord == True:  # We need to insert the record
      try :
        strSQL = 'INSERT INTO {0} ( date, action, name, alarm, description, E2advid, E2Timestamp, E2ControllerName, rtntimestamp ) ' \
          'VALUES ("{1}", "{2}", "{3}", "{4}", "{5}", {6}, "{7}", "{8}","{9}")'.format( self.LEOalarmRecTableName,
                          date, LEOaction, name, alarm, description, E2advid, E2timestamp, self.E2ControllerName, rtntimestamp )
        cur.execute( strSQL )
      except:
        log.exception("Error1 in _LEOupdateE2AlarmEntry")

    else:  # Record exists. Update Record.
      try:
        strSQL = 'UPDATE {0} SET date="{1}", action="{2}", name="{3}", alarm="{4}", description="{5}", ' \
                'E2ControllerName="{6}", rtntimestamp="{7}" where E2advid={8} and E2timestamp="{9}" and E2ControllerName="{10}"'.format(
                 self.LEOalarmRecTableName, date, LEOaction, name, alarm, description, self.E2ControllerName,
                 rtntimestamp, E2advid, E2timestamp, self.E2ControllerName)
        cur.execute(strSQL)
      except:
        log.exception("Error2 in _LEOupdateE2AlarmEntry")

    conn.commit()

  # This funciton will simply look for the alarm id in the Leo database and if exists, change the state to CLEARED.
  def _LEOupdateE2AlarmEntryToCleared(self, conn, advid) :
    try:
      cur = conn.cursor()
      strSQL = 'UPDATE {0} SET action="CLR" WHERE E2advid={1} and E2ControllerName="{2}"'.format(self.LEOalarmRecTableName,advid,self.E2ControllerName)
      cur.execute(strSQL)

    except Exception, e:
      strExcept = "Exception in _LEOupdateE2AlarmEntryToCleared: {0}".format(e)
      log.exception(strExcept)

    conn.commit()


  # This funciton will delete an entry from the LEO alarm log. This function should no longer be used.
  def _LEOdeleteE2AlarmEntry(self, conn, advidToDelete, E2timestamp):
    cur = conn.cursor()

    print "_LEOdeleteE2AlarmEntry - THIS SHOULD NOT BE CALLED."
    return

    if E2timestamp == None:
      strSQL = 'Delete FROM {0} WHERE E2advid={1} and E2ControllerName="{2}"'.format(self.LEOalarmRecTableName, advidToDelete, self.E2ControllerName )
    else :
      strSQL = 'Delete FROM {0} WHERE E2advid={1} and E2timestamp="{2}" and E2ControllerName="{3}"'.format(self.LEOalarmRecTableName, advidToDelete, E2timestamp, self.E2ControllerName )
    cur.execute(strSQL)
    recResult = cur.fetchone()
    conn.commit()

  # This function will simply confirm that the database is consistent between the E2 Alarm Database and the LEO Alarm Database
  # We should do this once a day and at every startup
  def _LEOToE2DBAlarmRecordTableSynchronize(self, JSONE2AlmList):

    # Open the LEO Alarm Database
    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()

    # Get Current E2 advids that are not in the CLR state in the LEO Alarm databaase - E2 Entries (advid >= 0)
    strSQL = 'SELECT E2advid FROM {0} WHERE E2advid >= 0 and E2ControllerName="{1}" and action != "CLR"'.format( self.LEOalarmRecTableName, self.E2ControllerName )
    cur.execute( strSQL )
    # Create a sorted list of the E2 Adv ids in LEO
    LEOdbAdvid = [x[0] for x in cur.fetchall()]
    LEOdbAdvid.sort()

    # Create a sorted list of the E2 Advids from the E2 alarm list.
    JSONE2AlmAdvidList = [x['advid'] for x in JSONE2AlmList]
    JSONE2AlmAdvidList.sort()


    # Counter creates a dict for each advid which is indexed (key) by advid and the value is the number of instances in the advid list.
    # This is how we manage duplicate advids in the list.
    counterdbAdvid = Counter(LEOdbAdvid)

    counterJSONE2Advid = Counter(JSONE2AlmAdvidList)

    # Let's see what are the differences in the alarm ids list
    # We use a counter python data structure because there could be two or more advisory
    # entries with the same advid. It also allows us to compare to make sure both the
    # JSON and the database have all the same advIDs.
    dictAddedIds = counterJSONE2Advid - counterdbAdvid
    dictClearedIds = counterdbAdvid - counterJSONE2Advid

    if len(dictAddedIds) == 0 and len(dictClearedIds) == 0:
      iDummy = 1
      # outStr = "{} - No LEO Records Added or Deleted".format( self.E2ControllerName )
      # print outStr

    else :
      # print "Controller:{}, Num Added:{}, Num Deleted:{}".format( self.E2ControllerName, dictAddedIds, dictClearedIds )
      # We have to add or remove records from the database
      # The goal is simply to make sure that for each advid changed, the proper number of records match between the
      # JSON and LEO database.
      # Once we have the proper records in the database that match the JSON, THEN we will make sure there are no changes
      # in the individual fields.

      # We no longer remove the IDs. If the ID exists in Leo, but does not exist in E2, the LEO alarm state will be changed to "Cleared"
      for advid in dictClearedIds:
        # print "Clearning ID:", advid
        numDBRecsForAdvid = counterdbAdvid[advid]
        numDBRecsToDelete = counterdbAdvid[advid] - counterJSONE2Advid[advid]
        # If there is only one record for the advid or all the records for the ID are deleted, then
        # just kill the record for this advid.(No timestamp needed)
        if numDBRecsForAdvid == 1 or numDBRecsToDelete == counterJSONE2Advid[advid] :
            self._LEOupdateE2AlarmEntryToCleared(conn, advid)
            # self._LEOdeleteE2AlarmEntry(conn, advid, None)
        else:
            # A bit more complicated because there are multiple records for the same advid, but not all are deleted.
            # Make sure we delete the right one...We do this by only deleting records that do not match the JSON timestamp
            # We have to get the database records for this advid and determine which one(s) to delete.

            # Get all LEO Database records for advid
            strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2ControllerName="{2}"'.format(self.LEOalarmRecTableName, advid, self.E2ControllerName )
            cur.execute(strSQL)
            DBRecsForAdvid = cur.fetchall()
            numDBRecsforAvid = len(DBRecsForAdvid)

            # Get JSON records for advid
            JSONRecsForAdvid = []
            for JSONrec in JSONE2AlmList:
                if JSONrec['advid'] == advid:
                    JSONRecsForAdvid.append(JSONrec)

            # Loop through database records. Delete if they don't match timestamp.
            for DBrec in DBRecsForAdvid:
                JSONrecFound = False  # Default not found
                for JSONrec in JSONRecsForAdvid:
                    if JSONrec['timestamp'] == DBrec['E2timestamp'] :
                        JSONrecFound = True
                if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                    self._LEOupdateE2AlarmEntryToCleared(conn, advid)
                    # self._LEOdeleteE2AlarmEntry(conn, advid, DBrec['E2timestamp'])

      for advid in dictAddedIds:

          # Get all Database records for advid
          strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2ControllerName="{2}"'.format(self.LEOalarmRecTableName, advid, self.E2ControllerName )
          cur.execute(strSQL)
          DBRecsForAdvid = cur.fetchall()
          numDBRecs = len(DBRecsForAdvid)

          # Get JSON records for advid
          JSONRecsForAdvid = []
          for JSONrec in JSONE2AlmList:
              if JSONrec['advid'] == advid:
                  JSONRecsForAdvid.append(JSONrec)

          for JSONrec in JSONRecsForAdvid:
              JSONrecFound = False  # Default to we found it...
              for DBrec in DBRecsForAdvid:
                  if JSONrec['timestamp'] == DBrec['E2timestamp'] :
                      JSONrecFound = True
              if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                # print "Adding ID:", advid
                self._LEOupdateE2AlarmEntry(conn, JSONrec, True)

    # For testing, Let's make sure the number of records between JSON and DB match...
    # Get the matching database record

    strSQL = 'SELECT COUNT(*) FROM {0} where E2ControllerName="{1}"'.format(self.LEOalarmRecTableName, self.E2ControllerName )
    try:
        cur.execute(strSQL)
        newNumDBAlarmList = cur.fetchone()[0]
        # strBuf = "LEO Alarm DB - Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, len(JSONE2AlmList))
        # print strBuf
    except:
        print "Unexpected error:", sys.exc_info()[0]

    # Now the number of records should all be in synch - between what we received from the E2 and what is in LEO's E2 alarm database.

    # Next we loop through each record ensuring the fields match the latest LEO alarm database
    # We do this by reading each advId from the LEO alarm database, create a memory record and comparing it to
    # a "memory" record that we create from the E2 Alarm List.
    for JSONE2AlmRec in JSONE2AlmList:

        # Get all Database records for advid
        strSQL = 'SELECT * FROM {0} where E2advid={1} and E2timestamp="{2}" and E2ControllerName="{3}"'.format(self.LEOalarmRecTableName, JSONE2AlmRec['advid'], JSONE2AlmRec['timestamp'], self.E2ControllerName )
#            try :
        cur.execute(strSQL)
        result = cur.fetchone()
        # If there are no alarms found in the LEO alarm database, no need to compare.
        if ( result != None ) :
            OrderedDBAlmRec = OrderedDict(zip(self.LEOdbFieldNames, result))
 #           except:
 #             strOut = "Unexpected error.:{0}".format( sys.exc_info()[0] )
 #             log.debug( strOut )
 #             log.debug( strSQL )

            # compare database record and E2 JSON alarm record
            # If the Database record does not match the current E2 Alarm list, update the LEO database.
            if self._LEOCompareAlarmToE2Alarm(JSONE2AlmRec, OrderedDBAlmRec) != True:
              buf = "_LEOToE2DBAlarmRecordTableSynchronize: Records Do NOT Match - Curr:{0}".format(JSONE2AlmRec)
              buf = "_LEOToE2DBAlarmRecordTableSynchronize: Records Do NOT Match - DB".format(OrderedDBAlmRec)
              self._LEOupdateE2AlarmEntry(conn, JSONE2AlmRec, False)
        else :
            # Update the database with this record since there is nothing to compare it to.
            self._LEOupdateE2AlarmEntry(conn, JSONE2AlmRec, False)

    strSQL = 'SELECT COUNT(*) FROM {0} where E2ControllerName="{1}"'.format(self.LEOalarmRecTableName, self.E2ControllerName )
    try:
      cur.execute(strSQL)
      newNumDBAlarmList = cur.fetchone()[0]
      # strBuf = "At End of Sychronize - Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, len(JSONE2AlmList))
      # print strBuf
      
    except:
      strOut = "Unexpected error:{0}".format( sys.exc_info()[0] )
      log.debug( strOut )
      log.debug( strSQL )

    conn.close()


  def _LEOCompareAlarmToE2Alarm(self, JSONE2AlmRec, LEODBAlmRec):
    # The purpose of this function is to ensure that the LEO alarm log AND the E2 Alarm Log are sychronized.
    # We do this by ensuring that each advid in E2 is in the LEO database. If not, we add.
    blMatch = True

    # Now compare the fields that may have changed. The priority is ACK, RTN, NEW.
    # So if both the ACK and RTN are set, the LEO should say ACK - even though RTN is active.

    leoAction = self._determineLEOAlmAction( JSONE2AlmRec )
    if  leoAction != LEODBAlmRec['action'] :
     blMatch = False

    return blMatch

  # This function will basically create the E2CellTypeInfo data structure - which is the "static" (non-changing) information
  # required for the E2 device and E2 status screen. This information is driven by the E2DeviceValues.csv file.
  def initE2CellTypeInfo(self):

    self._E2CellTypeInfo = {}

    self._processE2DeviceValuesFile() # Updates 'nameList', 'numList', <cellTypeNum>, <cellTypeName>, 'statusScreenLayout'
    self._E2CellTypeInfo['props'] = self._createE2CellTypeProperties( self._listEncStatusLine )
#    print "_E2CellTypeInfo:", self._E2CellTypeInfo
#    print "_listEncStatusLine: ", self._listEncStatusLine

  #########################################
  # Property Definition CSV file processing
  #########################################
  def _processE2DeviceValuesFile( self ) :

    PARSING_STATE_UNKNOWN = 0
    PARSING_CELLTYPE_TABLE = 1
    PARSING_CELLPROP_TABLE = 2
    PARSING_STATUS_SCREEN_TABLE = 3

    # Parse E2 Device information from the file.
    # This file contains all the information to dynamically create the static information for an E2 device
    # Open the file and read the columns (appType, propName, dataType, ValueType, DisplayName, unitType (opt), significantDigits (opt)
    # This file contains all of the properties we are intersted in "tracking" in the E2 device object.
    # In this function we will gather all the information for a cell type and then "dynamically" expand it in
    # another function where we learn the applications that are in an E2.

#    print "Working Dir = ", os.getcwd()
    strFilename = "{0}/system/devices/E2 Device/E2DeviceValues.csv".format( os.getcwd() )

    parseState = PARSING_STATE_UNKNOWN
    self._listEncStatusLine = []
    self._appTypeValueDescriptions = OrderedDict()
    self._E2CellTypeInfo['numList'] = []
    self._E2CellTypeInfo['nameList'] = []

    iLineCount = 0

    with open(strFilename, 'rb') as csvfile:
      fileLines = csv.reader(csvfile, delimiter=',')

      # process the lines...
      for strInLine in fileLines:
        iLineCount = iLineCount + 1
        params = strInLine # strInLine is already "split"

        if len(params) > 0 and params[0] != '#':  # blank line or comment line...
          if parseState == PARSING_STATE_UNKNOWN:
            if params[0] == 'CellType Table' :
              parseState = PARSING_CELLTYPE_TABLE

          elif parseState == PARSING_CELLTYPE_TABLE:
            if params[0] == 'CellType':
              parseState = PARSING_CELLPROP_TABLE
            elif params[0] != 'CellType Table' :
              # params[0] = AppType Numbers, params[1] = App Type Name
              if len(params[0]) > 0 :
                cellTypeNum = params[0]
                cellTypeName = params[1]
                self._E2CellTypeInfo[ cellTypeNum ] = cellTypeName # { '<appTypeNum>' : '<appTypeName>' }
                self._E2CellTypeInfo[ cellTypeName ] = cellTypeNum # { '<appTypeName>' : '<appTypeNum>' }
                if cellTypeNum not in self._E2CellTypeInfo['numList'] :
                  self._E2CellTypeInfo['numList'].append( cellTypeNum )
                if cellTypeName  not in self._E2CellTypeInfo['nameList']:
                  self._E2CellTypeInfo['nameList'].append(cellTypeName)

          elif parseState == PARSING_CELLPROP_TABLE:
            if params[0] == 'E2 Status Screen Data' :
              parseState = PARSING_STATUS_SCREEN_TABLE
            else:
              strPropName = "{0}:{1}".format(self._E2CellTypeInfo[params[0]], params[1])  # Property name is appTypeNum and PropValue.
              self._appTypeValueDescriptions[strPropName] = {"cellType": params[0], "propName": params[1],
                                                      "dataType": params[2], "valueType": params[3],
                                                      "displayName": params[4]}
              if len(params) > 5:
                  self._appTypeValueDescriptions[strPropName].update({"unitType": params[5]})
              if len(params) > 6:
                  self._appTypeValueDescriptions[strPropName].update({"significantDigits": params[6]})
              if len(params) > 7:
                  self._appTypeValueDescriptions[strPropName].update({"default": params[7]})
              if len(params) > 8:
                  self._appTypeValueDescriptions[strPropName].update({"description": params[8]})
              if len(params) > 9:
                  self._appTypeValueDescriptions[strPropName].update({"defaultLog": params[9]})

          elif parseState == PARSING_STATUS_SCREEN_TABLE:

            # Parses the status screen config lines and encodes to numbers for UI to interpret and render
            # Stored in _listEncStatusLine

            # Look for command in line
            try:
              tmpListEncLine = {}
              tmpListEncLine['cmd'] = 'Error'

              # Find command in list of commands
              for strCmd, valCmd in dictStatusLineCmds.iteritems():
                if valCmd == 4:
                    iStop = 1
                if strCmd == params[0]:
                  tmpListEncLine['cmd'] = valCmd

                  if valCmd == SGL_STATUS:
                    # Need to get description and property
                    tmpListEncLine['descStr'] = params[1]
                    tmpListEncLine['Prop'] = params[2]
                    break

                  elif valCmd == DBL_STATUS:
                    # Need to get TWO descriptions and properties
                    tmpListEncLine['descStr'] = params[1]
                    tmpListEncLine['Prop'] = params[2]
                    tmpListEncLine['descStr2'] = params[3]
                    tmpListEncLine['Prop2'] = params[4]
                    break

                  elif valCmd == APP_HEADER:
                    # Need to simply get string
                    tmpListEncLine['descStr'] = params[1]
                    break

                  if valCmd == APP_TYPE:
                    # Need to get description and property
                    tmpListEncLine['cellType'] = params[1]
                    tmpListEncLine['cellNum'] = int(params[2])
                    break

                  elif valCmd == STAGES_STATUS:
                    tmpListEncLine['MaxStages'] = int(params[1])
                    tmpListEncLine['NumStageProp'] = params[2]
                    tmpListEncLine['Prop'] = params[3]
                    break

                  elif valCmd == SECT_HEADER:
                    # Need to simply get string
                    tmpListEncLine['descStr'] = params[1]
                    break

                  elif valCmd == MULTI_HEADER or valCmd == MULTI_VALUE:
                    paramLen = len(params) - 1
                    iColNum = 1
                    while paramLen > 0:
                        strCol = 'col' + str(iColNum)
                        tmpListEncLine[strCol] = params[iColNum]
                        paramLen = paramLen - 1
                        iColNum = iColNum + 1
                    break

                  elif valCmd == MULTI_VALUE_STAR:
                    paramLen = len(params) - 1 # Let's get the number of rows
                    iColNum = 1
                    while paramLen > 0:
                        strCol = 'col' + str(iColNum)
                        tmpListEncLine[strCol] = params[iColNum]
                        paramLen = paramLen - 1
                        iColNum = iColNum + 1
                    break

                  elif valCmd == COMMENT_LINE:
                    tmpListEncLine.remove(strCmd)
                    break
                  else :
                    strOut = "ERROR on Line #{0} - Not Processed-->{1}".format(iLineCount,
                                                                               strInLine)
                    print strOut

            except:
                strOut = "ERROR on Line #{0} - Not Processed-->{1}".format(iLineCount, strInLine)
                print strOut

            # If there are entries, add  the list to the collection of status lines
            if len(tmpListEncLine) > 0:
                if tmpListEncLine['cmd'] != 'Error':
                    self._listEncStatusLine.append(tmpListEncLine)
                else:
                    strOut = "ERROR on Line #{0} - Not Processed-->{1}".format(iLineCount, strInLine)
                    print strOut

    printThis = False
    if printThis is True:
        print "__E2CellTypeInfo-->", self._E2CellTypeInfo
        print "_appTypeValueDescriptions-->", self._appTypeValueDescriptions
#        for line in self._appTypeValueDescriptions:
#            print line
        print "_listEncStatusLine-->", self._listEncStatusLine
#        for line in self._listEncStatusLine:
#            print line

  #######################################################################
  # This function utilizes the dictEncStatusLine and creates a list
  # of app/cell type properties that are desired for each CELL TYPE.
  # This is part of the creation of the E2CellTypeInfo structures
  #######################################################################
  def _createE2CellTypeProperties( self, dictEncStatusLine ) :

    # Let's go through the dictEncStatusLine and pick out the properties that need to be read.
    listCellTypeProperties = {} # Indexed by str(appType)
    strCellNum = '1'
    for dictLine in dictEncStatusLine:
        if dictLine['cmd'] == SGL_STATUS or dictLine['cmd'] == DBL_STATUS:
            listCellTypeProperties[strCellNum].append( dictLine['Prop'] )
            if dictLine['cmd'] == DBL_STATUS:
                listCellTypeProperties[strCellNum].append( dictLine['Prop2'] )
        elif dictLine['cmd'] == STAGES_STATUS:
            count = 0
            listCellTypeProperties[strCellNum].append( dictLine['NumStageProp'])      # store number of fans or compressors, etc. property
            while count < dictLine['MaxStages']:
                twoStarLoc = dictLine['Prop'].find("**")
                oneStarLoc = dictLine['Prop'].find("*")
                if twoStarLoc >= 0:
                    # Two stars = leading zero
                    strStageNoStar = dictLine['Prop'][:oneStarLoc]
                    # replace the * with the number - WITH leading zero
                    strProp = "{:s}{:02d}".format(strStageNoStar, count+1)
                    listCellTypeProperties[strCellNum].append( strProp )
                elif oneStarLoc >= 0:
                    # one star = no leading zero
                    strStageNoStar = dictLine['Prop'][:oneStarLoc]
                    # replace the * with the number - NO leading zero
                    strProp = "{0}{1}".format(strStageNoStar, str(count+1))
                    listCellTypeProperties[strCellNum].append( strProp )
                count = count + 1
        elif dictLine['cmd'] == APP_TYPE :
          strCellNum = str(dictLine['cellNum'])
          listCellTypeProperties[strCellNum] = []
        elif dictLine['cmd'] == MULTI_VALUE :
            # Get number of entries. We know there are is one extra property for 'cmd', but the rest are col1 thru col "n"
            iNumCols = len( dictLine ) - 1
            iCol = 1
            while iCol <= iNumCols : # relative 1
                strCol = 'col' + str(iCol)
                if len( dictLine[strCol]) > 0 :
                  listCellTypeProperties[strCellNum].append( dictLine[strCol] )
                iCol = iCol + 1
        elif dictLine['cmd'] == MULTI_VALUE_STAR: # Each property on this line that has a star will be replaced by an incrementing number.
          # Get number of entries. We know there are two extra properties - 'cmd' and 'count', but the rest are col1 thru col "n"
          iNumCols = len(dictLine) - 1
          iNumRows = int(dictLine['col1']) #contains the number of rows
          iCol = 2
          while iCol <= iNumCols:  # relative 1
            iRow = 0
            while iRow < iNumRows:
              strCol = 'col' + str(iCol)
              twoStarLoc = dictLine[strCol].find("**")
              oneStarLoc = dictLine[strCol].find("*")
              if twoStarLoc >= 0:
                # Two stars = leading zero
                updatePropName = dictLine[strCol][:twoStarLoc]
                # replace the * with the number - WITH leading zero
                strProp = "{:s}{:02d}".format(updatePropName, iRow + 1)
                listCellTypeProperties[strCellNum].append(strProp)
              elif oneStarLoc >= 0:
                # one star = no leading zero
                updatePropName = dictLine[strCol][:oneStarLoc]
                # replace the * with the number - NO leading zero
                strProp = "{0}{1}".format(updatePropName, str(iRow + 1))
                listCellTypeProperties[strCellNum].append(strProp)
              iRow = iRow + 1
            iCol = iCol + 1
    
    blPrintResults = False
    if blPrintResults is True :
      print "listCellTypeProperties", listCellTypeProperties
    return listCellTypeProperties


  #################################################################
  # This function converts from APP TYPE to a list of specific
  # E2 App Name queries so we can get mulitlple status values
  # in a single message to the E2.
  # This will be stored in listAppPathNameQueryProps
  #################################################################
  def _createE2AppQueryProps( self ) :
  # We now have a list of all the properties to be read for each apptype and a list of app names.
  # Now we have to translate this all into a list of queries for each appName
  # and the proper valueDescriptions.
  # This is also where we configure the default logging for each point.

#    print "Controller Name (1):", self._E2AppInfo['controllerName'], "Controller Name (2):", self.E2ControllerName

    ptsToBeLogged = []
    valueDescriptions = {}
    appPathNameQueryProps = {}

    if 'cellTypeAppList' in self._E2AppInfo :
      for appCellNum in self._E2AppInfo['cellTypeAppList']:
        for appName in self._E2AppInfo['cellTypeAppList'][appCellNum]:
          appPropList = self._E2CellTypeInfo['props'][str(appCellNum)]
          iNumProps = len( appPropList )
#          print "appPropList:{0}, iNumProps:{1}".format( appPropList, iNumProps )
          listTmpMsgProps = []
          appPathNameQueryProps[str(appName)] = []
          iPropCount = 0
#          appPathNameQueryProps[str(appName)][iPropCount] = []      # Will format multiple "groups" of property queries.

          for property in appPropList:
            appPathProp = '{0}:{1}:{2}'.format(self._E2AppInfo['controllerName'], appName, property) # for examle, E2 Demo:Condenser 1:PID OUTPUT
            listTmpMsgProps.append(appPathProp)

            # Create the valueDescriptions entry
            appTypeProp = '{0}:{1}'.format(appCellNum, property) # for example, 129:PID OUTPUT - to get cell type definiton
            appNameProp = appPathProp[appPathProp.find(":")+1:] # grab string to the right of the first colon to the end of the string.
            appNameProp = appNameProp.replace('"','')
            valueDescriptions[appNameProp] = copy.deepcopy( self._appTypeValueDescriptions[appTypeProp] )
            # For E2, we need to fix to fix up the display name from the "appType" property name (e.g. CONTROL VALUE) to
            # the full "path" property name (e.g. C29_ISLAND:CONTROL VALUE)
            valueDescriptions[appNameProp]['displayName'] = appNameProp

            if 'defaultLog' in self._appTypeValueDescriptions[appTypeProp] :
              if self._appTypeValueDescriptions[appTypeProp]['defaultLog'] != '':
                if self._appTypeValueDescriptions[appTypeProp]['defaultLog'] != 'N':
                # Default logging says to log this point, but don't log strings...
                  if self._appTypeValueDescriptions[appTypeProp]['unitType'] != 'string' :
                    ptsToBeLogged.append( appNameProp )

            iPropCount = iPropCount + 1
            iNumProps = iNumProps - 1
            if iPropCount % self.E2MaxValsPerMsg == 0 and iNumProps > 0:
              # Message is full. Move to next message.
              # Need to add commas
              iPropCount = 0
              appPathNameQueryProps[str(appName)].append(listTmpMsgProps)
              listTmpMsgProps = []
          if len(listTmpMsgProps) > 0:  # Make sure all props get appended to appPathNameQueryProps.
            appPathNameQueryProps[str(appName)].append(listTmpMsgProps)
          #log.debug(appPathNameQueryProps)
    self._valueDescriptions = valueDescriptions  # Update the deviceobject structures.
    self._alarmDescriptions = alarmDescriptions
    self._listAppPathNameQueryProps = appPathNameQueryProps
    #log.debug(valueDescriptions)
    #log.debug(alarmDescriptions)
    #log.debug(appPathNameQueryProps)

    # Setup the default logging.
    loggingMgr = self.deviceManager.directory.getLoggingManager()
    #abc = []
    abc = systemConstants.OLD_DEVICES
   # log.debug(abc)
   # log.debug(self.E2ControllerName)
    if self.E2ControllerName in abc:
     # log.debug(self.E2ControllerName)
      #log.debug(self.method)
      self.setValue = 0
    else:
      self.setValue = 1
    if self.method == "rebootMethod":
      if len(abc)!=0:
        if self.E2ControllerName in abc:
          self.setValue = 0
        else:
          self.setValue = 1
      else:
        self.setValue = 1
    loggingMgr.setLoggedValuesForDevice( self.E2ControllerName, ptsToBeLogged,self.setValue)


    printThis = False
    if printThis is True:
      print self._valueDescriptions
      print self._listAppPathNameQueryProps

  #################################################################
  # This is a function simply to update the last update time in the
  # database for the status screens
  #################################################################
  def _updateLastStatusUpdate(self) :
    strUpdateTimestamp = utilities.getUTCnowFormatted()
#    print "Updated E2 Status Timestamp-->", strUpdateTimestamp, "for: ", self.E2ControllerName

    conn = dbUtils.getE2AlarmDatabaseConnection()
    cur = conn.cursor()
    strSQL = 'update {0} set LastStatusUpdateTime="{1}" where controllerName="{2}"'.format( self.E2RealTimeTableName, strUpdateTimestamp, self.E2ControllerName )
    cur.execute( strSQL )
    conn.commit()
    conn.close()

