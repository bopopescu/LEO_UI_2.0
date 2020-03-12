#! /usr/bin/python

import sys
import time
import os
import signal
import gc
import version
import subprocess
import LeoFlaskUtils
import json

# utils will be accessible by everyone
sys.path.insert(1, os.path.join(sys.path[0], 'utils'))
# networks are needed for network plugins
sys.path.insert(1, os.path.join(sys.path[0], 'system'))
# networks are needed for network plugins
sys.path.insert(1, os.path.join(sys.path[0], 'system/networks'))
# devices are needed for device plugins
sys.path.insert(1, os.path.join(sys.path[0], 'system/devices'))

import logsystem
log = logsystem.getLogger()

import objectDirectory
import systemObject
import networkManager
import deviceManager
import loggingManager
import alarmManager
import dbUtils
import auditTrail
import elapsedTimer
import threading
import datetime
from stat import *
import networkConstants
import systemConstants
import authentication

BROWSER_WATCHDOG_TIMEOUT_SECS = 90 # If backend does not hear from the browser for 90 seconds, reboot LEO system

gLeonardo = None

def getLeoObject():
    global gLeonardo
    return gLeonardo

def setLeoObject( leoObject ):
    global gLeonardo
    gLeonardo = leoObject
    return False


class Leonardo:
  def __init__(self):
    global gLeonardo
    gLeonardo = self
    self.stopMainLoop = False
#    signal.signal(signal.SIGINT, self.signalTermHandler)

    self.directory = None
    self.jsonInterface = None

    self.systemObject = None
    self.alarmManager = None
    self.loggingManager = None
    self.cleanoutActive = False
    self.factoryResetType = 0

    # We don't want this to be the long term solution. A stop gap until we determine why LEO hangs without rebooting...
    self.dailyRebootEvent = elapsedTimer.DailyEvent(datetime.time(23,0,0)) # Restart system every day at 11:00 PM Local Time

    # Timer to detect when the browser goes down to force a reset.
    self.browserWatchdogTimer = elapsedTimer.Interval( BROWSER_WATCHDOG_TIMEOUT_SECS )
    self.browserWatchdogTimer.reset()

    # Set the thread name to Leonoardo for easy identification by the watchdog.
    # print "Renamed Thread - from:{0} to:{1}".format(threading.currentThread().getName(), "LeoThread")
    threading.currentThread().setName("LeoThread")

    # Register this thread to be watched by the Watchdog - Dynamic watchdog TODO Future
    # RegisterThread( "LeoThread" )

  def signalTermHandler(self, signal, frame):
    log.info("Signal caught")
    self.stopMainLoop = True

  def initializeDirectory(self):
    # create the object directory
    self.directory = objectDirectory.ObjectDirectory()

    # create and add the system object
    self.systemObject = systemObject.SystemObject(self.directory)
    self.directory.setSystemObject(self.systemObject)

  def initializeObjects(self):

#    strDebug = "initializeObject START. self.alarmManager:{0}".format( self.alarmManager )
#    log.debug( strDebug )

    # create and add the network manager
    self.directory.setNetworkManager(networkManager.NetworkManager(self.directory))

    # create and add the device manager
    self.directory.setDeviceManager(deviceManager.DeviceManager(self.directory))

    # alarm and logging managers
    self.alarmManager = alarmManager.AlarmManager(self.directory)
    self.directory.setAlarmManager(self.alarmManager)
    self.loggingManager = loggingManager.LoggingManager(self.directory)
    self.directory.setLoggingManager(self.loggingManager)

    # Once subsystems are "instantiated", initialize as required.
    # This is needed because because the some subsystems need to "re-init" after the networks, devices and logging manager are instantiated...
    self.directory.getDeviceManager().afterInitializeObjectsInit()
    self.alarmManager.afterInitializeObjectsInit()

    #strDebug = "initializeObject COMPLETED. self.alarmManager:{0}".format( self.alarmManager )
    #log.debug( strDebug )

  def startNetworks(self):
    self.browserWatchdogTimer.reset()   # Reset the browser watchdog again - in case it took a while to initialize.
    # start the networks
    keys = self.directory.getNetworkObjectKeys()
    for key in keys:
      network = self.directory.getNetworkObject(key)
      if network is not None:
        network.start()

  def stopNetworks(self):
    log.info("Closing Networks")
    keys = self.directory.getNetworkObjectKeys()
    for key in keys:
      network = self.directory.getNetworkObject(key)
      if network is not None:
        network.stop()

# This method is called about once a second.
  def executeDevices(self):

    keys = self.directory.getDeviceObjectKeys()
#    strDebug = "executeDevices. Devs={0}".format ( len(keys) )
#    log.debug( strDebug )
    for key in keys:
      device = self.directory.getDeviceObject(key)
      # this will execute the virtual device
      if device is not None:
        if device.isVirtualDevice():
          device.executeVirtualDevice()
        else: # this will execute the networked device
          # get the next network transaction
          networkTrans = device.getNetworkTransactions()
          # if there are transactions
          if networkTrans is not None:
            for trans in networkTrans:
              # find id of the network object
              networkObject = self.directory.getNetworkObject(trans.network)
              # if not, set offline to false and inform the device
              if networkObject is None:
                trans.online = False
                trans.message = "Network " + trans.network + " does not exist."
                device.putNetworkTransaction(trans)
                break
              # otherwise, send the message to the network
              else:
                networkObject.putNetworkTransaction(trans)


  def executeNetworks(self):

    keys = self.directory.getNetworkObjectKeys()
#    strDebug = "executeNetworks. Nets={0}".format ( len(keys) )
#    log.debug( strDebug )
    for key in keys:
      # for each network
      networkObject = self.directory.getNetworkObject(key)
      if networkObject is not None:
        while True:
          # get all the transactions from the network
          networkTrans = networkObject.getCompletedNetworkTransaction()
          # when we are out of transactions, go to the next network
          if networkTrans is None:
            break
          else:
            # set the network transaction to the device
            device = self.directory.getDeviceObject(networkTrans.name)
            if device is not None:
              device.putNetworkTransaction(networkTrans)

  def setFactoryResetType(self, resetType) :
    self.factoryResetType = resetType
    
  def LEOexecute(self, argc, argv):

    strStartup = "***** Leonardo Startup (ver {0}) *****".format( version.versionInfo['LeoVersionNumber'] )
    log.info( strStartup )

    # Make sure all the databases are up to the version for each database.
    dbUtils.upgradeDatabasesCheck()
    abc = []
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select * from devices")
    for loggingInfo in cur.fetchall():
      abc.append( loggingInfo["name"] )
    systemConstants.OLD_DEVICES = abc
   # log.debug(systemConstants.OLD_DEVICES)
    if not systemObject.initializeRTC():
      log.critical("No realtime clock detected.  Aborting.")
    else:
      try:
        strShutdown = 'Restart Due To Exit of leoObject Loop'

        auditTrail.initAuditTrail() # Need to do after RTC init for timezone adjustment
        strStartup = "System Startup - Version: {0}".format( version.versionInfo )
        auditTrail.AuditTrailAddEntry( strStartup )

        self.initializeDirectory()
#        debugBuf = "execute: systemObject:{0}".format( self.systemObject )
#        print debugBuf
#        log.info( debugBuf )

        # Update the ethernet settings in LEO if necessary.
        if os.name != 'nt':
          # Let's make sure the ethernet settings in the database match what is in the OS.
          dbEthernetDict = self.systemObject.getEthernetSettings()   # From database
          dbOrigEthernetDict = dbEthernetDict.copy()
          osIPInfo = LeoFlaskUtils.getNetworkStackIPInfo()    # From OS
          blUpdate = False
          if dbEthernetDict['dhcp'] == 0 :
            if osIPInfo['IP_ADDR'] != dbEthernetDict['address'] :
              dbEthernetDict['address'] = osIPInfo['IP_ADDR']
              blUpdate = True
            if osIPInfo['IP_MASK'] != dbEthernetDict['netmask'] :
              dbEthernetDict['netmask'] = osIPInfo['IP_MASK']
              blUpdate = True
            if osIPInfo['IP_GATEWAY'] != dbEthernetDict['gateway'] :
              dbEthernetDict['gateway'] = osIPInfo['IP_GATEWAY']
              blUpdate = True
            if osIPInfo['DNS_ADDRESS'] != dbEthernetDict['dnsaddress'] :
              dbEthernetDict['dnsaddress'] = osIPInfo['DNS_ADDRESS']
              blUpdate = True
          if blUpdate is True:
            self.systemObject.setEthernetSettings( dbEthernetDict )
            strBuf = "UPDATED Ethernet Settings. os:{}, Origdb:{}".format(json.dumps(osIPInfo), json.dumps(dbOrigEthernetDict))
            log.info(strBuf)
          else :
            strBuf = "Ethernet Settings. os:{}".format(json.dumps(osIPInfo))
            log.info(strBuf)

        while not self.stopMainLoop:

          self.initializeObjects()
          self.startNetworks()

          # At this time, all directories and objects should be created. We can start the browser.
          if os.name != 'nt':
            # print "Creating LeoReady"
            with open("/home/linaro/LeoReady", 'a') as csvfile:
              os.utime("/home/linaro/LeoReady", None)

          while not self.systemObject.mustReinitialize() and not self.stopMainLoop:

            # TODO: prior to this, set the connected inputs
            # print "!!! Start LEO Execute Loop {0}".format(datetime.datetime.utcnow() )

            # If the factory reset is NOT active, do normal processing
            if self.factoryResetType == 0 :
              # print "SysObj Exe {0}".format(datetime.datetime.utcnow() )
              self.systemObject.execute()
              # print "AlmMgr Exe {0}".format(datetime.datetime.utcnow() )
              self.alarmManager.execute()
              # print "LogMgr Exe {0}".format(datetime.datetime.utcnow() )
              self.loggingManager.execute()
              # print "Device Exe {0}".format(datetime.datetime.utcnow() )
              self.executeDevices()
              # print "Netwrk Exe {0}".format(datetime.datetime.utcnow() )
              self.executeNetworks()
              # We only care about the network objects threads being alive. LeoThread (which is this current thread) is
              # being montitored by the back-end watchdog thread in a completely external/separate process (not part of leo app)
              # Loop through all network names and make sure the associated task is alive.
              keys = self.directory.getNetworkObjectKeys()

              # We only have to do this if there are networks defined. And we put it in this if case becuase
              # the thread can be deleted which would cause a reset during the cleanout.
              if len(keys) > 0:
                # We want to do a quick check to make sure the network object threads are all running properly
                listOfThreads = threading.enumerate()
                aliveThreadNameList = []  # Will keep the name of threads that are alive
                # Create list of alive threads
                for thrd in listOfThreads:
                  if thrd.isAlive() is True:
                    aliveThreadNameList.append(thrd.getName())
  
                for key in keys:
                  # key should be the name of the thread
                  if key not in aliveThreadNameList:
                    # Need to shutdown and reboot.
                    strShutdown = "echo {0} - Rebooting Due to Missing {1} process in {2} >> /opt/monitor/log/LeoProcReboots.log".format(
                      time.strftime("%c"), key, aliveThreadNameList)
                    log.debug(strShutdown)
                    # print strShutdown
                    # We are going to stop this loop, close things out and kick the box to reset - e.g. restartSystem
                    self.stopMainLoop = True

              # print "Start Browser Wdog {0}".format(datetime.datetime.utcnow() )
              ####### DEBUG ONLY TO DISABLE SOFTWARE WATCHDOG ######
              enableWatchdog = 1
              if enableWatchdog > 0 :
                # This is the Browser Watchdog. It will make sure that the browser didn't crash.
                # Will get "pet" by getSiteStatus (which updates web page header)
                browserTimeLeft = self.browserWatchdogTimer.getTimeRemainingSecs()
                if browserTimeLeft < 20 :
                  if os.name != "nt" : # Only show this on LEO HW
                    # print "WARNING: getSiteStatus: Browser WDog Time Remaining -->", self.browserWatchdogTimer.getTimeRemainingSecs()
  
                    # We have not heard from the browser for too long. Reset the system
                    if browserTimeLeft == 0:
                      browserDownRebootPlease = 1
                      if browserDownRebootPlease > 0 :
                        strShutdown = "Browser is down. Shutting Down"
                        # We are going to stop this loop, close things out and kick the box to reset - e.g. restartSystem
                        self.stopMainLoop = True
                      else:
                        strShutdown = "Browser is down, but temporarily NOT shutting down for debug purposes..."
                        self.browserWatchdogTimer.reset()  # For testing, simply reset the watchdog timer so we don't always log.
                      log.debug(strShutdown)
                      # print strShutdown
              else :
                # We are on the PC. Just reset the timer.
                self.browserWatchdogTimer.reset()

            else :
              # Factory reset is needed...
              # This must be executed in the mainThread because when we tried to execute this from the SOAP interface,
              # it would take too long and NGINX would auto-reset the leoThread.
              self.executeFactoryReset(self.factoryResetType)
            
            # print "LEO Sleep  {0}".format(datetime.datetime.utcnow() )
            time.sleep(1)
            #  print "LEO Wakeup {0}".format(datetime.datetime.utcnow() )

            # if self.dailyRebootEvent.hasElapsed():
              # strShutdown = "System Check"
              # log.info("System Check.")
              # self.stopMainLoop = True # Stop the main loop so that we will reboot.

          self.stopNetworks()
          self.loggingManager.stop()
          self.directory.resetDirectory()

        log.info("Shutting Down System.")

        logsystem.shutdown()

        # If we hit here, we need to restart the system.
        self.systemObject.restartSystem( strShutdown )

      except Exception, e:
        strExcept = "Exception in leoObject loop: {0}".format(e)
        log.exception(strExcept)

      return -1

  def executeFactoryReset(self, factoryResetType ) :
 
    almMgrObj = self.directory.getAlarmManager()
    almMgrObj.strTestEmailMsg = "Begin Resetting To Factory Defaults..."
    strAudit = 'Received Request To Reset Device To Factory Defaults.'
    auditTrail.AuditTrailAddEntry(strAudit)
  
    # Remove devices
    almMgrObj.strTestEmailMsg = "Resetting To Factory Defaults: Removing Devices..."
    log.info(almMgrObj.strTestEmailMsg)
    self.directory.getDeviceManager().setDeviceDatabaseToFactorySettings()  # Clear out device database information
  
    # Clean out E2 database
    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Removing Networks..."
    log.info(almMgrObj.strTestEmailMsg)
    networkDict = self.directory.getNetworkManager().getNetworks()
    if networkDict is not None:
      # Since orderedDict, netrec will only be key into NetworkDict.
      for netrec in networkDict:
        if networkDict[netrec]['typeName'].find(networkConstants.networkE2NetText) == 0:
          E2NetObject = self.directory.getDeviceManager().getNetworkObjectByName(networkDict[netrec]['name'])
          E2NetObject.suspendTransactions()  # Suspend transactions so that we don't update the database anymore.
          E2NetObject.setE2SettingsToFactorySettings()  # Clear alarm tables

    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Removing Logs..."
    log.info(almMgrObj.strTestEmailMsg)
    self.directory.getLoggingManager().setLogDatabaseToFactorySettings()  # Clear out logging database

    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: System Settings..."
    log.info(almMgrObj.strTestEmailMsg)
    authentication.setAuthDatabaseToFactorySettings()  # Clear login usernames and passwords
    self.directory.getSystemObject().setSystemDatabaseToFactorySettings(factoryResetType)
  
    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Removing Email Records..."
    log.info(almMgrObj.strTestEmailMsg)
    almMgrObj.setEmailDatabaseToFactorySettings()  # Clear out email transaction log
    almMgrObj.strTestEmailMsg = "Please Wait. Resetting To Factory Defaults: Removing Alarm Records..."
    log.info(almMgrObj.strTestEmailMsg)
    almMgrObj.setAlarmDatabaseToFactorySettings()  # Clear out LEO alarms

    # Wait a few seconds to make sure that everything is written to disk properly.
    almMgrObj.strTestEmailMsg = "Please Wait. Final Writes: Resetting Controller in 15 seconds..."
    log.info(almMgrObj.strTestEmailMsg)
    time.sleep(15)
    self.directory.getSystemObject().restartSystem('Resetting To Factory Defaults Restarting')  # Restart the system

