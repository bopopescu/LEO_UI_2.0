#!/usr/bin/env python

import sys
import os
import subprocess
import glob
import datetime
import shutil
import stat

# Update this and version.py to the same version - but formatted differently...
patchVersion = '100B21000P1'

# Don't touch.
tarball = '{}.tar'.format( patchVersion )
finalname = '{}'.format( patchVersion )
basepath = '/opt/monitor'

initfile = basepath + '/init.py'

#
#  IMPORTANT - Pleaes list the changes made to each module that makes up the patch
#
# getAlarms.py - Needed to add a way to clear or retrieve historical alarms with cache disabled.
# getSiteStatus.py - Updated to avoid the NoneType error that occurs periodically at bootup
# setSiteCurrentTime.py - Watchdog was timing out when the timezone was changed and the time was advanced forward.
# pageAlarms.html - added support for selectively removing the historical alarm caching.
# pageSysconfig.html - The time and date were not being displayed properly.
# web.js - Minor update for refreshing the siteStatus
# rc.local - Part of linxuFiles list because it is NOT in the /opt/monitor folder tree. Updated to version 1.01 by
#      adding an option on the gunicorn command line to create a "pid" file for gunicorn.
# gunicorn - Part of linxuFiles list because it is NOT in the /opt/monitor folder tree. Adding a file in logrotate.d so
#      so that ALL LEO log files are limited in size and rotated.
packageFiles = [ 'views/version.py', 'system/loggingManager.py']
linuxFiles = [ '/etc/rc.local', '/etc/logrotate.d/gunicorn' ]

def createInitFile():

  # This function is responsible for creating the first file that runs after the firmware update (after reboot). This init file is responsible
  # updating the list of files found in the above packageFiles list.

  # init.py - This file will be in the root folder (/opt/monitor). Its function is two-fold. First, it is responsible for moving the
  #    files from the firmware update package into the proper folders in /opt/monitor (and sub-folders). This file is dynamically created below
  #    for each LEO file upgrade package.
  
  # This part can also be modified to do other types of functions than just copying files. See the uboot-upgrade patch
  # as an example.

  print "createInitFile-->", initfile
  initFile = open(initfile, "w")

  # we are dynamically writing the python software that will be init.py and run as part of the firmware update process.
  initFile.write("#!/usr/bin/env python\n")
  initFile.write("\nimport sys\nimport os\nimport subprocess\n")

  # Create the commands to copy the files into the system upon bootup.
  for srcFileName in packageFiles :
    destPath = basepath + '/' + srcFileName
    print "Patch: ", srcFileName, " Dest: ", destPath
    # Create the command to copy the file
    strSubprocessCp =   "subprocess.call( 'cp {0} {1}', shell=True)\n".format( srcFileName, destPath )
    print "CP->", strSubprocessCp
    initFile.write( strSubprocessCp )
    
  # Create the commands to copy the files into the system upon bootup.
  if len( linuxFiles ) > 0 :
    initFile.write( "\n# Copy Linux files\n")
    for destFullPath in linuxFiles :
      srcFileName = os.path.basename( destFullPath )
      print "Linux Patch File: ", srcFileName, " Dest: ", destFullPath
      # Create the command to copy the file
      strSubprocessCp =   "subprocess.call( 'cp {0} {1}', shell=True)\n".format( srcFileName, destFullPath )
      print "CP->", strSubprocessCp
      initFile.write( strSubprocessCp )
      
  initFile.close()

  print "statFile"
  st = os.stat(initfile)
  os.chmod(initfile, st.st_mode | stat.S_IEXEC)

def createPatchPkgFile():
  # create the tar ball
  print "Basename of ", initfile, " = ", os.path.basename( initfile )
  strTarCmd = 'tar -cvzf {0} {1} '.format( tarball, os.path.basename( initfile ) )
  # append the files that are required
  for srcFileName in packageFiles :
    strTarCmd = '{0} {1} '.format( strTarCmd, srcFileName )

  # Since the Linux files are NOT part of the LEO tree, we have to copy the files into the LEO root folder for
  # archiving into the tar.
  if len( linuxFiles ) > 0 :
    for srcFileName in linuxFiles:
      # First, copy the file to the current folder.
      baseName = os.path.basename( srcFileName )
      strCp = 'cp {0} .'.format( srcFileName )
      print "Calling copy of file-->{}".format( strCp )
      print subprocess.call( strCp, shell=True )

      # Add basename to tar
      strTarCmd = '{0} {1} '.format( strTarCmd, baseName )

  print "Create Patch Tar Cmd-->", strTarCmd
  subprocess.call( strTarCmd, shell=True)

  str = "EXECUTING-->gpg -o ' {0} .pkg --batch --passphrase-fd 0 -c ' + tarball, shell=True, stdin=subprocess.PIPE".format( finalname )
  print str

  ss = subprocess.Popen('gpg -o ' + finalname + '.pkg --batch --passphrase-fd 0 -c ' + tarball, shell=True, stdin=subprocess.PIPE)
  ss.communicate('HunterL!berty20\n')
  ss.wait()

  # Temporarity don't remove these files.
  #  os.remove(tarball)
  #  os.remove(initfile)

# get the revision
print "In Python of specialFileUpgrade.py - {}".format( patchVersion )

createInitFile()
createPatchPkgFile()



