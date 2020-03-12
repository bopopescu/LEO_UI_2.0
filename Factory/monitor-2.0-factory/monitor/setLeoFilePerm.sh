#! /bin/bash
set -x
# This script needs to be run as leosw

# Adjust permissions and settings
cd /opt/monitor
sudo find . -type f -exec chmod 644 {} +
sudo find . -type d -exec chmod 755 {} +
sudo chown -R leosw:www-data *
sudo chown -R www-data:www-data /opt/monitor/log
sudo chown -R www-data:www-data /opt/monitor/data
sudo chmod 775 /opt/monitor/log
sudo chmod 775 /opt/monitor/data
sudo chmod 775 /opt/monitor/log/*
sudo chmod 775 /opt/monitor/data/*

