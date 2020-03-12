from flask_restful import Resource
from flask import session, jsonify, redirect, url_for, render_template, request, send_file, current_app as app

import imghdr
import glob
from PIL import Image
from authentication import auth_delete_superuser, auth_add_superuser
import os
import shutil
import dbUtils
import subprocess

import logsystem
log = logsystem.getLogger()

listLeoBackupPaths = [ 'static/uimg' ]  # in case we need to backup other folders.


# Creates folder for backup and restore
def _backup_mkdir( strDir ) :
  # If the directory already exists, don't do anything.
  if os.path.exists( strDir ) == False:
    oldUmask = os.umask( 0 )
    os.mkdir( strDir, 0777 )
    os.umask( oldUmask )

# Recursively copies one folder to another
def _backup_recurse_copy( strSrc, strDest ) :
  _backup_mkdir( strDest )

#  print strSrc, " | ", strDest
#  print os.listdir( strSrc )

  for filename in os.listdir( strSrc ) :
    if filename != '.' and filename != '..' :
      strSrcPath = os.path.join( strSrc, filename )
      strDestPath = os.path.join( strDest, filename )
      if os.path.isdir( strSrcPath ) == True :
        _backup_recurse_copy( strSrcPath, strDestPath )
      else :
        shutil.copyfile( strSrcPath, strDestPath )
  return 0

def removeDir( strPath ) :
  # if the path exists, delete it.
  if os.path.exists(strPath) == True :
    shutil.rmtree(strPath)
  return 0

def eraseAndCreateDir( strPath ) :
  # Kill everything in the folder (if it exists) and create a new folder
  removeDir( strPath )
  _backup_mkdir( strPath )
  return 0

# Encapsulation of shell commands
# stdOutFileName can be "" if caller does not care about output from commmand
def _executeShell( strShell, stdOutFileName ) :

  # result contains the stdout
#  print "EXECUTE SHELL", strShell
  result = subprocess.check_output( strShell, shell=True )
#  print "RESULTS", result

  if len( stdOutFileName ) > 0 :
    # save stdout to the specified outputfile
    fp = open( stdOutFileName, "w")
    fp.write( result )
    fp.close()
  else :
    return result


# backup a single database file
def _system_backup_database( strBkupDir, strDbName ) :
  # Create backup filename based upon database file
  strPath, strFileName = os.path.split( strDbName )
  strFileName = strFileName + '.txt'

  strDbBackupFileName = os.path.join( strBkupDir, strFileName )

  if strFileName == dbUtils.authDatabasePath :
    auth_delete_superuser()  # Remove the superuser...

  # database dump and save in backup filename

  if os.name == "nt" : # We are on the PC.
    strShell = "sqlite3 {0} .dump".format( strDbName )
  else :
    strShell = '/usr/bin/sqlite3 {0} .dump'.format( strDbName )

  # Calls shell and saves stdout to second parameter file
#  print strShell
  _executeShell( strShell, strDbBackupFileName )

  if strFileName == dbUtils.authDatabasePath :
    auth_add_superuser()  # Add the superuser back

  return strDbBackupFileName


# Backup the entire system
# The file is internally named, created and stored in a backup directory and then named on the "send_file" call.
def backup_system() :

#  print "Backup System"
  # Create the backup folder and delete previous contents
  strBkupDir = os.path.join( app.root_path, 'bkup' )
  eraseAndCreateDir( strBkupDir ) # Single operation to check if exists and if so, delete and re-create empty
#  print "strBkupDir", strBkupDir

  # Create database backup files
  strAuthDbBackupFileName = _system_backup_database( strBkupDir, dbUtils.authDatabasePath )
  strDevicesDbName = _system_backup_database( strBkupDir, dbUtils.deviceDatabasePath )
  strSystemDbName = _system_backup_database( strBkupDir, dbUtils.systemDatabasePath )
  strE2DbName = _system_backup_database( strBkupDir, dbUtils.E2AlarmDatabasePath )

  # Create user image backup location
  strStaticBackupPath = os.path.join( strBkupDir, 'static' )
  eraseAndCreateDir( strStaticBackupPath ) # Single operation to check if exists and if so, delete and re-create empty

  # Loop through list of paths to backup (and sub-directories)
  for strPath in listLeoBackupPaths :
    strBackupPath = os.path.join( strBkupDir, strPath  )
    strSrcPath = os.path.join( app.root_path, strPath  )
    eraseAndCreateDir( strBackupPath ) # Single operation to check if exists and if so, delete and re-create empty
#    print "Backing up from:" + strSrcPath + " to " + strBackupPath
    # This will copy all files into
    _backup_recurse_copy( strSrcPath, strBackupPath )

  # Now zip backup folder up.
  strBackupZipFullPath = os.path.join( strBkupDir, 'bkup.7z' )

  # compress
  if os.name == "nt" : # We are on the PC.
    str7zPath = os.path.join( app.root_path, 'install\winTools' )
    strShell = "{0}/7z.exe a -mhe=on -pHL103Bkup {1} {2}".format( str7zPath, strBackupZipFullPath, strBkupDir )
  else : # We are running on Linux
    strShell = "/usr/bin/7z a -mhe=on -pHL103Bkup {0} {1}".format( strBackupZipFullPath, strBkupDir )

#  print "Zip Cmd: ", strShell
  execResult = _executeShell( strShell, "" )

  result = {}
  result['error'] = False
  result['filename'] = strBackupZipFullPath
  result['length'] = os.path.getsize(strBackupZipFullPath)

#  print "backup_system result->", result

  return result

# Create the debug log files.
def createDebugLog() :

  result = {}
#  print "createDebugLog"
  # Create the debug backup folder previously created.
  strDebugFileDir = os.path.join( app.root_path, 'dbug' )
  eraseAndCreateDir( strDebugFileDir ) # Single operation to check if exists and if so, delete and re-create empty
#  print "strDebugFileDir", strDebugFileDir
  strDebugFileZipFullPath = os.path.join( strDebugFileDir, 'bkup.7z' )
  # We now have an empty folder for storing the debugReport zip file.
  strDebugLogsFullPath = os.path.join( app.root_path, 'log' )
  strAuditTrailDbPath = os.path.join( app.root_path, 'data/AuditTrail.db' )
  strAlarmsDbPath = os.path.join( app.root_path, 'data/alarms.db' )

  # We need to manually backup the audittrail and alarms database since these are not part of the backup.
  strShell = "/usr/bin/7z a -mhe=on -pHL103Bkup {0} {1} {2}".format( strDebugFileZipFullPath, strAuditTrailDbPath, strAlarmsDbPath)
#  print "Zip Cmd: ", strShell

  # Now compress the log files into the zip.
  if os.name == "nt" : # We are on the PC.
    str7zPath = os.path.join( app.root_path, 'install\winTools' )
    # We can't compress the log files on Windows because the active file is exclusively locked. So for the PC, we skip this.
    # Need to validate it for Linux.
#    strShell = "{0}/7z.exe a -mhe=on -pHL103Bkup {1} {2}".format( str7zPath, strDebugFileZipFullPath, strDebugLogsFullPath )
  else : # We are running on Linux
    strShell = "/usr/bin/7z a -mhe=on -pHL103Bkup {0} {1}".format( strDebugFileZipFullPath, strDebugLogsFullPath )
#    print "Zip Cmd: ", strShell
    execResult = _executeShell( strShell, "" )

  # Now, using the same zip file, add the backup of the system.
  result = backup_system() # returns result['error'], result['filename'], result['length']
#  print "backup_system result-->", result

  if result['error'] == False :
    # We can add the backup file to the zip.
    strConfigBackupFile = result['filename']
    if os.name == "nt" : # We are on the PC.
      str7zPath = os.path.join( app.root_path, 'install\winTools' )
      strShell = "{0}/7z.exe a -mhe=on -pHL103Bkup {1} {2}".format( str7zPath, strDebugFileZipFullPath, strConfigBackupFile )
    else : # We are running on Linux
      strShell = "/usr/bin/7z a -mhe=on -pHL103Bkup {0} {1}".format( strDebugFileZipFullPath, strConfigBackupFile )
#    print "Zip Cmd: ", strShell
    execResult = _executeShell( strShell, "" )
#    print "execResult = ", execResult
  else :
    return result

  # Now, let's return the information.
  result['error'] = False
  result['filename'] = strDebugFileZipFullPath
  result['length'] = os.path.getsize(strDebugFileZipFullPath)

#  print "DebugLog Creation result->", result

  return result


def createDownloadFileInfo( strFileName, strMorePath ) :

  # Create the full path to the file. This function can be used to download specific files
  if len( strMorePath ) > 0 :
    strFullPath = os.path.join( app.root_path, strMorePath )
    strDownloadFile = os.path.join( strFullPath, strFileName )
  else :
    # Filename can be full path based if necessary
    strDownloadFile = strFileName
#  print "File to download-->", strDownloadFile

  result = {}
  result['error'] = False
  result['filename'] = strDownloadFile
  try:
    result['length'] = os.path.getsize(strDownloadFile)
  except Exception, e:
    result['error'] = True
    strError = 'Error finding File {0} ({1})'.format( strDownloadFile, str(e) )
    result['strError'] = strError

  return result

# Restore the an individual database backup
def _system_restore_database( strBkupDir, strDbName ) :

#  print "Restore Database. strBkupDir, strDbName-->", strBkupDir, strDbName

  # Restore the backup file
  strPath, strFileName = os.path.split( strDbName )
  strFileName = strFileName + '.txt'

  strDbBackupFileName = os.path.join( strBkupDir, strFileName )

  if os.path.isfile( strDbName ):
#    print "Remove Database File before restore-->", strDbName
    os.remove( strDbName )

  if os.name == "nt" : # We are on the PC.
    strShell = "sqlite3 {0} < {1}".format( strDbName, strDbBackupFileName )
  else :
    strShell = "/usr/bin/sqlite3 {0} < {1}".format( strDbName, strDbBackupFileName )

  _executeShell( strShell, "")

  oldUmask = os.umask( 0 )
  os.chmod( strDbName, 0666 )
  os.umask( oldUmask )

  if strDbName == dbUtils.authDatabasePath :
    auth_add_superuser()  # Make sure the superuser password is in there.

  return strDbName
#  return json_decode(response['result'])


# Restore the complete system
def restore_system( strFullPathRestoreFile ) :

  result = {}
  result['success'] = False
  result['error'] = ''

  # Location of the .zip backup file to be restored.
  strBackupFileLoc = os.path.dirname( strFullPathRestoreFile )
#  print "strBackupFileLoc-->", strBackupFileLoc

  # Location where files are to be extracted. Let's do it "inline" in the same folder.
  strBkupDir = strBackupFileLoc

  try:

    # decompress into working directory
    if os.name == "nt" : # We are on the PC.
      str7zPath = os.path.join( app.root_path, 'install\winTools' )
      strShell = "{0}/7z.exe e -y -mhe=on -pHL103Bkup {1} -o{2}".format( str7zPath, strFullPathRestoreFile, strBkupDir )
    else : # We are running on Linux
      # The zip file will automatically expand it to the folder it was saved with (which is /opt/monitor/bkup) - when the "-d /" parameter is added.
      strShell = "/usr/bin/7z e -y -mhe=on -pHL103Bkup {0} -o{1}".format( strFullPathRestoreFile, strBkupDir )
#      strShell = "unzip -P HL103Bkup {0} -d /".format( strFullPathRestoreFile )
#      print "UNZIP strShell -->", strShell

    _executeShell( strShell, "")

    # Restore database backup files
    _system_restore_database(strBkupDir, dbUtils.authDatabasePath)
    _system_restore_database(strBkupDir, dbUtils.deviceDatabasePath)
    _system_restore_database(strBkupDir, dbUtils.systemDatabasePath)
    _system_restore_database(strBkupDir, dbUtils.E2AlarmDatabasePath)
    # We need to clear out the alarms from the database.

    # Restore image files. There is the uimg folder and the uimg/device folder.
    # Very important the order this is created.

    # Loop through list of paths to backup (and sub-directories)
    # appRoot "static" path will exist.
    for strPath in listLeoBackupPaths :
      strRestorePath = os.path.join( app.root_path, strPath )
      strSrcPath = os.path.join( strBkupDir, strPath )
#      print "Restore from:" + strSrcPath + " to " + strRestorePath
      # This will copy all files into
      _backup_recurse_copy( strSrcPath, strRestorePath )

    # removeDir( strBkupDir )

  except Exception, e:
    log.debug("Error During Restore: " + str(e))
    result['error'] = str(e)
    return result

  result['success'] = True

  return result

  def debugReport(strFilename) :
    createDebugReportFile()

