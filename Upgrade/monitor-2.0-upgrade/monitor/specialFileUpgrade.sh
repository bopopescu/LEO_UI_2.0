#!/bin/bash
echo "Creating a SPECIAL package file that only will update files listed in specialFileUpgrade.py"
cd /opt/monitor
echo "Running specialFileUpgrade.py"
/usr/bin/python /opt/monitor/specialFileUpgrade.py
echo Done...
