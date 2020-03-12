#!/usr/bin/env python

# This python script is NOT part of the LEO system software.

# This file is responsible for creating either a factory firmware update package (and tar file)
# OR an upgrade package file and appropriate installation python (init.py) script.
# THE user of this script is responsible for cleaning out contents of the Leo databases - e.g. audit trails, alarm, data logs.

import sys
import os
import subprocess
import glob
import datetime
import shutil
import stat
import fwupdate

basepath = '/opt/monitor'
versionscript = basepath + '/views/version.py'
initfile = basepath + '/init.py'

basepathFilesToTar = [ '*.py', '*.sh', 'imageResizer', '*.ico', '.conf' ]

pkgFactoryFoldersToTar = [ 'system', 'views', 'static', 'templates', 'utils', 'bootFiles', 'data']
pkgUpgradeFoldersToTar = [ 'system', 'views', 'static', 'templates', 'utils', 'bootFiles'  ]
linuxFiles = [ '/etc/rc.local', '/etc/logrotate.d/gunicorn', '/usr/share/X11/xorg.conf.d/50-novtswitch.conf', '/etc/ssh/sshd_config', '/etc/postfix/main.cf', ' /etc/ntp.conf-ORIG','/etc/ntp.conf-CUST','/etc/postfix/sasl_passwd']

def writeVersionFile(version):
  print "WriteVersionFile", versionscript, "Version-->", version,
  # Update the version file
  f = open(versionscript, 'w')
  f.write('#! /usr/bin/python\n\nversionInfo = {\n"LeoVersionNumber" : "')
  f.write(version)
  f.write('",\n"LeoVersionDate" : "')
  f.write(datetime.date.today().isoformat())
  f.write('"\n}')
  f.close()

def createInitFile( newVersion, pkgType ):

  # This function is responsible for creating the module that is called by install.py - after the fimrware update (after reboot).
  # This init file is responsible for upgrading the "CORE" leo files from the backup into the proper folders for running LEO.

  # init.py - This file will be in the root folder (/opt/monitor). Its function is two-fold. First, it is responsible for moving the
  #    files from the firmware update package (now found in the /install folder - thanks to install.py)
  #    into the proper folders in /opt/monitor (and sub-folders). Second, handle any special upgrade "things"

  print "createInitFile-->", initfile
  initFile = open(initfile, "w")

  initFile.write("#!/usr/bin/env python\n")
  initFile.write("\nimport sys\nimport os\nimport subprocess\n")
  initFile.write("\nimport os\nimport subprocess\nimport fwupdate\n")

  if pkgType == 'factory':
    packageFoldersToTar = pkgFactoryFoldersToTar
  else:
    packageFoldersToTar = pkgUpgradeFoldersToTar
  initFile.write('\nfwupdate.fwupdateBeforeCopy( "{0}" )\n'.format( pkgType ) )

  for folder in packageFoldersToTar :
    print "Folder: ", folder
    strSubprocessRm = "\nsubprocess.call( 'rm -rf {0}/{1}/*', shell=True)\n".format( basepath, folder )
    print "RM->", strSubprocessRm
    initFile.write( strSubprocessRm )
    strSubprocessCp =   "subprocess.call( 'cp -R  ./{0} {1}', shell=True)\n".format( folder, basepath )
    print "CP->", strSubprocessCp
    initFile.write( strSubprocessCp )

  # Copy files from the root. Don't delete files in the basepath folder; just update them.
  print "Folder: ", basepath
  strSubprocessCp = "subprocess.call( 'cp * {0}', shell=True)\n".format( basepath )
  print "CP->", strSubprocessCp
  initFile.write( strSubprocessCp )
  
  if len( linuxFiles ) > 0 :
    initFile.write( "\n# Copy Linux files\n")
    for destFullPath in linuxFiles :
      srcFileName = os.path.basename( destFullPath )
      print "Linux Patch File: ", srcFileName, " Dest: ", destFullPath
      # Create the command to copy the file
      strSubprocessCp =   "subprocess.call( 'cp {0} {1}', shell=True)\n".format( srcFileName, destFullPath )
      print "CP->", strSubprocessCp
      initFile.write( strSubprocessCp )

  initFile.write('\nfwupdate.fwupdateAfterCopy( "{0}" )\n'.format( pkgType ) )

  initFile.close()

  print "statFile"
  st = os.stat(initfile)
  os.chmod(initfile, st.st_mode | stat.S_IEXEC)

def createRelease(version, pkgType):
  tarball = 'Leonardo'
  if pkgType == 'factory' :
    blFactory = True
    finalname = 'LeoFactoryRelease'
  else:
    blFactory = False
    finalname = 'LeoUpgradeRelease'

  print "createFactoryRelease", version
  # create the tar ball
  print "glob.glob - ",  glob.glob("Leonardo*")
  for hgx in glob.glob("Leonardo*"):
    print "removing -->", hgx
    os.remove(hgx)

  # Add specific files from the "basepath" folder.
  tarballName = tarball
  strTarCmd = 'tar -cvzf {0}'.format( tarballName )
  # loop through the types of files to backup
  for baseFilename in basepathFilesToTar :
    strTarCmd = '{0} {1} '.format( strTarCmd, baseFilename )

  # Remove files we don't need. (log files, bkup folder)
  try:
    os.remove('/opt/monitor/log/*')
  except:
    print "OK. Log files do not exist"

  try:
    os.remove('/opt/monitor/bkup/*')
  except:
    print "OK. Bkup files do not exist"

  # append the folders that are required
  if blFactory == True :
    for folder in pkgFactoryFoldersToTar :
      strTarCmd = '{0} {1} '.format( strTarCmd, folder )

  else:
    for folder in pkgUpgradeFoldersToTar :
      strTarCmd = '{0} {1} '.format( strTarCmd, folder )

  if len( linuxFiles ) > 0 :
    for srcFileName in linuxFiles:
      # First, copy the file to the current folder.
      baseName = os.path.basename( srcFileName )
      strCp = 'cp {0} .'.format( srcFileName )
      print "Calling copy of file-->{}".format( strCp )
      print subprocess.call( strCp, shell=True )

      # Add basename to tar
      strTarCmd = '{0} {1} '.format( strTarCmd, baseName )

  print "Create Release Tar Cmd-->", strTarCmd
  subprocess.call( strTarCmd, shell=True)

#  str = "EXECUTING-->gpg -o '{0}.pkg --batch --passphrase-fd 0 -c ' + tarballName, shell=True, stdin=subprocess.PIPE".format( tarballName )
  str = 'gpg -o ' + finalname + version + '-' + '.pkg --batch --passphrase-fd 0 -c ' + tarballName
  print str

  ss = subprocess.Popen('gpg -o ' + finalname + '-' + version + '.pkg --batch --passphrase-fd 0 -c ' + tarballName, shell=True, stdin=subprocess.PIPE)
  ss.communicate('HunterL!berty20\n')
  ss.wait()

  os.remove(tarball)
  os.remove(initfile)


# get the revision
print "In Python of Release.py"
argv = sys.argv
argc = len(argv)

if argc != 3:
  print 'Usage: release.py <versionNum> [factory | upgrade]'
  sys.exit(2)

version = argv[1]
pkgType = argv[2]
if pkgType != 'factory' and pkgType != 'upgrade':
  print "Invalid Package Selection. Exiting"
  exit(1)

print "Version = ", version, "pkg Type = ", pkgType

strClean = 'sh {0}/clean.sh'.format( basepath )
subprocess.call( strClean, shell=True)

writeVersionFile(version)
createInitFile(version, pkgType )
createRelease(version, pkgType )



