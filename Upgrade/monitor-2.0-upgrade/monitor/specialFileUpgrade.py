#!/usr/bin/env python

import sys
import os
import subprocess
import glob
import datetime
import shutil
import stat

tarball = 'LSU-UploadLimit.tar'
finalname = 'LSU-UploadLimit'

basepath = '/opt/monitor'

# Don't change version number
initfile = basepath + '/init.py'

# For this file, we will explicitly list the names of the files that we want to place into a sprecial file upgrade package. We prefer to use this VERY, VERY rarely.
packageFiles = [ 'views/uploadcheck.py', 'views/version.py' ]

def createInitFile():

  # This function is responsible for creating the first file that runs after the firmware update (after reboot). This init file is responsible
  # updating the list of files found in the above packageFiles list.

  # init.py - This file will be in the root folder (/opt/monitor). Its function is two-fold. First, it is responsible for moving the
  #    files from the firmware update package into the proper folders in /opt/monitor (and sub-folders). This file is dynamically created below
  #    for each LEO file upgrade package.

  print "createInitFile-->", initfile
  initFile = open(initfile, "w")

  initFile.write("#!/usr/bin/env python\n")
  initFile.write("\nimport sys\nimport os\nimport subprocess\n")

  # Create the commands to copy the files into the system upon bootup.
  for srcFileName in packageFiles :
    destPath = basepath + '/' + srcFileName
    print "Special Upgrade Src: ", srcFileName, " Dest: ", destPath
    # Create the command to copy the file
    strSubprocessCp =   "subprocess.call( 'cp {0} {1}', shell=True)\n".format( srcFileName, destPath )
    print "CP->", strSubprocessCp
    initFile.write( strSubprocessCp )
  initFile.close()

  print "statFile"
  st = os.stat(initfile)
  os.chmod(initfile, st.st_mode | stat.S_IEXEC)

def createFileUpgradePackage():
  # create the tar ball
  print "Basename of ", initfile, " = ", os.path.basename( initfile )
  strTarCmd = 'tar -cvzf {0} {1} '.format( tarball, os.path.basename( initfile ) )
  # append the files that are required
  for srcFileName in packageFiles :
    strTarCmd = '{0} {1} '.format( strTarCmd, srcFileName )

  print "Create Release Tar Cmd-->", strTarCmd
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
print "In Python of specialFileUpgrade.py"

createInitFile()
createFileUpgradePackage()



