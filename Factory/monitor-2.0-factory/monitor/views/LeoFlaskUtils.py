from flask import session, request
from flask import current_app as app
import sys
import os
import version
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], 'utils'))
import logsystem
log = logsystem.getLogger()

# This function simply centralizes the "base" functionality for preparing the context for Leo Screens
def prepareContext( strScreenName ):

    if 'localhost' in request.host or '127.0.0.1' in request.host:
      blLocal = True
      blOSKeybd = True
    else:
      blLocal = False
      blOSKeybd = False

    if os.name == "nt" : # We are running on the PC. Choose to run remote (False) or touchscreen (True).
      # Both false = act like remote
      # Both true = act like touchscren; hide cursor
      blOSKeybd = False             # When true, show screen keyboard
      blLocal = False                # When true, act as local UI.

    if 'loginHidden' in session :
      if session['loginHidden'] == 1 :
        session['dev'] = True
    else :
      session['dev'] = False

    ctx = {
            'IPInfo': app.dictIPInfo,
            'SESSION': None,
            'localhost': blLocal,
            'osKeybd' : blOSKeybd,
            'versionInfo': version.versionInfo,
            'dev' : session['dev'],
            'clienttype' : 'local' # clienttype will ALWAYS be local - part of path. Each screen will key off of 'localhost' keyword for remote vs. local screens.
          }

#    print 'clientypte =', ctx['clienttype'], 'reqeust.host =', request.host, 'Local = ', ctx['localhost'], 'Version = ', ctx['versionInfo']

    return ctx


def IsARMProcessor() :
  bArm = False

  if os.name != "nt":  # We are NOT on the PC.
  
    with open('/proc/cpuinfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
          if line.find('Processor') == 0:
            if line.find('ARM') > -1:
              bArm = True

  return bArm

# This module reads the IP information AFTER the OS has attempted to initialize the hardware stack. If there are NO
# errors, the NetworkStackIPInfo AND the /etc/network/interfaces IP information should be the same.
# IF there are network initilization errors - e.g. bad gateway or bad subnet mask, the information will NOT be the same.
# This is why there are two functions to get IP information.
def getNetworkStackIPInfo() :
  # Read the ethernet information and parse out the ipaddr, subnetmask and gateway addr.
  dictIPInfo = {}

  # Strings to look for to get IP information
  HWaddr = 'HWaddr'
  ipAddrTitle = 'inet addr:'
  ipGWTitle = 'Bcast:'
  ipMask = 'Mask:'

  if IsARMProcessor() is True :

    # This will give us IP address and subnet mask
    ifconfigInfo = subprocess.check_output('ifconfig')
    strIpAddr = "Unknown"
    strIpMask = ""
    strGW = ""
    strDNS = ""

    # Let's get this out of the way
    HWaddrLoc = ifconfigInfo.find(HWaddr)
    strHWaddr = ifconfigInfo[HWaddrLoc + 7:HWaddrLoc + 24]
    # We need to remove the colons and turn it all to uppercase.
    strHWaddr = strHWaddr.replace(":", "").upper()

    # Typically in the file, the interfaces are listed by eth0, lo and then wlan. So if the interface is on wlan, we need to
    # ignore the ip address that is in
    strEthLoc = ifconfigInfo.find( "eth" )
    strLoLoc = ifconfigInfo.find("lo")
    strWlanLoc = ifconfigInfo.find("wlan")

    strEthInfo = ""
    strLoInfo = ""
    strWlanInfo = ""
    if strLoLoc >= 0 :
      strEthInfo = ifconfigInfo[strEthLoc:strLoLoc-1]
    if strWlanLoc >= 0 :
      strLoInfo = ifconfigInfo[strLoLoc:strWlanLoc-1]
      strWlanInfo = ifconfigInfo[strWlanLoc:]
    else :
      strLoInfo = ifconfigInfo[strLoLoc:]

    # try to parse out ipaddr from eth0
    ipAddrLoc = strEthInfo.find( ipAddrTitle )
    if ipAddrLoc >= 0 :
      ipGWTitleLoc = strEthInfo.find( ipGWTitle )
      ipMaskLoc = strEthInfo.find( ipMask )
      upBrdLoc = strEthInfo.find( 'UP BROADCAST')
      strIpAddr = strEthInfo[ipAddrLoc:ipGWTitleLoc]
      strIpMask = strEthInfo[ipMaskLoc:upBrdLoc]

      # param[0] will be the title and param
      # param[1] will be the info and need some white space cleanup
      params = strIpAddr.split(':')
      strIpAddr = "".join(params[1].split())
      params = strIpMask.split(':')
      strIpMask= "".join(params[1].split())

      # This will give us gateway information
      routeInfo = subprocess.check_output(['route','-n'])
  
      # Determine gateway address from "route -n"
      routeFields = routeInfo.split() # Turns into a list of words
      if 'UG' in routeFields :
        # We found the line with the UG (which is gateway address)
        # Now get the index for the UG field and the gateway address is 2
        # list entries before it.
        iUG = routeFields.index( 'UG' )
        strGW = routeFields[iUG - 2]

      # Determine the name server
      dnsaddress = subprocess.check_output(['cat','/etc/resolv.conf'])
      dnsaddressLoc = dnsaddress.find('nameserver')
      if  dnsaddressLoc >= 0 :
        dnsaddress = subprocess.Popen("grep nameserver /etc/resolv.conf | awk '{print $2}' ORS=' '", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        #dnsStart = dnsaddressLoc+len('nameserver')
        strDNS =  dnsaddress#dnsaddress[dnsStart:]
      else :
        strDNS = strGW

    else : # There is NO ETH0 IP address
      strIpAddr = "No Eth0"
      strIpMask = ""
      strGW = ""
      strDNS = ""

    # For now, if both ETH0 and WLAN are active, we will only show ETH0
    # This is because we don't want to add UI support for WLAN activation
    # at this time (version 1)
    if len( strIpMask ) == 0 and strWlanLoc >= 0:
      # Let's see if we can process the WLAN interface
      ipAddrLoc = strWlanInfo.find( ipAddrTitle )
      if ipAddrLoc >= 0 :
        ipGWTitleLoc = strWlanInfo.find( ipGWTitle )
        ipMaskLoc = strWlanInfo.find( ipMask )
        upBrdLoc = strWlanInfo.find( 'UP BROADCAST')
        strIpAddr = strWlanInfo[ipAddrLoc:ipGWTitleLoc]
        strIpMask = strWlanInfo[ipMaskLoc:upBrdLoc]
        strGW = strWlanInfo[ipGWTitleLoc:ipMaskLoc]

        # param[0] will be the title and param
        # param[1] will be the info and need some white space cleanup
        params = strIpAddr.split(':')
        strIpAddr = "".join(params[1].split())
        params = strGW.split(':')
        strGW = "".join(params[1].split())
        params = strIpMask.split(':')
        strIpMask= "".join(params[1].split())
      else :
        # There remains NO IP interface (eth0 AND wlan)
        strIpAddr = "No Eth0 and WLAN"
        strIpMask = ""
        strGW = ""

    dictIPInfo['IP_ADDR'] = strIpAddr.strip()
    dictIPInfo['IP_GATEWAY'] = strGW.strip()
    dictIPInfo['IP_MASK'] = strIpMask.strip()
    dictIPInfo['HW_ADDR'] = strHWaddr.strip()
    dictIPInfo['DNS_ADDRESS'] = strDNS.strip()
  else :
    dictIPInfo['IP_ADDR'] = 'On PC - Unknown'
    dictIPInfo['IP_GATEWAY'] = 'Unknown'
    dictIPInfo['IP_MASK'] = 'Unknown'
    dictIPInfo['HW_ADDR'] = 'Unknown'
    dictIPInfo['DNS_ADDRESS'] = 'Unknown'

  return dictIPInfo


def startSession() :
    if 'init' not in session :
      session['reqHost'] = request.host
      session['bArm'] = IsARMProcessor()
      session['init'] = 'True'
      session.permanent = True # Activate session timeout. Timeout set in leo_ui.py (as part of Flask app - see permanent_session_lifetime).

def endSession() :
    session['reqHost'] = request.host
    session['username'] = 'Not Logged In'
    session['loginUsername'] = ''
    session['is_authenticated'] = False
    session['can_edit_users'] = False
    session['can_edit_logging'] = False
    session['can_edit_system'] = False
    session['can_access_files'] = False
    session['can_edit_device'] = False
    session['can_action_command'] = False
    session['loginRoles'] = ''
    session['loginHidden'] = 0
    session['dev'] = False

    if 'init' in session :
      del session['init']

    session.clear()

# This method will be reached for each session request.
# Setting the modified field to true reset the session expiration timer
def refreshSession( session ) :
    session.modified = True

def getSessionUsername( session ) :
  if 'username' in session :
    return session['username']
  else :
    return 'Unknown session'
