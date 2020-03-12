#!/bin/bash
if [ $# -eq --h ]
  then
    echo "USAGE: createPatchPkgFile.sh"
    echo ""
    echo "This must be run from the Linux command line"
    exit 1
fi

echo "Creating a PATCH package file that only will update files listed in specialFileUpgrade.py"
cd /opt/monitor
echo "Running createPatchPkgFile.py"
/usr/bin/python createPatchPkgFile.py
echo Done...
