#! /usr/bin/python

import threading
import sqlite3
import datetime
import glob
import os
import time
import shutil
import fileinput
import subprocess
from flask import json

import dbUtils
import elapsedTimer
import systemInterface
import utilities
import auditTrail
import systemConstants
import alarmEmailer

import logsystem
log = logsystem.getLogger()
import leoObject
from collections import OrderedDict

watchExpirationSeconds = 10

def initializeRTC():
  return systemInterface.initializeRTC(30)

class SystemObject:
  def __init__(self, directory):
    self.lock = threading.RLock()
    self.directory = directory

    self.checkRestoredDatabases()

    self.statusWatchList = {}
    self.statusWatchConfigurationUpdate = elapsedTimer.Interval(30)   # should this come from the database

    self.periodicallyUpdateValues = elapsedTimer.Interval(30)  # start with thirty then switch to 600

    self.periodicallyEmailDataLogValues = elapsedTimer.Interval(30)

    self.periodicallySyncValues = elapsedTimer.Interval(30)

    self.initialize = False

  def mustReinitialize(self):
    with self.lock:
      retval = self.initialize
      self.initialize = False
      return retval

  def reinitialize(self):
    with self.lock:
      self.initialize = True

  def getSiteInfo(self):
    # no lock needed here as we are NOT writing to the database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select * from site")
      return dbUtils.dictFromRow(cur.fetchone())
    finally:
      conn.close()
    return {}

  def setSiteInfo(self, newInfo):
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("update site set name=?, address=?", (newInfo["name"], newInfo["address"]))
      conn.commit()
      return True
    finally:
      conn.close()
    return False

  def getEmailSettings(self, version=1):
    # no lock needed here as we are writing to the database
    conn = dbUtils.getSystemDatabaseConnection()
#    try:
    cur = conn.cursor()
    if version == 2:
      retVal = {}
      retVal['version'] = version
      # Get email address records
      cur.execute("select * from emailaddresses")
      emailAddrRecs = []
      for dbRec in cur.fetchall():
        dict = dbUtils.dictFromRow(dbRec)
        emailAddrRecs.append(dict)
      retVal['emailAddrRecs'] = emailAddrRecs
      
      # Get email server records
      cur.execute("select * from emailservers")
      emailServerRecs = []
      for dbRec in cur.fetchall():
        dict = dbUtils.dictFromRow(dbRec)
        emailServerRecs.append(dict)
      retVal['emailServerRecs'] = emailServerRecs
      
      # Get "Single" settings for alarm email subsystem (e.g. Enable Alarm Email, Email Reports perday)
      cur.execute("select alarmReportsPerDay,statusReportsPerHour, enablealarmemail, alarmemaildelay, emailretrydelay from emailsettings")
      dbRec = cur.fetchone()
      dict = dbUtils.dictFromRow(dbRec)
      retVal['alarmReportsPerDay'] = dict['alarmReportsPerDay']
      retVal['statusReportsPerHour'] = dict['statusReportsPerHour']
      retVal['enablealarmemail'] = dict['enablealarmemail']
      retVal['alarmemaildelay'] = dict['alarmemaildelay']
      retVal['emailretrydelay'] = dict['emailretrydelay']
      conn.close()
      return retVal
    
    else :
      cur.execute("select * from emailsettings")
      emailRecord = cur.fetchone()
      conn.close()
      if emailRecord == None :
        return None
      else :
        return dbUtils.dictFromRow(emailRecord)

  def setEmailSettings(self, newSettings, version=1):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()

    try:
      if version == 2: # New mulitiple email addresses.
        # One day we may want to be smarter and compare and adjust the records, but right now, we need to get this done.
        # Delete stored email address records and insert new settings.
        cur.execute("delete from emailaddresses")

        for rec in newSettings['emailAddrRecs'] :
          # We need to create a new record in each table and copy over the existing values.
          strSQL = 'INSERT INTO emailaddresses ( toaddress,emailservername,enableemail,enablealarmreport) VALUES ("{0}","{1}",{2},{3})' \
              .format(  rec['toaddress'], rec['emailservername'], rec['enableemail'], rec['enablealarmreport'] )
          cur.execute(strSQL)
        conn.commit()

        cur.execute("delete from emailservers")
        
        for rec in newSettings['emailServerRecs'] :
          # We need to add the email servers table and record
          # We need to create a new record in each table and copy over the existing values.
          strSQL = 'INSERT INTO emailservers ( emailservername,smtpserver,smtpport,fromaddress,enableauthentication,authaccount,' \
                   'authpassword,enabletls,defaultServer) VALUES ("{0}","{1}","{2}","{3}",{4},"{5}","{6}",{7},{8})'. \
                    format(rec['emailservername'], rec['smtpserver'],rec['smtpport'], rec['fromaddress'], \
                           rec['enableauthentication'], rec['authaccount'], rec['authpassword'], rec['enabletls'],rec['defaultServer'])
          if (rec['defaultServer'] == 1):
            self.writePostfixConfig(rec)

          cur.execute(strSQL)
        conn.commit()

        # Centralized email alarm subsystem settings.
        cur.execute("update emailsettings set enablealarmemail=?, alarmReportsPerDay=?, alarmemaildelay=?, emailretrydelay=?, statusReportsPerHour=?",
          (newSettings["enablealarmemail"],newSettings["alarmReportsPerDay"],newSettings["alarmemaildelay"],newSettings["emailretrydelay"],newSettings["statusReportsPerHour"]))
        conn.commit()

      else :
        # Version 1
        cur.execute("update emailsettings set alarmemailperday=?, fromaddress=?, toaddress=?",
          (newSettings["alarmemailperday"], newSettings["fromaddress"], newSettings["toaddress"]))
  
        cur.execute("update emailsettings set smtpserver=?, smtpport=?, enableauthentication=?, authaccount=?, authpassword=?, enablealarmemail=?, enabletls=?, alarmReportsPerDay=?, statusReportsPerHour=?",
          (newSettings["smtpserver"],newSettings["smtpport"],newSettings["enableauthentication"],newSettings["authaccount"],
          newSettings["authpassword"],newSettings["enablealarmemail"],newSettings["enabletls"],newSettings["alarmReportsPerDay"],newSettings["statusReportsPerHour"]))

      conn.commit()
      conn.close()

      # Re-init values in alarm manager settings (e.g. timers, etc) based upon changes
      self.directory.getAlarmManager().initAlarmManagerSettings()

      return True
    except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      log.exception( strEx )
    finally:
      conn.close()
    return False

  def writePostfixConfig(self,rec):
    if (rec['enableauthentication'] == 0):
      with open("/etc/postfix/main.cf", "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
          if (("smtp_sasl_password_maps" in i) or ("relayhost = [" in i) or ("smtp_sasl_auth_enable" in i)):
            # newLine = "#"+i+"\n"
            # f.write(newLine)
            abc =0
          else:
            f.write(i)
        newLine = "\n"+"relayhost = ["+rec["smtpserver"]+"]:"+rec["smtpport"]+"\n"
        f.write(newLine)
        newLine = "#smtp_sasl_auth_enable = yes"+"\n"
        f.write(newLine)
        newLine = "#smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd"+"\n"
        f.write(newLine)
        f.truncate()
    elif (rec['enableauthentication'] == 1):
      with open("/etc/postfix/main.cf", "r+") as f:
        d = f.readlines()
        f.seek(0)
        for i in d:
          if (("smtp_sasl_password_maps" in i) or ("relayhost = [" in i) or ("smtp_sasl_auth_enable" in i)):
            # i.replace("#","")
            # f.write(i)
            abc = 0
          else:
            f.write(i)
        newLine = "\n"+"relayhost = ["+rec["smtpserver"]+"]:"+rec["smtpport"]+"\n"
        f.write(newLine)
        newLine = "smtp_sasl_auth_enable = yes"+"\n"
        f.write(newLine)
        newLine = "smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd"+"\n"
        f.write(newLine)
        f.truncate()
      with open("/etc/postfix/sasl_passwd", "r+") as p:
        d = p.readlines()
        p.seek(0)
        for i in d:
          #if i.find("["):
          abc = 0
        newLine = "["+rec["smtpserver"]+"]:"+rec["smtpport"]+" "+rec["authaccount"]+":"+rec["authpassword"]+"\n"
        p.write(newLine)
        p.truncate()
      subprocess.call("postmap /etc/postfix/sasl_passwd", shell=True)


  def getCurrentTime(self):
    retval = {}
    retval["timeZone"] = systemInterface.getSystemTimeZone()
    retval["timeZoneList"] = systemInterface.getSystemTimeZoneList()
    retval["currentTime"] = utilities.getUTCnowFormatted()
#    retval["currentTime"] = utilities.getUTCnowFormatted("UTC")
    # print "Current Time in UTC = ", retval["currentTime"]

    # timezone offset in minutes
    retval["currentTimeZoneOffsetMinutes"] = utilities.getCurrentUTCOffsetMinutes()
    return retval

  # This function will set the system time. timeInfo is a dict made up of the timezone and the date in ISO8601 format.
  def setCurrentTime(self, timeInfo):

    systemInterface.setSystemTimeZone(timeInfo["timeZone"])
    # The currentTime must be in UTC and formatted in ISO8601
    log.debug( 'setCurrentTime:{}'.format( timeInfo ) )
    # 2014-10-11T11:09:00.000Z
    log.debug( "setCurrentTime:{}".format( timeInfo["currentTime"] ) )
    # Need for format to proper dateFormat
    
    systemInterface.setSystemTime( timeInfo["currentTime"] )

    return utilities.getUTCnowFormatted()

  def getEthernetSettings(self):
    # no lock needed here as we are NOT writing to the database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select * from ethernet")
      return dbUtils.dictFromRow(cur.fetchone())
    finally:
      conn.close()
    return {}

  def setEthernetSettings(self, settings):
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()

      # Let's remove leading and trailing spaces - just in case.
      settings['address'] = settings['address'].strip()
      settings['netmask'] = settings['netmask'].strip()
      settings['network'] = settings['network'].strip()
      settings['gateway'] = settings['gateway'].strip()
      settings['dnsaddress'] = settings['dnsaddress'].strip()

      # If DHCP is set, we do NOT want to store  any IP Address in the database. Only used for displaying
      if settings["dhcp"] > 0 :
        settings['address'] = ''
        settings['netmask'] = ''
        settings['network'] = ''
        settings['gateway'] = ''
        settings['dnsaddress'] = ''

      cur.execute("update ethernet set hostname=?, dhcp=?, address=?, netmask=?, network=?, gateway=?, dnsaddress=?",
        (settings["hostname"],
        settings["dhcp"],
        settings["address"],
        settings["netmask"],
        settings["network"],
        settings["gateway"],
        settings["dnsaddress"]))
      conn.commit()

      systemInterface.setHostName(settings["hostname"])
      systemInterface.writeConfigFileEthernetSettings(settings["dhcp"],
                                          settings["address"],
                                          settings["netmask"],
                                          settings["network"],
                                          settings["gateway"],
                                          settings["dnsaddress"])

      return True
    except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      log.exception( strEx )
    finally:
      conn.close()
    return False

  def getSystemSettings(self):
    # no lock needed here as we are reading from the database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select * from system")
      values = dbUtils.dictFromRow(cur.fetchone())
      values["timeServer"] = str(values["timeServer"])
      return values #dbUtils.dictFromRow(cur.fetchone())
    finally:
      conn.close()
    return {}

  def setSystemSettings(self, settings):
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      # Loop through settings and update database fields - so that we can simply add information to the database and automatically save...
      strSQL = "update system set "
      for key in settings:
        if key == "timeServer":
          strSQL = strSQL + "{0}='{1}',".format( key, settings[key] )
        else:
          strSQL = strSQL + "{0}={1},".format( key, settings[key] )
      # remove last comma
      strSQL = strSQL[0:strSQL.rfind(",")]
      self.setTimeServerValue(settings["timeServer"])
#      print "setSystemSettings SQL->", strSQL
      cur.execute( strSQL )
      conn.commit()
      self.reinitialize()
      # Re-init values in alarm manager settings based upon user settings
      self.directory.getAlarmManager().initAlarmManagerSettings()
      return True
    except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      log.exception( strEx )
    finally:
      conn.close()
    return False

  def setTimeServerValue(self, value):
    if (value != "NA"):
      with open('/etc/ntp.conf-CUST', 'r') as file:
        filedata = file.read()
        filedata = filedata.replace('##########',value)
      with open('/etc/ntp.conf','w') as file:
        file.write(filedata)
      strCommand = "/etc/init.d/ntp stop && /usr/sbin/ntpdate "+ value +" && /sbin/hwclock --systohc && /etc/init.d/ntp start"
      subprocess.call(strCommand, shell=True)
    elif (value == "NA"):
      with open('/etc/ntp.conf-ORIG', 'r') as file:
        filedata = file.read()
      with open('/etc/ntp.conf','w') as file:
        file.write(filedata)
      strCommand = "/etc/init.d/ntp stop && /usr/sbin/ntpdate ntp.ubuntu.com && /sbin/hwclock --systohc && /etc/init.d/ntp start"
      subprocess.call(strCommand, shell=True)
    return True

  ###########################################
  #  System Database Blue-R
  ###########################################
  # iResetType: 0 = Do Nothing, 1 = Reset ALL & Set IP Information to blank, 2 = Reset All EXCEPT IP Information
  #######################################################################
  def setSystemDatabaseToFactorySettings(self, iResetType ) :
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    # "Reset" all records.
    cur.execute('delete from devices')

    # Re-Init LEGACY email settings
    cur.execute('update emailsettings set alarmemailperday=12, alarmemaildelay=0, fromaddress="", toaddress="", statusReportsPerHour=12')
    cur.execute('update emailsettings set smtpserver="",smtpport=0,enableauthentication=0,authaccount="",authpassword=""')
    cur.execute('update emailsettings set enablealarmemail=1,enabletls=0')
    cur.execute('update emailsettings set alarmReportsPerDay=1, emailretrydelay=5')
 
    # We only want to clear out the ethernet settings on a specific use case.
    # We want the device to stay at the same IP settings so the user does not lose communications capabilities.
    # However, if we have to "reformat" a device for RG, we need to clear out the settings.
    if iResetType == 1 : # This is a RG/Factory INSTALLATION setting - which is a cleared out IP information.
      cur.execute('update ethernet set hostname="",dhcp=1,address="",netmask="",network="",gateway==""')

    # Clear network device list
    cur.execute('delete from networks')

    # Clear site name
    cur.execute('update site set name="Site Name", defaultPage="pageAlarms", address=""')

    # Clear Leo alarm settings
    cur.execute('update system set loggingCycleTime=300, loggingDurationDays=60, alarmCycleTime=30,alarmDurationDays=180')
    cur.execute('update system set alarmChimeEnable=0, alarmChimeInterval=15, alarmChimeVolume=5, alarmChimeSnoozeEnable=0, alarmChimeSnoozeMins=15')
    cur.execute('update system set alarmChimeInterval=60, alarmChimeVolume=50, alarmChimeSnoozeEnable=0, alarmChimeSnoozeMins=15')
    cur.execute('update system set enableLeoCloud=0, timeServer = "NA"')
    # Set NEW Email Settings to factory defaults.
    dbUtils.setEmailAddressAndServerTablesToFactoryDefaults(conn, False)

    conn.commit()
    conn.close()
    dbUtils.vacuumDatabase( dbUtils.systemDatabasePath ) # Compress database

  def getDatabaseBackup(self, database, filename):
    log.info('Backing up database: ' + database)
    conn = dbUtils.getRawDbConnectionByName(database)
    #conn.execute("vacuum")
    try:
      with open(filename, 'w') as f:
        for line in conn.iterdump():
          f.write('%s\n' % line)
    except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      log.exception( strEx )
    finally:
      conn.close()
    return filename

  def setDatabaseRestore(self, database, filename):
    log.info('Restoring database at next restart: ' + database)
    database = database + '.restore'
    conn = dbUtils.getRawDbConnectionByName(database)
    cur = conn.cursor()
    try:
      with open(filename, 'r') as f:
        dbdata = f.read()
        cur.executescript(dbdata)
        conn.commit()
    except Exception, e:
      log.exception( '***** Error ***** {0}'.format( str(e) ) )
      
    finally:
      conn.close()
    return filename

  # called during instantiation
  def checkRestoredDatabases(self):
    # log.info('Checking for database restore files.')
    for f in glob.glob(dbUtils.dbPath + '/*.restore'):
      dbname = os.path.splitext(f)[0]
      if dbname in dbUtils.systemDatabases:
        shutil.copy2(f, dbname)
        log.info('Restoring Database:' + f)
      os.remove(f)

  def setScreenBrightness(self, percent):
    systemInterface.setScreenBrightness(percent)
    return percent

  def recalibrateScreen(self):
    log.info('recalibrateScreen')
    systemInterface.recalibrateScreen()

  def getOsInfo(self):
    return systemInterface.getOsInfo()

  def getSoftwareModulesVersion(self, strSelect):
    return systemInterface.getSoftwareModulesVersion( strSelect )


  # Factory Reset Types: 0 = Do Nothing, 1 = Reset ALL & Set IP Information to blank, 2 = Reset All EXCEPT IP Information
  def factoryReset(self, factoryResetType) :
    print "FACTORY RESET HIT"
    if factoryResetType > 0 :
      leoObject.getLeoObject().setFactoryResetType(factoryResetType)  # Indicate cleanout is in process to suspend execution.
      return "Initiated Reqeuest To Reset Device To Factory Defaults. Restarting System When Reset Complete."
    return "Unknown Factory Reset Request"


  def restartSystem(self, strReasonForReset ):
    # Add Entry to the audit trail and reason for reset.
    strAudit = 'Restarting System - {0}'.format( strReasonForReset )
    auditTrail.AuditTrailAddEntry( strAudit )
    log.info( strAudit )
    time.sleep(2) # Make sure it gets written.
    systemInterface.restartSystem()
    return "Shutdown In Progress"

  def statusWatch(self, device):
    with self.lock:
      self.statusWatchList[device] = datetime.datetime.utcnow()

  def getAuditTrailEntries(self):
    return auditTrail.AuditTrailGetEntries()

  def deleteAllAuditTrailEntries(self):
    return auditTrail.AuditTrailDeleteAllEntries()

  def _executeStatusWatch(self):
    with self.lock:

      # execute the watch

      # first check to see if we should update configuration
      updateConfig = self.statusWatchConfigurationUpdate.hasElapsed()

      # now iterate through the keys
      keysToDelete = []
#      if len( self.statusWatchList ) > 0 :
#        strTemp = "Watching->".format( len( self.statusWatchList ) )
#        log.debug( strTemp )
      for key in self.statusWatchList:
        # if being watched - current time is less than expiration time.
        if ( (datetime.datetime.utcnow()) < self.statusWatchList[key] + datetime.timedelta(0, watchExpirationSeconds)):
          device = self.directory.getDeviceObject(key)
          if device is not None and device.isNetworkDevice():
            device.updateStatus()
            if updateConfig:
              device.updateDeviceConfiguration()
        else:
          # time expired. Delete this watchpoint.
          keysToDelete.append(key)

      for key in keysToDelete:
        del self.statusWatchList[key]

  def _executePeriodicUpdate(self):
    # update status and configuration periodically
    if self.periodicallyUpdateValues.hasElapsed():
      self.periodicallyUpdateValues.setTimeout(600)
#      self.periodicallyUpdateValues.setTimeout(100) - For Testing
#      print "Running: _executePeriodicUpdate"

#      log.info("Updating values on all devices")
      for key in self.directory.getDeviceObjectKeys():
        device = self.directory.getDeviceObject(key)
        if device is not None and device.isNetworkDevice():
          device.updateStatus()
          device.updateDeviceConfiguration()


  def _executePeriodicSync(self):

    if self.periodicallySyncValues.hasElapsed():
      #self.periodicallyUpdateValues.setTimeout(600)
      self.periodicallySyncValues.setTimeout(600) #- For Testing
#      print "Running: _executePeriodicUpdate"

#      log.info("Updating values on all devices")
      for key in self.directory.getDeviceObjectKeys():
        device = self.directory.getDeviceObject(key)
        if device is not None and device.isNetworkDevice():
          date_time = datetime.datetime.now()
          time = date_time.time()
          #log.debug(time.hour)
          #log.debug(time.minute)
          conn = dbUtils.getDeviceDatabaseConnection()
          cur = conn.cursor()
          cur.execute('select * from syncVal')
          devNames = cur.fetchall()
          conn.close()

          i =0
          configBit1 = OrderedDict()
          for device in devNames:
            configBit1[i] = {"deviceName":device[0],"enableBit":device[1]}
            #print configBit1[i]
            i = i+1

          for row in configBit1:

            if configBit1[row]["enableBit"] == 1 and configBit1[row]["deviceName"] == key :
              values = OrderedDict()
              #print ("entered daily loop")
              if time.hour == 22 and time.minute < 15: #and time.second <30:
                #log.debug("Inside Time Condition") 
                values = self.directory.getDeviceObject(key).loadConstantConfigVals()
                #cur.execute('select * from idealConfigs')
                #data = cur.fetchall()
                #log.debug(values)
                self.directory.getDeviceObject(key).setConfigValues(values)
                #print ("completed")
    


  def _executePeriodicDataLogEmail(self):

    if self.periodicallyEmailDataLogValues.hasElapsed():
      conn = dbUtils.getSystemDatabaseConnection()
      cur = conn.cursor()
      cur.execute("select * from emailsettings")
      valueMins = cur.fetchone()
      conn.close()
      elapsedMins = (60/int(valueMins["statusReportsPerHour"]))*60
      self.periodicallyEmailDataLogValues.setTimeout(elapsedMins)

      logCloudValues = OrderedDict()
      logCloudValues = systemConstants.LOGGING_VALUES
      siteName = systemConstants.SITENAME
      len1 = systemConstants.DEVICE_LEN
      enableLeoCloud = alarmEmailer.getEnableLeoCloudValue()

      if len(logCloudValues) != 0:
        if enableLeoCloud["enableLeoCloud"]!=0:
          alarmEmailer.sendDataEmail(logCloudValues, siteName, len1 )

  def execute(self):
    #print "START _executeStatusWatch {0} ".format(datetime.datetime.utcnow())
    self._executeStatusWatch()
    #print "END _executeStatusWatch {0} ".format(datetime.datetime.utcnow())
    #print "START _executePeriodicUpdate {0} ".format(datetime.datetime.utcnow())
    self._executePeriodicUpdate()
    #print "END _executePeriodicUpdate {0} ".format(datetime.datetime.utcnow())
    self._executePeriodicSync()
    self._executePeriodicDataLogEmail()




