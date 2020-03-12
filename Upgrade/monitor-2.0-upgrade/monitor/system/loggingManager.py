#! /usr/bin/python
from flask import session
import threading
import sqlite3
import datetime
import cStringIO
from collections import OrderedDict
import copy
import time
import itertools

import alarmEmailer
import dbUtils
import auditTrail
import utilities
import elapsedTimer
from LeoFlaskUtils import getSessionUsername
import systemConstants

import logsystem
log = logsystem.getLogger()


class LoggingManager:
  def __init__(self, directory):
    self.directory = directory

    self.logLock = threading.RLock()
    self.logThread = None
    self.logActiveOps = OrderedDict()
    self.logNextId = 1000
    self.stopLogThread = False
    self.logCloudData = OrderedDict()
    self.replaceValue = False
    self.replaceValueData = {}

    self.logCycle = elapsedTimer.Interval()
    self._readLoggingCycleTimeFromDatabase()

    self.databaseCleanupEvent = elapsedTimer.DailyEvent(datetime.time(0))
    #self.databaseCleanupEvent.trigger()

    self._insertStartNone()

  def __del__(self):
    self.stop();

  # This function will read the "system wide" logging interval setting
  def _readLoggingCycleTimeFromDatabase(self):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select loggingCycleTime from system")
    systemInfo = cur.fetchone()
    self.logCycle.setTimeout(int(systemInfo["loggingCycleTime"]))
    conn.close()

  # This function will simply determine the properties that are logged for
  # a specific device
  def _getDeviceKeysWithLoggedValues(self):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select distinct deviceName from logging")
    retval = []
    for loggingInfo in cur.fetchall():
      retval.append(loggingInfo["deviceName"])
    conn.close()
    return retval

  # This function will do the following:
  # 1. call a method in the device to get the values that are to be logged
  # 2. Get the current values for each of these logged properties
  # 3. Write them into the database
  # 4. Reset the logging timer
  def _updateLoggedValuesFromDevices(self):
    # if our time has elapsed
    if self.logCycle.hasElapsed():

      # To avoid log retrieval "skewing", immediately reset the logCycle timer.
      self._readLoggingCycleTimeFromDatabase()
      self.logCycle.reset()

#      log.debug( "locCycle has elapsed..." )
      # Get a list of devices that have logged points from logging database.
      deviceKeys = self._getDeviceKeysWithLoggedValues()

      # Loop through the devices and request logging.
      for deviceKey in deviceKeys:
        device = self.directory.getDeviceObject(deviceKey)
        if device is not None:
#          log.info("Requesting logged values from '" + deviceKey + "'")
          # Get names of points to be logged for this device.
          valueNames = self.getLoggedValuesForDevice(deviceKey)
          # Tell the device object that log values are needed (via _logready)
          device.updateLoggedValues(valueNames)

  # This function notes the starting time for the logging subsystem
  def _insertStartNone(self):
    conn = dbUtils.getLogDatabaseConnection()
    cur = conn.cursor()
    cur.execute("INSERT INTO [dates] ([date]) VALUES (?)", (datetime.datetime.utcnow(),))
    dateIdx = cur.lastrowid

    cur.execute("select * from devicevalues where deviceName=? and valueName=?", ('_SYSTEM_START_', '_SYSTEM_START_'))
    logValueInfo = cur.fetchone()
    if logValueInfo is None:
      cur.execute("INSERT INTO devicevalues (deviceName, valueName) VALUES (?, ?)", ('_SYSTEM_START_', '_SYSTEM_START_'))
      valueIdx = cur.lastrowid
    else:
      valueIdx = logValueInfo["idx"]

    cur.execute("INSERT INTO logs values(?, ?, ?)", (dateIdx, valueIdx, None))
    conn.commit()
    conn.close()

  # This function converts the value to be logged into the appropriate database value format.
  def _prepareListedValuesForLogging(self, device, values):
    valueDesciptions = device.getValueDescriptions()
    for key in values:
      value = values[key]
      if not value is None:
        valueDescription = valueDesciptions[key]
        if valueDescription['dataType'] == 'float':
          sigdigs = int(valueDescription['significantDigits']) + 1  # we add one because we want "enough" accuracy
          fmt = '{:.' + str(sigdigs) +'f}'
          values[key] = fmt.format(round(value, sigdigs))
        elif valueDescription['dataType'] == 'list' or valueDescription['dataType'] == 'int':
          values[key] = str(int(value))
        elif valueDescription['dataType'] == 'string':
          values[key] = str(value)
        elif valueDescription['dataType'] == 'bool':
            if value == "On" or value == "Active" or value == "Loss" or value == True or value == "Closed":
                values[key] = '1'
            else:
                values[key] = '0' 
        else:
          values[key] = str(value)
    return values



  # This function writes the logged values to the database
  def _saveLoggedValuesToDatabase(self):
    self.replaceValue = False
    self.replaceValueData = {}
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select name from site")
    siteName = cur.fetchone()
    siteName = siteName[0]
    subStrings = []
    subStrings = systemConstants.DATA_LOG_SUB_STRINGS
    #log.debug(siteName)
    conn.close()
    logCloudData = OrderedDict()
    logCloudData1 = OrderedDict()
    conn = dbUtils.getLogDatabaseConnection()
    try:
      currentDateTime = datetime.datetime.utcnow()
      dateIdx = None
      cur = conn.cursor()

      deviceKeys = self.directory.getDeviceObjectKeys()
      len1 = 0
      noOfDevices = len(deviceKeys)
      for deviceKey in deviceKeys:
        len1 = len1 + 1
        device = self.directory.getDeviceObject(deviceKey)
        if device is not None:
          if device.areLoggedValuesReady():
            device.clearLoggedValuesReady()
          else:
            continue

          if dateIdx is None:
            cur.execute("INSERT INTO [dates] ([date]) values (?)", (currentDateTime,))
            dateIdx = cur.lastrowid
          valueNames = self.getLoggedValuesForDevice(deviceKey)
          values = device.getListedValues(valueNames)
          values = self._prepareListedValuesForLogging(device, values)
          self.logCloudData[deviceKey] = OrderedDict()
          k = 0
          for valueKey in values:
            if any(val in valueKey for val in subStrings):
              deviceValueKey = valueKey
              deviceValueKey = deviceValueKey.replace("SUCT PRES OUT", "FILTERED PRES")
              deviceValueKey = deviceValueKey.replace("CUR PRES SETPT", "SUCT PRES SETPT")
              deviceValueKey = deviceValueKey.replace("CUR PRESS SETPT", "SUCT PRES SETPT")
              #valueKey.replace("CUR PRES SETPT", "SUCT PRES SETPT")
              #valueKey.replace("CUR PRESS SETPT", "SUCT PRES SETPT")
              # if valueKey.find("CUR PRES SETPT") >=0 or valueKey.find("CUR PRESS SETPT") >=0:
                # self.replaceValue = True
                # if deviceKey in self.replaceValueData:
                  # self.replaceValueData[deviceKey]["curKey"] = k
                  # self.replaceValueData[deviceKey]["value"] = values[valueKey]
                # else:
                  # self.replaceValueData[deviceKey] = {}
                  # self.replaceValueData[deviceKey]["curKey"] = k
                  # self.replaceValueData[deviceKey]["value"] = values[valueKey]
              # if valueKey.find("SUCT PRES SETPT") >=0:
                # if deviceKey in self.replaceValueData:
                  # self.replaceValueData[deviceKey]["suctionKey"] = k
                # else:
                  # self.replaceValueData[deviceKey] = {}
                  # self.replaceValueData[deviceKey]["suctionKey"] = k
              self.logCloudData[deviceKey][k] = OrderedDict()
              self.logCloudData[deviceKey][k]['date'] = currentDateTime
              self.logCloudData[deviceKey][k]['valueKey'] = deviceValueKey
              self.logCloudData[deviceKey][k]['value'] = values[valueKey]
              k=k+1
            # check to see if an index exists for device value pair
            # if not, add it
            # regardless you will end up with a value index
            cur.execute("select * from devicevalues where deviceName=? and valueName=?", (deviceKey, valueKey))
            #logCloudData[deviceKey]['deviceKey'] = deviceKey
            logValueInfo = cur.fetchone()
            if logValueInfo is None:
              cur.execute("INSERT INTO devicevalues (deviceName, valueName) values (?, ?)", (deviceKey, valueKey))
              valueIdx = cur.lastrowid
            else:
              valueIdx = logValueInfo["idx"]

            # get that number and insert the dateIdx, valueIdx and value into the database
            # log.debug("Adding value: " +  deviceKey + ", " + valueKey + ", " + str(values[valueKey]))
            cur.execute("INSERT INTO logs values(?, ?, ?)", (dateIdx, valueIdx, values[valueKey]))
        #log.debug(self.logCloudData)
        if len1 == noOfDevices:
          #log.debug("All Devices are looped")
          # if self.replaceValue == True:
            # for deviceKey in self.replaceValueData:
              # self.logCloudData[deviceKey][self.replaceValueData[deviceKey]["suctionKey"]]['value'] = self.replaceValueData[deviceKey]["value"]
          systemConstants.LOGGING_VALUES = self.logCloudData
          systemConstants.SITENAME = siteName
          systemConstants.DEVICE_LEN = len1
          #alarmEmailer.sendDataEmail(self.logCloudData, siteName, len1)
          #log.debug(systemConstants.LOGGING_VALUES)

      conn.commit()

    except:
      log.exception("Error in saveLoggedValuesToDatabase")
    finally:
      conn.close()

  # Returns a dict of all parameter names being logged for a device in the format: retval[deviceName] = { 'key':<parameter key>, 'displayName' : readable parameter name }
  def getAllLoggedValues(self):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select * from logging")
    retval = {}
    for loggingInfo in cur.fetchall():
      deviceName = loggingInfo["deviceName"]
      deviceObj = self.directory.getDeviceObject(deviceName)
      if not deviceObj is None:
        if not deviceName in retval:
          retval[deviceName] = []
        valueName = loggingInfo["valueName"]
        if deviceObj.deviceTypeName == 'E2 Device': # For E2, the key needs to be the display name - because it is a collection of apps/device not single device
          retval[deviceName].append({"key": valueName, "displayName": valueName })
        else :
          retval[deviceName].append({"key": valueName, "displayName": deviceObj.getValueDescriptions()[valueName]["displayName"] })
    conn.close()
    return retval


  # Returns a list of LOGGED parameter "KEY" names for a device
  def getLoggedValuesForDevice(self, deviceName):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select valueName from logging where deviceName = ?", (deviceName,))
    retval = []
    for loggingInfo in cur.fetchall():
      retval.append(loggingInfo["valueName"])
    conn.close()
    return retval

  # Sets a list of LOGGED parameter "KEY" names for a device
  def setLoggedValuesForDevice(self, deviceName, newValues, setValue=1):
    # update database
   # log.debug(deviceName)
   # log.debug(setValue)
    if setValue == 1:

      conn = dbUtils.getSystemDatabaseConnection()
      try:
        cur = conn.cursor()
        cur.execute("delete from logging where deviceName = ?", (deviceName,))
        for value in newValues:
          cur.execute("INSERT INTO logging values (?, ?)", (deviceName, value))
        conn.commit()

      except Exception, e:
        log.exception("Error in setLoggedValuesForDevice" + deviceName + " " + newValues + str(e))
      finally:
        conn.close()

  ###############################################################################
  # EXTERNAL INTERFACES
  
  #############################################################################
  #  Clears all tables in the log database files to default configuration.
  def setLogDatabaseToFactorySettings(self) :
    log.debug( "setLogDatabaseToFactorySettings")
    conn = dbUtils.getLogDatabaseConnection()
    try:
      cur = conn.cursor()
      # "Reset" all log records.
      cur.execute('delete from dates')
      cur.execute('delete from devicevalues')
      almMgrObj = self.directory.getAlarmManager()
      almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Deleting Logs...This could take a few minutes"
      log.debug(almMgrObj.strTestEmailMsg)
      cur.execute('delete from logs')
      cur.execute('delete from sqlite_sequence')
      almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Updating Log Database. Please Wait"
      log.debug(almMgrObj.strTestEmailMsg)
      conn.commit()
    except:
      log.exception("Error in setLogDatabaseToFactorySettings - log")
      
    conn.close()
    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Compressing Database"
    log.debug(almMgrObj.strTestEmailMsg)
    dbUtils.vacuumDatabase( dbUtils.logDatabasePath ) # Compress database

    # Clear logging information in the system database.
    # update system database to remove device from logged points
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute('delete from logging')
      conn.commit()
    except:
      log.exception("Error in setLogDatabaseToFactorySettings - system")
    conn.close()
    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Log Database Update Complete"
    log.debug(almMgrObj.strTestEmailMsg)




  def _databaseCleanup(self):
    # first read the logging duration days from database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select loggingDurationDays from system")
      systemInfo = cur.fetchone()
      loggingDurationDays = int(systemInfo["loggingDurationDays"])
    except:
      log.exception("Error in databaseCleanup")
    finally:
      conn.close()

   # loggingDurationDays = 90 # For limiting the logging to 90 days if needed.
    
    conn = dbUtils.getLogDatabaseConnection()
    try:
      # execute a query that will delete all records older than this
      deleteDate = datetime.datetime.utcnow() - datetime.timedelta(loggingDurationDays)

      cur = conn.cursor()
      log.info('Deleting dates older than ' + str(deleteDate))
      cur.execute("delete from dates where [date] < ?", (deleteDate,) )
      log.info('Deleting log entries where device no longer exists')
      cur.execute("delete from logs where valueIdx not in (select idx from devicevalues)")
      log.info('Deleting log entries where date no longer exists')
      cur.execute("delete from logs where dateIdx not in (select idx from dates)")
      log.info('Deleting from dates where log no longer exists')
      cur.execute("delete from dates where idx not in (select dateidx from logs)")
      conn.commit()


      '''
      cur = conn.cursor()
      log.info('Deleting logs older than ' + str(deleteDate))
      cur.execute("select max([date]) as timestamp, idx from dates where [date] < ?", (deleteDate,) )
      deleteRec = cur.fetchone()
      if deleteRec is not None:
        cur.execute("delete from dates where idx <= ?", (deleteRec["idx"],))
        cur.execute("delete from logs where dateIdx <= ?", (deleteRec["idx"],))
      conn.commit()
      '''

      #log.debug("Vacuum logging database")
      #conn.execute("vacuum")
    except:
      log.exception("Error in databaseCleanup")
    finally:
      conn.close()


  # This also deletes any future logging - part of deleting a device
  def deleteLogsForDevice(self, deviceName):
    log.info('Deleting logs for device ' + deviceName)

    # update system database to remove device from logged points
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("delete from logging where deviceName=?", (deviceName,))
      strAudit = 'Delete all logs for device {0}'.format( deviceName )
      auditTrail.AuditTrailAddEntry( strAudit )
      conn.commit()
    except:
      log.exception("Error in deleteLogsForDevice")
    finally:
      conn.close()

    # no lock needed here as we are writing to the database
    conn = dbUtils.getLogDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute('delete from devicevalues where deviceName=?', (deviceName,))
      conn.commit()
    except:
      log.exception("Error in deleteLogsForDevice")
    finally:
      conn.close()

    self.directory.getSystemObject().reinitialize() # restarts the system

  # This deletes DATA logs but the device's log entries persist - used to clear data values only
  def deleteAllLogs(self):
    log.info("Deleting all logs")
    # no lock needed here as we are writing to the database
    conn = dbUtils.getLogDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("delete from devicevalues")
      conn.commit()

      strAudit = '{0} Deleted All Log Data'.format( getSessionUsername( session ) )
      auditTrail.AuditTrailAddEntry( strAudit )
      self.databaseCleanupEvent.trigger()
    except:
      log.exception("Error in deleteAllLogs")

    conn.close()
    # we need to do this after the close because vacuumDatabase opens and closes the database.
    dbUtils.vacuumDatabase(dbUtils.logDatabasePath)  # Compress database

  def stop(self):
    if self.logThread is not None:
      if self.logThread.isAlive():
        log.info("Stopping get logging value")
        self.stopLogThread = True
        try:
          self.logThread.join()
        except Exception:
          log.exception("Exception when stopping logging thread")

  def execute(self):
    # If it is time to log, notify all devices that log points are needed.
    self._updateLoggedValuesFromDevices()
    # Stores log point into the database for all "_logready" devices and points.
    self._saveLoggedValuesToDatabase()
    # See if we need to condense the log database
    if self.databaseCleanupEvent.hasElapsed():
      self._databaseCleanup()



##################################################


  def _getLogForValue(self, conn, op):
    try:
      idx = op['idx']
      request = op['request']
      values = request['values']
      deviceName = values[idx]['deviceName']
      valueName = values[idx]['valueName']
      startdate = request['startdate']
      enddate = request['enddate']

      cur = conn.cursor()
      buf = 'select date as date, [value] from logs join dates on logs.dateIdx = dates.idx join devicevalues on logs.valueIdx = devicevalues.idx where ((deviceName="{0}" and valueName="{1}") or deviceName="{2}") and date between "{3}" and "{4}" order by date asc'.format( deviceName, valueName, "_SYSTEM_START_", startdate, enddate)
      cur.execute( buf )
#      cur.execute('select date as date, [value] from logs join dates on logs.dateIdx = dates.idx join devicevalues on logs.valueIdx = devicevalues.idx where ((deviceName=? and valueName=?) or deviceName=?) and date between ? and ? order by date asc', (deviceName, valueName, '_SYSTEM_START_', startdate, enddate) )
      return (cur, deviceName, valueName)

    except:
      log.exception("Error in _getLogForValue")

  def _formatRowToLocalTime(self, data, format):
    datepart, timepart = data.split(" ")
    year, month, day = map(int, datepart.split("-"))
    timepart_full = timepart.split(".")
    hours, minutes, seconds = map(int, timepart_full[0].split(":"))
    dt = datetime.datetime(year, month, day, hours, minutes, seconds) + datetime.timedelta(0, utilities.getCurrentUTCOffsetSeconds())
    return dt.strftime(format)

  def _convertUnits( self, value, unitConvertType ) :

    if value != None :
      fValue = float(value)
      if unitConvertType == "tempToF" :
        retVal = str( (fValue * 1.8) + 32.0 )
      elif unitConvertType == "deltatempToF" :
        retVal = str( (fValue / 1.8) )
      elif unitConvertType == "tempToK" :
        retVal = str( fvalue + 273.0 )
      elif unitConvertType == "prsTopsi" :
        retVal = str( fValue * 0.000145037738007 )
      elif unitConvertType == "prsTokPa" :
        retVal = str( fValue * 0.001 )
      elif unitConvertType == "prsToinH2O" :
        retVal = str( fValue * 0.00401474213311 )
      else :
        retVal = value        # value unchanged.
    else :
      retVal = None
    return retVal

  def _formatLogCsv(self, op, cur, deviceName, valueName):
    csvlog = []
    # write header here
    try:
      dictValueDescription = self.directory.getDeviceObject(deviceName).getValueDescriptions()[valueName]
      displayName = dictValueDescription['displayName']
      unitType = dictValueDescription['unitType']
      if unitType.find("temperature") == 0 and op['displayUnit']['temperature'].find("F") >= 0 :
        unitConvertType = "tempToF"
      elif unitType.find("deltatemperature") == 0 and op['displayUnit']['temperature'].find("F") >= 0 :
        unitConvertType = "deltatempToF"
      elif unitType.find("temperature") == 0 and op['displayUnit']['temperature'].find("K") >= 0 :
        unitConvertType = "tempToK"
      elif unitType.find("pressure") >= 0 :
        if op['displayUnit']['pressure'].find("psi") >= 0 :
          unitConvertType = "prsTopsi"
        elif op['displayUnit']['pressure'].find("kPa") >= 0 :
          unitConvertType = "prsTokPa"
        elif op['displayUnit']['pressure'].find("inH2O") >= 0 :
          unitConvertType = "prsToinH2O"
        else :
          unitConvertType = None
      else:
        unitConvertType = None
    except:
      displayName = "Invalid device or value"
      blUnitTypeConvert = False

    hdr = '"' + deviceName + '/' + displayName
    csvlog.append(hdr + '/Date",' + hdr + '/Value"')
    row = cur.fetchone()
    while not row is None:
      logio = cStringIO.StringIO()
      logio.write('\"')
      logio.write(self._formatRowToLocalTime(row[0], op['request']['csvDateFormat']))
      logio.write('\",\"')
      value = row[1]
      if value != None :
        if unitConvertType != None :
          value = self._convertUnits( row[1], unitConvertType )
      else :
        value = 'None'
      logio.write(value)
      logio.write('\"')
      csvlog.append(logio.getvalue())
      row = cur.fetchone()
    op['logs'].append(csvlog)

  def _finalizeLogCsv(self, op):
    data = itertools.izip_longest(*op['logs'], fillvalue = ',')
    op['logs'] = '\n'.join(map(lambda x: ','.join(x), data))

  def _formatLogJson(self, op, cur, deviceName, valueName):
    try:
      valueDescription = self.directory.getDeviceObject(deviceName).getValueDescriptions()[valueName]
    except:
      valueDescription = {}

    logItem = { 'deviceName': deviceName, 'valueName': valueName, 'valueDescription': valueDescription, 'data': '' }
    logio = cStringIO.StringIO()
    logio.write('[')
    bComma = False
    row = cur.fetchone()
    while not row is None:
      if bComma:
        logio.write(',')
      else:
        bComma = True
      logio.write('[\"')
      logio.write(row[0].replace(' ', 'T'))
      logio.write('Z\",\"')
      logio.write(row[1] if row[1] != None else 'None')
      logio.write('\"]')
      row = cur.fetchone()
    logio.write(']')
    logItem['data'] = logio.getvalue()
    op['logs'].append(logItem)

  def _formatLog(self, op, cur, deviceName, valueName):
    request = op['request']
    if request['dataform'] == 'csv':
      self._formatLogCsv(op, cur, deviceName, valueName)
    else:
      self._formatLogJson(op, cur, deviceName, valueName)

  def _finalizeLog(self, op):
    request = op['request']
    if request['dataform'] == 'csv':
      self._finalizeLogCsv(op)


#    self.logLock = threading.RLock()
#    self.logThread = None
#    self.logActiveOps = {}
#    self.logNextId = 0

# dataform: 'csv/json', values: [{deviceName, valueName},...], startdate, enddate, csvDateFormat

# id: { progress: X, state: 'active/done', access: datetime, request: {}, idx: 0, logs: []}

  def _getLogThread(self):
#    log.debug("Starting log retrieval thread")
    conn = dbUtils.getLogDatabaseConnectionRaw()
    try:
      while not self.stopLogThread:
        with self.logLock:
          ids = copy.deepcopy(self.logActiveOps.keys())
          if len(ids) == 0:
#            log.debug('Exiting log retrieval thread')
            return

        for id in ids:
          op = None
          with self.logLock:
            op = self.logActiveOps[id]

            if (datetime.datetime.utcnow() - op['access']) > datetime.timedelta(0, 30):
              del self.logActiveOps[id]
              continue

            if op['state'] == 'done':
              continue

          if op != None:
            cur, deviceName, valueName = self._getLogForValue(conn, op)
            self._formatLog(op, cur, deviceName, valueName)
            idx = op['idx'] + 1
            numberOfValues = len(op['request']['values'])
            if idx == numberOfValues:
              self._finalizeLog(op)

            with self.logLock:
              op['idx'] = idx
              if idx == numberOfValues:
                op['progress'] = 100.0
                op['state'] = 'done'
              else:
                op['progress'] = (float(idx) / float(numberOfValues)) * 100.0

        time.sleep(0.01)
    except:
      log.exception("Log retrieval failed")

  def getLogStart(self, dataform, values, startdate, enddate, displayUnit, csvDateFormat=None):
    if len(values) == 0:
      return { 'id': 'id Error' }

    if csvDateFormat is None:
      csvDateFormat = '%Y-%m-%d %H:%M:%S'

    with self.logLock:
      request = { 'dataform':dataform, 'values': values,
        'startdate': utilities.iso8601ToDateTime(startdate),
        'enddate': utilities.iso8601ToDateTime(enddate),
        'csvDateFormat': csvDateFormat }
      op = {'progress': 0, 'state': 'active', 'access': datetime.datetime.utcnow(), 'request': request, 'idx': 0, 'logs': [], 'displayUnit': displayUnit }
      id = str(self.logNextId)
      self.logActiveOps[id] = op
      self.logNextId = self.logNextId + 1

      if self.logThread is None or not self.logThread.isAlive():
        self.logThread = threading.Thread(target=self._getLogThread)
        # print "Logging Thread = {0}".format( self.logThread.getName() )

        self.logThread.start()
      return {'id': id, 'progress': op['progress'], 'state': op['state']}

  def getLogProgress(self, id):
    id = str(id)
    with self.logLock:
      if not id in self.logActiveOps:
        return {'id': 'id Error'}
      op = self.logActiveOps[id]
      op['access'] = datetime.datetime.utcnow()
      return {'id': id, 'progress': op['progress'], 'state': op['state']}

  def getLogCancel(self, id):
    id = str(id)
    with self.logLock:
      if not id in self.logActiveOps:
        return {'id': 'id Error'}
      del self.logActiveOps[id]
      return {'id': id}

  def getLogFinish(self, id):
    id = str(id)
    with self.logLock:
      if not id in self.logActiveOps:
        return {'id': 'id Error', 'strError' : 'Could Not Find CSV Buffer'}
      op = self.logActiveOps[id]
      if op['state'] == 'done':
        retval = {'id': id, 'logs': op['logs']}
        del self.logActiveOps[id]
        return retval
      else:
        op['access'] = datetime.datetime.utcnow()
        return {'id': id, 'progress': op['progress'], 'state': op['state']}



