#!/bin/bash
# This script will create a monitor.tar file (without .pyc files) and will be placed in the /opt folder.
echo Tar LEO
cd /opt
tar -cf monitor.tar monitor 
# echo Delete .pyc files in tar file. Delete any .tar files within the tar.
# tar --wildcards --delete -f monitor.tar *.pyc
# tar --wildcards --delete -f monitor.tar *.tar

echo Done...

