#! /usr/bin/python

import sqlite3
from collections import OrderedDict
import os
import sys
import logsystem
import csv
import subprocess


NUM_EMAIL_ADDRESSES = 7
NUM_EMAIL_SERVERS   = 2

log = logsystem.getLogger()

if os.name == "nt" : # We are running on PC. Option to point to different database files.
#   dbPath = "C:/Users/tcoyl/Documents/GitHub/leo_ui/monitor/data"
  dbPath = '{0}/data'.format( sys.path[0] )
else :
  dbPath = '{0}/data'.format( sys.path[0] )
systemDatabasePath = dbPath + "/system.db"
logDatabasePath = dbPath + "/logs.db"
alarmDatabasePath = dbPath + "/alarms.db"
deviceDatabasePath = dbPath + "/devices.db"
E2AlarmDatabasePath = dbPath + "/E2.db"
AuditTrailDatabasePath = dbPath + "/audit.db"
authDatabasePath = dbPath + "/auth.db"
emailDatabasePath = dbPath + "/email.db"

# List of databases to backup
systemDatabases = [systemDatabasePath, logDatabasePath, alarmDatabasePath, deviceDatabasePath, E2AlarmDatabasePath, authDatabasePath, emailDatabasePath]

# Function to get data from database in standard Python dict format
# to use this, after the _getConnection call, set conn.row_factory = dictFactory
def dictFactory(cursor, row):
    retDict = {}
    for idx, col in enumerate(cursor.description):
        retDict[col[0]] = row[idx]
    return retDict


def getRawDbConnectionByName(dbName):
    return sqlite3.connect(dbPath + '/' + dbName )


def _getConnection(dbname):
    conn = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn


def getSystemDatabaseConnection():
    return _getConnection(systemDatabasePath)

def getLogDatabaseConnection():
    return _getConnection(logDatabasePath)

def getLogDatabaseConnectionRaw():
    return sqlite3.connect(logDatabasePath)

def getAlarmDatabaseConnection():
    return _getConnection(alarmDatabasePath)

def getE2AlarmDatabaseConnection():
    return _getConnection(E2AlarmDatabasePath)

def getDeviceDatabaseConnection():
    return _getConnection(deviceDatabasePath)

def getAuditTrailDatabaseConnection():
    return _getConnection(AuditTrailDatabasePath)

def getAuthDatabaseConnection():
    return _getConnection(authDatabasePath)

def getEmailDatabaseConnection():
  return _getConnection(emailDatabasePath)


def dictFromRow(row):
    if ( row != None ) :
      return OrderedDict(zip(row.keys(), row))
    else :
      return None


def vacuumDatabase( databasePathAndName ) :
    conn = sqlite3.connect(databasePathAndName, isolation_level=None)
    conn.execute("VACUUM")
    conn.close()


###################################################################################################
#
# ALARM DATABASE CENTRALIZED FUNCTIONS. THIS PROVIDES A WAY TO MAKE SURE THAT ALL ENTITIES
# HANDLE THE QUERYING OF THE ALARM DATABASE CONSISTENCY - whether it is alarm lists, alarm states
# or alarm reports.
###################################################################################################

# getAlarmEntries() - iTypeOfAlarms parameter values
#
GETLEOACTIVEALARMS = 1      # All active alarms (E2 and device - because it takes two queries)
GETLEOHISTORYALARMS = 2     # All historical alarms (E2 and device)
GETDEVICEACTIVEALARMS = 3
GETDEVICEHISTORYALARMS = 4
GETE2ACTIVEALARMS = 5
GETE2HISTORYALARMS = 6
GETE2DEVICEACTIVEALARMS = 7
GETE2DEVICEHISTORYALARMS = 8
GETTIMERANGEALARMS = 9
GETTIMERANGEALARMSANDALLACTIVE = 10
GETLEOHISTORYLATESTALARMENTRY = 11 # Returns a single alarm entry that is the "latest" or "newest" alarm history entry
GETAKSC255DEVICEACTIVEALARMS = 12
GETAKSC255DEVICEHISTORYALARMS = 13
GETSITESUPERVISORDEVICEACTIVEALARMS = 12
GETSITESUPERVISORDEVICEHISTORYALARMS = 13

strTypeOfAlarms = [ "HUH ALARM TYPE???", "LEO ACTIVE", "LEO HISTORY", "DEVICE ACTIVE", "DEVICE HISTORY",
                    "ALL E2 ACTIVE", "ALL E2 HISTORY", "E2 DEVICE ACTIVE", "E2 DEVICE HISTORY", "TIME RANGE", "TIME RANGE AND ALL ACTIVE" ]
#
# This method will provide a way to get any type of alarm entry list of alarms
#
def getAlarmEntries( iTypeOfAlarms, dictParams={} ) :
  retval = []
#   log.info("START getAlarmEntries Type:{0}({1}), Params:{2}".format( iTypeOfAlarms, strTypeOfAlarms[iTypeOfAlarms], dictParams ) )
  try:
    conn = getAlarmDatabaseConnection()
    cur = conn.cursor()

    if iTypeOfAlarms == GETLEOACTIVEALARMS:
      # Get all active alarms
      strSQL = 'select date, name, action, alarm, description, E2advid, EBrecId from devicealarms where action = "NEW" order by date desc limit 1000'
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETLEOHISTORYLATESTALARMENTRY:
      strSQL = 'select max(date), name, action, alarm from devicealarms where action <> "NEW"'
      cur.execute(strSQL)
      dict = dictFromRow(cur.fetchone())
      retval.append(dict)

    elif iTypeOfAlarms == GETLEOHISTORYALARMS:
      # Get ALL history alarms
      cur = conn.cursor()
      strSQL = 'select date, name, action, alarm, description, E2advid from devicealarms where action <> "NEW" order by date desc limit 1000'
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETE2DEVICEACTIVEALARMS:  # Individual E2 Active Alarms
      # Get active alarms for an E2 by E2controllerName
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName FROM devicealarms where E2ControllerName="{0}" and action = "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETE2DEVICEHISTORYALARMS: # Individual E2 NOT Active Alarms
      # Get active alarms for a non-E2 device by name
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName  FROM devicealarms where E2ControllerName="{0}" and action <> "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETSITESUPERVISORDEVICEACTIVEALARMS:  # Individual Site Supervisor Active Alarms
      # Get active alarms for an E2 by E2controllerName
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName FROM devicealarms where E2ControllerName="{0}" and action = "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETSITESUPERVISORDEVICEHISTORYALARMS: # Individual E2 NOT Active Alarms
      # Get active alarms for a non-E2 device by name
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName  FROM devicealarms where E2ControllerName="{0}" and action <> "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETAKSC255DEVICEACTIVEALARMS:  # Individual AKSC255 Active Alarms
      # Get active alarms for an E2 by E2controllerName
      #log.debug(dictParams['deviceName'])
      #dictParams['deviceName'] = (dictParams['deviceName']).replace('\\','\\\\')
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName FROM devicealarms where E2ControllerName like "%{0}%" and action = "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETAKSC255DEVICEHISTORYALARMS: # Individual AKSC255 NOT Active Alarms
      # Get active alarms for a non-E2 device by name
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName  FROM devicealarms where E2ControllerName like "%{0}%" and action <> "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETDEVICEACTIVEALARMS:
      # Get active alarms for an E2 by E2controllerName
      strSQL = 'SELECT date, name, alarm, action, description, E2advid, E2ControllerName FROM devicealarms where name="{0}" and action = "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      #log.debug(strSQL)
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETDEVICEHISTORYALARMS:
      # Get specific device non-E2 historical alarms
      cur = conn.cursor()
      strSQL = 'SELECT DISTINCT date, name, alarm, action, description, E2advid FROM devicealarms group by name, alarm having action <> "NEW" and E2advid < 0 and name="{0}" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETE2ACTIVEALARMS:    # ALL E2 Alarms that are active
      # Get ALL E2 device alarms
      cur = conn.cursor()
      strSQL = 'select date, name, action, alarm, description, E2advid, E2ControllerName  from devicealarms where E2ControllerName <> "" and action == "NEW" order by date desc limit 1000'
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETE2HISTORYALARMS:   # ALL E2 Alarms that are NOT active
      # Get ALL E2 historical alarms
      strSQL = 'select date, name, action, alarm, description, E2advid, E2ControllerName from devicealarms where E2ControllerName <> "" and action <> "NEW" order by date desc limit 1000'.format( dictParams['deviceName'] )
      cur = conn.cursor()
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETTIMERANGEALARMS:
      # Get all alarm entries within a time range - THAT WERE SENT OUT
      # SELECT date, name, alarm, action, description, E2advid, EBRecId FROM devicealarms where date >= datetime("2017-11-03 16:59:00") AND date <=  datetime('2017-11-13 16:00:00') order by date desc limit 1000

      cur = conn.cursor()
      strSQL = "SELECT date, name, alarm, action, description, E2advid FROM devicealarms where date >= datetime('{0}') AND date <=  datetime('{1}') group by name, alarm order by date desc limit 1000".format( dictParams['lastTime'], dictParams['currentTime'])
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    elif iTypeOfAlarms == GETTIMERANGEALARMSANDALLACTIVE:
      # Get all alarm entries within a time range - THAT WERE SENT OUT -- AND all currently active alarms
      cur = conn.cursor()
      strSQL = "SELECT date, name, alarm, action, description, E2advid FROM devicealarms where action == 'NEW' " \
        "UNION ALL SELECT date, name, alarm, action, description, E2advid FROM devicealarms where action != 'NEW' " \
        "and date >= datetime('{}') AND date <=  datetime('{}') order by date desc limit 1000".format(dictParams['lastTime'], dictParams['currentTime'] )
      cur.execute(strSQL)
      for alarm in cur.fetchall():
        dict = dictFromRow(alarm)
        retval.append(dict)

    else:
      log.debug("Unknown Get Alarms Request:{0}".format( iTypeOfAlarms ) )

  except Exception, e:
    strExcept = 'Exception = {0} {1}'.format( e, Exception )
    log.exception( strExcept )
  finally:
    conn.close()
#    log.info("END getAlarmEntries Type:{0}, Params:{1}, ENTRIES={2}".format( iTypeOfAlarms, dictParams, len(retval) ) )

  return retval

def EmailDatabaseCleanup():
  # We will limit the email transaction and email body table to specific number of entries.
  MAX_EMAIL_TRANSACTIONS = 500

  # First, delete the oldest records greater than the max email transactions.
  conn = getEmailDatabaseConnection()
  cur = conn.cursor()
  strSQL = "delete from emailtransactionsTable where date not in ( select date from emailtransactionsTable order by date desc limit {0} )".format( MAX_EMAIL_TRANSACTIONS )
  cur.execute(strSQL)
  conn.commit()

  # Next, based upon the transaction records removed from the transaction table, delete all emailBody entries that no longer
  # are referenced by the emailtransactionsTable
  strSQL = "delete from emailbodyTable where recId not in ( select EBrecId from emailtransactionsTable )"
  cur.execute(strSQL)
  conn.commit()
  conn.close()
  vacuumDatabase(emailDatabasePath)  # Compress database
  log.debug("Database cleanup of email log entries")



def setEmailAddressAndServerTablesToFactoryDefaults( conn, blUpgrade=False ):

  cur = conn.cursor()

  if blUpgrade == False:
    ###########################################################
    # INITIALIZE *** OLD/LEGACY *** EMAIL ADDRESS TABLE TO DEFAULT VALUES. Only use 2 values in this table after database version 4.
    # enablealarmemail and alarmReportsPerDay
    ###########################################################
    # Re-Init legacy email settings
    cur.execute('update emailsettings set alarmemailperday=12, alarmemaildelay=0, fromaddress="", toaddress=""')
    cur.execute('update emailsettings set smtpserver="",smtpport=0,enableauthentication=0,authaccount="",authpassword="",statusReportsperHour=6 ')
    cur.execute('update emailsettings set enabletls=0')
    conn.commit()

  # Read LEGACY or DEFAULT email settings
  strSQL = 'SELECT * from emailsettings'
  cur.execute(strSQL)
  origSettings = dictFromRow(cur.fetchone())

  ####################################################
  # INITIALIZE EMAIL ADDRESS TABLE VALUES
  ####################################################
  # Delete current records.
  cur.execute("delete from emailaddresses")

  iRecNum = 0
  # Create 6 email address records. + 1 for status reports
  while iRecNum < NUM_EMAIL_ADDRESSES:

    # Default Values
    strServerName = "Server 1"
    strToAddress = ""
    iEnableEmail = 0
    iEnableAlarmReport = 0
    if iRecNum == 0:  # Set first record based upon version 3 database settings.
      strToAddress = origSettings['toaddress']
      if len(strToAddress) > 0:
        iEnableEmail = 1
      if origSettings['alarmReportsPerDay'] > 0:
        iEnableAlarmReport = 1

    # We need to create a new record in each table and copy over the existing values.
    if iRecNum == 6:

      strSQL = 'INSERT INTO emailaddresses ( toaddress,emailservername,enableemail,enablealarmreport) VALUES ' \
               '("{0}","{1}",{2},{3})'.format("leocloudalarms@gmail.com", strServerName, 1, 1)
    else: 
      strSQL = 'INSERT INTO emailaddresses ( toaddress,emailservername,enableemail,enablealarmreport) VALUES ' \
               '("{0}","{1}",{2},{3})'.format(strToAddress, strServerName, iEnableEmail, iEnableAlarmReport)

    cur.execute(strSQL)

    iRecNum = iRecNum + 1

  ####################################################
  # INITIALIZE EMAIL SERVER TABLE VALUES
  ####################################################
  # Delete current records.
  cur.execute("delete from emailservers")

  # We need to add the email servers table and record
  iRecNum = 0
  # Create 3 email server records.
  while iRecNum < NUM_EMAIL_SERVERS:
     # ******************** NOTE ****************************
     # After LEO version 1.2 there will only be 2 Email servers of which the 1st one will be a HLC default email server and the second one will be a user defined server.
     # Hence we have changed the factory reset logic for the emails servers and hard coded the values for both these servers.
     # ******************** END *****************************

    strServerName = "Server {0}".format(iRecNum + 1)
    if iRecNum == 0:  # First record will be based upon version 3 email settings.
      # strFromAddress = origSettings['fromaddress']
      # strServerAddress = origSettings['smtpserver']
      # strServerPort = origSettings['smtpport']
      # iEnabletls = origSettings['enabletls']
      # iEnableAuth = origSettings['enableauthentication']
      # strAuthAcct = origSettings['authaccount']
      # strAuthPassword = origSettings['authpassword']
      strSQL = 'INSERT into emailservers VALUES("Server 1","alarms@leocloud.us","mail.leocloud.us",587,1,1,"alarms@leocloud.us","leoalarms!",1)'
      cur.execute(strSQL)
    else:
      # strFromAddress = ""
      # strServerAddress = ""
      # strServerPort = ""
      # iEnabletls = 1
      # iEnableAuth = 1
      # strAuthAcct = ""
      # strAuthPassword = ""
      cur.execute('INSERT into emailservers VALUES("Server 2","","",0,1,1,"","",0)')

    # # We need to create a new record in each table and copy over the existing values.
    # strSQL = 'INSERT INTO emailservers ( emailservername,fromaddress,smtpserver,smtpport,enabletls, ' \
             # 'enableauthentication,authaccount,authpassword ) VALUES ("{0}","{1}","{2}",' \
             # '"{3}",{4},{5},"{6}","{7}")'.format(strServerName, strFromAddress, strServerAddress,
                                                 # strServerPort, iEnabletls, iEnableAuth, strAuthAcct, strAuthPassword)

    iRecNum = iRecNum + 1
    # cur.execute(strSQL)

  conn.commit()  # in case called directly.

# The following is code to upgrade databases
# This method makes sure the database is at the correct version and updates it if it is not.

# When changes are made to the database schema/structure, increment the version number here - NOT IN THE DATABASE. Code (that you will add below) will update the database and the version.
databaseVersionDict = { systemDatabasePath : 8, logDatabasePath : 1, alarmDatabasePath : 4, deviceDatabasePath : 2, E2AlarmDatabasePath : 5, AuditTrailDatabasePath : 1, authDatabasePath : 1, emailDatabasePath : 2 }

# This function is used to create a default email database (this should be done for each database...)
def createEmailDatabase():

  conn = _getConnection(emailDatabasePath)
  cur = conn.cursor()
  strSQL = 'CREATE TABLE emailtransactionsTable (' \
           'date TIMESTAMP,' \
           'recId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,' \
           'transcmd INTEGER DEFAULT -1,' \
           'transstatus	INTEGER DEFAULT -1,' \
           'emailtype INTEGER DEFAULT -1,' \
           'EBrecId INTEGER DEFAULT -1,' \
           'toaddress TEXT DEFAULT NULL,' \
           'servername TEXT DEFAULT NULL,' \
           'subjectline TEXT DEFAULT NULL,' \
           'emailstatus TEXT DEFAULT NULL )'
  cur.execute(strSQL)

  strSQL = 'CREATE TABLE emailbodyTable (' \
           'date TIMESTAMP,' \
           'recId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,' \
           'jsonEmailInfo TEXT DEFAULT NULL)'

  cur.execute(strSQL)

  # Create the database version table
  strSQL = 'CREATE TABLE DBInfo ( version INTEGER DEFAULT -1, factoryInitNeeded INTEGER DEFAULT 0 )'
  cur.execute(strSQL)
  # Set the proper version for the database.
  strSQL = 'INSERT INTO DBInfo(version) VALUES( {} )'.format( databaseVersionDict[emailDatabasePath] )
  cur.execute(strSQL)

  conn.commit()
  conn.close()


#   Database Version History
#   Version 1 - For all databases, added DBInfo table with a version number for each database.
#   Version 2 - system.db - Added "enunciated" column into device alarms for future use indicating enunciated alarms (for alarm notification - active and need to be sent out - made it through the alarm filter)
#             - system.db - Added table for enunciated alarm filters. Added table for "miscellaneous" settings to hold enunciated alarm filters enable setting.
#             - E2.db - Added additional fields for E2 device offline and E2 device RTN alarm delays and alarm clear timeout (E2DevOfflineAlmDelay, E2DevOfflineRTNDelay)

#   Version 2 - alarms.db - 9/19/2017 Need to add emailaddress record to lastemail table for multiple email addreesses.
#   Version 3 - system.db - Added dnsaddress as separate field in ethernet table.
#             - alarms.db - Added emailtransactionsTable and emailbodyTable for improved email tracking. Add column to devicealarms for crossreference.
#             - E2.db - Added one database field which will hold a "dict" for settings to improve communications with LEO and E2
#   Version 4 - system.db - 9/4/2017 - Added new tables for multiple email settings and email server settings.
#             - E2.db - Added column for storing E2 alarm timestamp in UTC for sorting purposes.
#   Version 5 - system.db - 11/9/2017 - Added new entry in emailsettings to specify the delay between email retries.
#   Version 6 - system.db - 06/21/2018 - Added new entry in emailsettings to specify the statusReportsPerHour for LEO HeartBeat email frequency.

def upgradeDatabasesCheck():

  log.info("Checking Database Versions")
  # Let's make sure the emailDatabase exists, and if not, let's create it.
  if os.path.exists(emailDatabasePath) is False :
    createEmailDatabase()

  for fullDatabasePath in databaseVersionDict:
    conn = _getConnection(fullDatabasePath)
    cur = conn.cursor()

    # Get Database Table Names
    strSQL = 'select name from sqlite_master where type = "table"'
    cur.execute(strSQL)
    dbTableNames = cur.fetchall()  # Get the list of table names for this database
    # dbTableNames = [[str(item) for item in results] for results in cur.fetchall()]
    # print "Database: ", fullDatabasePath, " Table Names = ", dbTableNames
    dbTables = ([x[0] for x in dbTableNames])
    # Create DBInfo if it does not exist
    if not 'DBInfo' in dbTables:
      # We need to add this table and set the version to 1.
      strSQL = 'CREATE TABLE DBInfo ( version INTEGER DEFAULT -1, factoryInitNeeded INTEGER DEFAULT 0 )'
      cur.execute(strSQL)
      strSQL = 'INSERT INTO DBInfo(version) VALUES(1)'
      cur.execute(strSQL)
      dbVersion = 0
      log.info("UPGRADED Database:{} to Version:{}".format(fullDatabasePath, dbVersion))
    else:  #
      # DBInfo exists. Get the database version number.
      strSQL = 'SELECT version from DBInfo'
      cur.execute(strSQL)
      dbVersion = cur.fetchone()[0]

    # Don't check the database if it is up to date.
    if dbVersion < databaseVersionDict[fullDatabasePath] :
      str = "Need to upgrade {0} from version:{1} to version:{2}".format( fullDatabasePath, dbVersion, databaseVersionDict[fullDatabasePath] )
      log.info( str )
      dbVersion = dbVersion + 1
      while dbVersion <= databaseVersionDict[fullDatabasePath]:  # Loop through "upgrade" revisions
            # @@@@@ NOTE  @@@@@@@@--  Add the subprocess command and the postmap command in all the future builds as well.

        # DBVERSION 8
        #########################
        if dbVersion == 8:  # code to get db to version 7
          ##########################
          # SYSTEM DATABASE
          #########################



          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB

            strSQL = 'ALTER TABLE system ADD COLUMN enableLeoCloud INTEGER DEFAULT 0'
            cur.execute(strSQL)
            strSQL = 'ALTER TABLE system ADD COLUMN timeServer TEXT DEFAULT "NA"'
            cur.execute(strSQL)
            # strSQL = 'ALTER TABLE system ADD COLUMN storeMarkerId INTEGER DEFAULT 0'
            # cur.execute(strSQL)
            strSQL = 'UPDATE DBInfo SET version=8'
            cur.execute(strSQL)
            conn.commit()
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

        # DBVERSION 7
        #########################
        if dbVersion == 7:  # code to get db to version 7
          ##########################
          # SYSTEM DATABASE
          #########################



          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB

            strSQL = 'ALTER TABLE emailservers ADD COLUMN defaultServer INTEGER DEFAULT NULL'
            cur.execute(strSQL)

            cur.execute( 'delete from emailservers' )
            strSQL = 'INSERT into emailservers VALUES("Server 1","alarms@leocloud.us","mail.leocloud.us",587,1,1,"alarms@leocloud.us","leoalarms!",1)'
            cur.execute(strSQL)
            cur.execute('INSERT into emailservers VALUES("Server 2","","",?,1,1,"","",0)',(None,))
            strSQL = 'UPDATE ethernet set hostname="leo.leocloud.us"'
            cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version=7'
            cur.execute(strSQL)
            conn.commit()
            subprocess.call("/usr/bin/crontab -l 2>/dev/null | grep -q 'reboot'  && echo 'cronttab entry already exists' || echo '30 5 * * * /sbin/reboot >> /opt/monitor/log/gunicorn-err.log' | /usr/bin/crontab -", shell=True)
            log.info( "ADDED Daily Reboot Cron job using subprocess command")
            # subprocess.call('debconf-set-selections <<< "postfix postfix/mailname string leo.leocloud.us"', shell=True)
            # command = "debconf-set-selections <<< "+ '"postfix postfix/main_mailer_type string "'+"'Internet Site'"
            # log.debug(command)
            # subprocess.call(command, shell=True)
            # subprocess.call("apt-get install -y postfix", shell=True)
            subprocess.call("postmap /etc/postfix/sasl_passwd", shell=True)
            log.info( "postmap command executed")
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

        # DBVERSION 6
        #########################
        if dbVersion == 6:  # code to get db to version 6
          ##########################
          # SYSTEM DATABASE
          #########################

          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB

            strSQL = 'ALTER TABLE emailsettings ADD COLUMN statusReportsPerHour INTEGER DEFAULT 6'
            cur.execute(strSQL)

            strSQL = 'INSERT into emailaddresses VALUES("","Server 1",0,1)'
            cur.execute(strSQL)

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
            strFilename = "{0}/system/enunciatedAlarmFilters.csv".format(sys.path[0])

            parseState = PARSING_STATE_UNKNOWN
            enunciatedAlarmFilters = []

            iLineCount = 0

            with open(strFilename, 'rb') as csvfile:
              fileLines = csv.reader(csvfile, delimiter=',')

              # process the lines...
              for strInLine in fileLines:
                iLineCount = iLineCount + 1
                params = strInLine  # strInLine is already "split" based upon commas...

                if len(params) > 0 and params[0][0] != '#':  # blank line or comment line...
                  if parseState == PARSING_STATE_UNKNOWN:
                    if params[0] == 'Group Type':
                      parseState = PARSING_LINES

                  elif parseState == PARSING_LINES:
                    if len(params[0]) > 0:
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
                      enunciatedAlarmFilters.append(dictAlarmFilter)

            #        print "Factory: ", self.enunciatedAlarmFilters
            _saveEnunciatedAlarmFilters(enunciatedAlarmFilters, 0, cur)

            strSQL = 'UPDATE DBInfo SET version=6'
            cur.execute(strSQL)
            conn.commit()
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

        ##########################
        # DBVERSION 5
        #########################
        if dbVersion == 5:  # code to get db to version 5
          ##########################
          # SYSTEM DATABASE
          #########################
          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB
            # We just need to add a field to a the emailsettings table
            strSQL = 'ALTER TABLE emailsettings ADD COLUMN emailretrydelay INTEGER DEFAULT 5'
            cur.execute(strSQL)

            strSQL = 'ALTER TABLE emailsettings ADD COLUMN statusReportsperHour INTEGER DEFAULT 6'
            cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version=5'
            cur.execute(strSQL)
            conn.commit()
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # E2 DATABASE
          #########################
          # if fullDatabasePath == E2AlarmDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB
            # # E2.db - Need to add table for SC255 settings
            # dbTableFound = False
            # for tableName in dbTableNames:
              # if tableName[0] == 'AKSC255AlarmEntryTable' or tableName[0] == 'AKSC255Settings':
                # dbTableFound = True
  
            # if dbTableFound == False:
              # blUpgrade = True
            # else:
              # blUpgrade = False
  
            # # CREATE Danfoss Alarm Entry Table
            # # We need to add the email addresses table and set the version to 5
            # strSQL = 'CREATE TABLE AKSC255AlarmEntryTable( toaddress TEXT DEFAULT NULL, emailservername TEXT DEFAULT NULL,  ' \
                     # 'enableemail INTEGER DEFAULT 1, enablealarmreport INTEGER DEFAULT 1 )'
            # cur.execute(strSQL)
  
            # # CREATE Danfoss Settings Table
            # strSQL = 'CREATE TABLE AKSC255Settings( deviceGetAlarms INTEGER DEFAULT 1, deviceAlarmCycleTime INTEGER DEFAULT 30, ' \
                     # 'deviceAlarmPriorityFilter INTEGER DEFAULT 20, deviceAlarmFilterNotice INTEGER DEFAULT 1, ' \
                     # 'deviceAlarmFilterFail INTEGER DEFAULT 0, deviceAlarmFilterAlarm INTEGER DEFAULT 0, ' \
                     # 'deviceAlarmFilterRTN INTEGER DEFAULT 1, deviceOfflineRTNDelay INTEGER DEFAULT 60, ' \
                     # 'deviceOfflineAlmDelay INTEGER DEFAULT 60, deviceMaxValsPerMsg INTEGER DEFAULT 10, ' \
                     # 'deviceDelayBetweenMsgsMS INTEGER DEFAULT 500 )'
            # cur.execute(strSQL)
            # # Add a record with default values.
            # cur.execute( 'INSERT INTO AKSC255Settings default values' )
  
            # strSQL = 'UPDATE DBInfo SET version=5'
            # cur.execute(strSQL)
            # conn.commit()
            # print "UPGRADED Database:", fullDatabasePath, " to Version:", dbVersion

          # factoryDeviceSettings = {"deviceGetAlarms": 1,
                                   # "deviceAlarmCycleTime": 30,
                                   # "deviceAlarmPriorityFilter": 20,
                                   # "deviceAlarmFilterNotice": 1,
                                   # "deviceAlarmFilterFail": 0,
                                   # "deviceAlarmFilterAlarm": 0,
                                   # "deviceAlarmFilterRTN": 1,
                                   # "deviceOfflineRTNDelay": 60,
                                   # "deviceOfflineAlmDelay": 60,
                                   # "deviceMaxValsPerMsg": 10,
                                   # "deviceDelayBetweenMsgsMS": 500}


        ##########################
        # DBVERSION 4
        #########################
        if dbVersion == 4:  # code to get db to version 4
          ##########################
          # SYSTEM DATABASE
          #########################
          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB
            # system.db - Need to add tables for multiple email settings
            dbTableFound = False
            for tableName in dbTableNames:
              if tableName[0] == 'emailaddresses' or tableName[0] == 'emailservers':
                dbTableFound = True

            if dbTableFound == False:
              blUpgrade = True
            else :
              blUpgrade = False


            # CREATE EMAIL ADDRESS TABLE
            # We need to add the email addresses table and set the version to 4
            strSQL = 'CREATE TABLE emailaddresses( toaddress TEXT DEFAULT NULL, emailservername TEXT DEFAULT NULL,  ' \
                      'enableemail INTEGER DEFAULT 1, enablealarmreport INTEGER DEFAULT 1 )'
            cur.execute(strSQL)

            # CREATE EMAIL SERVER TABLE
            strSQL = 'CREATE TABLE emailservers( emailservername TEXT DEFAULT NULL, fromaddress TEXT DEFAULT NULL, ' \
                     'smtpserver TEXT DEFAULT NULL, smtpport TEXT DEFAULT NULL, ' \
                     'enabletls INTEGER DEFAULT 1, enableauthentication INTEGER DEFAULT 1, ' \
                     'authaccount TEXT DEFAULT NULL, authpassword TEXT DEFAULT NULL )'
            cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version=4'
            cur.execute(strSQL)
            conn.commit()
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

            # Set initial/default values.
            setEmailAddressAndServerTablesToFactoryDefaults(conn, blUpgrade)  # db upgrade of email settings

          ##########################
          # ALARM DATABASE
          #########################
          if fullDatabasePath == alarmDatabasePath:
            # We just need to add a field to a the devicealarmstable to store return to normal timestamp
            strSQL = 'ALTER TABLE devicealarms ADD COLUMN rtntimestamp TEXT DEFAULT null'
            cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version=4'
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # E2 DATABASE - Version 4
          #########################
          # Need to add column for UTC formatted E2 alarm and rtn date so we can sort the alarms properly.
          if fullDatabasePath == E2AlarmDatabasePath:
            strSQL = 'ALTER TABLE E2AlarmEntryTable ADD COLUMN UTCdbTimestamp TIMESTAMP DEFAULT null'
            cur.execute(strSQL)
            strSQL = 'ALTER TABLE E2AlarmEntryTable ADD COLUMN UTCrtntimestamp TIMESTAMP DEFAULT null'
            cur.execute(strSQL)
            strSQL = 'UPDATE DBInfo SET version=4'
            cur.execute(strSQL)
            log.info("UPGRADED Database:{} to Version:{}".format(fullDatabasePath, dbVersion))
            # Also, change E2 device online/offline timers to minutes from seconds.
            strSQL = 'SELECT E2DevOfflineAlmDelay,E2DevOfflineRTNDelay FROM E2Settings'
            cur.execute(strSQL)
            result = cur.fetchone()
            dbEntries = OrderedDict(result)
            offDelay = int( dbEntries['E2DevOfflineAlmDelay'] ) / 60
            rtnDelay = int( dbEntries['E2DevOfflineRTNDelay'] ) / 60
            # In version 4, online and offline delay settings are minutes, not seconds.
            strSQL = 'UPDATE E2Settings set E2DevOfflineAlmDelay={}, E2DevOfflineRTNDelay={}'.format( offDelay, rtnDelay )
            cur.execute(strSQL)
            conn.commit()

        ##########################
        # DBVERSION 3
        #########################
        if dbVersion == 3:  # code to get db to version 3
          ##########################
          # SYSTEM DATABASE - Version 3
          #########################
          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 3 for SYSTEM.DB
            # We just need to add a field to a table
            strSQL = 'ALTER TABLE ethernet ADD COLUMN dnsaddress TEXT'
            cur.execute(strSQL)
            # We are adding a table. Let's put a "key" value in so that we know this table needs
            # a default configuration - since this is called before the Alarm Manager is initilazed.

            strSQL = 'UPDATE DBInfo SET version={}'.format( dbVersion )
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # ALARM DATABASE - Version 3
          #########################
          if fullDatabasePath == alarmDatabasePath:
            # We just need to add a field to a the devicealarmstable to track alarms that are emailed.
            strSQL = 'ALTER TABLE devicealarms ADD COLUMN EBrecId INTEGER DEFAULT -1'
            cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version={}'.format( dbVersion )
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # E2 DATABASE - Version 3
          #########################
          if fullDatabasePath == E2AlarmDatabasePath:
            strSQL = 'ALTER TABLE E2Settings ADD COLUMN E2MaxValsPerMsg INT DEFAULT 10'
            cur.execute(strSQL)
            strSQL = 'ALTER TABLE E2Settings ADD COLUMN E2DelayBetweenMsgsMS INT DEFAULT 500'
            cur.execute(strSQL)
            strSQL = 'UPDATE DBInfo SET version={}'.format( dbVersion )
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

        ##########################
        # DBVERSION 2
        #########################
        if dbVersion == 2:  # code to get db to version 2


          ##########################
          # Device DATABASE
          #########################
          if fullDatabasePath == deviceDatabasePath:  # Specific code for device database to get to version 2 for SYSTEM.DB
            dbTableFound = False
            dbTableFound1 = False
            for tableName in dbTableNames:
                if tableName[0] == 'idealConfigs':
                    dbTableFound = True
                if tableName[0] == 'syncVal':
                    dbTableFound1 = True

            if dbTableFound == False:
              strSQL = 'CREATE TABLE idealConfigs( deviceName TEXT, valueName TEXT,  ' \
                      'value TEXT )'
              cur.execute(strSQL)
              strSQL = 'CREATE TABLE syncVal( deviceName TEXT, enableBit INTEGER )'
              cur.execute(strSQL)
              strSQL = 'UPDATE DBInfo SET version={}'.format( dbVersion )
              cur.execute(strSQL)
              log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )


          ##########################
          # SYSTEM DATABASE
          #########################
          if fullDatabasePath == systemDatabasePath:  # Specific code for system database to get to version 2 for SYSTEM.DB
            dbTableFound = False
            for tableName in dbTableNames:
                if tableName[0] == 'enunciatedAlmFilters':
                    dbTableFound = True

            if dbTableFound == False:
              # We need to add this table and set the version to 2
              strSQL = 'CREATE TABLE enunciatedAlmFilters ( enable INTEGER DEFAULT 0, groupType TEXT DEFAULT NULL, ' \
                       'alarmType TEXT DEFAULT NULL, alarm TEXT DEFAULT NULL,  description TEXT DEFAULT NULL, ' \
                       'deviceType TEXT DEFAULT NULL, deviceName TEXT DEFAULT NULL, appName TEXT DEFAULT NULL, ' \
                       'appProp TEXT DEFAULT NULL )'
              cur.execute(strSQL)
              # We are adding a table. Let's put a "key" value in so that we know this table needs
              # a default configuration - since this is called before the Alarm Manager is initilazed.

            dbTableFound = False
            for tableName in dbTableNames:
                if tableName[0] == 'miscsettings':
                    dbTableFound = True

            if dbTableFound == False:
              # We need to add this table and set the version to 2
              strSQL = 'CREATE TABLE miscsettings(enunciatedAlarmFiltersActive INTEGER)'
              cur.execute(strSQL)
              # Create the record, but let factory init set it properly.
              strSQL = 'INSERT INTO miscsettings(enunciatedAlarmFiltersActive) VALUES(0)'
              cur.execute(strSQL)

            strSQL = 'UPDATE DBInfo SET version=2, factoryInitNeeded=1'
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # ALARM DATABASE
          #########################
          if fullDatabasePath == alarmDatabasePath:
            strSQL = 'ALTER TABLE lastemail ADD COLUMN emailaddress TEXT'
            cur.execute(strSQL)
            strSQL = 'UPDATE DBInfo SET version=2'
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # E2 DATABASE
          #########################
          if fullDatabasePath == E2AlarmDatabasePath:
            strSQL = 'ALTER TABLE E2Settings ADD COLUMN E2DevOfflineAlmDelay INTEGER DEFAULT 60'
            cur.execute(strSQL)
            strSQL = 'ALTER TABLE E2Settings ADD COLUMN E2DevOfflineRTNDelay INTEGER DEFAULT 60'
            cur.execute(strSQL)
            strSQL = 'UPDATE DBInfo SET version=2'
            cur.execute(strSQL)
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

          ##########################
          # EMAIL DATABASE
          #########################
          if fullDatabasePath == emailDatabasePath:
            # This funciton will delete and re-create the email database. This is requied
            # because in version 2 we had to change the date field from TEXT to TIMESTAMP
            createEmailDatabase()
            log.info( "UPGRADED Database:{} to Version:{}".format( fullDatabasePath, dbVersion ) )

        dbVersion = dbVersion + 1

    conn.commit()
    conn.close()


def _saveEnunciatedAlarmFilters( enunciatedAlarmFilters, ienunciatedAlarmFiltersActive,cur ) :
    #conn = getSystemDatabaseConnection()
    #cur = conn.cursor()
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
# The following are functions to create empty databases in the case of a corrupted or non-existent database. TODO
# The code for erasing of all of the database records is found elsewhere in the software.

