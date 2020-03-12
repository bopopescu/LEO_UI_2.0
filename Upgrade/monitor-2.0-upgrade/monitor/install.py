#!/usr/bin/env python

import sys
import os
import subprocess
import glob

import logging
import logging.handlers

# create logger
log = logging.getLogger('')

log.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
_fileHandler = logging.handlers.RotatingFileHandler('/opt/monitor/log/install.log', maxBytes=100000, backupCount=1)
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



tarball = 'Leonardo'
installDir = '/opt/monitor/install'

IsARMProcessor()

try:
  # if the path does not exist, create it.
  if os.path.exists(installDir) != True :
    os.mkdir( installDir, 0700 )
  os.chdir(installDir)
  log.info('checking ' + installDir)

  # find package name
  pkgFile = glob.glob(installDir + '/*.pkg')
  if len(pkgFile) > 0:
    pkgFile = pkgFile[0]
    log.info('Opening ' + pkgFile)

    ss = subprocess.Popen('gpg --output ' + tarball + ' --batch --passphrase-fd 0 --decrypt ' + pkgFile, shell=True, stdin=subprocess.PIPE)
    ss.communicate('HunterL!berty20\n')
    ss.wait()

    subprocess.call('tar -xzf ' + tarball, shell=True)
#    subprocess.call(installDir + '/init.py', shell=True)
  else:
    log.info('No install file exists.')

except Exception, e:
    print 'Exception in install' + str(e)
    log.exception('Exception in install' + str(e) )
finally:
  subprocess.call("/usr/bin/crontab -l 2>/dev/null | grep -q 'reboot'  && echo 'cronttab entry already exists' || echo '30 5 * * * /sbin/reboot >> /opt/monitor/log/gunicorn-err.log' | /usr/bin/crontab -", shell=True)
  try:
#    subprocess.call('rm -rf ' + installDir + '/*', shell=True)
    i = 0
  except:
    pass
