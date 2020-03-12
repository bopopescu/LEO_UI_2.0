#! /bin/bash
# This script needs to be run as root and requires the path to LeoInstall folder to be passed in.
# The purpose of this script is to remove ALL access
# to ALL Leo related execution related files.
# It will also disable the control-alt-F1-F7 switching by adding a file in X11.
#
# Here is the current list of folders that will be protected:
# bkup, data, install, log, static, system, templates, utils, views
# In the opt/monitor folder, we will protect all *.py, *.sh, *.bat, *.ico
echo Begin LEO Executible Files Protection...

# To be honest, I'm not sure if we just lock down /opt if this is enough, so
# we are going to lock all files that run LEO down.
chmod go= /opt
chmod go= /opt/monitor

# Lock down individual files in the /opt/monitor folder
chmod go= /opt/monitor/*.py
chmod go= /opt/monitor/*.pyc
chmod go= /opt/monitor/*.sh
chmod go= /opt/monitor/*.ico
chmod go= /opt/monitor/*.bat

# All files in specific folders
chmod -R go= /opt/monitor/bkup
chmod -R go= /opt/monitor/data
chmod -R go= /opt/monitor/install
chmod -R go= /opt/monitor/log
chmod -R go= /opt/monitor/static
chmod -R go= /opt/monitor/system
chmod -R go= /opt/monitor/templates
chmod -R go= /opt/monitor/utils
chmod -R go= /opt/monitor/views

echo LEO Executible Files Have Been Protected...

# The following removes control-alt-<F1-F7> capabilities
cp 50-novtswitch.conf /usr/share/X11/xorg.conf.d
echo Locked down VTSwitch...

echo All Done Leo Lockdow

