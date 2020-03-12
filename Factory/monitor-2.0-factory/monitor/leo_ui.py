#!/usr/bin/env python
from flask import Flask
from flask_restful import Api
from flask import session, request
import logging
import sys
import os
import time
from datetime import timedelta
import datetime
# utils will be accessible by everyone
sys.path.insert(1, os.path.join(sys.path[0], 'views'))
sys.path.insert(1, os.path.join(sys.path[0], 'system'))

import LeoFlaskUtils

import thread
import threading
import views
import leoObject
import subprocess
import logsystem
import pageAuditTrail
import pageDevices
import auditTrail
import systemInterface

pycharmRemoteDebug = 0  # change to 1 if you want to debug remotely.

# The following is to enable debugging remotely through Pycharm
if os.name != 'nt' and pycharmRemoteDebug > 0 : # if we are NOT running on the PC
  sys.path.append( '/opt/monitor/pycharm-debug.egg')
  #from pydev import pydevd
  import pydevd
  # the IP address below is the PC from which pycharm is running.
  print "Calling pydevd NOW"

  # For HOME
  # pydevd.settrace('192.168.0.30', port=61555, stdoutToServer=True, stderrToServer=True, suspend=False)

  # For OFFICE
  pydevd.settrace('10.1.10.60', port=61555, stdoutToServer=True, stderrToServer=True, suspend=False)

  print "AFTER pydevd Call"
  # end debugging
  
log = logsystem.getLogger()

###########################################
# Threads started from MainThread
###########################################
def LeoThread():
  gLeonardo = leoObject.Leonardo()
#    print "Starting LeoThread, gLeo =", gLeonardo

  leoObject.setLeoObject(gLeonardo)
  gLeonardo.LEOexecute(1, "")     # Does not return

############################################################################################
# Watchdog thread to independently ensure Leonardo backend threads do not unexpectedly exit
############################################################################################
def backEndWatchdog():
#    print "Starting backEndWatchdog"

  # These are the "static" threads we need to check
  # ServerThread (Flask), LeoThread (Leo Core), MainThread (leo_ui.py)
  # For version 1, this is a dynamic one. Need to determine how to check this: E2 Annunciator:Desk E2
  # In the future, we need to add support for dynamic threads (e.g. one for each device)

  # Rename the thread so it is legible
  # print "Renamed Thread - from:{0} to:{1}".format(threading.currentThread().getName(), "BEWatchdog")
  threading.currentThread().setName("BEWatchdog") # BackEnd Watchdog

  while 1 :
    # Sleep and make sure no threads have died.
    time.sleep( 45 )
    threadNamesList = []
    for i in threading.enumerate():
      threadNamesList.append( i.getName() )

    # TODO - Today, these are hard coded thread names, but in the future, this list should be dynamic.
    if "MainThread" in threadNamesList and "LeoThread" in threadNamesList :
      iDummy = 0 # Dummy statement so that we don't have to reverse the above logic...
    else : # Missing thread
      strRestartMessage = "Restart System. A Key Thread is missing[MainThread or LeoThread]. Active Threads:{}".format( threadNamesList )
      print strRestartMessage
      log.debug( strRestartMessage )
      auditTrail.AuditTrailAddEntry( strRestartMessage )
      time.sleep(2) # Make sure it gets written.
      systemInterface.restartSystem()

############################################################
# flaskThread MAIN Starting Point
############################################################

# Start the Leo "core" thread and let it get running before starting Flask.
thread.start_new_thread(LeoThread,() )

# Give the LeoThread some time to initialize properly before activating the web interface.
time.sleep(3)

############################################################
# FLASK INITIALIZATIONS
############################################################

# log.info( "Setting up Flask app and api" )
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

api = Api(app)
app.permanent_session_lifetime = timedelta(seconds=600) # 10 minutes after browser is closed = automated logout. Currently there is no automatic logout remotely - while in the browser.

# function to one-time initialize the session
@app.before_first_request
def before_first_request():
# COMMENT THIS OUT IF YOU DON'T WANT TO CLEAR SESSION DURING DEVELOPMENT
  # print "os.environ-->", os.environ
  if "PYCHARM_HOSTED" in os.environ:
    i = 0 # Here in case you comment out SESSION Clearing lines
    print "DO NOT CLEAR SESSION!!!"
    # LeoFlaskUtils.endSession()
    # LeoFlaskUtils.startSession()
  elif 'init' in session :
    LeoFlaskUtils.endSession()
    LeoFlaskUtils.startSession()

# Before each request, "modify/renew" the session so it does not expire until there is no activity.
@app.before_request
def before_request():
  LeoFlaskUtils.refreshSession( session )

# html returning UI urls.
api.add_resource(views.pageIndex, '/')
api.add_resource(views.pageAlarms, '/pageAlarms')
api.add_resource(views.pageLogin, '/pageLogin')
api.add_resource(views.pageLogout, '/pageLogout')
api.add_resource(views.pageE2alarms, '/pageE2alarms')
api.add_resource(views.pageAuditTrail, '/pageAuditTrail')
api.add_resource(views.pageEmailHistory, '/pageEmailHistory')
api.add_resource(views.pageDevices, '/pageDevices')
api.add_resource(views.pageService, '/pageService')
api.add_resource(views.pageNetworkStatus, '/pageNetworkStatus')
api.add_resource(views.pageSysconfig, '/pageSysconfig')
api.add_resource(views.pageUsers, '/pageUsers')
api.add_resource(views.pageUnits, '/pageUnits')
api.add_resource(views.pageUpload, '/pageUpload')
api.add_resource(views.pageE2status, '/pageE2status')
api.add_resource(views.pageSitemap, '/pageSitemap')
api.add_resource(views.pageAnalysis, '/pageAnalysis')
api.add_resource(views.pageExport, '/pageExport')
api.add_resource(views.pageTestPage, '/pageTestPage')
api.add_resource(views.pageTestStatus, '/pageTestStatus')


# Product Designer library (aka Floorplan)
api.add_resource(views.productdesigner, '/html/productdesigner.html')

# json returning urls
api.add_resource(views.getSiteStatus, '/getSiteStatus')
api.add_resource(views.setSiteInfo, '/setSiteInfo')
api.add_resource(views.setSiteCurrentTime, '/setSiteCurrentTime')

api.add_resource(views.setScreenBrightness, '/setScreenBrightness')
api.add_resource(views.restartSystem, '/restartSystem')
api.add_resource(views.getSystemVersion, '/getSystemVersion')
api.add_resource(views.getSWMVersion, '/getSWMVersion')

api.add_resource(views.getEthernetSettings, '/getEthernetSettings')
api.add_resource(views.setEthernetSettings, '/setEthernetSettings')

api.add_resource(views.getNetworkTypes, '/getNetworkTypes')
api.add_resource(views.getNetworks, '/getNetworks')
api.add_resource(views.setNetworks, '/setNetworks')

api.add_resource(views.getDevices, '/getDevices')
api.add_resource(views.getDeviceAlarms, '/getDeviceAlarms')
api.add_resource(views.getDeviceStatus, '/getDeviceStatus')
api.add_resource(views.getDeviceTypes, '/getDeviceTypes')
api.add_resource(views.getDeviceDataValues, '/getDeviceDataValues')
api.add_resource(views.getDeviceInformation, '/getDeviceInformation')
api.add_resource(views.getDeviceValueDescriptions, '/getDeviceValueDescriptions')
api.add_resource(views.getDeviceConfigValues, '/getDeviceConfigValues')
api.add_resource(views.getDeviceConstantConfigValues, '/getDeviceConstantConfigValues')

api.add_resource(views.setDevices, '/setDevices')
api.add_resource(views.setDeviceConfigValues, '/setDeviceConfigValues')
api.add_resource(views.setDeviceConstantConfigValues, '/setDeviceConstantConfigValues')
api.add_resource(views.setConfigSyncDaily, '/setConfigSyncDaily')
api.add_resource(views.getConfigSyncDaily, '/getConfigSyncDaily')
api.add_resource(views.useExternal, '/useExternal')

api.add_resource(views.performDeviceUserAction, '/performDeviceUserAction')

api.add_resource(views.getEmailSettings, '/getEmailSettings')
api.add_resource(views.setEmailSettings, '/setEmailSettings')

api.add_resource(views.getAlarms, '/getAlarms')
api.add_resource(views.getEnunciatedAlarms, '/getEnunciatedAlarms')
api.add_resource(views.getEnunciatedAlarmFilters, '/getEnunciatedAlarmFilters')
api.add_resource(views.setEnunciatedAlarmFilters, '/setEnunciatedAlarmFilters')
api.add_resource(views.getActiveAlarms, '/getActiveAlarms')
api.add_resource(views.getAlarmHistory, '/getAlarmHistory')
api.add_resource(views.deleteAllAlarms, '/deleteAllAlarms')
api.add_resource(views.getEmailHistoryEntries, '/getEmailHistoryEntries')

api.add_resource(views.getAllLoggedValues, '/getAllLoggedValues')
api.add_resource(views.deleteAllLogs, '/deleteAllLogs')
api.add_resource(views.getLoggedValuesForDevice, '/getLoggedValuesForDevice')
api.add_resource(views.setLoggedValuesForDevice, '/setLoggedValuesForDevice')

api.add_resource(views.getLogStart, '/getLogStart')
api.add_resource(views.getLogProgress, '/getLogProgress')
api.add_resource(views.getLogCancel, '/getLogCancel')
api.add_resource(views.getLogFinish, '/getLogFinish')

api.add_resource(views.getSystemSettings, '/getSystemSettings')
api.add_resource(views.setSystemSettings, '/setSystemSettings')

api.add_resource(views.getDatabaseBackup, '/getDatabaseBackup')
api.add_resource(views.setDatabaseRestore, '/setDatabaseRestore')
api.add_resource(views.uploadcheck, '/uploadcheck')
api.add_resource(views.factoryreset, '/factoryreset')


api.add_resource(views.getMultiDeviceInfo, '/getMultiDeviceInfo')

api.add_resource(views.getE2AllAlarms, '/getE2AllAlarms')
api.add_resource(views.deleteAllE2Alarms, '/deleteAllE2Alarms')
api.add_resource(views.getE2Settings, '/getE2Settings')
api.add_resource(views.setE2Settings, '/setE2Settings')
api.add_resource(views.getE2ControllerNameByIP, '/getE2ControllerNameByIP' )
api.add_resource(views.getE2StatusScreenData, '/getE2StatusScreenData')

api.add_resource(views.getAuditTrailEntries, '/getAuditTrailEntries')
api.add_resource(views.deleteAllAuditTrailEntries, '/deleteAllAuditTrailEntries')
api.add_resource(views.logincheck, '/logincheck')

api.add_resource(views.deleteAllEmailLogEntries, '/deleteAllEmailLogEntries' )

#api.add_resource(views.setManualDefrost, '/setManualDefrost' )

api.add_resource(views.usrData, '/usrData')
api.add_resource(views.fileData, '/fileData')
api.add_resource(views.almData, '/almData')
api.add_resource(views.sendTestEmail, '/sendTestEmail')
api.add_resource(views.actions, '/actions')


app.secret_key = 'IOJWEAli32iu4soi34nsfdac3!'
# app.use_reloader=False    # TODO TEMPORARY

# The following lines remove the logger information for web requests.
# Comment out all three lines to add this back.
wlog = logging.getLogger('werkzeug')
wlog.setLevel(logging.ERROR)
#  wlog.disabled = True

# For debugging and unit testing
#app.run(port=5000, debug=True, host='0.0.0.0', use_reloader=False)
#app.run(port=5000, debug=True, host='127.0.0.1', use_reloader=False)
#app.run(debug=True)
#app.run(debug=False)

# strThreadInfo = 'Flask ThreadName = {0}'.format(threading.current Thread().getName() )
# log.info( strThreadInfo )

# print "Printing all threads before starting Flask"
# for i in threading.enumerate():
#    print "     Thread: ", i.name

# Start the "backend" watchdog to make sure everything keeps running
# This will make sure the KNOWN threads are running and will reset if not.
thread.start_new_thread(backEndWatchdog, ())

log.info( "Starting Web Server" )
app.dictIPInfo = LeoFlaskUtils.getNetworkStackIPInfo()
# app.pycharmRemoteDebug = pycharmRemoteDebug   # Set this so we can do conditional code based upon debugging

# For remote web server.
if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=False)
