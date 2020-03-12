#!/usr/bin/python

import smtplib
import datetime
import sys
sys.path.append('system/utils')
import dbUtils
import utilities

import logsystem
log = logsystem.getLogger()

########################
# AuditTrailConstants
########################

#Default timestamp for unused Audit Trail entries
AuditTrailDefaultTimestamp = '2001-01-01 00:00:00'
MAX_LEO_AUDIT_TRAIL_ENTRIES = 1000
###################################################
# Audit Trail Functions
###################################################

###########################################
# Audit Trail Database Blue-R
def setAuditDatabaseToFactorySettings() :
  conn = dbUtils.getAuditTrailDatabaseConnection()
  cur = conn.cursor()
  # Clear all the alarm records.
  cur.execute('delete from AuditTable')
  # Clear last email information
  cur.execute('update Settings set MaxAuditSamples=1000')
  conn.commit()
  conn.close()
  dbUtils.vacuumDatabase( dbUtils.AuditTrailDatabasePath ) # Compress database


def initAuditTrail() :
  # Place holder...
  return 0

def AuditTrailDatabaseCleanup():
  # We will limit the audit trail to a specific number of entries.
  conn = dbUtils.getAuditTrailDatabaseConnection()
  cur = conn.cursor()
  strSQL = "delete from AuditTable where dbTimestamp not in ( select dbTimestamp from AuditTable order by dbTimestamp desc limit {0} )".format( MAX_LEO_AUDIT_TRAIL_ENTRIES )
  cur.execute(strSQL)
  conn.commit()
  conn.close()
  dbUtils.vacuumDatabase(dbUtils.AuditTrailDatabasePath)  # Compress database
  log.debug("Database cleanup of LEO audit trail entries")


def AuditTrailAddEntry( strDescription ) :

  conn = dbUtils.getAuditTrailDatabaseConnection()
  cur = conn.cursor()

  try:
    strTimestamp = utilities.getUTCnowFormatted()
    buf = 'Audit Trail Timestamp = {0} - Str:{1}'.format( strTimestamp, strDescription )
    log.info( buf )
#    print "Adding Audit Trail Entry-->", strDescription
    try:
      cur.execute( 'INSERT INTO AuditTable VALUES (?,?)', ( strTimestamp, strDescription ) )
    except:
      log.exception("Error in Filling Audit Trail Database")
  except:
    log.exception("Error in oldest row id in Audit Trail Database")

  conn.commit()
  conn.close()

  return 0

def AuditTrailGetEntries() :
  conn = dbUtils.getAuditTrailDatabaseConnection()
  cur = conn.cursor()

  try:
    cur = conn.cursor()
    cur.execute( 'select dbTimeStamp, auditDescription from AuditTable order by [dbTimestamp] desc' )
    retval = []
    for ATEntry in cur.fetchall():
      dict = dbUtils.dictFromRow(ATEntry)
      retval.append(dict)
    return retval
  except:
    log.exception("Error in AuditTrailGetEntries")

  conn.close()

def AuditTrailDeleteAllEntries() :
#  print 'Deleting ALL Audit Log Entries from Database'
  conn = dbUtils.getAuditTrailDatabaseConnection()

  try:
    cur = conn.cursor()
    cur.execute('delete from AuditTable')
    conn.execute("VACUUM")
    conn.commit()
    conn.close()
    AuditTrailAddEntry("All Audit Trail Entries Deleted")
    return "All Audit Trails Entries Deleted"
  except:
    print("Error in AuditTrailDeleteAllEntries")
    return "Error in AuditTrailDeleteAllEntries"
    conn.close()



