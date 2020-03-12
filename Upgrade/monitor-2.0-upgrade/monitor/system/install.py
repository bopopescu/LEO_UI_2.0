#!/usr/bin/env python

import sys
import os
import subprocess
import glob

import logging
import logging.handlers


#
# This is the module that gets run BEFORE LEO Is started to determine if a firmware update package is present.
# It is not part of LEO runtime
#

# create logger
log = logging.getLogger('')
log.setLevel(logging.DEBUG)

tarball = 'Leonardo'
LeoRootPath = "/opt/monitor"
installDir = "{0}/install".format( LeoRootPath )

# create file handler which logs even debug messages
# For this module, sys.path is the system folder. "repath" to log folder.
strInstallFileName = '{0}/log/install.log'.format( LeoRootPath )
_fileHandler = logging.handlers.RotatingFileHandler( strInstallFileName, maxBytes=100000, backupCount=1)
_fileHandler.setLevel(logging.DEBUG)

# create console handler with a higher log level
_consoleHandler = logging.StreamHandler()
_consoleHandler.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d %(message)s')
_fileHandler.setFormatter(_formatter)
_consoleHandler.setFormatter(_formatter)

# add the handlers to the logger
log.addHandler(_fileHandler)
log.addHandler(_consoleHandler)

def IsARMProcessor() :
  bArm = False

  try:
    with open('/proc/cpuinfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
          if line.find('model name') == 0:
            if line.find('ARM') > -1:
              bArm = True
              log.info('ARM Based Machine Detected.')
            else :
              bArm = False
              log.info('PC or Non-ARM machine... ')

    return bArm
  except Exception, e:
    log.exception('Error reading /proc/cpuinfo: ' + str(e) )

IsARMProcessor()

try:

  log.info('checking ' + installDir)

  # find package name
  pkgFile = glob.glob(installDir + '/*.pkg')
  if len(pkgFile) > 0:
    strInfo = "Found Package File ->{0}".format( pkgFile )
    log.info( strInfo )
    pkgFile = pkgFile[0]
    log.info('Opening ' + pkgFile)

    os.chdir(installDir)
    ss = subprocess.Popen('gpg --output ' + tarball + ' --batch --passphrase-fd 0 --decrypt ' + pkgFile, shell=True, stdin=subprocess.PIPE)
    ss.communicate('HunterL!berty20\n')
    ss.wait()

    log.info( "Start upgrade" )
    
    subprocess.call('tar -xzf ' + tarball, shell=True)
    subprocess.call(installDir + '/init.py', shell=True)
    
    subprocess.call('rm -rf ' + installDir + '/*', shell=True) # remove all install files.
    subprocess.call('rm ' + LeoRootPath + '/*.pkg', shell=True) # Remove package file.
    log.info('Upgrade complete')
  else:
    log.info('No install file exists.')

except Exception, e:
  
  log.exception( 'Exception in install' + str(e) )
  
