#! /usr/bin/python
from flask import session
import threading
import copy
import sqlite3
import datetime
import os
import subprocess
import json
import utilities
import sys
import os

import time,sys

import dbUtils
import elapsedTimer

import alarmEmailer
import auditTrail
import systemInterface
from LeoFlaskUtils import getSessionUsername
import systemConstants
import leoScheduler
import csv

import logsystem
log = logsystem.getLogger()


MAX_LEO_ALARM_ENTRIES             = 700

# These are bits so that we can represent the type of email action needed in a single variable.
# emailActionBits
SEND_EMAIL_ALARM_REPORT_BIT       = 1

# Events for LEOScheduler
EVENT_SEND_ALARM_REPORT = 1

class AlarmManager:

  def __init__(self, directory):
    self.directory = directory

    self.lock = threading.RLock()
    self.thread = None

    # Things to get passed to the thread
#    self.emailAlarms = None
    self.currentEmailDate = utilities.getUTCnowFormatted()
    self.siteInfo = None

    # Initialize the leoScheduler instance for the alarm manager.
    self.alarmMgrScheduler = []
    self.alarmMgrScheduler.append( leoScheduler )

    # Get AlarmManager initialization values from the database
    self.initAlarmManagerSettings()

    self.systemSettings = None

    # initialize mixer for alarm chime
    self.audioPresent = systemInterface.soundInit()

    self.databaseCleanupEvent = elapsedTimer.DailyEvent(datetime.time(0))
    # self._databaseCleanup()
    self.blSendTestAlarm = False
    self.blSendAlarmReport = False

    self.strTestEmailMsg = ""
    self.strTestEmailError = ""
    self.strTestEmailMsgTimer = elapsedTimer.Timeout()
    self.alarmChimeSnoozeTimeout = elapsedTimer.Timeout() # Simple init required for getSiteStatus

    self.iEnunciatedAlarmFilterEnable = 0
    self.prevdictLatestHistoryAlarmEntry = {}  # Holds latest historical alarm entry so we can reduce database query
    self.autoGetHistoryAlarmsTimer = elapsedTimer.Timeout(180)   # How often to refresh history alarms when there are no changes

  # We need this funciton because there is stuff we need to set AFTER the network and devices have been loaded.
  def afterInitializeObjectsInit(self):
    self.systemSettings = self.directory.getSystemObject().getSystemSettings()

    self.alarmChimeInterval = elapsedTimer.Timeout()
    self.alarmChimeInterval.setTimeout(self.systemSettings["alarmChimeInterval"])
    self.alarmChimeInterval.elapse() # Default to timer expired.

    # We use the Timeout class because we don't want the timer to automatically reset when elapsed.
    self.alarmChimeSnoozeTimeout = elapsedTimer.Timeout()
    self.alarmChimeSnoozeTimeout.setTimeout(self.systemSettings["alarmChimeSnoozeMins"] * 60)
    self.alarmChimeSnoozeTimeout.elapse() # Default to timer expired.
    self.blEnunciatedAlarmsActive = 0

    self._loadEnunciatedAlarmFilters() # Get Leo Alarm Filters from file

      ###########################################
    #
    # basic alarm functions
    #
    ###########################################

    # Alarm Database Blue-R
  def setAlarmDatabaseToFactorySettings(self) :
      conn = dbUtils.getAlarmDatabaseConnection()
      cur = conn.cursor()
      # Clear all the alarm records.
      cur.execute('delete from devicealarms')
      cur.execute('delete from lastemail')
      conn.commit()
      conn.close()
      dbUtils.vacuumDatabase( dbUtils.alarmDatabasePath ) # Compress database
      self._initEnunciatedAlarmFiltersToFactorySettings()

    # Purging older alarms based the maximum number
  def _databaseCleanup(self):
      # first read the logging duration days from database - DEPRECATED
      doThis = 0
      if doThis > 0 :
        conn = dbUtils.getSystemDatabaseConnection()
        cur = conn.cursor()
        cur.execute("select alarmDurationDays from system")
        systemInfo = cur.fetchone()
        alarmDurationDays = int(systemInfo["alarmDurationDays"])
        conn.close()

      # We will delete alarm database records based upon the number of records.
      conn = dbUtils.getAlarmDatabaseConnection()
      cur = conn.cursor()
      strSQL = "delete from devicealarms where date not in ( select date from devicealarms order by date desc limit {0} )".format( MAX_LEO_ALARM_ENTRIES )
      cur.execute( strSQL )
      conn.commit()
      conn.close()
      dbUtils.vacuumDatabase( dbUtils.alarmDatabasePath ) # Compress database
      log.debug("Database cleanup of LEO alarm entries")
      dbUtils.EmailDatabaseCleanup()

      # Looping through devices to request an alarm update
  def _executeAlarmUpdateOnDevices(self):
      # update status and configuration periodically
      if self.alarmCycleTimer.hasElapsed():
#         log.debug("Updating alarms on all devices")
        for key in self.directory.getDeviceObjectKeys():
          device = self.directory.getDeviceObject(key)
          if device is not None and device.isNetworkDevice():
            device.updateAlarms()

        self.alarmCycleTimer.setTimeout(int(self.alarmCycleTime))
        self.alarmCycleTimer.reset()
        return True
      return False

  # Determine if it is time to play the alarm chime and enabled.
  def _alarmChimeUpdate(self) :

      # log.debug( "_alarmChimeUpdate" )
      # print "_alarmChimeUpdate - Enun:{0}, Time Remain:{1}".format( self.blEnunciatedAlarmsActive, self.alarmChimeSnoozeTimeout.getTimeRemainingSecs())

      # if there are active alarms
      if self.blEnunciatedAlarmsActive > 0 :

        blPlayChime = False # default to no alarm chime.

        # Let's determine if we have to play the alarm chime

        # If alarm chime is enabled, AND the chime interval is elapsed, then it is time to play a chime.
        if self.systemSettings["alarmChimeEnable"] > 0 :
          # if alarm snooze is enabled, let's see if it is active.
          if self.systemSettings["alarmChimeSnoozeEnable"] > 0 :
            # print "_alarmChimeSnoozeTimeout timeRemaining:{0}".format( self.alarmChimeSnoozeTimeout.getTimeRemainingSecs())
            if self.alarmChimeSnoozeTimeout.getTimeRemainingSecs() <= 0 :
              blPlayChime = True
              # The only place the alarm chime snooze timer can be reset is through the UI. Otherwise, it should stay elapsed.
          else : # Alarm Snooze not active, we can play the chime regardless.
              blPlayChime = True

          if blPlayChime == True :
            # print "_alarmChimeInterval Elapsed?:{0} Remaining:{1}".format( self.alarmChimeInterval.hasElapsed(), self.alarmChimeInterval.getTimeRemainingSecs() )
            if self.alarmChimeInterval.hasElapsed() :
              # Reset the timer so it is "n" number of seconds instead of waiting until end and then resetting
              self.alarmChimeInterval.setTimeout(int(self.systemSettings["alarmChimeInterval"]))
              self.alarmChimeInterval.reset()
              if os.name == "nt" : # We are on the PC. Files relative.
                strSoundFile = "system/AlarmChime.wav"
              else :
                strSoundFile = "/opt/monitor/system/AlarmChime.wav"
              if self.audioPresent is True :
                systemInterface.soundPlayFile( strSoundFile, self.systemSettings["alarmChimeVolume"] )
      else :
        # elapse snooze timer. Needed in case alarm activates while timer still counting down.
        self.alarmChimeSnoozeTimeout.elapse()

  # main loop for alarm manager. Gets run every second
  def execute(self):
    # log.debug("alarmManager execute")
  
    # If we updated the alarms, determine if something needs to be emailed.
    if self._executeAlarmUpdateOnDevices():
      self._processAlarmsEmailing()

      # If it is time to purge old alarm entries.
      if self.databaseCleanupEvent.hasElapsed():
        self._databaseCleanup()
        auditTrail.AuditTrailDatabaseCleanup()
        auditTrail.AuditTrailAddEntry( 'Database Cleanup Was Run Successfully' )
   
      # Time to send test Email
      if self.strTestEmailMsgTimer.hasElapsed():
        # If there is text in the message, make sure it is not in the progress message.
        if len( self.strTestEmailMsg ) > 0 :
          # we don't want to clear the in progress message.
          if self.strTestEmailMsg.find( "In Progress" ) < 0 :
            # It is not in progress. Clear the contents.
            self.strTestEmailMsg = ""
            
    # determine if need to play chime.
    self._alarmChimeUpdate()
    
    #      log.debug("Checking Scheduler Events")
    self.alarmMgrScheduler[0].run_pending()        # Run the leoScheduler "run_pending" to see if any events have triggered.

  ###########################################
  # This should only be called at init and any times the email or alarm settings
  # are changed
  ##########################################
  def initAlarmManagerSettings(self):

      conn = dbUtils.getSystemDatabaseConnection()
      cur = conn.cursor()
      cur.execute("select alarmCycleTime from system")
      systemInfo = cur.fetchone()
      self.alarmCycleTime = int(systemInfo["alarmCycleTime"])

      # Update Alarm manager timers and initialize
      # alarmCycleTimer is free-running...
      self.alarmCycleTimer = elapsedTimer.Interval()
      self.alarmCycleTimer.setTimeout(int(self.alarmCycleTime))
      self.alarmCycleTimer.elapse() # Forces to run

      # Initiliaze Test Email member variables
      self.dictSendTestEmail = { 'blActive' : 0, 'addrserverkey' : "", 'emailtype' : systemConstants.SEND_EMAIL_NONE }

      # Read the latest email settings and set timers and local memory aoppropriately.
      # Make sure we get the right version of email settings
      self.dictEmailSettings = self.directory.getSystemObject().getEmailSettings(2)
      self.initDictAlarmEmailStatus( self.dictEmailSettings )
      conn.close()

  def initDictAlarmEmailStatus(self, inDictEmailSettings ):

      self.dictAlarmEmailStatus = {}
      self.alarmMgrScheduler[0].clear()  # Restart the alarm manager scheduler events.
      val = 0
      enableLeoCloudResult = alarmEmailer.getEnableLeoCloudValue()
      # Loop through email address records. Make sure records in DB are correct.
      for addrRec in inDictEmailSettings['emailAddrRecs'] :
        val = val + 1
        # We use the 'toaddress' as an key into the dictAlarmEmailStatus.
        toaddress = addrRec['toaddress']
        
        # Don't add blank address records.
        if len( toaddress ) > 0 :

          # dictalarmEmailStatus will be "keyed/index" by a combination of email address and server name. This
          # is so that the user can have duplicate email addressed that get sent to through DIFFERENT servers.
          servername = addrRec['emailservername']
          # For Version 1.00B16 - there are settings which were previously configurable that are now STATIC.
          addrserverkey = self.getAddrServerKey( toaddress, servername )
          addrRec['addrserverkey'] = addrserverkey

          # Create dict to hold status information for each email address defined.
          self.dictAlarmEmailStatus[addrserverkey] = {}
          dictEmailStatus = self.dictAlarmEmailStatus[addrserverkey]
          
          # Need to find the matching email address record and get the email settings.
          dictEmailStatus['toaddr'] = toaddress
          dictEmailStatus['servername'] = servername
          dictEmailStatus['emailSettings'] = self.getEmailSettingsForAddrServer(toaddress, servername)
          dictEmailStatus['consecutiveEmailFailures'] = 0
          dictEmailStatus['emailActionBits'] = 0

          # Configure alarmEmailDelayTimer for each address
          dictEmailStatus['alarmEmailDelayTimer'] = elapsedTimer.Timeout()
          dictEmailStatus['alarmEmailDelayTimer'].setTimeout(inDictEmailSettings['alarmemaildelay'] * 60)  # Convert to seconds
          dictEmailStatus['alarmEmailDelayTimer'].reset()  # Reset countdown timer
  
          # Configure alarmEmailFailTimer for each address
          dictEmailStatus['alarmEmailFailTimer'] = elapsedTimer.Timeout()
          dictEmailStatus['alarmEmailFailTimer'].setTimeout(300)  # 300 seconds/5 minute alarm retry
          dictEmailStatus['alarmEmailFailTimer'].reset()  # Reset countdown timer
          
          if addrRec['enablealarmreport'] > 0:
            # alarmReports are scheduled through the leoScheduler module.
            doTestThis = 0
            if doTestThis > 0 :
              # print "TESTING - FORCED SEND ALARM REPORT"
              self.alarmMgrScheduler[0].every(1).minutes.do(self.alarmMgrSchedulerEvent,EVENT_SEND_ALARM_REPORT, addrserverkey)
            else :
              if inDictEmailSettings['alarmReportsPerDay'] > 0 :
                if inDictEmailSettings['alarmReportsPerDay']  == 1 : # Single scheduled job every day at midnight.
                  self.alarmMgrScheduler[0].every().day.at('00:00').do( self.alarmMgrSchedulerEvent, EVENT_SEND_ALARM_REPORT, addrserverkey )
                else :
                  interval = 24 / inDictEmailSettings['alarmReportsPerDay']
                  # print "Alarm Report Interval = ", interval
                  self.alarmMgrScheduler[0].every( interval ).hours.at(':00').do( self.alarmMgrSchedulerEvent, EVENT_SEND_ALARM_REPORT, addrserverkey )
              # This is to obtain continous alarm reports which are used to obtain the status of alarms for LEO enterprise. We have added an extra email record number 7 exclusively for this so for that we have included the below logic to run only for that email settings.
              if val > 6 :
                  interval = 60 / inDictEmailSettings['statusReportsPerHour']
                  # print "Alarm Report Interval = ", interval
                  
                  self.alarmMgrScheduler[0].every(interval).minutes.do(self.alarmMgrSchedulerEvent, EVENT_SEND_ALARM_REPORT, addrserverkey)


      self.verifyDBLastemailTable( inDictEmailSettings['emailAddrRecs'] )
      self.siteInfo = self.directory.getSystemObject().getSiteInfo()



  def verifyDBLastemailTable(self, emailAddrRecs):
    # Verity there are records that match the 6 email addresses.
    conn = dbUtils.getAlarmDatabaseConnection()
    conn.row_factory = dbUtils.dictFactory  # function to translate SQL results to dict
    cur = conn.cursor()
    cur.execute('select * from lastemail')
    alarmLastemailRecords = cur.fetchall()
    # Make sure the lastemail table has ALL current email addresses.
    # Loop email addresses
    for emailAddr in emailAddrRecs:
      # Loop lastemail table
      if len( emailAddr['toaddress'] ) > 0 :
        blEmailAddressFound = 0
        for lastemailRec in alarmLastemailRecords :
          if lastemailRec['emailaddress'] == emailAddr['toaddress'] :
            blEmailAddressFound = 1
        
        if blEmailAddressFound == 0 :
          # did not find it. Insert the record for it using default values.
          # The default value for the lastAlarmReportSent is when this table is built. It's too difficult to dynamically
          # calculate what should be the previous time/date the alarm report was sent.
          utcNow = utilities.getUTCnowFormatted()
          strSQL = 'INSERT INTO lastemail( lastemail,consecutiveEmailFailures,lastAlarmReportSent,emailaddress) VALUES ' \
                   '("{0}",{1},"{2}","{3}")'.format(utcNow, 0, utcNow, emailAddr['toaddress'])
          cur.execute( strSQL )

    conn.commit()
    conn.close()

    
  # this function will get called based upon events scheduled through the alarmMgrScheduler.
  def alarmMgrSchedulerEvent(self, eventNum, addrserverkey ):
      if eventNum == EVENT_SEND_ALARM_REPORT :
#        print "RUNNING EVENT_SEND_ALARM_REPORT"
        # print "Hit alarmMgrScheduler eventNum={0}, toaddress={1}".format( eventNum, addrserverkey )
        if addrserverkey in self.dictAlarmEmailStatus :
          dictEmailStatus = self.dictAlarmEmailStatus[addrserverkey]
          dictEmailStatus['emailActionBits'] = dictEmailStatus['emailActionBits'] | SEND_EMAIL_ALARM_REPORT_BIT
          dictEmailStatus['lastAlarmReportTime'] = self._getLastAlarmReportTime(addrserverkey)
          dictEmailStatus['currAlarmReportTime'] = utilities.getUTCnowFormatted() # To ensure accurate 'lastAlarmReportTime'


  def _getLastAlarmReportTime(self, addrserverkey):
    # type: (Union[str, unicode]) -> object
    # read the last date time we sent alarm email.
    conn = dbUtils.getAlarmDatabaseConnection()
    cur = conn.cursor()
    cur.execute('select lastAlarmReportSent from lastemail where emailaddress="{0}"'.format(addrserverkey))
    # lastAlarmReportTime = cur.fetchone()
    lastAlarmReportTime = dbUtils.dictFromRow(cur.fetchone() )
    if lastAlarmReportTime == None:
#      log.debug("No lastAlarmReportSent date exists in database")
      lastAlarmReportTime = utilities.getUTCnowFormatted()
    else:
      lastAlarmReportTime = lastAlarmReportTime['lastAlarmReportSent']
    conn.close()
    return lastAlarmReportTime

  def _updateLastAlarmReportTime(self, newDate, toaddr ):
  
      conn = dbUtils.getAlarmDatabaseConnection()
      try:
        cur = conn.cursor()
        strSQL = 'update lastemail set lastAlarmReportSent="{0}" where emailaddress="{1}"'.format( newDate, toaddr )
        cur.execute( strSQL )
        
      except Exception, e:
        log.debug( "Error in _updateLastalarmReportTime {0}, {1}".format( e, str(e)) )
        
      conn.commit()
      conn.close()


  def _updateLastEmailTime(self, newDate, toaddr ):
      conn = dbUtils.getAlarmDatabaseConnection()
      cur = conn.cursor()
      strSQL = 'update lastemail set lastemail="{0}" where emailaddress="{1}"'.format( newDate, toaddr )
      cur.execute( strSQL )
      conn.commit()
      conn.close()

  def _getLastEmailDate(self, toaddr):
      # read the last date time we sent alarm email.
      conn = dbUtils.getAlarmDatabaseConnection()
      cur = conn.cursor()
      cur.execute( 'select lastemail from lastemail where emailaddress="{0}"'.format( toaddr ) )
      lastEmailDataRecord = cur.fetchone()
      
      if lastEmailDataRecord is None:
#          log.debug("No lastemail date exists in alarm database")
          lastEmailDate = utilities.getUTCnowFormatted()
      else:
          lastEmailDate = lastEmailDataRecord["lastemail"]
      conn.close()
      return lastEmailDate

  def getEmailSettingsForAddrServer( self, toaddress, servername ) :
    
      emailSettings = {}  # emailSettings is a singleton of toaddress, fromaddress,smtpserver,smtpport,enabletls, etc.
      # Find matching email address record
      
      for emailRec in self.dictEmailSettings['emailAddrRecs']:
        if toaddress == emailRec['toaddress'] :
          # Now match the servername.
          for serverRec in self.dictEmailSettings['emailServerRecs']:
            if servername == serverRec['emailservername'] :
              blFound = True
              emailSettings['toaddress'] = toaddress
              emailSettings['servername'] = servername
              emailSettings['fromaddress'] = serverRec['fromaddress']
              emailSettings['smtpserver'] = serverRec['smtpserver']
              emailSettings['smtpport'] = serverRec['smtpport']
              emailSettings['enabletls'] = serverRec['enabletls']
              emailSettings['enableauthentication'] = serverRec['enableauthentication']
              emailSettings['authaccount'] = serverRec['authaccount']
              emailSettings['authpassword'] = serverRec['authpassword']
              # The following are configured once for all address records.
              emailSettings['alarmReportsPerDay'] = self.dictEmailSettings['alarmReportsPerDay']
              emailSettings['alarmemaildelay'] = 0
              break
      # print "getEmailSettings RETURNING = ", emailSettings
      return emailSettings

  def _emailAlarmThread(self):

#    try:

      # log.debug("_emailAlarmThread")

      # Let's first figure out what needs to be sent based upon the emailTransactions.
      currentEmailDate = copy.deepcopy(self.currentEmailDate)
      siteInfo = copy.deepcopy(self.siteInfo)

      # We need to get all the information (active emailTransactions, associate emailBody AND enunciated alarms dict)
      emailInfoDict = copy.deepcopy( self._getActiveEmailInfo() )

      # We will loop through the email transactions to create the formatted emailBody for the required EBrecId
      emailFormatted = {}
      emailAlarmsList = []
      blSendSuccess = None # Need to set based upon whether sent or not.

      for emailTrans in emailInfoDict['etDict'] :
        
        # If the transaction is a retry, we need to make sure the current time is equal to or greater than
        # the time of the transaction. (This is the emailretrudelay handling)
        blSendNow = True
        if emailTrans['transcmd'] == systemConstants.TRANS_SEND_TRY2 or emailTrans['transcmd'] == systemConstants.TRANS_SEND_TRY3:
          # Convert date to datetime type
          # emailTransDate = emailTrans['date'], '%Y-%m-%d %H:%M:%S')
          # if the time to retry is in the future, don't send now.
          if emailTrans['date'] > datetime.datetime.utcnow() :
            blSendNow = False
            
        if blSendNow is True:
          toaddress = emailTrans['toaddress']
          servername = emailTrans['servername']
          addrserverkey = self.getAddrServerKey( toaddress, servername )
          
          # Protect in the case an email address is different than what is queued. If so, just terminate the request
          # by setting the EBrecId to -1.
          if addrserverkey in self.dictAlarmEmailStatus :
            # all good.
            dictEmailStatus = self.dictAlarmEmailStatus[ addrserverkey ]
            EBrecId = emailTrans['EBrecId']
          else :
            # address in email request does not match current configuration. terminate the transaction request.
            dictEmailStatus = None
            EBrecId = -1

          # Let's start creating the email send transactions.
          # If we have a valid EBrecId OR we are sending a test message (where there is no email body
          if EBrecId > 0 or emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
            blEBrecIdOK = True
          else:
            # If we get here because the EBrecId is -1, we need to "terminate" this email transaction request - since
            # it was incorrectly "completed". So simply put the transction to TERMINATE.
            blEBrecIdOK = False
            self.updateEmailTransactionRecord(emailTrans['recId'], systemConstants.TRANS_TERMINATE,
                    systemConstants.SEND_FAIL, "Internal Error", "Could Not Find Email Body")

          # There are times that the email subject and body will be used for another transaction.
          # So if we have not yet formated the email subject and body, do it and store it in case it is needed again.
          if blEBrecIdOK is True and EBrecId not in emailFormatted :
            
            # we need to format the email body.
            if emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_ALARM :
              # We need to format a standard email alarm.
              # We need to get the alarmRecs
              # log.debug( "EBrecID:{0}, emailInfoDict{1}".format( EBrecId, emailInfoDict ) )
              emailInfo = json.loads( emailInfoDict['ebDict'][EBrecId]['jsonEmailInfo'] )
              emailAlarmsList = emailInfo['alarmRecs']
            elif emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
              # We need to format a standard email alarm.
              emailInfo = {}
            elif emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT:
              emailInfo = json.loads(emailInfoDict['ebDict'][EBrecId]['jsonEmailInfo'])
              emailAlarmsList = emailInfo['alarmReportInfo']
            elif emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:
              # print "Send Alarm Report"
              emailInfo = json.loads( emailInfoDict['ebDict'][EBrecId]['jsonEmailInfo'] )
              emailAlarmsList = emailInfo['alarmReportInfo']

          if blEBrecIdOK:
            emailSubject = alarmEmailer.formatEmailSubject( emailAlarmsList, siteInfo, emailTrans['emailtype'] )
            
            emailFormatted[EBrecId] = {}
            emailFormatted[EBrecId]['emailSubject'] = emailSubject
            emailBody = alarmEmailer.formatEmailBody(  emailSubject, emailAlarmsList, siteInfo, emailTrans['emailtype'] )
            emailFormatted[EBrecId]['emailBody'] = emailBody
            # We need to parse off the site name and get to the email subject line (without the site name)
            emailSubjectTextLoc = len( siteInfo["name"] ) + 3
            emailFormatted[EBrecId]['strSubjectLine'] = emailSubject[emailSubjectTextLoc:]

            emailSettings = dictEmailStatus['emailSettings']
            strDebug = "Initiated Send - {} to {}".format(emailFormatted[EBrecId]['emailSubject'], dictEmailStatus['emailSettings']["toaddress"] )
            log.debug( strDebug )
            result = alarmEmailer.sendEmail( dictEmailStatus['emailSettings'], emailFormatted[EBrecId]['emailSubject'],
                                             emailFormatted[EBrecId]['emailBody'] )
    
            if emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
              doNothingSpecial = True
    
            elif emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT:
              if result['blSendSuccess'] is True:
                if 'currAlarmReportTime' not in dictEmailStatus:
                  dictEmailStatus['currAlarmReportTime'] = utilities.getUTCnowFormatted()
                self._updateLastAlarmReportTime(dictEmailStatus['currAlarmReportTime'], dictEmailStatus['toaddr'])
    
            elif emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:
              if result['blSendSuccess'] is True:
                if 'currAlarmReportTime' not in dictEmailStatus:
                  dictEmailStatus['currAlarmReportTime'] = utilities.getUTCnowFormatted()
                # IF this is a test alarm report email, we DO NOT UPDATE THE LAST SENT TIME
  
            if result['blSendSuccess'] is True:
              self.updateEmailTransactionRecord( emailTrans['recId'], systemConstants.TRANS_DONE,
                   systemConstants.SEND_SUCCESS, emailFormatted[EBrecId]['strSubjectLine'], result['strEmailStatus'] )
            else:
              # We had an email failure
              nextCmd = -1
              statusCode = -1
              statuscodeNewTransaction = -1

              statusCodeNewTransaction = systemConstants.QUEUE_TRY3 # Default to make lint happy
              # We do not retry Test Alarm transactions.
              if emailTrans['emailtype'] != systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
    
                if emailTrans['transcmd'] == systemConstants.TRANS_SEND_TRY1:
                  nextCmd = systemConstants.TRANS_SEND_TRY2
                  statusCode = systemConstants.SEND_TRY1_FAIL
                  statusCodeNewTransaction = systemConstants.QUEUE_TRY2
      
                elif emailTrans['transcmd'] == systemConstants.TRANS_SEND_TRY2:
                  nextCmd = systemConstants.TRANS_SEND_TRY3
                  statusCode = systemConstants.SEND_TRY2_FAIL
                  statusCodeNewTransaction = systemConstants.QUEUE_TRY3
  
                elif emailTrans['transcmd'] == systemConstants.TRANS_SEND_TRY3:
                  nextCmd = systemConstants.TRANS_DONE
                  statusCode = systemConstants.SEND_FAIL
  
              else:
                # for test alarm, no retries.
                nextCmd = systemConstants.TRANS_DONE
                statusCode = systemConstants.SEND_FAIL
    
              # print 'NEXT STATE:{0}, STATUS CODE:{1}'.format( nextCmd, statusCode  )
              # Failure, IF we need some type of retry, add a new record with the proper new transaction action command
              if nextCmd >= systemConstants.TRANS_SEND_START_ACTIVE_CMDS and \
                  nextCmd <= systemConstants.TRANS_SEND_END_ACTIVE_CMDS:
                
                # We have failed email. When we add the transaction, we need to "forward" date it for when we want to retry.
                # We will allow the user to set the delay between email messages (in miutes). The way this will work is that
                # we will add the "new" retry email transaction with a timestamp that is in the future by the time of the delay
                # specified to the current time.
                if nextCmd == systemConstants.TRANS_SEND_TRY2 or nextCmd == systemConstants.TRANS_SEND_TRY3 :
                  dtRetryTimeUTC = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.dictEmailSettings['emailretrydelay'])
                  utcDate = dtRetryTimeUTC.strftime('%Y-%m-%d %H:%M:%S')
                else:
                  utcDate = utilities.getUTCnowFormatted()
                # Create the NEW email transaction record for the retry.
                self.addEmailTransactionRecord(utcDate, nextCmd, statusCodeNewTransaction, emailTrans['emailtype'],
                                               EBrecId, dictEmailStatus['toaddr'], dictEmailStatus['servername'],
                                               emailFormatted[EBrecId]['strSubjectLine'] )
            
              # update the current email transation status and action code.
              self.updateEmailTransactionRecord(emailTrans['recId'], systemConstants.TRANS_SEND_FAIL, statusCode,
                                          emailFormatted[EBrecId]['strSubjectLine'], result['strEmailStatus'])
    
          # Let's determine if we sent a test email in this pass.
          if emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM or \
             emailTrans['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT :
            blTestSendEmail = True
          else:
            blTestSendEmail = False
            
          # If the send test email is active and we sent a test email, start the timer for displaying it.
          if self.dictSendTestEmail['blActive'] and blTestSendEmail is True :
            self.strTestEmailMsg = result['strEmailStatus']
            self.strTestEmailMsgTimer.setTimeout(20)  # Show the status message for a little bit
            self.strTestEmailMsgTimer.reset()
            self.dictSendTestEmail['blActive'] = 0

#    except Exception, e:
#      log.debug( "Exception - {}, {}".format( e, str(e) ) )
      
    
  def _processAlarmsEmailing(self):
      ################################################
      # ENUNCIATED ALARMS HANDLING
      # First, see if the email alarm option is enabled
      # Second, get the enunciated alarm list.
      # Third, determine if any of the alarms have not been "bundled". One email bundle (body) per detected alarms that have not been sent.
      # Fourth, for each email bundle, create an email transaction for EACH email address.
      # Look at the test email status and create email transactions as required for test emails.
      ################################################

      # Check to see if the user wants alarm emails sent.
      if self.dictEmailSettings['enablealarmemail'] > 0 :

        # Enuciated alarms are typcially a subset of the active alarms. Enuciated alarms are those alarms
        # that need to be seen and sent out after the alarm filter (if active).
        # If there are no enunciated alarm filters, then active and enunciated alarms are the same.
        rawActiveAlarms = self.getLeoActiveAlarms()  # if we have alarms, we may need to do something
        # Check to see if the active alarms pass through the enunciated alarm filter.
        enunciatedAlarms = self.getLeoEnunciatedAlarms(rawActiveAlarms)
        
        # print "Raw:{0}, Filtered:{1}\nRaw:{2}\nActive:{3}".format( len( rawActiveAlarms ), len( enunciatedAlarms ), rawActiveAlarms, enunciatedAlarms )
        # print 'enunciatedAlarms: {0}'.format( enunciatedAlarms )
  
        if len( enunciatedAlarms ) > 0 :
          self.blEnunciatedAlarmsActive =  1
        else:
          self.blEnunciatedAlarmsActive = 0
  
        # First see if any of the enunciated alarms need to be emailed. This is determined
        # by looping through the enunciated alarms and see if there has been an email body record
        # created for each of the enunciated alarms.
        blNewEnunciatedAlarms = 0
        for alarmRec in enunciatedAlarms :
          # if this alarm has not yet been put into an email
          if alarmRec['EBrecId'] < 0 :
            # We need to create a new email bundle/body.
            blNewEnunciatedAlarms = 1
        # print "_processAlarmsEmailing - New Enunciated Alarms?", blNewEnunciatedAlarms
  
        EBalarmReportIdx = -99 # Nothing special, just a negative number.
        EBenunAlarmIdx = -1
        blSendEmail = 0
  
        # Get the current date and time.
        currentEmailDate = utilities.getUTCnowFormatted()

        # If there are new enunciated alarms, create the email body record.
        if blNewEnunciatedAlarms > 0:
          EBenunAlarmIdx = self.addEmailBodyRecord(systemConstants.SEND_EMAIL_SEND_ALARM, enunciatedAlarms)
        else :
          EBenumAlarmIdx = -1

        ##################################################################
        # Create any necessary Email Transactions for the following reasons:
        # 1) Active alarm that has not been sent
        # 2) Test Alarm
        # 3) Alarm Report
        # by looping through the email addresses
        ##################################################################
        dictEmailAddrRecs = self.dictEmailSettings['emailAddrRecs']
        dictEmailServerRecs = self.dictEmailSettings['emailServerRecs']
        # For each email address to be sent to
        for addrRec in dictEmailAddrRecs:

          # Make sure we didn't have an error creating the alarm email body. We have only seen this
          # in a corruption due to an unexpected reset. So instead of continually creating "bad database" records,
          # we will skip the enunciation if we didn't get a valid email body record index - because we won't be able to
          # send anything anyway.
          # dictEmailStatus contains run-time status/infornmation/timers for each email address
          toaddress = addrRec['toaddress']

          # If the toaddress is blank, skip this entry.
          if len(toaddress) > 0:
            servername = addrRec['emailservername']
            addrserverkey = self.getAddrServerKey(toaddress, servername)
            dictEmailStatus = self.dictAlarmEmailStatus[addrserverkey]

            if EBenunAlarmIdx > 0 or self.dictSendTestEmail['blActive'] or dictEmailStatus['emailActionBits'] > 0 :
    
              #############################################
              # Build transaction for enunciated alarms
              #############################################
              # If we need to enunciate alarms AND this address is enabled for emailing alarms, create email transaction
              if blNewEnunciatedAlarms > 0 and addrRec['enableemail'] > 0 :
                self.addEmailTransactionRecord(currentEmailDate, systemConstants.TRANS_SEND_TRY1,
                  systemConstants.SEND_REQUEST, systemConstants.SEND_EMAIL_SEND_ALARM, EBenunAlarmIdx, toaddress, servername )
                blSendEmail = 1
    
              ##################################################################
              # check for triggered alarm report (time to run the alarm report
              ##################################################################
              #  print "CheckAlarmActionBits- Addr:{0}, ActionBits:{1}".format(toaddress, dictEmailStatus['emailActionBits'])
              if dictEmailStatus['emailActionBits'] & SEND_EMAIL_ALARM_REPORT_BIT > 0 :
                dictEmailStatus['lastAlarmReportSent'] = self._getLastAlarmReportTime(toaddress)
                if EBalarmReportIdx < 0:  # if we have not created the email body record yet
                  lastAlarmReportSent = dictEmailStatus['lastAlarmReportSent']
                  EBalarmReportIdx = self.addEmailBodyRecord(systemConstants.SEND_EMAIL_SEND_ALARM_REPORT,
                                                             [], lastAlarmReportSent, currentEmailDate)
                self.addEmailTransactionRecord(currentEmailDate,systemConstants.TRANS_SEND_TRY1,
                  systemConstants.SEND_REQUEST, systemConstants.SEND_EMAIL_SEND_ALARM_REPORT,
                  EBalarmReportIdx, toaddress, servername )
                # Once the entries are added to the database, clear the Alarm Report request bit
                dictEmailStatus['emailActionBits'] = dictEmailStatus['emailActionBits'] & ~SEND_EMAIL_ALARM_REPORT_BIT
                blSendEmail = 1
    
              #############################################
              # Check for test alarms and reports
              #############################################
              if self.dictSendTestEmail['blActive'] > 0:
                if self.dictSendTestEmail['addrserverkey'] == addrserverkey:
                  if self.dictSendTestEmail['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
                    # Create the emailTransaction. No emailBody index needed.
                    self.addEmailTransactionRecord(currentEmailDate, systemConstants.TRANS_SEND_TRY1,
                                                   systemConstants.SEND_REQUEST,
                                                   systemConstants.SEND_EMAIL_SEND_TEST_ALARM, -1, toaddress, servername )
                    blSendEmail = 1
    
                  elif self.dictSendTestEmail['emailtype'] == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:
                    if EBalarmReportIdx <= 0:  # if we have not created the email body record yet
                      dictEmailStatus['lastAlarmReportSent'] = self._getLastAlarmReportTime(toaddress)
                      lastAlarmReportSent = dictEmailStatus['lastAlarmReportSent']
                      EBalarmReportIdx = self.addEmailBodyRecord( systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT,
                                                                  [], lastAlarmReportSent, currentEmailDate)
                    self.addEmailTransactionRecord(currentEmailDate, systemConstants.TRANS_SEND_TRY1,
                               systemConstants.SEND_REQUEST, systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT,
                               EBalarmReportIdx, toaddress, servername )
                    blSendEmail = 1
           
              
          # If we detected new enunciated alarms, we need to place the emailbody record ID
          # into the appropriate devicealarms EBrecId field so that we know we already created an email body for this
          # specific alarm(s)
          if blNewEnunciatedAlarms > 0:
            myEnunciatedAlarms = copy.deepcopy( enunciatedAlarms )
            conn = dbUtils.getAlarmDatabaseConnection()
            try:
              cur = conn.cursor()
              for alarmRec in enunciatedAlarms:
                # if this alarm has not yet been put into an email
                if alarmRec['EBrecId'] < 0:
                  strSQL = 'UPDATE devicealarms set EBrecId={0} where EBRecId=-1 and date="{1}" and name="{2}" and alarm="{3}"'.format( \
                    EBenunAlarmIdx, alarmRec['date'], alarmRec['name'], alarmRec['alarm'])
                  cur.execute( strSQL )
    
            except Exception, e:
              log.debug("Error in SQL: {0}, {1}, SQL:{2}".format(e, str(e), strSQL))
              
            conn.commit()
            conn.close()
  
        numActiveTransactions = 0
        # Let's see if we have any retries to do.
        if blSendEmail == 0 :
          conn = dbUtils.getEmailDatabaseConnection()
          cur = conn.cursor()
          # Let's get all active transactions.
          cur.execute('SELECT COUNT() from emailtransactionsTable WHERE transcmd >={0} AND transcmd <={1}'.format(
            systemConstants.TRANS_SEND_START_ACTIVE_CMDS, systemConstants.TRANS_SEND_END_ACTIVE_CMDS))
          numActiveTransactions = cur.fetchone()[0]
          conn.close()
          
  
        # If we determined that we need to send an email, or retries to send, launch the thread to handle the formatting and emailing.
        if blSendEmail > 0 or numActiveTransactions > 0 :
          self.siteInfo = self.directory.getSystemObject().getSiteInfo()
          with self.lock:
            if self.thread is None or not self.thread.isAlive():
              self.thread = threading.Thread(target=self._emailAlarmThread)
              #self.thread.daemon = True
              self.thread.start()
              # The below lines of code checks if the thread is still alive even after 15 mins 50 secs (950) it shutsdown with a reboot command.
              self.thread.join(1200)
              if self.thread.isAlive():
                try:
                  log.debug("_processAlarmsEmailing thread is hung, Thread 20 mins watchdog reboot")
                  #self.thread._stop()
                except Exception, e:
                  log.debug( "Error in try block of _processAlarmsEmailing, Thread is in hung state and going down for a watchdog reboot of 15 mins 50 secs")
                os.system("reboot")

              # print "Email Thread = {0}".format(self.thread.getName())

  ##############################################################
  #
  # DATABASE OPERATIONS FOR EMAIL DATABASE
  #
  #############################################################
  
  # This function simply opens the email database and executes a SQL command so we don't have to duplicate this
  # code everywhere.
  def emailDBstrSQL(self, strSQL ):

    conn = dbUtils.getEmailDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute(strSQL)

    except Exception, e:
      log.debug("Error in emailDBstrSQL {0}, {1}, {2}".format(e, str(e), strSQL ))

    conn.commit()
    conn.close()

  # This function is required because json.dumps is unable to serialize a datetime.datetime object natively
  # so we need to supply this capability.
  def LEOjsonDumpsExtension(self, o):
    if isinstance(o, datetime.datetime):
      return o.__str__()
#    else:
#      print "LEOjsonDumpExtension UNKNOWN",

  # This function is responsible for creating the emailBody record for either a enunciated alarm email or alarm report email.
  # An emailBody is not reequired for the test alarm - since the text in the alarm is fixed.
  def addEmailBodyRecord(self, emailtype, alarmRecs=[], lastTime="", currentTime=utilities.getUTCnowFormatted()):

      emailInfo = {}
      emailInfo['emailtype'] = emailtype
      
      if emailtype == systemConstants.SEND_EMAIL_SEND_ALARM:
        emailInfo['alarmRecs'] = copy.deepcopy(alarmRecs)

      elif emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
        doNothing = True
 
      elif emailtype == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT or \
           emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT :
        # We need to get the alarm report records.
        emailInfo['alarmReportInfo'] = self.getAlarmReportAlarms(lastTime, currentTime)
  
      # print "emailInfo PRE-SERIAL=", emailInfo
      jsonEmailInfo = json.dumps(emailInfo, default = self.LEOjsonDumpsExtension )
      # print "SERIALIZED jsonEmailInfo=", jsonEmailInfo

      conn = dbUtils.getEmailDatabaseConnection()
      try:
        EBrecIndex = -1
        cur = conn.cursor()
  
        strSQL = "INSERT INTO emailbodyTable (date, jsonEmailInfo) VALUES ( '{0}', '{1}')".format(currentTime, jsonEmailInfo)
        cur.execute(strSQL)
        EBrecIndex = cur.lastrowid
        conn.commit()
        conn.close()
  
      except Exception, e:
        log.debug("Error in addEmailBodyRecord {0}, {1}, jsonEmailInfo:{2}".format(e, str(e), jsonEmailInfo ) )
        EBrecIndex = -2
  
      return EBrecIndex
   
  # This function will create a new emailTransaction record in the emailTransaction database
  def addEmailTransactionRecord(self, date, transcmd, transstatus, emailtype, EBrecId, toaddress, server, strSubjectLine="" ):
  
    if transcmd >= systemConstants.TRANS_SEND_TRY1 and transcmd <= systemConstants.TRANS_SEND_TRY3:
      emailstatus = "Waiting to be sent (retry)."
    else:
      emailstatus = ""
 
    strSQL = 'INSERT INTO emailtransactionsTable (date, transcmd, transstatus, emailtype, EBrecId, toaddress, servername, subjectline, emailstatus) ' \
             'VALUES("{0}",{1},{2},{3},{4},"{5}","{6}","{7}","{8}")'.format( date, transcmd, transstatus, emailtype, EBrecId, toaddress, server, strSubjectLine, emailstatus )
    self.emailDBstrSQL( strSQL )

  # This function will update an emailTransaction record in the emailTransaction database with a new transcmd and
  # transstatus
  def updateEmailTransactionRecord(self, transRecId, transcmd, transstatus, strSubjectLine="", strStatus="" ):
  
    if len(strSubjectLine) + len(strStatus) == 0 :
      strSQL = 'UPDATE emailtransactionsTable SET transcmd={0}, transstatus={1} where recId={2}'.format(
                        transcmd, transstatus, transRecId )
    else:
      strSQL = 'UPDATE emailtransactionsTable SET transcmd={0}, transstatus={1}, subjectline="{2}", emailstatus="{3}"' \
               ' where recId={4}'.format( transcmd, transstatus, strSubjectLine, strStatus, transRecId )
    self.emailDBstrSQL( strSQL )

  # this function will retrevie the active email transactions AND associated email body for
  # the purpose of creating andl formatting the email body. It will also obtain ALL active enunciated alarms.
  def _getActiveEmailInfo(self):
    emailBodyDict = {}  # indexed by EBrecId
    emailRecInfo = {}   # Combined active emailTransactions and emailBody recofds

    conn = dbUtils.getEmailDatabaseConnection()
    conn.row_factory = dbUtils.dictFactory # function to translate to SQL results to dict
    cur = conn.cursor()
    # Let's get all active transactions.
    cur.execute( 'SELECT * FROM emailtransactionsTable WHERE transcmd >={0} AND transcmd <={1}'.format(
         systemConstants.TRANS_SEND_START_ACTIVE_CMDS, systemConstants.TRANS_SEND_END_ACTIVE_CMDS ) )
    activeEmailTransDict = cur.fetchall()
    # print "_getActiveEmailInfo - activeEmailTransDict:", activeEmailTransDict

    # Loop through the records getting the unique emailBody record reference for each emailTransaction
    for ETrec in activeEmailTransDict:
      # if we have not retrieved the emailBody for this emailTransaction, get it.
      EBrecId = ETrec['EBrecId']
      if EBrecId not in emailBodyDict:
        cur.execute('select * from emailbodyTable where recId={0}'.format( EBrecId ) )
        emailBodyRec = cur.fetchone()
        if emailBodyRec is not None:
          emailBodyDict[EBrecId] = emailBodyRec

    emailRecInfo['ebDict'] = emailBodyDict
    emailRecInfo['etDict'] = activeEmailTransDict
    conn.close()

    return emailRecInfo

    # Alarm Database Blue-R
  def setEmailDatabaseToFactorySettings(self) :
      conn = dbUtils.getEmailDatabaseConnection()
      cur = conn.cursor()
      # Clear all the alarm records.
      cur.execute('DELETE FROM emailbodyTable')
      cur.execute('DELETE FROM emailtransactionsTable')
      # Reset the sequence row id.
      cur.execute( "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='emailbodyTable'" )
      cur.execute( "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='emailtransactionsTable'" )
      conn.commit()
      conn.close()
      dbUtils.vacuumDatabase( dbUtils.emailDatabasePath ) # Compress database
      log.info( "Setting Email database to factory settings" )

    # Purging older alarms based upon emailDurationDays setting
  def _emailDatabaseCleanup(self, emailDurationDays):
      conn = dbUtils.getEmailDatabaseConnection()

      cur = conn.cursor()
      deleteDate = datetime.datetime.utcnow() - datetime.timedelta(emailDurationDays)
      log.info('Deleting email transactions older than ' + str(deleteDate))
      # GET EMAIL TRANSACTIONS TO BE DELETED
      cur.execute("DELETE FROM emailtransactionsTable WHERE [date] < ?", (deleteDate,))
      conn.commit()
      # Clean out EMAIL Body information based upon the date
      cur.execute("DELETE FROM emailbodyTable WHERE [date] < ?", (deleteDate,))
      conn.commit()

      dbUtils.vacuumDatabase( dbUtils.emailDatabasePath ) # Compress database
      conn.close()


  ####################################################
  #
  # external methods for alarms
  #
  ####################################################
  
  
  def deleteAlarmsForDevice(self, device):
      log.info('Deleting alarms for device ' + device)
      # no lock needed here as we are writing to the database
      conn = dbUtils.getAlarmDatabaseConnection()
      try:
        cur = conn.cursor()
        cur.execute('delete from devicealarms where name=?', (device,))
        conn.commit()
        strAudit = '{0} Deleted All Device Alarms for device {1}'.format( getSessionUsername( session ), device )
        auditTrail.AuditTrailAddEntry( strAudit )

      except:
        log.exception("Error in deleteAlarmsForDevice")
      finally:
        conn.close()

  def deleteAllAlarms(self):
      log.info('Deleting all LEO alarms')
#     print "Deleting ALL LEO Alarms"
      # no lock needed here as we are writing to the database
      conn = dbUtils.getAlarmDatabaseConnection()
      try:
        cur = conn.cursor()
        cur.execute('delete from devicealarms')
        conn.commit()
        strAudit = '{0} Deleted ALL Leo Alarms'.format( getSessionUsername( session ) )
        auditTrail.AuditTrailAddEntry( strAudit )

      except:
        log.exception("Error in deleteAllAlarms")
      finally:
        conn.close()

      self.directory.getSystemObject().reinitialize()
      return("All System Alarms Deleted")

  ###########################################################################################################################################
  # This method optionally takes in the list of active alarms and returns only the alarms that filtered as enunciated -
  # which means they need to be emailed based upon self._dictLeoAlarmFilters
  ###########################################################################################################################################
  def getLeoEnunciatedAlarms( self, rawActiveAlarms=[] ) :
      # If the user did not get the active alarms before calling, get them here.
      # log.debug("getLeoEnunciatedAlarms")
      enunciatedAlarmList = []
  
      # If a raw active alarm list was not passed in, get the latest active alarms.
      if len(rawActiveAlarms) <= 0 :
        rawActiveAlarms = self.getLeoActiveAlarms()

      # if enunciated alarm filters are disabled or there are no filters, just return the current active list
      if self.iEnunciatedAlarmFilterEnable == 0 or len( self.enunciatedAlarmFilters ) == 0 :
        enunciatedAlarmList = rawActiveAlarms
      elif len( rawActiveAlarms ) > 0 :
        # There are active alarms and enunciated alarm filters. Filter the active alarms for enunciation.
        for alarmEntry in rawActiveAlarms :
          # Network failures are ALWAYS enunciated.
          if alarmEntry['alarm'] == 'LEO Network Failure' :
            enunciatedAlarmList.append( alarmEntry )    # User cannot filter enable or disable Network Failure
          else :
            # Loop through the enunciatted filters - first checking to see if the filter is enabled.
            for enunciatedAlarmFilterRec in self.enunciatedAlarmFilters:
              if enunciatedAlarmFilterRec['enable'] > 0 : # We don't need to check if the filter is not enabled...
                # Is it an E2 initiated alarm?
                if alarmEntry['description'].find( 'E2' ) >= 0 :
                  # Handle filters where the appname is specified.
                  if enunciatedAlarmFilterRec['appName'] != '*' : # Non-wildcard appname is encountered.
                    # Split the deviceName:AppName:AppProp from the alarms source string.
                    appPath = alarmEntry['name'].split( ':' )
                    if len( appPath ) > 1:
                      appName = appPath[1]
                      appNameLen = len( appName )
                      starLoc = enunciatedAlarmFilterRec['appName'].find( '*' )
                      if starLoc < 0 : # No star. We look for specific appName
                        # Need to parse full app path. E2Name:AppName:AppProp
                        filterRecAppName = enunciatedAlarmFilterRec['appName']
                        filterRecAppNameLen = len( enunciatedAlarmFilterRec['appName'] )
                        if filterRecAppName.find( appName ) == 0 and appNameLen == filterRecAppNameLen :
                          enunciatedAlarmList.append( alarmEntry )
                      elif starLoc >= 0: # We have a star somewhere in the filter app name.
                        filterRecAppName = enunciatedAlarmFilterRec['appName']
                        filterRecAppName = filterRecAppName[0:filterRecAppName.find('*')-1] # Remove from the star to the end of the appName
                        # See if we can find the shortened filter appName in app name
                        # If we find the name, add the alarm to the enunciate list.
                        if appName.find( filterRecAppName ) == 0 :
                          enunciatedAlarmList.append( alarmEntry )
                    else:
                      enunciatedAlarmList.append(alarmEntry) # IF not E2:app:prop alarm, can't filter.

                  # Just check the alarm text (assuming all other fields are '*')
                  elif enunciatedAlarmFilterRec['alarm'] == alarmEntry['alarm']:
                      enunciatedAlarmList.append(alarmEntry)

                else :
                  # Not E2. First we will handle the "HARD CODED" alarms (non-filterable alarm type) - will always be enunciated.
                  if enunciatedAlarmFilterRec['alarm'] == alarmEntry['alarm']  or ( alarmEntry['alarm'].find( enunciatedAlarmFilterRec['alarm'] ) >= 0):
                      enunciatedAlarmList.append( alarmEntry )

      return enunciatedAlarmList

  def getLeoActiveAlarms(self):
      dictAlarmList = dbUtils.getAlarmEntries( dbUtils.GETLEOACTIVEALARMS )
      
      retval = []
      for alarmEntry in dictAlarmList:
        device = self.directory.getDeviceObject(alarmEntry['name'])
        if device is not None:
          valueDescriptions = device.getValueDescriptions()
          if alarmEntry['alarm'] in valueDescriptions:
            valueDescription = valueDescriptions[alarmEntry['alarm']]
            if 'displayName' in valueDescription:
              alarmEntry['displayName'] = valueDescription['displayName']
          else:  # The device is not found. make the alarm the displayName
              alarmEntry['displayName'] = alarmEntry['alarm']
        else: # The device is not found. make the alarm the displayName
          alarmEntry['displayName'] = alarmEntry['alarm']
        retval.append(alarmEntry)
      #log.debug(retval)
      return retval


  def getLeoAlarmLatestHistoryAlarm(self):
    dictLatestHistoryAlarmEntry = dbUtils.getAlarmEntries(dbUtils.GETLEOHISTORYLATESTALARMENTRY)
    return dictLatestHistoryAlarmEntry
    

  def getLeoAlarmHistory(self):
      # We have added a caching method so this only does a database query on an interval - instead of everytime called; since it is called many times.
      # print "LeoHAlarm DBGet {0} ".format(datetime.datetime.utcnow() )
      dictAlarmList = dbUtils.getAlarmEntries( dbUtils.GETLEOHISTORYALARMS )
      # print "LeoHAlarm DBEnd {0} ".format(datetime.datetime.utcnow() )

      retval = []
      # print "LeoHAlarm Loop START {0} - Num Recs:{1}".format(datetime.datetime.utcnow(), len(dictAlarmList) )
      for alarmEntry in dictAlarmList:
        device = self.directory.getDeviceObject(alarmEntry['name'])
        if device is not None:
          valueDescriptions = device.getValueDescriptions()
          if alarmEntry['alarm'] in valueDescriptions:
            valueDescription = valueDescriptions[alarmEntry['alarm']]
            if 'displayName' in valueDescription:
              alarmEntry['displayName'] = valueDescription['displayName']
              retval.append(alarmEntry)
            else:  # The device is not found. make the alarm the displayName
              alarmEntry['displayName'] = alarmEntry['alarm']
        else:  # The device is not found. make the alarm the displayName
          alarmEntry['displayName'] = alarmEntry['alarm']
        retval.append(alarmEntry)
      # print "LeoHAlarm Loop END {0} ".format(datetime.datetime.utcnow() )
      
      return retval

  def getAlarmStatus(self):

      retval = {}

      dictActiveAlarmList = self.getLeoActiveAlarms()
      if len( dictActiveAlarmList ) > 0 :
        retval['activeAlarms'] = True
      else :
        retval['activeAlarms'] = False

      enunciatedAlarms = self.getLeoEnunciatedAlarms( dictActiveAlarmList )
      if len( enunciatedAlarms ) > 0 :
        retval['enunciatedAlarms'] = True
      else :
        retval['enunciatedAlarms'] = False

      return retval

  # We need to get a data structure full of information to send for the alarm report.
  def getAlarmReportAlarms( self, lastTime, currentTime ) :

      # The alarm report has two parts. 1) Counting of the number of alarm events since the last Alarm Report and 2) A list/count of ALL active alarms AT THE TIME OF THE REPORT
      # (e.g. not only alarms that have become active since the last report). In order to achieve this, we do a special query and then just tally.
      dictParams = { 'lastTime': lastTime, 'currentTime': currentTime }
      dictAlarmList = dbUtils.getAlarmEntries(dbUtils.GETTIMERANGEALARMSANDALLACTIVE, dictParams )
      # log.debug( "getlAlarmReportalarms lastTime:{0}, currTime:{1},dictAlarmList:{2}".format( lastTime, currentTime, dictAlarmList ) )

      # Let's tally the number of occurances
      dictAlmInfo = {} # Will store dictAlmInfo['name']['alarm'] = number of times occurred
      totalAlarmEvents = 0
      totalActiveAlarms = 0
      for rec in dictAlarmList :
        almName = rec['name']
        alm = rec['alarm']
        if almName not in dictAlmInfo: # If we haven't saved this app and alarm
          dictAlmInfo[almName] = {}
        if alm not in dictAlmInfo[almName]:
          dictAlmInfo[almName][alm] = {'count': 1, 'active' : False } # Default to false.
        else:
          dictAlmInfo[almName][alm]['count'] = dictAlmInfo[almName][alm]['count'] + 1

        # Denote and count the active alarms
        if rec['action'] == "NEW":
          dictAlmInfo[almName][alm]['active'] = True
          # Subtract the current time from the time of the alarm.
          alarmGeneratedDate = datetime.datetime.strptime( rec['date'], '%Y-%m-%d %H:%M:%S')
          currentTimeDate = datetime.datetime.strptime( currentTime, '%Y-%m-%d %H:%M:%S')
          # Calculate duration - datetime to str does this nicely - e.g. 2 days, 12:30:00
          dictAlmInfo[almName][alm]['activeDuration'] = str(currentTimeDate - alarmGeneratedDate)
          totalActiveAlarms = totalActiveAlarms + 1
        else:
          dictAlmInfo[almName][alm]['activeDuration'] = ""

        totalAlarmEvents = totalAlarmEvents + 1

      # Turn the dict into a list of sets so we can sort it based upon occurrences.
      alarmSummaryList = []
      for dictAlmName in dictAlmInfo:
          for dictAlm in dictAlmInfo[dictAlmName]:
              alarmSummaryList.append( (dictAlmName, dictAlm, dictAlmInfo[dictAlmName][dictAlm]['count'],
                  dictAlmInfo[dictAlmName][dictAlm]['active'],dictAlmInfo[dictAlmName][dictAlm]['activeDuration'] )  )
      # Now sort them in reverse order - from most to least occurances.
      sortedAlarmSummaryList = sorted(alarmSummaryList, key=lambda myKey: myKey[2], reverse=True)

      # Debug Report Information:
      # print "Total # of Alarm Events =", totalAlarmEvents
      # print "Total # of Active Alarms = ", totalActiveAlarms
      # print "Alarm Summary"
      # print "-------------"
      # for listEntry in sortedAlarmSummaryList:
      #     print "Entry:", listEntry[0], listEntry[1], "Occurances:", listEntry[2], "Active:",listEntry[3], "Active Duration:", listEntry[4]

      self.alarmReportInfo = { 'totalAlarmEvents' : totalAlarmEvents, 'totalActiveAlarms' : totalActiveAlarms,
          'alarmSummaryList' : sortedAlarmSummaryList, 'lastReportTime' : lastTime, 'currentReportTime' : currentTime }
      # print "RETURN - self.alarmReportInfo",self.alarmReportInfo

      return self.alarmReportInfo

  def getEmailHistoryEntries(self, transType, ETrecId=-1, EBrecId=-1 ):
      # Get email transaction records.
      retval = []
      ETrecDict = {}
      EBrecDict = {}
      conn = dbUtils.getSystemDatabaseConnection()
      cur = conn.cursor()
      strSQL = "SELECT toaddress from emailaddresses"
      cur.execute( strSQL )
      cloudEmailAddress = cur.fetchall()
      i =0
      for emailTransaction in cloudEmailAddress:
        if (i > 5):
          recordVal = emailTransaction[0]
          #log.debug(recordVal)
        i=i+1
      conn.close()
      conn = dbUtils.getEmailDatabaseConnection()
      cur = conn.cursor()

      # Get all EmailTransaction Records
      if transType == "allEmailTrans" :
        # Let's get all active transactions.
        #log.debug(recordVal)
        strSQL = ('SELECT date, recId, transcmd, transstatus, emailtype, toaddress, subjectline, emailstatus, EBrecId ' \
                 'FROM emailtransactionsTable where toaddress!="{0}" ORDER BY date DESC LIMIT 1000').format(recordVal)
        cur.execute( strSQL )
        for emailTransaction in cur.fetchall():
          dict = dbUtils.dictFromRow(emailTransaction)
          retval.append(dict)

      # Get a specific Email Transaction record
      if transType == "emailTransRec" or transType == "emailTransAndBodyRec" or transType == "emailTransAndBodyRecHTML" :
        cur.execute('select * from emailtransactionsTable where recId={0}'.format(ETrecId))
        ETrec = cur.fetchone()
        ETrecDict = dbUtils.dictFromRow(ETrec)
        # We will set the EBrecId based upon the id found in the email transaction record ONLY if it is not passed in.
        # If the emailtype is 2 (test alarm) there is no email body to get.
        if EBrecId < 0 and ETrecDict['emailtype'] != systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
          EBrecId = ETrecDict['EBrecId']
        retval = { 'ETrecDict' : ETrecDict }

      # Get a specific Email Body record
      if transType == "emailBodyRec" or transType == "emailTransAndBodyRec" or transType == "emailTransAndBodyRecHTML":
        EBrecDict = {}
        if EBrecId > 0 :
          cur.execute('select * from emailbodyTable where recId={0}'.format(EBrecId))
          EBrec = cur.fetchone()
          EBrecDict = dbUtils.dictFromRow(EBrec)
          # We have to deserialize the jsonEmailInfo
          jsonEmailInfo = json.loads(EBrecDict['jsonEmailInfo'])
          # Overwrite jsonEmailInfo in the dict with the de-serialized version.
          EBrecDict['jsonEmailInfo'] = jsonEmailInfo
          retval = { 'EBrecDict' : EBrecDict }

      conn.close()
      
      # Get a specific transaction and the associated body records
      alarmRecsList = []
      ebRecError = False
      if transType == "emailTransAndBodyRec" :
        retval = { 'ETrecDict' : ETrecDict, 'EBrecDict' : EBrecDict, 'emailBody' : ""}
      elif transType == "emailTransAndBodyRecHTML" :
        emailtype = ETrecDict['emailtype']
        if emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
          retval = {'ETrecDict': ETrecDict, 'EBrecDict': EBrecDict, 'emailBody' : ""}
        elif emailtype == systemConstants.SEND_EMAIL_SEND_ALARM or \
             emailtype == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT or \
             emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT :
          if emailtype == systemConstants.SEND_EMAIL_SEND_ALARM :
            if len( EBrecDict ) > 0 :
              alarmRecsList = EBrecDict['jsonEmailInfo']['alarmRecs']
            else:
              ebRecError = True
          elif emailtype == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT or \
               emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:
            if len( EBrecDict ) > 0 :
              alarmRecsList = EBrecDict['jsonEmailInfo']['alarmReportInfo']
            else:
              ebRecError = True
          
          if ebRecError is False:
            subjectLine = alarmEmailer.formatEmailSubject(alarmRecsList, self.siteInfo, emailtype)
            emailBody = alarmEmailer.formatEmailBody(subjectLine, alarmRecsList, self.siteInfo, emailtype)
            # This simply removes all the "escaped" strings - so the HTML will render properly.
            emailBody = emailBody.encode('ascii', 'xmlcharrefreplace')
            retval = { "subjectLine" : subjectLine, 'ETrecDict' : ETrecDict, "emailBody" : emailBody }
          else:
            retval = { "subjectLine" : "Error in Record (ebRecError)", 'ETrecDict' : "", "emailBody" : "" }

      return retval

  def snoozeAlarm(self) :
      # Simply reset the snooze alarm timer.
      self.alarmChimeSnoozeTimeout.reset() # Simply reset the timer.
      # print "Snooze Pressed. Timeout=", self.alarmChimeSnoozeTimeout.timeout
      return self.alarmChimeSnoozeTimeout.timeout

  def getAlarmChimeSnoozeTimeRemaining(self) :
      retVal = self.alarmChimeSnoozeTimeout.getTimeRemainingSecs()
      # print "Alarm Chime Snooze Time Remaining --->", retVal
      return retVal

  def getAlarmChimeSnoozeEnable(self) :
      return self.systemSettings["alarmChimeSnoozeEnable"]

  def getTestEmailMsg(self) :
      return self.strTestEmailMsg

  def getAddrServerKey(self, toaddress, servername):
    return '{0}-{1}'.format(toaddress, servername)

  def setTestEmailInfo(self, emailtype, toaddress, servername ):
      # If a set test email is in progress, return this.
      # The 'strTestEmailError' is really for internal debugging. Not shown to user.
      if len( self.strTestEmailMsg ) > 0 :
        self.strTestEmailError = "Send test email is already in progress...Please standby for the results."
        self.strTestEmailMsg = self.strTestEmailError
      else :
        # We simply will set the alarmManager property to indicate to send a test email.
        addrserverkey = self.getAddrServerKey( toaddress, servername )
        if len( addrserverkey ) > 0 : # information is correct.
          # if there is NOTHING in progress, start it.
          if self.dictSendTestEmail['blActive'] ==  0 :
            self.dictSendTestEmail['addrserverkey'] = addrserverkey
            self.dictSendTestEmail['emailtype'] = emailtype
            self.strTestEmailMsg = "Send Test Email In Progress to {0}...Please standby for the results.".format( toaddress )
            self.dictSendTestEmail['blActive'] = 1
          else :
            self.strTestEmailError = "Send Test Email Already In Progress. Request Ignored."
        else :
          self.strTestEmailError = "ERROR. No toaddress found"
      if len( self.strTestEmailError ) > 0 :  log.debug(self.strTestEmailError)

  ###########################################
  #
  # enunciated alarm filter methods
  #
  ###########################################

  # This module reads the enunciated alarm filter settings from the database into the enunciatedAlarmFilters memory
  def _loadEnunciatedAlarmFilters( self ) :
      self.enunciatedAlarmFilters = {}
      # First see if the enunciated alarm filter is active. If not, no need to get enunciated alarm filters.
      conn = dbUtils.getSystemDatabaseConnection()
      conn.row_factory = dbUtils.dictFactory # function to translate SQL results to dict
      cur = conn.cursor()
      cur.execute( 'SELECT * from DBInfo' )
      dbInfoDict = cur.fetchall()[0]
      # If the database says to "re-init" the enunciated alarm filters in the database (from the CSV file)
      # then perform the factory reset AND make sure we reset the database factoryInitNeeded flag.
      if dbInfoDict['factoryInitNeeded'] > 0 :
        self._initEnunciatedAlarmFiltersToFactorySettings()
        cur.execute( 'UPDATE DBInfo SET factoryInitNeeded=0' )
        conn.commit()

      cur.execute("select enunciatedAlarmFiltersActive from miscsettings")
      # Returns in dict. Just need value.
      self.iEnunciatedAlarmFilterEnable = cur.fetchone()['enunciatedAlarmFiltersActive']
#      print "self.iEnunciatedAlarmFilterEnable:", self.iEnunciatedAlarmFilterEnable

      conn.row_factory = dbUtils.dictFactory # function to translate SQL results to dict
      cur = conn.cursor()
      cur.execute("select * from enunciatedAlmFilters")
      self.enunciatedAlarmFilters = cur.fetchall()
      conn.close()

      # Based upon information read from the database, rebuild the consolidated view.
      uTypes = {}
      for uRec in self.enunciatedAlarmFilters:
        # First, group by group type (which is E2 or LAE, etc)
        groupType = uRec['groupType']
        if not groupType in uTypes:
          uTypes[groupType] = {}

        if not 'alarmTypes' in uTypes[groupType]:
          uTypes[groupType]['alarmTypes'] = {}

        alarmType = uRec['alarmType']
        if not alarmType in uTypes[groupType]['alarmTypes']:
          uTypes[groupType]['alarmTypes'][alarmType] = {}
          alarmTypeRec = uTypes[groupType]['alarmTypes'][alarmType]
          alarmTypeRec['alarms'] = []
        else:
          alarmTypeRec = uTypes[groupType]['alarmTypes'][alarmType]

        alarmRec = {}
        if uRec['enable'] > 0:
          alarmRec['enable'] = True
        else :
          alarmRec['enable'] = False
        alarmRec['alarm'] = uRec['alarm']
        alarmRec['appName'] = uRec['appName']
        alarmTypeRec['alarms'].append( alarmRec )

      self.enunciatedAlarmFiltersCondensed = uTypes


  def getEnunciatedAlarmFilters( self ) :
      # We will provide the "detailed" enunciatedAlarmFilters as well as the "consolidated" values.
      retDict = {}

      retDict['alarmTypes'] = self.enunciatedAlarmFiltersCondensed    # Provide "consolidated view" - grouped by alarmType
      retDict['enunciatedAlarmFilters'] = self.enunciatedAlarmFilters # Provide "basic" enunciated alarm records
      retDict['enunciatedAlarmFiltersActive'] = self.iEnunciatedAlarmFilterEnable
      return retDict

  def setEnunciatedAlarmFilters( self, enunciatedAlarmFilters, iEnunciatedAlarmFilterEnable, reInit=0 ) :
      # The save will update the "self." settings for enunciatedAlarmFilters, iEnunciatedAlarmFilterEnable by reloading.
      if reInit > 0 :
        self._initEnunciatedAlarmFiltersToFactorySettings()
      else :
        self._saveEnunciatedAlarmFilters( enunciatedAlarmFilters, iEnunciatedAlarmFilterEnable )
      self._loadEnunciatedAlarmFilters()  # Update memory.

  # This module saves the enunciated alarm filter settings to the database.
  def _saveEnunciatedAlarmFilters( self, enunciatedAlarmFilters, ienunciatedAlarmFiltersActive ) :
      conn = dbUtils.getSystemDatabaseConnection()
      cur = conn.cursor()
      # For simplification, every time we write, we erase the database and insert new records.
      try:
        cur.execute( 'delete from enunciatedAlmFilters' )
      except:
        # print("Table enunciatedAlmFilters does not exist. Creating...")
        log.debug("Table enunciatedAlmFilters does not exist. Creating...")

      if len( enunciatedAlarmFilters ) > 0 :
        # Turn the dict keys into database field names.
        colNames = ''.join(str(e)+',' for e in enunciatedAlarmFilters[0].keys() )
        colNames = colNames[:len(colNames)-1] # Remove last/trailing comma

        for alarmFilterRec in enunciatedAlarmFilters :
          values = ''.join("'" + str(e) + "'," for e in alarmFilterRec.values() )
          values = values[:len(values) - 1]  # Remove last/trailing comma
          cur.execute( 'INSERT INTO enunciatedAlmFilters ({0}) VALUES ({1})'.format(colNames,values) )

      # Update enunciatedAlarmFiltersActive active setting
      cur.execute( 'UPDATE miscsettings SET enunciatedAlarmFiltersActive={0}'.format( ienunciatedAlarmFiltersActive ) )
      conn.commit()
      conn.close()

  # This method is responsible for reading the default enunciated alarm filter settings found in the
  # enunciatedAlarmFilters.csv file
  def _initEnunciatedAlarmFiltersToFactorySettings(self) :

      # print "_initEnunciatedAlarmFiltersToFactorySettings called"
      PARSING_STATE_UNKNOWN = 0
      PARSING_LINES = 1

      # Parse Alarm Filter Settings
      # This module contains all the information to dynamically create a dictionary used for filtering E2 alarms for emailing.
      # Open the file and read the columns
      # For the current implementation, the entries listed are the only types of alarms that will be sent.
      # A Wildcard character can be used for any of the fields.
      # Sample Lines...
      #   See the .csv file for definition and comments about the file format.

      # print "Working Dir = ", os.getcwd()
      strFilename = "{0}/system/enunciatedAlarmFilters.csv".format( sys.path[0] )

      parseState = PARSING_STATE_UNKNOWN
      self.enunciatedAlarmFilters = []

      iLineCount = 0

      with open(strFilename, 'rb') as csvfile:
        fileLines = csv.reader(csvfile, delimiter=',')

        # process the lines...
        for strInLine in fileLines:
          iLineCount = iLineCount + 1
          params = strInLine # strInLine is already "split" based upon commas...

          if len(params) > 0 and params[0][0] != '#':  # blank line or comment line...
            if parseState == PARSING_STATE_UNKNOWN:
              if params[0] == 'Group Type' :
                parseState = PARSING_LINES

            elif parseState == PARSING_LINES:
              if len(params[0]) > 0 :
                dictAlarmFilter = {}
                dictAlarmFilter['enable'] = 0
                dictAlarmFilter['groupType'] = params[0]
                dictAlarmFilter['alarmType'] = params[1]
                dictAlarmFilter['alarm'] = params[2]
                dictAlarmFilter['description'] = params[3]
                dictAlarmFilter['deviceType'] = params[4]
                dictAlarmFilter['deviceName'] = params[5]
                dictAlarmFilter['appName'] = params[6]
                dictAlarmFilter['appProp'] = params[7]
                self.enunciatedAlarmFilters.append( dictAlarmFilter )

#        print "Factory: ", self.enunciatedAlarmFilters
      self._saveEnunciatedAlarmFilters(self.enunciatedAlarmFilters, 0)
      
