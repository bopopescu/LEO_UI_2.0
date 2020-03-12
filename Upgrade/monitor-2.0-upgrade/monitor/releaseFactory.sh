#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No version number supplied. Exiting"
    exit 1
fi
echo "Creating the package file for the $1 release - including new databases"
cd /opt/monitor
echo "Running releaseFactory.py"
/usr/bin/python /opt/monitor/releaseFactory.py $1

# Lastly, run the tarLeoCreate.sh BASH script to create the monitor.tar file.
# This simply is a separate backup file - use by the LeoUSB, but not Leo upgrade
echo "Creating the monitor.tar file for the $1 release"
sh tarLeoCreate.sh
mv /opt/monitor.tar /opt/monitor/monitorFactory-$1.tar
echo Done...

