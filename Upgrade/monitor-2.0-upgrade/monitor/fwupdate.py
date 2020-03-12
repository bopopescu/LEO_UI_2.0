#!/usr/bin/env python

# This python file is not part of the running LEO, but instead part of the firmware upgrade process.
# This file contains two functions. The first is called by init BEFORE the files are copied from the /opt/monitor/installed
# folder to the proper location in opt/monitor folders. The second is called AFTER all the files are updated in the opt/monitor folders.

import sys
import os
import subprocess
import glob
import datetime
import stat

LEORootPath = '/opt/monitor'
installDir = '{0}/install'.format( LEORootPath )

def fwupdateBeforeCopy( strPkgType ):
  
  # print "Running fwupdateBeforeCopy - ", strPkgType
  if strPkgType == 'upgrade':
    blUpgrade = True
  else:
    blUpgrade = False
  
  if blUpgrade is True:
    # Save the customer logo file
    print 'saving' + installDir + 'custlogo.png'
    subprocess.call('rm /opt/monitor/custlogo.png; mv /opt/monitor/static/local/img/custlogo.png /opt/monitor/custlogo.png', shell=True)
  

def fwupdateAfterCopy( strPkgType ):

  print "Running fwupdateAfterCopy - ", strPkgType
  if strPkgType == 'upgrade':
    blUpgrade = True
  else:
    blUpgrade = False
    
  if blUpgrade is True:
    # Restore the customer logo file
    print 'restoring' + installDir + 'custlogo.png'
    subprocess.call(
      'rm /opt/monitor/static/local/img/custlogo.png; mv /opt/monitor/custlogo.png /opt/monitor/static/local/img/custlogo.png ',
      shell=True)

    ######################################################
    # Special "non-opt/monitor..." folder file updates - Files that need to be updated that are NOT part of the /opt/monitor tree.
    #####################################################

  # /etc/rc.local -- grep for version in /etc/rc.local - if it is not the version we want, copy from /opt/monitor/bootFiles to /etc.
  cpRCFile = False
  try:
    # rc.local update
    strCmd = '/bin/grep VERSION: /etc/rc.local'
    print 'checking /etc/rc.local'
    strVersionLine = subprocess.check_output(strCmd, shell=True)
    # FUTURE - in a future version, we will need to add code to look at the version number to determine if the file needs to be copyied.

  except Exception, e:  # We will get an exception if the string cannot be found in /etc/rc.local
    # There is no VERSION string in the file. Need to copy new version.
    print 'Need to update /etc/rc.local'
    cpRCFile = True

  if cpRCFile is True:
    # Copy the updated version of rc.local
    strCpSyntax = '/bin/cp /opt/monitor/bootFiles/rc.local /etc/rc.local'
    print 'Copying rc.local File - {0}'.format( strCpSyntax )
    strResult = subprocess.call(strCpSyntax, shell=True)

  # Update xfce to disable popup window when usb drive is inserted in LEO
  strCpSyntax = '/bin/cp /opt/monitor/bootFiles/xfce/thunar-volman.xml /home/linaro/.config/xfce4/xfconf/xfce-perchannel-xml/thunar-volman.xml'
  strResult = subprocess.call(strCpSyntax, shell=True)
  strCpSyntax = 'chown linaro:linaro /home/linaro/.config/xfce4/xfconf/xfce-perchannel-xml/thunar-volman.xml'
  strResult = subprocess.call(strCpSyntax, shell=True)

  # Update the linaro autostart.sh to make sure the proper startup file is used.
  strCpSyntax = '/bin/cp /opt/monitor/bootFiles/autostart.sh /home/linaro/autostart.sh'
  strResult = subprocess.call(strCpSyntax, shell=True)
  print "AUTOSTART COPY result=", strResult

  print "Install Package Process Completed"



