from flask_restful import Resource
from flask import session, request, current_app as app
import glob
import os
import time
import backup
import leoObject
from werkzeug.utils import secure_filename
import subprocess
import authentication
import auditTrail
from LeoFlaskUtils import getSessionUsername

MAX_FILE_LENGTH = 100000000

class uploadcheck(Resource):
  def __init__(self):
    self.gLeonardo = leoObject.getLeoObject()

  def post(self):

    result = {}
#    print "UploadCheck - ", request

    if request.is_xhr == True :  # This is an ajax call instead of JSON.
#      print "XHR Request"

      # Assume all good and modfiy when not.
      result['success'] = True
      result['error'] = ""
      result['restart'] = ""
      strAuditOperation = "Upload Function Unknown"
      strFileName = ""

      if request.form['location'] == "devices" and "action" in request.form :

        if request.form['action'] == "delete" :

#          print "Delete device image"
          strAuditOperation = 'Delete Device Image'
          strFileToDelete = request.form['fileToDelete']
          if len(strFileToDelete) > 0:
            strTgtDir = app.root_path + '/static/uimg/devices'
            os.unlink(os.path.join(strTgtDir, strFileToDelete))
          else:
            result['success'] = False
            strAuditOperation = "Delete Device Image"
            result['error'] = "No File Specificed"

      elif request.form['location'] == "devices1" and "action" in request.form :

        if request.form['action'] == "delete" :

#          print "Delete device image"
          strAuditOperation = 'Delete Device Image'
          strFileToDelete = request.form['fileToDelete']
          if len(strFileToDelete) > 0:
            strTgtDir = app.root_path + '/static/local/img'
            os.unlink(os.path.join(strTgtDir, strFileToDelete))
          else:
            result['success'] = False
            strAuditOperation = "Delete Device Image"
            result['error'] = "No File Specificed"

      else : # This is a file upload

        # Make sure the file has a name...
#        print "Files = ", request.files['fileToUpload']
        fileHandle = request.files['fileToUpload']
        if len( fileHandle.filename ) <= 0 :
          strAuditOperation = "Upload File"
          result['error'] = "No File Specificed"
        else :
          # Get all information about the file
#          print "Filename = ", fileHandle.filename
          strFileName = fileHandle.filename
          fileHandle.seek( 0, os.SEEK_END )
          fileLength = fileHandle.tell()
          # Reset the file pointer to the beginning of the file - otherwise we will transfer an empty file.
          fileHandle.seek( 0, 0 )
#          print "File Size = ", fileLength

          strSaveDir = ""

          if request.form['location'] == "firmware" :
#            print "Firmware Update"
            strAuditOperation = 'SW Upload'
            strTgtDir = app.root_path + '/install'
            if fileLength > MAX_FILE_LENGTH:
              result['error'] = 'File is too large'

          elif request.form['location'] == "restore" :
#            print "Upload Restore"
            strAuditOperation = 'Restore Configuration'
            strTgtDir = app.root_path + '/bkup'
#            print "strTgtDir, fileLength -->", strTgtDir, fileLength
            if fileLength > MAX_FILE_LENGTH:
              result['error'] = 'File is too large'

          elif request.form['location'] == "devices" :
#            print "Upload Device Images"
            strAuditOperation = 'Upload Device Image'
            strTgtDir = app.root_path + '/static/uimg/devices'
            if fileLength > MAX_FILE_LENGTH:
              result['error'] = 'File is too large'

          elif request.form['location'] == "devices1" :
#            print "Upload Device Images"
            strAuditOperation = 'Upload Device Image'
            strTgtDir = app.root_path + '/static/local/img'
            if fileLength > MAX_FILE_LENGTH:
              result['error'] = 'File is too large'

          strTgtFile = os.path.join( strTgtDir, strFileName )
#          print "strTgtFile-->", strTgtFile
          fileRoot, fileExt = os.path.splitext(strFileName)
#          print "fileRoot, fileExt-->", fileRoot, fileExt
#          print "request.form['location']-->", request.form['location']

          # We want to make sure we are uploading the right file types.
          if request.form['location'] == "summary" or request.form['location'] == "devices" or request.form['location'] == "devices1":
            # make sure the file is a valid image file
            if fileExt != '.png' and fileExt != '.jpg' and fileExt != '.jpeg' and fileExt !=  '.gif' and fileExt != '.tif' :
              result['error'] = "File is not an image (png, jpg, jpeg, gif, tif)."

            elif request.form['location'] == "summary" :
              # Get all file names
              strPattern = strTgtDir + '*'
              listOfFiles = glob.glob( strPattern )
              for filename in listOfFiles :
                if os.path.isfile(filename) is True:
                  os.unlink( filename ) # delete file
            elif request.form['location'] == "devices" :
              if os.path.isfile(strTgtFile) is True:
                os.unlink( strTgtFile ) # delete file

            elif request.form['location'] == "devices1" :
              if os.path.isfile(strTgtFile) is True:
                os.unlink( strTgtFile ) # delete file

          elif request.form['location'] == "restore" :
            if fileExt != '.zip':
              result['error'] = "Only ZIP files are allowed."

          elif request.form['location'] == "firmware" :
            if fileExt != '.pkg':
              result['error'] = "Only PKG files are allowed."

              # Get all file names in the destination directory and make sure it's empty...
              strPattern = os.path.join( strTgtDir, '*')
              listOfFiles = glob.glob( strPattern )
              for filename in listOfFiles :
                if os.path.isfile(filename) is True:
                  os.unlink( filename ) # delete file

          # If all good, start upload.
          if len( result['error'] ) == 0 :
#            print "All is good. UPLOAD IS OKAY!!!"

            if strAuditOperation == 'Restore Config File' or strAuditOperation == 'Firmware Update' :
              # Erase and re-create ONLY if restoring or firmware update.
              # Let's create the folder. this will erase all other contents in the folder.
#              print "eraseandCreate ->", strTgtDir
              backup.eraseAndCreateDir( strTgtDir )


            strSaveLoc = os.path.join( strTgtDir, strFileName )
#            print "Start Upload: strTgtDir, strFileName-->", strTgtDir, strFileName
            strSaveFile = secure_filename( strFileName )
#            print "Start Upload: strSaveFiole-->", strSaveFile
            strSaveFullPath = os.path.join( strTgtDir, strSaveFile )
#            print "Join: strSaveFullPath-->", strSaveFullPath
#            print "Save is Next..."
            fileHandle.save( strSaveFullPath )
#            print "Start Upload: strSaveLoc, strSaveFile-->", strSaveLoc, strSaveFile
#            print "strSaveFullPath-->", strSaveFullPath

            if request.form['location']  == "restore" :
#              print "Calling Restore System!!!"

              strAuditOperation = 'Restore Config File'
              backupResult = backup.restore_system( strSaveFullPath )
              if backupResult['success'] == True :
                # site_restart_system()
                result['restart'] = "System Configuration Restore"
              else :
                result['error'] = "Failed. Error:{0}".format( backupResult['error'] )

            elif request.form['location'] == "firmware" :
              strAuditOperation = 'Firmware Update'
              result['restart'] = "System Firmware Update"

            elif request.form['location'] == "devices" :
              # resize the image - sizes are stored inside python script
              strAuditOperation = 'Upload Device Image'
              if os.name != "nt":  # We are NOT on the PC.
                subprocess.call( [ "/usr/bin/python","imageResizer",strSaveLoc ])
              else :
                # What do we do on the pc???
                strShell = "python imageResizer {0}".format( strSaveLoc )
                backup._executeShell(strShell, "")

            elif request.form['location'] == "devices1" :
              # resize the image - sizes are stored inside python script
              strAuditOperation = 'Upload Customer Image'
              if os.name != "nt":  # We are NOT on the PC.
                subprocess.call( [ "/usr/bin/python","imageResizer",strSaveLoc ])
              else :
                # What do we do on the pc???
                strShell = "python imageResizer {0}".format( strSaveLoc )
                backup._executeShell(strShell, "")

        # If still no error, update the audit trail
        if len( result['error'] ) > 0 :
          strAudit = '{0} FAILED - {1} {2} {3}'.format( getSessionUsername( session ), strAuditOperation, result['error'], strFileName)
          result['sucess'] = False
        else :
          strAudit = '{0} SUCCESS - {1} {2}.'.format( getSessionUsername( session ), strAuditOperation, strFileName )
          result['sucess'] = True


        auditTrail.AuditTrailAddEntry( strAudit )

        if len( result['restart'] ) > 0 :
          time.sleep( 10 ) # Sleep 10 seconds to make sure the files are uploaded and restored properly before the restart.
          if result['success'] == True:
            # clear out the LEO alarm log and reboot
            self.gLeonardo.directory.getAlarmManager().setAlarmDatabaseToFactorySettings()  # Clear out LEO alarms
          self.gLeonardo.directory.getSystemObject().restartSystem( result['restart'] )

    return result
