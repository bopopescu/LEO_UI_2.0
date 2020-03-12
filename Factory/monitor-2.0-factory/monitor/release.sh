#!/bin/bash
if [ $# -lt 2 ]
  then
    echo "USAGE: release.sh <versionNum> [factory | upgrade]"
    exit 1
fi

echo "Remove log and backup files"
rm -rf /opt/monitor/log
mkdir /opt/monitor/log
rm -rf /opt/monitor/bkup
mkdir /opt/monitor/bkup
echo "Clear customer logo"
cp /opt/monitor/static/local/img/custlogo-blank.png /opt/monitor/static/local/img/custlogo.png

echo "Creating the package file for the $1 upgrade"
cd /opt/monitor
echo "Running release.py"
/usr/bin/python /opt/monitor/release.py $1 $2

# Lastly, run the tarLeoCreate.sh BASH script to create the monitor.tar file.
echo "Creating the monitor.tar file in /opt/monitor for the $1 $2"
sh -x tarLeoCreate.sh
mv /opt/monitor.tar /opt/monitor/monitor-$1-$2.tar
mv /opt/monitor/*.tar /opt
mv /opt/monitor/*.pkg /opt
echo Done...

