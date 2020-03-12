#! /usr/bin/python

import sys
import time
import os
import subprocess
import logging
import logging.handlers

# Create our own logging system for the LEO watchdog.

# create logger
_logger = logging.getLogger('LEOwatchdog')
_logger.setLevel(logging.DEBUG)

# We need to make sure the log folder actually exists.
# create file handler which logs even debug messages
strLeoLogPath = '{0}/log'.format( sys.path[0] )

if os.path.exists( strLeoLogPath ) == False:
  oldUmask = os.umask( 0 )
  os.mkdir( strLeoLogPath, 0777 )
  os.umask( oldUmask )

strLeoLogFile = "{0}/LEOWatchdog.log".format( strLeoLogPath )
_fileHandler = logging.handlers.RotatingFileHandler(strLeoLogFile, maxBytes=300000, backupCount=1)
_fileHandler.setLevel(logging.NOTSET)

# create console handler with a higher log level
_consoleHandler = logging.StreamHandler()
_consoleHandler.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
# logging.basicConfig(format="%(threadName)s:%(message)s")
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(threadName)s:%(filename)s:%(funcName)s:%(lineno)d %(message)s')
# formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d %(message)s')
_fileHandler.setFormatter(_formatter)
_consoleHandler.setFormatter(_formatter)

# add the handlers to the logger
_logger.addHandler(_fileHandler)
_logger.addHandler(_consoleHandler)

def getLEOWdogLogger():
  return _logger

def LEOWdogLoggerShutdown():
  logging.shutdown()


# The purpose of this process is simply to find the leo_ui process and make sure it is functioning properly.
# This process will be named BEWatchdog.
# The leo_ui process is basically the LeoThread. The LeoThread also has a watchdog that makes sure
# that the "Network Object" threads do not crash.
# If it the process is not present, this watchdog process will restart the system.
def LeoProcWatchdog():

    # this gets started pretty early. Give the system three minutes to start up.
    # print "Starting LeoProcWatchdog"
    time.sleep( 60 )

    # initialize LEO Watchdog logger
    log = getLEOWdogLogger()
    log.info( "Watchdog Started")

    # Now we will write the the watchdog device driver to activate it.
    # The way the watchdog works, by default - the watchdog is set to reboot the system in 1 minute if it does not get written to
    # within that time period. So we plan to write to the watchdog about 6 times a minute (e.g. every 9 seconds or so)
    # Here we open the device driver and within the watchdog loop, we write to the watchdog as long as we are running AND all
    # of the LEO processes are active.
    wDogFile = open('/dev/watchdog','w')
    wDogFile.write('j')
    wDogFile.flush() # Make sure it is not buffered.

    while 1 :

      # We are actually looking to make sure that the "primary" guinicorn launched leo_ui process is present.
      # There are two processes for gunicorn and they are differentiated by S and S1
      # Process "S "  = gunicorn bridge between NGINX and leo_ui:app
      # Process "S1"  = gunicorn initiated "core" python leo_ui:app. When S1 dies, gunicorn restarts it; so we won't
      # watchdog this process. We will only watchdog the gunicorn primary/bridge process "S "
      # This is because gunicorn will restart the python program (S1) if it exits unexpectedly.
#      strPSret = subprocess.check_output( 'ps ax | grep "leo_ui"', shell=True )
      strPSret = subprocess.check_output( 'ps -fC gunicorn | wc -l', shell=True )
      iNumLeoProcesses = int( strPSret )
      # print strPSret
      # log.info( strPSret )


      # If this one process is not running, we need to log and reboot the system.
      # We look for less than 2 because there will be three lines from the command:
      # 1) actual gunicorn process 2) the "subprocess" and 3) "grep wc -l". So we will need to make sure the line
      # count is at least 2 entries.
      if iNumLeoProcesses < 2 :
        strRebootInfo = "Rebooting Due to Missing primary gunicorn process. Num Processes:{0}".format( iNumLeoProcesses )
        log.info( strRebootInfo )
        # wait a few seconds to make sure the write gets saved.
        time.sleep(3)
        # Now, Reset the entire system
        ss = subprocess.Popen('shutdown -r now', shell=True)
        time.sleep(15) # Should not get out of here...
        log.info( "Watchdog - We should never see this - unless the system does not reboot...")
      else:
        # Pet the watchdog so he does not reboot the system and check again in a bit.
        wDogFile.write('j')
        wDogFile.flush() # Make sure it is not buffered.
        # The watchdog needs to be pet every minute. So we'll make sure it's written at least 3 times a minute.
        time.sleep( 15 )

LeoProcWatchdog()
