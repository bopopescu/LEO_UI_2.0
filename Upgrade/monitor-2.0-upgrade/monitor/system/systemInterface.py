#! /usr/bin/python

import os
import sys
import datetime
import time
import glob
import socket
import struct
import subprocess
import threading

import LeoFlaskUtils


import logsystem
log = logsystem.getLogger()

timeZoneList = {}
timeZoneList["America/New_York"] = "US Eastern"
timeZoneList["America/Los_Angeles"] = "US Pacific"
timeZoneList["America/North_Dakota/Center"] = "US Central"
timeZoneList["America/Phoenix"] = "US Mountain Without DST"
timeZoneList["America/Ojinaga"] = "US Mountain"
timeZoneList["America/Regina"] = "US Central Without DST"
timeZoneList["America/Atikokan"] = "US Eastern Without DST"
timeZoneList["America/Puerto_Rico"] = "Atlantic Time Without DST"
timeZoneList["America/Moncton"] = "Atlantic Time"
timeZoneList["America/St_Johns"] = "Newfoundland Time"
timeZoneList["America/Sitka"] = "Alaska Time"
timeZoneList["America/Adak"] = "Hawaii Time"
timeZoneList["Pacific/Kiritimati"] = "Hawaii Time without DST"


# backlight settings - read from various files from the drivers.
backlightMaxbrightness = 192          # Will read from device
backlightName = ""                  # Can change between HW platforms.

try:
  if os.name != "nt":  # We are NOT on the PC.
    with open('/proc/cpuinfo', 'r') as f:
      lines = f.readlines()
      for line in lines:
        if line.find('Processor') == 0:
          if line.find('ARMv7') > -1:
            # Get Backlight information
            backlightPath = str( glob.glob( '/sys/class/backlight/*' ) )
            # This if test is due to a variant in hardware where the ver2 hardware has 2 backlight "instances".
            if len( backlightPath ) > 1 :
              # For this new hardware, backlight.0 is the one that controls the backlight.
              backlightPath = glob.glob( '/sys/class/backlight/*' )
              lastSlashLoc = backlightPath[0].rfind('/')
              backlightName = backlightPath[0][lastSlashLoc+1:]
            else:
              lastSlashLoc = backlightPath.rfind('/')
              lastQuoteLoc = backlightPath.rfind("'")
              backlightName = backlightPath[lastSlashLoc+1:lastQuoteLoc]
            strMaxBrightName = '/sys/class/backlight/{0}/max_brightness'.format( backlightName )
  
            try:
              with open(strMaxBrightName, 'r') as f:
                strMaxBrightness = f.readline().replace('\n','')
              iBacklightMaxBrightness = strMaxBrightName
    #        print "Backlight Name = ", backlightName, " Max Brightness = ", iBacklightMaxBrightness
            except Exception, e:
              log.debug("Error Reading backlight: " + str(e))
            break
    os.system('hwclock -s -f /dev/rtc0') # Chipsee only has one RTC
except Exception, e:
  log.debug("Could not open /proc/cpuinfo: " + str(e))


def initializeRTC(timeout):
  if os.name != "nt":  # We are NOT on the PC.
    count = 0
    while not os.path.exists('/dev/rtc0'):
      time.sleep(1)
      count = count + 1
      if count > timeout:
        log.debug('Could not find /dev/rtc0')
        return False
    time.sleep(2)
    try:
      os.system('hwclock -s -f /dev/rtc0') # Chipsee only has one RTC
    except Exception, e:
      log.debug("Error init system clock: " + str(e))

  return True

# Sets the time based. Must be sent in UTC and in the 8601 date format: YYYY-MM-DD HH:MM:SS
def setSystemTime(strNewUTCDate):
  #
  dtNewUTCDate = datetime.datetime.strptime(strNewUTCDate, '%Y-%m-%d %H:%M:%S')
  dateString = "%02d%02d%02d%02d%04d" % (dtNewUTCDate.month, dtNewUTCDate.day, dtNewUTCDate.hour, dtNewUTCDate.minute, dtNewUTCDate.year)
  log.debug( "dtNewUTCDate:{}, dateString:{}".format( dtNewUTCDate, dateString))

  if os.name != "nt":  # We are NOT on the PC.
    log.debug('Setting cpu and /dev/rtc0')
    try:
      log.info( "New Linux system time = {}, {}".format( dtNewUTCDate, dateString ) )
      os.system('date -u ' + dateString)
      os.system('hwclock -w -f /dev/rtc0')
    except Exception, e:
      log.debug("Error set system time: " + str(e))


def setSystemTimeZone(tz):
    if tz in timeZoneList.keys():
      try:
        if os.name != 'nt':
          with open('/etc/timezone', 'w') as f:
            f.write(tz + '\n')

          try:
            os.system('dpkg-reconfigure -f noninteractive tzdata')
            log.info('Setting timezone to ' + tz)
          except Exception, e:
            log.debug("Error setting time zone: " + str(e))
      except Exception, e:
        log.debug("Error opening /etc/timezone: " + str(e))

def getSystemTimeZone():
  try:
    if os.name != 'nt':
      with open('/etc/timezone', 'r') as f:
        retval = f.readline().replace('\n','')
    else:
      retval = "America/New_York" # If on the PC, just default to eastern time zone.
      
    return retval
  except Exception, e:
    log.debug("Error opening /etc/timezone: " + str(e))
    return None

def getSystemTimeZoneList():
  return timeZoneList


# This function will return the version information for the OS / low lever system version
def getOsInfo():

  dictVersion = { 'osName': os.name }

  if os.name != "nt":  # We are NOT on the PC.
    dictVersion['uname'] = os.uname()

  else: # PC does not have uname, use ver
    strShell = "ver"
    dictVersion['uname'] = subprocess.check_output( strShell, shell=True )
  return dictVersion

# This function will currently return the verison information for the python installed modules
# and the apt installed modules
def getSoftwareModulesVersion( strSelect ):
  result = {}

  if len( strSelect ) == 0 :
    strSelect = "PIP"

  if strSelect == "PIP" :
    strShell = "pip freeze"
    result['pip'] = subprocess.check_output( strShell, shell=True )
    # print "PIP Freeze RESULTS", result

  elif strSelect == "APT" :
    if os.name != "nt":  # We are NOT on the PC.
      strShell = "dpkg -l"
      result['apt'] = subprocess.check_output( strShell, shell=True )
#      print "APT RESULTS", result
    else :
      result['apt'] = "None. On PC"

  elif strSelect == "LEOSW" :
    if os.name != "nt":  # We are NOT on the PC.
      strShell = "ls -lR {0}".format( sys.path[0] )
      # print "Leo SW RESULTS", result
    else :
      strShell = "dir /s {0}".format( os.path.normpath( sys.path[0] ) )
    result['leosw'] = subprocess.check_output( strShell, shell=True )
    # print "Leo SW RESULTS", result

  return result

def setHostName(hostname):
  if os.name != "nt":  # We are NOT on the PC.
    # log.info('Setting hostname to ' + str(hostname))

    try:
      with open('/etc/hostname', 'w') as f:
        f.write(hostname + '\n')

      with open('/etc/hosts', 'w') as f:
        f.write('127.0.0.1       localhost\n')
        f.write('127.0.1.1       ' + hostname + '\n')

    except Exception, e:
      log.debug("Error opening /etc/hostname: " + str(e))


# This function updates the OS file with the proper Ethernet information (etc/network/interfaces
def writeConfigFileEthernetSettings(dhcp, address, netmask, network, gateway, dnsaddress ):
  if os.name != "nt":  # We are NOT on the PC.
    # We will only change the eth0 and loopback settings. Need to create another function to manage the WLAN
    try:
      log.info('Setting ethernet settings.  Check /etc/network/interfaces. DHCP=' + str(dhcp))
      with open('/etc/network/interfaces', 'w') as f:
        f.write('# The loopback network interface\n')
        f.write('auto lo\n')
        f.write('iface lo inet loopback\n')
        f.write('\n')
        f.write('# The primary network interface\n')
        f.write('auto eth0\n')
        if dhcp:
          f.write('iface eth0 inet dhcp\n')
        else:
          f.write('iface eth0 inet static\n')
          f.write('    address ' + address + '\n')
          f.write('    netmask ' + netmask + '\n')
          f.write('    gateway ' + gateway + '\n')
  #          f.write('    broadcast ' + gateway + '\n')   # Ubuntu wants this, but not sure if it's really required
          if len( dnsaddress ) == 0 :       # if dnsaddress is not set, set it to the gateway address.
            dnsaddress = gateway
          f.write('    dns-nameservers ' + dnsaddress + '\n')

        f.write('\n')
    except Exception, e:
      log.debug("Error opening /etc/network/interfaces: " + str(e))
    
# This method is for reading the Ethernet CONFIGURATION from an OS based file. (e.g. /etc/network/interfaces )
def readConfigFileEthernetSettings():
  blInterfaceFound = False
 
  if os.name != "nt":  # We are NOT on the PC.
    # We will only change the eth0 and loopback settings. Need to create another function to manage the WLAN
    try:
      log.info('Reading OS ethernet settings from /etc/network/interfaces.')
      with open('/etc/network/interfaces', 'r') as f:
        strInterfacesFile = f.read()
        # The line we are looking for is iface eth0 inet [static|dhcp] to determine if statis or dynamic.
        ifaceLoc = strInterfacesFile.find("iface eth0 inet ")
        blInterfaceFound = False
        if ifaceLoc >= 0:
          eth0NetParams = strInterfacesFile.split(" ")
          # Let's find dhcp or statis.
          if 'inet' in eth0NetParams :
            strDhcpOrStatic = eth0NetParams[ eth0NetParams.index('inet') + 1 ]
            if strDhcpOrStatic == "static" :
              dictHwIPInfo = {}
              if 'address' in eth0NetParams:
                dictHwIPInfo['IP_ADDR'] = eth0NetParams[eth0NetParams.index('address') + 1]
              if 'netmask' in eth0NetParams:
                dictHwIPInfo['IP_MASK'] = eth0NetParams[eth0NetParams.index('netmask') + 1]
              if 'gateway' in eth0NetParams:
                dictHwIPInfo['IP_GATEWAY'] = eth0NetParams[eth0NetParams.index('gateway') + 1]
              if 'dns-nameservers' in eth0NetParams:
                dictHwIPInfo['DNS_ADDRESS'] = eth0NetParams[eth0NetParams.index('dns-nameservers') + 1]
              blInterfaceFound = True
            
    except Exception, e:
      log.debug("Error opening /etc/network/interfaces: " + str(e))
      
  if blInterfaceFound is False :
    dictHwIPInfo =  LeoFlaskUtils.getNetworkStackIPInfo()

  return dictHwIPInfo


def getHwAddr(ifname):
  if os.name != 'nt':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])
  else:
    return ("Running PC SIM")

def setScreenBrightness(percent):
  if os.name != "nt":  # We are NOT on the PC.
    try:
      # The screen brightness is from 0 - 248. Convert percent to proper value.
      percent = ( percent * backlightMaxbrightness) / 100
      percent = int(percent)
      strCmd = 'echo {0} > /sys/class/backlight/{1}/brightness'.format( str(percent), backlightName )
  #    print "setScreenBrightness: strCmd ->", strCmd
      os.system( strCmd )
    except Exception, e:
      log.debug("*** Error Setting backlight: " + str(e))
      blAudioPresent = False

#def recalibrateScreen():
#    ss = subprocess.Popen('nohup rm /etc/pointercal.xinput; service lightdm restart;', shell=True)
#    ss.wait()

def restartSystem():

  if os.name != "nt":  # We are NOT on the PC.
    ss = subprocess.Popen('sudo shutdown -r now', shell=True)
  else:
    log.warning('This is not an arm system so you must manually restart.')
    print 'This is not an arm system so you must manual restart.'
    print "Exiting this thread: ",threading.currentThread().getName()
    exit(1)


def soundInit():

  blAudioPresent = True
  try:
    if os.name == "nt" : # We are on the PC. This does not work on Chipsee.
      i = 1

    # nothing needed for Chipsee

  except Exception, e:
    log.debug("Error Initializing Audio: " + str(e))
    blAudioPresent = False

  return blAudioPresent

def soundPlayFile( strSoundFile, vol ):
  if os.name == "nt" : # We are on the PC. This does not work on Chipsee.
    vol = 1.0

  else : # We are on Linux

    fVol = float(vol / 5.0)  # user interface is 0-50
    if fVol > 10.0: fVol = 10.0  # Cap volume at 10.0 Above that gets distorted...
    volStr = "{0:.1f}".format(fVol)
    # -q to suppress stderr/stdout during playing of wave file
    strCommand = "play -q -V0 {0} vol {1}".format(strSoundFile, volStr)
    # print "Called Sound Play - " + strCommand
    os.system(strCommand)
#    except Exception, e:

