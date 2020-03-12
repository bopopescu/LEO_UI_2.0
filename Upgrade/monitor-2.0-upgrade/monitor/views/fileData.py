from flask_restful import Resource
from flask import session, jsonify, request, flash, url_for, redirect, send_file, current_app as app
from backup import backup_system, createDownloadFileInfo, createDebugLog
from slugify import slugify
import os
import auditTrail
import StringIO

import leoObject
import authentication
from LeoFlaskUtils import getSessionUsername

# This class handles POST events related to file operations
class fileData(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "POST fileData ", self.gLeonardo

      if request.form['reqType'] == 'BackupRequest' :
        if 'can_access_files' in session :
          if session['can_access_files'] == True :
            result = backup_system()
            # Make sure there are not any invalid characters in the filename. (done by slugify)
            backupFileName = request.form['backuprequest']
            strDownloadFileName = slugify( backupFileName ) + ".zip"
            # print strDownloadFileName
  #          print "Downloading: ", result['filename'], "Rename: ", strDownloadFileName

            strAudit = '{0} Successfully Backed Up System - {1}'.format( getSessionUsername( session ), strDownloadFileName )
            auditTrail.AuditTrailAddEntry( strAudit )

            return( send_file(result['filename'], mimetype='application/octet-stream', as_attachment=True, attachment_filename=strDownloadFileName ) )

          else :
            return( 'You are not authorized to access this page' )
        else :
          return( 'You are not authorized to access this page' )

      # The Restore capability is handled in uploadcheck.py - since it is handled through file upload.


      elif request.form['reqType'] == 'DebugReport' :
        result = createDebugLog()

        # Make sure there are not any invalid characters in the filename. (done by slugify)
        debugReportFileName = request.form['DebugLogDownload']
        strDownloadFileName = slugify( debugReportFileName ) + ".zip"
#        print "Downloading: ", result['filename'], "Rename: ", strDownloadFileName
        return( send_file(result['filename'], mimetype='application/octet-stream', as_attachment=True, attachment_filename=strDownloadFileName ) )

      elif request.form['reqType'] == 'DevDownloadLog' or request.form['reqType'] == 'LeoFileDownload' or request.form['reqType'] == 'FileDownload' :

        if request.form['reqType'] == 'DevDownloadLog' : # filename located in log folder
          # filename only - located in log folder. Create full path
          strDownloadFilePath = request.form['file']
          strMorePath = "log"

        elif request.form['reqType'] == 'LeoFileDownload' : # filename relative to app.root_path
          # Filename path passed in should be relative to app.root_path. Create full path.
          strDownloadFilePath = os.path.join( app.root_path, request.form['file'] )
          strMorePath = ""

        elif request.form['reqType'] == 'FileDownload' : # any full qualified path
          strDownloadFilePath = request.form['file']
          strMorePath = ""

        result = createDownloadFileInfo( strDownloadFilePath, strMorePath ) # create full pathname
        if result['error'] == False :
          strDownloadFileName = os.path.basename( result['filename'] )
#          print "DownloadFileName ->", strDownloadFileName
          return( send_file(result['filename'], mimetype='application/octet-stream', as_attachment=True, attachment_filename=strDownloadFileName ) )
        else :
#          print "Download Error" +  result['strError']
          return result['strError']

      elif request.form['reqType'] == 'CSVPost' :
        # User is requesting a CSV file download

        # The request.form['csvrequest'] is a unicode string. Convert it to a dict using eval()
        dictCsvRequest = eval( request.form['csvrequest'] )
        #
        strDownloadFileName = '{0}.csv'.format( dictCsvRequest['file'] )
        id = dictCsvRequest['id']
#        strDebug = 'Parameters = {0}, strDownloadFileName = {1}, ID = {2}'.format( params, strDownloadFileName, id)
#        print strDebug
        result = self.gLeonardo.directory.getLoggingManager().getLogFinish(id)
#        strDebug = 'Result = {0}'.format( result )
#        print strDebug
#        print result

        if result['id'] != 'id Error':
#          print "DownloadFileName ->", strDownloadFileName
          strIO = StringIO.StringIO()
          strIO.write( str(result['logs']) )
          strIO.seek(0)
          return( send_file(strIO, attachment_filename=strDownloadFileName, mimetype='application/octet-stream', as_attachment=True,  ) )
        else :
#          print "CSV Download Error - " +  result['strError']
          return result['strError']

