#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys

sys.path.append('system/devices')
sys.path.append('system/utils')
sys.path.append('system')

from deviceConstants import *
from networkConstants import *

import deviceObject
import systemInterface

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

from collections import OrderedDict
from collections import Counter

import logsystem

E2_COMM_FAIL_ALM = 'Site Supervisor COMM FAILURE'
E2_STATUS_UPDATE_FILTER_SECS = (10)

GETALMDBFIELD_NAMES = 1
GETALMDBFIELD_TYPES = 2

UTC_TO_E2LOCAL_TIMESTAMP = 1
E2LOCAL_TO_UTC_TIMESTAMP = 2

sys.path.insert(1, os.path.join(sys.path[0], 'system/devices/SiteSupervisor Device'))
log = logsystem.getLogger()

import datetime
import pytz
from pytz import timezone
from datetime import datetime

deviceType = "SiteSupervisor"
deviceTypeName = deviceSiteExecutionText
executionType = deviceSiteExecution

valueDescriptions = OrderedDict()
alarmDescriptions = OrderedDict()

# For E2 Device, the valueDescription list/dict variables will be created dynamically - currently based upon the status screen "dictionary"
# For alarms, this module will simply get the E2 alarm log and sychronize it with the Leo alarm database for the specific e2 device.
valueDescriptions["IncorrectType"] = {"dataType": dataTypeBool, "valueType": valueTypeOutput,
                                      "displayName": "Incorrect Type"}
alarmDescriptions[networkFailureKey] = {"description": ""}

valueTypeInput = "input"
valueTypeOutput = "output"
valueTypeConfig = "config"


class Device(deviceObject.NetworkDeviceObject):
    def __init__(self, deviceManager, name, description, network, networkAddress, image, method="", setValue=1):
        deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress,
                                                  deviceType, deviceTypeName, image)
        self.setValue = setValue
        # store the network address.
        self.SiteControllerName = name
        self.SiteControllerNameRcvd = self.SiteControllerName  # initliaze to match until actually received from E2
        #log.debug("Site Controller Name Received - "+self.SiteControllerName)
        self.method = method
        self.name = name
        self.description = description
        self.LEOalarmRecTableName = 'devicealarms'
        self.E2CommStateToOnlineTimer = elapsedTimer.Interval(30)
        self.E2CommStateToOfflineTimer= elapsedTimer.Interval(30)

        # We need to help the address...If there is no port number, add it.
        if networkAddress.find(":") >= 0:
            self.networkAddress = networkAddress
        else:
            self.networkAddress = "{}:{}".format(networkAddress, SITE_JSON_INTERFACE_PORT)
        self.E2StatusUpdateFilter = elapsedTimer.Interval(E2_STATUS_UPDATE_FILTER_SECS)
        self.E2StatusUpdateFilter.elapse()
        self.timeZoneValue = systemInterface.getSystemTimeZone()

        self.InitSiteDevice()
        self.InitSiteDeviceSettings()

    ####################################################
    # external methods for the E2DeviceObject
    ####################################################
    # This method will provide the deletion of "other" information that is specific to the E2 device (e.g. not part of the DeviceObject data management)

    # def __del__(self):
    # log.debug("Object Deleted")

    def initLeoAlarmDatabase(self, deviceName):

        # Init device object information
        self._alarmDescriptions = alarmDescriptions

        self.UpdateE2AlarmState()

        # Check for specific alarms in the list and initalize as appropriate.
        if networkFailureKey in self._alarms:
            # E2 Device has offline alarm.
            self.online = False
            self._alarms[networkFailureKey] = True
            self.E2CommState = "Offline"
            self.E2CommStateToOfflineTimer.elapse()
        else:
            self.online = True
            self._alarms[networkFailureKey] = False
            self.E2CommState = "Online"
            self.E2CommStateToOnlineTimer.elapse()

        self.RTOnline = self.online
        self.RTMsg = self.msg

        # print "*** initLeoAlarmDatabase ***: Online at init from leo alarm log:{0}, Messasge:{1}".format( self.online, self.msg )

    def InitSiteDevice(self):
        #    print "InitE2Device"
        # self.InitE2DeviceSettings() # Make sure these settings are up to date from the database.

        # Determine current state of communications from looking for an active alarm in the database.
        if self.SiteControllerName is not None:
            self.InitSiteAlarmDatabases(self.SiteControllerName)  # Setup database information
            self.initLeoAlarmDatabase(self.SiteControllerName)  # Ensure E2 specifc database records are initialized

            # setup informatioon for updating status screen data
            #self.SiteControllerName = {}
            # self.initE2CellTypeInfo()
            return True
        return False

    def InitSiteDeviceSettings(self):

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

            if OrderedDictE2Settings["E2GetAlarms"] > 0:
                self.blE2GetAlarms = True
            else:
                self.blE2GetAlarms = False

            # This is commented out until we want to do futher filtering in the LEO alarm log...
            doThis = 0
            if doThis == 0:
                self.blE2AlarmFilterRTN = 0
                self.blE2GetAdvisoryOrAnnunciatorLog = 0
                self.blE2AlarmFilterNotice = 0
                self.blE2AlarmFilterFail = 0
                self.blE2AlarmFilterAlarm = 0
            else:
                if OrderedDictE2Settings["E2AlarmFilterRTN"] > 0:
                    self.blE2AlarmFilterRTN = 1
                else:
                    self.blE2AlarmFilterRTN = 0
                if OrderedDictE2Settings["E2GetAdvisoryOrAnnunciatorLog"] > 0:
                    self.blE2GetAdvisoryOrAnnunciatorLog = 1
                else:
                    self.blE2GetAdvisoryOrAnnunciatorLog = 0
                if OrderedDictE2Settings["E2AlarmFilterNotice"] > 0:
                    self.blE2AlarmFilterNotice = 1
                else:
                    self.blE2AlarmFilterNotice = 0
                if OrderedDictE2Settings["E2AlarmFilterFail"] > 0:
                    self.blE2AlarmFilterFail = 1
                else:
                    self.blE2AlarmFilterFail = 0
                if OrderedDictE2Settings["E2AlarmFilterAlarm"] > 0:
                    self.blE2AlarmFilterAlarm = 1
                else:
                    self.blE2AlarmFilterAlarm = 0

            self.iE2AlarmPriorityFilter = OrderedDictE2Settings["E2AlarmPriorityFilter"]
            self.E2GetAlarmInterval = OrderedDictE2Settings["E2alarmCycleTime"]  # Setting is in seconds
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

    def deleteSiteDeviceInformation(self, devObject, deviceName):
        # print "CALLED deleteE2DeviceInformation"
        # # self.blStopE2Device = True # Don't allow _execute loop to run anymore. (System manager restart will stop)

        # Clean out E2 database records
        # # conn = dbUtils.getE2AlarmDatabaseConnection()
        # # cur = conn.cursor()

        # # try:
        # print "Clear out E2 database Records for ", deviceName
        # Clear out the E2 alarm database records for the specific device.
        # # strSQL = 'delete from {0} where controllerName="{1}"'.format( self.E2alarmRecTableName, deviceName )
        # print strSQL
        # # cur.execute( strSQL )
        # # except Exception, e:
        # # strExcept = "Exception: ".format( str(e) )
        # # log.exception( strExcept )

        # # try:
        # print "Clear out Realtime database Records for ", deviceName
        # Clear out the REALTIME status information.
        # # strSQL = 'DELETE FROM {0} where controllerName="{1}"'.format( self.E2RealTimeTableName, deviceName )
        # print strSQL
        # # cur.execute(strSQL)
        # # except Exception, e:
        # # strExcept = "Exception: ".format( str(e) )
        # # log.exception( strExcept )

        # # conn.commit()
        # # conn.close()

        # Open system (LEO) alarm database.
        conn = dbUtils.getAlarmDatabaseConnection()
        cur = conn.cursor()
        try:
            #      print "Clear out E2 database Records in LEO ALARM LOG for ", deviceName
            # Clear out the E2 alarm database records for the specific device.
            strSQL = 'delete from {0} where E2ControllerName="{1}"'.format(self.LEOalarmRecTableName, deviceName)
            #log.debug( strSQL )
            cur.execute(strSQL)
        except Exception, e:
            strExcept = "Exception: ".format(str(e))
            log.exception(strExcept)
        conn.commit()
        conn.close()
        del devObject

    def InitSiteAlarmDatabases(self, deviceName):
        #    print "InitE2AlarmDatabases"
        self.alarmRecTableKey = ['advid']
        self.JSONBooleanFieldNames = ["reset", "notice", "unacked", "alarm", "rtn", "acked", "fail"]

        # self.E2alarmRecTableName = 'E2AlarmEntryTable'
        # self.E2RealTimeTableName = 'E2RealTimeInfo'  ### Stores last update time for alarms and status

        self.LEOalarmRecTableName = 'devicealarms'

        if len(self.alarmRecTableKey) > 1:
            self.strAlarmRecTableKey = ",".join(self.alarmRecTableKey)
        else:
            self.strAlarmRecTableKey = self.alarmRecTableKey

        # conn = dbUtils.getE2AlarmDatabaseConnection()
        # self.E2dbFieldNames = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_NAMES, self.E2alarmRecTableName)
        # self.E2dbFieldTypes = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_TYPES, self.E2alarmRecTableName)

        # Let's make sure there is an entry in the alarm timestamp database for this E2Controller
        # cur = conn.cursor()
        # strSQL = 'SELECT COUNT(*) FROM {0} where controllerName="{1}"'.format(self.E2RealTimeTableName,
        # deviceName )
        # cur.execute(strSQL)
        # numRecords = cur.fetchone()[0]

        # if numRecords == 0 :
        # try:
        # strSQL = 'INSERT INTO ' + self.E2RealTimeTableName + ' (controllerName, LastUpdateTime, LastAlarmUpdateTime, LastStatusUpdateTime) VALUES ("' + deviceName + '", 0, 0, 0)'
        # cur.execute(strSQL)
        # conn.commit()
        # except Exception, e:
        # strBuf = "Error Creating Realtime Table Information - {} {}".format(e , deviceName )
        # log.exception(strBuf)

        # # We need to make sure all E2 alarms have their timestamps converted into UTC.
        # # We didn't re-architect the database due to the extensive re-testing and validation required (e.g. not enough time)
        # try:
        # cur = conn.cursor()
        # strSQL = 'SELECT dbTimestamp, rtntimestamp, advid, UTCdbTimestamp from E2AlarmEntryTable where advid > 0 and UTCdbTimestamp is null'
        # cur.execute(strSQL)
        # # Convert E2 Timestamp to UTC formatted timestamp - because sqlite cannot sort E2 timestamp.
        # for alarmRec in cur.fetchall():
        # alarm = dbUtils.dictFromRow(alarmRec)
        # # E2 Alarm = 01-03-18  8:05, Need to convert to 2018-01-03 08:05:00 and add to newly created columns
        # UTCdbTimestamp = self.E2AlarmDateToUTC( alarm['dbTimestamp'] )
        # UTCrtntimestamp = self.E2AlarmDateToUTC( alarm['rtntimestamp'] )
        # strSQL = 'update E2AlarmEntryTable set UTCdbTimestamp="{}", UTCrtntimestamp="{}" where advid = {}'.format( UTCdbTimestamp, UTCrtntimestamp, alarm['advid'] )
        # cur.execute(strSQL)
        # conn.commit()
        # except Exception, e:
        # strBuf = "Error Updating UTC date fields {} for ({})".format(e , deviceName )
        # log.exception(strBuf)

        # conn.close()

        conn = dbUtils.getAlarmDatabaseConnection()
        cur = conn.cursor()
        self.LEOdbFieldNames = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_NAMES, self.LEOalarmRecTableName)
        self.LEOdbFieldTypes = self._GetAlmDbFieldInfo(conn, GETALMDBFIELD_TYPES, self.LEOalarmRecTableName)

        conn.close()

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

    def InitSiteNetworkTransaction(self, tag):
        networkTrans = NetworkTransaction(tag)
        networkTrans.networkAddress = self.networkAddress
        return networkTrans

    def _prepareJsonRequest(self, tag, method, params=['']):
        self.jsonId = tag
        request = {'id': tag, 'method': method, 'params': params, 'addr': self.networkAddress}
        nm = NetworkMessage(request, tag)
        #    strInfo = "_prepareJsonRequest: {0}, Req:{1}".format( nm, request)
        #    log.info( strInfo )
        return nm

    def _prepareUpdateDeviceConfigurationTransactions(self):
        #    log.debug( "Do Nothing" )
        return []

    def _prepareUpdateStatusTransactions(self):
        # networkTrans = self.InitE2NetworkTransaction("Status")
        # if self.E2StatusUpdateFilter.hasElapsed() is True:
        # self.E2StatusUpdateFilter.reset()           # Reset the timer
        #self._addStatusToNetworkTransaction(networkTrans)
        # #    else:
        # #      log.debug( "+++ _prepareUpdateStatusTransactions FILTERED +++" )
        # #    strDebug = "--- Added Status - {0} Transactions".format( len( networkTrans.transactions ) )
        # #    log.info( strDebug )
        return []  # networkTrans

    def _prepareUpdateAlarmsTransactions(self):
        networkTrans = self.InitSiteNetworkTransaction("Alarms")
        # Refresh E2celltypes and timezone at a periodic interval.
        self._addGetSiteInfoToNetworkTransaction(networkTrans)
        # paramStr = '["{0}", {1}]'.format(self.SiteControllerName, self.blE2GetAdvisoryOrAnnunciatorLog )
        # networkTrans.transactions.append(self._prepareJsonRequest('GetAlarmList', '<cmd action="alarm_detail_group" compress="0" lang="eng">', '[[]]' ))
        networkTrans.transactions.append(self._prepareJsonRequest('GetAlarmSummary', 'GetAlarmSummary', '[[]]'))
        #    strInfo = "networkTrans:{0}, Len:{1}".format( networkTrans, len(networkTrans.transactions) )
        #    log.info( strInfo )

        return [networkTrans]

    def _addGetSiteInfoToNetworkTransaction(self, networkTrans):
        #networkTrans.transactions.append(self._prepareJsonRequest('GetReadDevices', '<cmd action="read_devices" compress="0" lang="eng">', '[[]]'))
        # networkTrans.transactions.append(self._prepareJsonRequest('GetConfigValues', '<cmd action="read_device_group" compress="0" lang="eng">', '[[]]' ))
        networkTrans.transactions.append(self._prepareJsonRequest('GetThisControllerName', 'GetThisControllerName', '[[]]'))
        networkTrans.transactions.append(self._prepareJsonRequest('GetAlarmSummary', 'GetAlarmSummary', '[[]]'))
        # self.E2CommState = "Online" #Just for debugging need to remove later

    # This will compare an E2 Alarm JSON record against the user defined filter options
    # The function returns True if the record is supposed to be kept (placed into LEO Alarm Log)
    def _CheckSiteAlmRecWithFilters(self, SiteAlmRec):
        blKeepRecord = True

        # The first thing we will do is filter out alarms that are not part of this controller.
        # If the controller name IS NOT in the alarm name, we filter it out. We only want only alarms
        # for "this controller"
        if SiteAlmRec['sitename'].find(self.SiteControllerName) != 0:
            blKeepRecord = False
        # if SiteAlmRec['rtn'] == True and self.blE2AlarmFilterRTN > 0 :
        # blKeepRecord = False
        # elif E2AlmRec['fail'] == True and self.blE2AlarmFilterFail > 0 :
        # blKeepRecord = False
        # elif E2AlmRec['notice'] == True and self.blE2AlarmFilterNotice > 0 :
        # blKeepRecord = False
        elif SiteAlmRec['resolution'] == "ACTIVE" and self.blE2AlarmFilterAlarm > 0:
            blKeepRecord = False
        # elif E2AlmRec['priority'] > self.iE2AlarmPriorityFilter :
        # blKeepRecord = False

        return blKeepRecord

    def ProcessSiteGetAlarmList(self, data):

        self.SiteJSONAlmList = data
        #log.debug(self.SiteJSONAlmList)

        if len(self.SiteJSONAlmList) > 0:  # AKSC255 Alarm and LEO Database Synchronization operations

            # Before we process the alarms, we need to handle some issues we have found in the syntax of the alarm list
            # as sent by E2
            # 1. the ackuser and other E2 strings cannot contain a ' (single quote) -- this does really bad things.
            # 2. E2 can be put into AM/PM mode - instead of 24 hours. So we have to strip off the A or P and
            # update the time and dates to military times.
            # For the sake of SQLite, we also need to make sure that none of the strings have a single quote as part of the string. We will simply remove these.
            dummyAlarmList = []
            for SiteAlmRec in self.SiteJSONAlmList:
                #log.debug(SiteAlmRec["timestamp"])
                timeValue = datetime.fromtimestamp(float(int(str(SiteAlmRec["timestamp"]))), pytz.timezone(self.timeZoneValue)).strftime('%m-%d-%Y %H:%M')
                SiteAlmRec["timestamp"] = timeValue
                SiteAlmRec["uid"] = int(SiteAlmRec["uid"])
                if 'resolutiontimestamp' in SiteAlmRec:
                    #log.debug(SiteAlmRec)
                    SiteAlmRec["rtntimestamp"] = datetime.fromtimestamp(float(int(str(SiteAlmRec["resolutiontimestamp"]))), pytz.timezone(self.timeZoneValue)).strftime('%m-%d-%Y %H:%M')
                else:
                    SiteAlmRec["rtntimestamp"] = None             # (timeValue.strftime('%Y-%m-%d %H:%M'))
                # First, check to make sure no ' in fields where there "might" be single quotes.
                listStrChkKeys = ["sitename", "originator", "messagekey"]  # , "text"
                for strChkKey in listStrChkKeys:
                    singleQuoteLoc = SiteAlmRec[strChkKey].find("'")

                    # Remove all single quotes from the string
                    while singleQuoteLoc >= 0:
                        if singleQuoteLoc == 0:
                            SiteAlmRec[strChkKey] = ' '
                        else:
                            SiteAlmRec[strChkKey] = SiteAlmRec[strChkKey][0:singleQuoteLoc] + " " + SiteAlmRec[
                                                                                                              strChkKey][
                                                                                                          singleQuoteLoc + 1:]
                        singleQuoteLoc = SiteAlmRec[strChkKey].find("'")
                dummyAlarmList.append(SiteAlmRec)
                # Second, make sure we fix up 12 hour times to military times.
                # listTimeKeys = [ "timestamp", "acktimestamp", "rtntimestamp" ]
                # for timeKey in listTimeKeys :
                # if SiteAlmRec[timeKey].rfind("A") >= 0 :
                # ltrLoc = len( SiteAlmRec[timeKey] )
                # SiteAlmRec[timeKey] = SiteAlmRec[timeKey][:ltrLoc-1]
                # elif SiteAlmRec[timeKey].rfind("P") >= 0 :
                # ltrLoc = len( SiteAlmRec[timeKey] )
                # SiteAlmRec[timeKey] = SiteAlmRec[timeKey][:ltrLoc-1]
                # Convert time
                # Add 12 hours

            # We will only synchornize when we get the E2 alarm log
            # The E2 Synchornization makes sure that what is in the E2 (and only alarms for "this controller")
            # is an exact copy in LEO's E2 Alarm Log (NOT in the LEO alarm log)
            # self._E2AlarmRecordTableSynchronize(self.E2JSONAlmList)

            # Now we want to clear out entries that are meant to be filtered based upon E2Settings
            # (e.g. filter notice, alarm, fail, etc)
            # We will remove all of these E2 alarm entries that do not pass the filter settings.
            # self.SiteJSONAlmList = []
            # for SiteAlmRec in self.SiteJSONAlmList :
            # # Check to see if record can pass through the filter
            # # This is the E2 alarm filter.
            # blKeep = self._CheckE2AlmRecWithFilters( SiteAlmRec )
            # if blKeep == True :
            # self.E2JSONAlmListFiltered.append( SiteAlmRec )

            #                print "E2FilteredAlarmList-->", self.E2JSONAlmListFiltered
            self.SiteJSONAlmList = dummyAlarmList
            self._LEOAlarmRecordTableSynchronize(self.SiteJSONAlmList)
            # log.debug(self.SiteJSONAlmList)
        else:
            # We will NOT synchornize when we don't get the E2 alarm log
            self.SiteJSONAlmList = {}

    def ProcessAKSC255GetMultiExpandedStatus(self, data):
        if len(data) > 0:
            # Read the response and update the status values in memory
            valueDescription = {}
            valueDescription["SI"] = {}
            valueDescription["RO"] = {}
            valueDescription["Monitoring"] = {}
            valueDescription["OI"] = {}
            i = 0
            j = 0
            k = 0
            l = 0
            for propertyStatus in data:
                # log.debug(propertyStatus)
                # params = propertyStatus['prop'].split( ":" ) # Param[0] = controller, Param[1] = appName, Param[2] = property
                if (propertyStatus["type"] == "Monitoring"):
                    params = propertyStatus['val'].split(" ")
                    tempValue = params[0]
                    unitType = params[1]
                    valueDescription["Monitoring"][i] = {}
                    valueDescription["Monitoring"][i]["appName"] = propertyStatus["name"]
                    valueDescription["Monitoring"][i]["model"] = propertyStatus["model"]
                    valueDescription["Monitoring"][i]["stat"] = propertyStatus["stat"]
                    valueDescription["Monitoring"][i]["dataType"] = dataTypeFloat
                    valueDescription["Monitoring"][i]["unitType"] = unitTypeTemperature
                    if (unitType == "F"):
                        valueDescription["Monitoring"][i]["val"] = self._convertF2C(float(tempValue))
                    elif (unitType == "C"):
                        valueDescription["Monitoring"][i]["val"] = tempValue
                    i = i + 1
                elif (propertyStatus["type"] == "SI"):
                    params = propertyStatus['val'].split(" ")
                    tempValue = params[0]
                    unitType = params[1]
                    valueDescription["SI"][j] = {}
                    valueDescription["SI"][j]["appName"] = propertyStatus["name"]
                    valueDescription["SI"][j]["model"] = propertyStatus["model"]
                    valueDescription["SI"][j]["stat"] = propertyStatus["stat"]
                    valueDescription["SI"][j]["dataType"] = dataTypeFloat
                    valueDescription["SI"][j]["unitType"] = unitTypeTemperature
                    if (unitType == "F"):
                        valueDescription["SI"][j]["val"] = self._convertF2C(float(tempValue))
                    elif (unitType == "C"):
                        valueDescription["SI"][j]["val"] = tempValue
                    j = j + 1
                elif (propertyStatus["type"] == "RO"):
                    # params = propertyStatus['val'].split( " " )
                    # tempValue = params[0]
                    # unitType = params[1]
                    valueDescription["RO"][k] = {}
                    valueDescription["RO"][k]["appName"] = propertyStatus["name"]
                    valueDescription["RO"][k]["model"] = propertyStatus["model"]
                    valueDescription["RO"][k]["stat"] = propertyStatus["stat"]
                    valueDescription["RO"][k]["dataType"] = dataTypeFloat
                    valueDescription["RO"][k]["unitType"] = "OnOff"
                    valueDescription["RO"][k]["val"] = propertyStatus["val"]
                    k = k + 1
                elif (propertyStatus["type"] == "OI"):
                    # params = propertyStatus['val'].split( " " )
                    # tempValue = params[0]
                    # unitType = params[1]
                    valueDescription["OI"][l] = {}
                    valueDescription["OI"][l]["appName"] = propertyStatus["name"]
                    valueDescription["OI"][l]["model"] = propertyStatus["model"]
                    valueDescription["OI"][l]["stat"] = propertyStatus["stat"]
                    valueDescription["OI"][l]["dataType"] = dataTypeFloat
                    valueDescription["OI"][l]["unitType"] = "OnOff"
                    valueDescription["OI"][l]["val"] = propertyStatus["val"]
                    l = l + 1
            # log.debug(valueDescription)
            self._valueDescriptions = valueDescription

    def _LEOTranslateTimeStamp(self, strTimestamp, translateDirection):

        retStrTimestamp = ""

        if strTimestamp != "  0:00":  # Default un-initialized time in E2

            # E2 Timestamp is: "06-20-16 17:07", LEO Timestamp is: "2016-04-22 10:12:05.536618" AND UTC
            strTimestamp = strTimestamp.replace('  ', ' ')  # We do this in case the hour is less than 10

            strTimestampParams = strTimestamp.split(' ')  # param[0] = date, param[1] = time
            strDate = strTimestampParams[0].split('-')
            # log.debug(strDate)
            strTime = strTimestampParams[1].split(':')

            if translateDirection == E2LOCAL_TO_UTC_TIMESTAMP:
                # Expand E2 Time To Leo Format. We also need to convert it to UTC.
                iYear = int(strDate[2])  # + 2000
                curE2PyTzObj = timezone(self.timeZoneValue)  # self.E2PythonTimeZone
                utcPyTzObj = pytz.utc

                loc_dt = curE2PyTzObj.localize(
                    datetime(iYear, int(strDate[0]), int(strDate[1]), int(strTime[0]), int(strTime[1]), 0))
                utc_dt = loc_dt.astimezone(utcPyTzObj)

                # Adjust the utc_dt string to fill in record for LEO database entry - We have to cut off the UTC offset.
                utc_dt = loc_dt.astimezone(utcPyTzObj)
                utc_dt_str = str(utc_dt)

                # Adjust the utc_dt string to fill in record for LEO database entry - We have to cut off the UTC offset.
                utcOffsetLoc = utc_dt_str.rfind('+')
                if utcOffsetLoc >= 0:
                    utc_dt_str = utc_dt_str[0:utcOffsetLoc]
                else:
                    utcOffsetLoc = utc_dt_str.rfind('-')
                    if utcOffsetLoc >= 0:
                        utc_dt_str = utc_dt_str[0:utcOffsetLoc]

                retStrTimestamp = utc_dt_str

        return retStrTimestamp

    def _LEOupdateSiteAlarmEntryToCleared(self, conn, advid):
        try:
            cur = conn.cursor()
            strSQL = 'UPDATE {0} SET action="CLR" WHERE E2advid={1} and E2ControllerName="{2}"'.format(
                self.LEOalarmRecTableName, advid, self.SiteControllerName)
            cur.execute(strSQL)

        except Exception, e:
            strExcept = "Exception in _LEOupdateSiteAlarmEntryToCleared: {0}".format(e)
            log.exception(strExcept)

        conn.commit()

    def _LEOCompareAlarmToSiteAlarm(self, JSONE2AlmRec, LEODBAlmRec):
        # The purpose of this function is to ensure that the LEO alarm log AND the E2 Alarm Log are sychronized.
        # We do this by ensuring that each advid in E2 is in the LEO database. If not, we add.
        blMatch = True

        # Now compare the fields that may have changed. The priority is ACK, RTN, NEW.
        # So if both the ACK and RTN are set, the LEO should say ACK - even though RTN is active.

        leoAction = self._determineLEOAlmAction(JSONE2AlmRec)
        if leoAction != LEODBAlmRec['action']:
            blMatch = False

        return blMatch

    # We should do this once a day and at every startup
    def _LEOAlarmRecordTableSynchronize(self, JSONSiteAlmList):

        # Open the LEO Alarm Database
        conn = dbUtils.getAlarmDatabaseConnection()
        cur = conn.cursor()

        # Get Current E2 advids that are not in the CLR state in the LEO Alarm databaase - E2 Entries (advid >= 0)
        strSQL = 'SELECT E2advid FROM {0} WHERE E2advid >= 0 and E2ControllerName="{1}" and action != "CLR"'.format(
            self.LEOalarmRecTableName, self.SiteControllerName)
        cur.execute(strSQL)
        # Create a sorted list of the E2 Adv ids in LEO
        LEOdbAdvid = [x[0] for x in cur.fetchall()]
        LEOdbAdvid.sort()

        # Create a sorted list of the E2 Advids from the E2 alarm list.
        JSONSiteAlmAdvidList = [x['uid'] for x in JSONSiteAlmList]
        JSONSiteAlmAdvidList.sort()

        # Counter creates a dict for each advid which is indexed (key) by advid and the value is the number of instances in the advid list.
        # This is how we manage duplicate advids in the list.
        counterdbAdvid = Counter(LEOdbAdvid)

        counterJSONSiteAdvid = Counter(JSONSiteAlmAdvidList)

        # Let's see what are the differences in the alarm ids list
        # We use a counter python data structure because there could be two or more advisory
        # entries with the same advid. It also allows us to compare to make sure both the
        # JSON and the database have all the same advIDs.
        dictAddedIds = counterJSONSiteAdvid - counterdbAdvid
        dictClearedIds = counterdbAdvid - counterJSONSiteAdvid
        # log.debug(dictAddedIds)
        # log.debug(dictClearedIds)

        if len(dictAddedIds) == 0 and len(dictClearedIds) == 0:
            iDummy = 1
            # outStr = "{} - No LEO Records Added or Deleted".format( self.SiteControllerName )
            # print outStr

        else:
            # print "Controller:{}, Num Added:{}, Num Deleted:{}".format( self.SiteControllerName, dictAddedIds, dictClearedIds )
            # We have to add or remove records from the database
            # The goal is simply to make sure that for each advid changed, the proper number of records match between the
            # JSON and LEO database.
            # Once we have the proper records in the database that match the JSON, THEN we will make sure there are no changes
            # in the individual fields.

            # We no longer remove the IDs. If the ID exists in Leo, but does not exist in E2, the LEO alarm state will be changed to "Cleared"
            for advid in dictClearedIds:
                # print "Clearning ID:", advid
                numDBRecsForAdvid = counterdbAdvid[advid]
                numDBRecsToDelete = counterdbAdvid[advid] - counterJSONSiteAdvid[advid]
                # If there is only one record for the advid or all the records for the ID are deleted, then
                # just kill the record for this advid.(No timestamp needed)
                if numDBRecsForAdvid == 1 or numDBRecsToDelete == counterJSONSiteAdvid[advid]:
                    self._LEOupdateSiteAlarmEntryToCleared(conn, advid)
                    # self._LEOdeleteE2AlarmEntry(conn, advid, None)
                else:
                    # A bit more complicated because there are multiple records for the same advid, but not all are deleted.
                    # Make sure we delete the right one...We do this by only deleting records that do not match the JSON timestamp
                    # We have to get the database records for this advid and determine which one(s) to delete.

                    # Get all LEO Database records for advid
                    strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2ControllerName="{2}"'.format(
                        self.LEOalarmRecTableName, advid, self.SiteControllerName)
                    cur.execute(strSQL)
                    DBRecsForAdvid = cur.fetchall()
                    numDBRecsforAvid = len(DBRecsForAdvid)

                    # Get JSON records for advid
                    JSONRecsForAdvid = []
                    for JSONrec in JSONSiteAlmList:
                        if JSONrec['uid'] == advid:
                            JSONRecsForAdvid.append(JSONrec)

                    # Loop through database records. Delete if they don't match timestamp.
                    for DBrec in DBRecsForAdvid:
                        JSONrecFound = False  # Default not found
                        for JSONrec in JSONRecsForAdvid:
                            if JSONrec['timestamp'] == DBrec['E2timestamp']:
                                JSONrecFound = True
                        if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                            self._LEOupdateSiteAlarmEntryToCleared(conn, advid)
                            # self._LEOdeleteE2AlarmEntry(conn, advid, DBrec['E2timestamp'])

            for advid in dictAddedIds:

                # Get all Database records for advid
                strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2ControllerName="{2}"'.format(
                    self.LEOalarmRecTableName, advid, self.SiteControllerName)
                cur.execute(strSQL)
                DBRecsForAdvid = cur.fetchall()
                numDBRecs = len(DBRecsForAdvid)

                # Get JSON records for advid
                JSONRecsForAdvid = []
                for JSONrec in JSONSiteAlmList:
                    if JSONrec['uid'] == advid:
                        JSONRecsForAdvid.append(JSONrec)

                for JSONrec in JSONRecsForAdvid:
                    JSONrecFound = False  # Default to we found it...
                    for DBrec in DBRecsForAdvid:
                        if JSONrec['timestamp'] == DBrec['E2timestamp']:
                            JSONrecFound = True
                    if JSONrecFound == False:  # IF we didn't find a record, delete this record from the database.
                        # print "Adding ID:", advid
                        self._LEOupdateSiteAlarmEntry(conn, JSONrec, True)

        # For testing, Let's make sure the number of records between JSON and DB match...
        # Get the matching database record

        strSQL = 'SELECT COUNT(*) FROM {0} where E2ControllerName="{1}"'.format(self.LEOalarmRecTableName,
                                                                                self.SiteControllerName)
        try:
            cur.execute(strSQL)
            newNumDBAlarmList = cur.fetchone()[0]
            # strBuf = "LEO Alarm DB - Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, len(JSONSiteAlmList))
            # print strBuf
        except:
            print "Unexpected error:", sys.exc_info()[0]

        # Now the number of records should all be in synch - between what we received from the E2 and what is in LEO's E2 alarm database.

        # Next we loop through each record ensuring the fields match the latest LEO alarm database
        # We do this by reading each advId from the LEO alarm database, create a memory record and comparing it to
        # a "memory" record that we create from the E2 Alarm List.
        for JSONE2AlmRec in JSONSiteAlmList:

            # Get all Database records for advid
            strSQL = 'SELECT * FROM {0} where E2advid={1} and E2timestamp="{2}" and E2ControllerName="{3}"'.format(
                self.LEOalarmRecTableName, JSONE2AlmRec['uid'], JSONE2AlmRec['timestamp'], self.SiteControllerName)
            #            try :
            cur.execute(strSQL)
            result = cur.fetchone()
            # If there are no alarms found in the LEO alarm database, no need to compare.
            if (result != None):
                OrderedDBAlmRec = OrderedDict(zip(self.LEOdbFieldNames, result))
                #           except:
                #             strOut = "Unexpected error.:{0}".format( sys.exc_info()[0] )
                #             log.debug( strOut )
                #             log.debug( strSQL )

                # compare database record and E2 JSON alarm record
                # If the Database record does not match the current E2 Alarm list, update the LEO database.
                if self._LEOCompareAlarmToSiteAlarm(JSONE2AlmRec, OrderedDBAlmRec) != True:
                    buf = "_LEOToE2DBAlarmRecordTableSynchronize: Records Do NOT Match - Curr:{0}".format(JSONE2AlmRec)
                    buf = "_LEOToE2DBAlarmRecordTableSynchronize: Records Do NOT Match - DB".format(OrderedDBAlmRec)
                    self._LEOupdateSiteAlarmEntry(conn, JSONE2AlmRec, False)
            else:
                # Update the database with this record since there is nothing to compare it to.
                self._LEOupdateSiteAlarmEntry(conn, JSONE2AlmRec, False)

        strSQL = 'SELECT COUNT(*) FROM {0} where E2ControllerName="{1}"'.format(self.LEOalarmRecTableName,
                                                                                self.SiteControllerName)
        try:
            cur.execute(strSQL)
            newNumDBAlarmList = cur.fetchone()[0]
            # strBuf = "At End of Sychronize - Num DB Recs = {0}, Num JSON Recs = {1}".format(newNumDBAlarmList, len(JSONSiteAlmList))
            # print strBuf

        except:
            strOut = "Unexpected error:{0}".format(sys.exc_info()[0])
            log.debug(strOut)
            log.debug(strSQL)

        conn.close()

    def _determineLEOAlmAction(self, JSONE2AlmRec):

        almState = JSONE2AlmRec['resolution']

        if almState.find("AUTO") >= 0 or almState.find("N-FL") >= 0 or almState.find("N-NTC") >= 0:
            LEOaction = 'RTN'
        if almState.find("R-ALM") >= 0 or almState.find("RESET") >= 0 or almState.find("R-NTC") >= 0:
            LEOaction = 'RST'
        elif almState.find("ACTIVE") >= 0:  # or almState.find( "FAIL*" ) >= 0 or almState.find("NOTCE*") >= 0 :
            LEOaction = 'NEW'
        elif almState.find("ALARM-") >= 0 or almState.find("FAIL-") >= 0 or almState.find("NOTCE-") >= 0:
            LEOaction = 'ACK'
        elif almState.find("cleared") >= 0:  # or almState.find( "FAIL-" ) >= 0 or almState.find("NOTCE-") >= 0 :
            LEOaction = 'CLR'

        return LEOaction

    def _LEOupdateSiteAlarmEntry(self, conn, E2JSONAlmRec, blForceInsert):

        # We will convert the record based upon the alarm state string. We do this because
        # the various properties in the alarm record are rather "screwed up". Converting the
        # alarm state to the proper LEO action is the most reliable way to do this.

        LEOaction = self._determineLEOAlmAction(E2JSONAlmRec)

        # Convert LEO Timestamp to E2 timestamp
        date = self._LEOTranslateTimeStamp(E2JSONAlmRec['timestamp'], E2LOCAL_TO_UTC_TIMESTAMP)
        rtntimestamp = E2JSONAlmRec['rtntimestamp']
        if not rtntimestamp is None:
            rtntimestamp = self._LEOTranslateTimeStamp(E2JSONAlmRec['rtntimestamp'], E2LOCAL_TO_UTC_TIMESTAMP)

        name = E2JSONAlmRec['sitename'] + ":" + E2JSONAlmRec['originator'] + ":" + E2JSONAlmRec['messagekey'] + " (" + E2JSONAlmRec['category']+ ")"
        alarm = E2JSONAlmRec['messagekey'] + " (" + E2JSONAlmRec['category']+ ")"
        description = "SiteSupervisor Alarm"
        E2advid = E2JSONAlmRec['uid']
        E2timestamp = E2JSONAlmRec['timestamp']

        # See if the record is currently in the database...
        # Get the database records for this advid and timestamp
        cur = conn.cursor()
        strSQL = 'SELECT * FROM {0} WHERE E2advid={1} and E2timestamp="{2}" and E2ControllerName="{3}"'.format(
            self.LEOalarmRecTableName,
            E2JSONAlmRec['uid'], E2JSONAlmRec['timestamp'], self.SiteControllerName)
        cur.execute(strSQL)
        DBAdvidRecs = cur.fetchone()
        # If there are no records for the advid in the database, we simply need to add the new records.
        if DBAdvidRecs == None or blForceInsert == True:
            blInsertRecord = True
        else:
            # there are record(s) for the advid in the database. Now we need to match the advid and dbTimestamp with the JSONAlmRecs.
            # This could mean adding or deleting records.
            blInsertRecord = False

        if blInsertRecord == True:  # We need to insert the record
            try:
                strSQL = 'INSERT INTO {0} ( date, action, name, alarm, description, E2advid, E2Timestamp, E2ControllerName, rtntimestamp ) ' \
                         'VALUES ("{1}", "{2}", "{3}", "{4}", "{5}", {6}, "{7}", "{8}","{9}")'.format(
                    self.LEOalarmRecTableName,
                    date, LEOaction, name, alarm, description, E2advid, E2timestamp, self.SiteControllerName,
                    rtntimestamp)
                cur.execute(strSQL)
            except:
                log.exception("Error1 in _LEOupdateSiteAlarmEntry")

        else:  # Record exists. Update Record.
            try:
                strSQL = 'UPDATE {0} SET date="{1}", action="{2}", name="{3}", alarm="{4}", description="{5}", ' \
                         'E2ControllerName="{6}", rtntimestamp="{7}" where E2advid={8} and E2timestamp="{9}" and E2ControllerName="{10}"'.format(
                    self.LEOalarmRecTableName, date, LEOaction, name, alarm, description, self.SiteControllerName,
                    rtntimestamp, E2advid, E2timestamp, self.SiteControllerName)
                cur.execute(strSQL)
            except:
                log.exception("Error2 in _LEOupdateSiteAlarmEntry")

        conn.commit()

    #################################################################
    # This function sets the device alarm state based upon a query of the LEO alarms database (for E2 alarms)
    # or a _alarms property in the case of device offline (even though the query should find this)
    #################################################################
    def UpdateE2AlarmState(self):
        try:
            # Let's determine if there are any active LEO alarms for this device.
            dictDBActiveAlmList = dbUtils.getAlarmEntries(dbUtils.GETSITESUPERVISORDEVICEACTIVEALARMS,
                                                          {'deviceName': self.SiteControllerName})

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

    def _executeTransaction(self, networkTrans):

        # print "*** Execute Transactions for E2. networkTrans.online-->", networkTrans.online
        # Default to current filter online status and msg as well as real-time online status and msg
        online = self.online  # True #
        currMsg = self.msg

        RTOnline = self.RTOnline  # True #
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
                if numMessages > 0:
                    # Messages were sent, loop through the transactions and responses
                    for transaction in networkTrans.transactions:
                        with self.lock:
                            response = transaction.response

                            if response is not None:
                                #log.debug(response)
                                response = json.loads(response)
                                json.loads(transaction.response)
                                #log.debug(response)
                                # Let's update the E2ControllerNameRcvd variable if the message is a GetControllerName. Otherwise, we won't update E2ControllerNameRcvd.
                                if transaction.tag == 'GetThisControllerName':
                                    jsonValue = json.loads(transaction.response)
                                    self.SiteControllerNameRcvd = jsonValue["result"]
                                    #log.debug(self.SiteControllerNameRcvd)
                            # Message sent with no response OR the initailized E2 controller name does NOT match the name recevied in the response.
                            i = 0
                            if response is None or self.SiteControllerName != self.SiteControllerNameRcvd:
                                iDummy = 1
                                RTOnline = False
                                RTMsg = networkFailureKey
                                # strInfo = "RECEIVE IS NONE. THIS IS VERY, VERY BAD. Trans:{0}, Request:{1}".format(
                                    # transaction, transaction.request)
                                # log.info( strInfo )
                            else:
                                if transaction.tag == 'GetThisControllerName':  # Let's abbreviate multiexpandedstatusmessages...
                                    iDummy = 2
                                    # strInfo = "E2 RECEIVE-->Trans:{0}, GetThisControllerName Len:{1}".format(transaction,
                                                                                                    # response)
                                    # log.info( strInfo )
                                else:
                                    iDummy = 3
                                    # strInfo = "E2 RECEIVE-->Trans:{0}, Request:{1}, Len:{2}".format(transaction,
                                                                                                    # transaction.request,response)
                                                                                                    
                                    # log.info( strInfo )
                                response = transaction.response
                                response = json.loads(response)
                                if response.has_key("error"):
                                    errorValue = 1  # int(errorValue["resp"]["@error"])
                                else:
                                    errorValue = 0
                                #log.debug(errorValue)
                                if errorValue != 0:  # response.has_key('error') and 'RSP_INVALID_NAME' in response['error']['msg']:
                                    self._nullOutputValues()
                                    RTOnline = False
                                    RTMsg = "Site Supervisor controller or application does not exist - Confirm consistent naming with Site Supervisor"
                                else:
                                    if len(response) > 0:
                                        RTOnline = True  # We get a message. We are talking. Move towards online...
                                        result = response  # response['result']
                                        # print "E2 _executeTransactions result = ", result

                                        if transaction.tag == 'GetReadDevices':
                                            data = result  # result['data']
                                            # log.debug(data)
                                            data = json.loads(data)  # result['data']
                                            data = data["resp"]["dev"]
                                            self.ProcessAKSC255GetMultiExpandedStatus(data)

                                        elif transaction.tag == 'GetConfigValues':
                                            # print 'ConfigValues = ', result['data']
                                            data = result  # result['data']
                                            strInfo = "Danfoss GetConfigValues, GetConfigValues Len:{0}".format(data)

                                        elif transaction.tag == 'GetAlarmSummary':
                                            #log.debug("Inside GetAlarmSummary Tag")
                                            data = result["result"]["alarms"]
                                            #log.debug(data)
                                            strInfo = "Site Supervisor GetAlarmSummary, GetAlarmSummary Len:{0}".format(
                                                str(data))
                                            #log.debug(strInfo)
                                            if len(data) > 0:
                                                self.ProcessSiteGetAlarmList(data)

                                        else:
                                            #print "***** UNPROCESSED TRANSACTION.TAG *****-->", transaction.tag
                                            doNothing = 1
                #                  else:
                #                    print "***** ERROR No response to -->", transaction.request
                else:
                    iDummy = 4
                    #log.debug("No Messages To Process")
                    # There were no messages to process. No changes to the states

                # update the alarm status.
                self.UpdateE2AlarmState()

        except Exception, e:
            strBuf = "exception - {0} ({1})".format(e, self.SiteControllerName)
            log.exception(strBuf)

        # For E2, we are going to add some filtering here to avoid nuisance alarms caused by periodic "hiccups"
        # RTOnline will be the "raw" communications state of messages sent.
        # self.E2CommState will represent the current communications state machine that represents either online or offline or the a transition state.
        # online will be the filtered boolean online (True) or offline (False) translated from the E2CommState Online or Offline
        # Therefore, the return value "online" will be the "filtered" online state for the E2.

        # We will only transition comm state if there were messages sent/processed OR the network is offline.
        if numMessages > 0 or networkTrans.online is False:
            # log.debug( "+++ Processing Transition - RTOnline:{0}, CommState:{1}, Num Msgs:{2}, ToOnlineTimer:{3}, ToOfflineTmer:{4}".format ( RTOnline, self.E2CommState,
            #               numMessages, self.E2CommStateToOnlineTimer.getTimeRemainingSecs(), self.E2CommStateToOfflineTimer.getTimeRemainingSecs() ) )
            if RTOnline is True:  # GOOD MESSAGE PROCESSED
                if self.E2CommState == "Online":  # All good. Update filtered state
                    online = True
                    currMsg = ""
                elif self.E2CommState == "Offline":  # Good message, but current state is offline; restart to online timer
                    self.E2CommState = "ToOnline"
                    self.E2CommStateToOnlineTimer.setTimeout((self.E2DevOfflineRTNDelay * 60) - 2)
                    self.E2CommStateToOnlineTimer.reset()
                elif self.E2CommState == "ToOnline":  # Comm is good but are still considered offline until timer elapses.
                    if self.E2CommStateToOnlineTimer.hasElapsed():
                        self.E2CommState = "Online"
                        online = True
                        currMsg = ""
                elif self.E2CommState == "ToOffline":  # Comm is now good, but was heading offline. Reset and move toward online
                    self.E2CommStateToOnlineTimer.setTimeout((self.E2DevOfflineRTNDelay * 60) - 2)
                    self.E2CommStateToOnlineTimer.reset()
                    self.E2CommState = "ToOnline"
            elif RTOnline is False:  # bad communications.
                if self.E2CommState == "Offline":  # Offline and still no good messages.
                    online = False
                    currMsg = "LEO is unable to communicate with Site Supervisor"
                elif self.E2CommState == "Online":  # current state is online; restart timer to transition to offline
                    # We are "considered" online and have problems, start the transition to offline.
                    self.E2CommState = "ToOffline"
                    self.E2CommStateToOfflineTimer.setTimeout((self.E2DevOfflineAlmDelay * 60) - 2)
                    self.E2CommStateToOfflineTimer.reset()
                elif self.E2CommState == "ToOffline":  # Comm is bad and heading to offline.
                    if self.E2CommStateToOfflineTimer.hasElapsed():
                        self.E2CommState = "Offline"
                        online = False
                        currMsg = "LEO is unable to communicate with Site Supervisor"
                elif self.E2CommState == "ToOnline":  # Was trying to go online, but got bad message. Start Transition back to offline
                    self.E2CommStateToOfflineTimer.setTimeout((self.E2DevOfflineAlmDelay * 60) - 2)
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

        return {'online': online, 'message': currMsg}

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

