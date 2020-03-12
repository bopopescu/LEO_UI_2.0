# Start LEO Core
echo Start LEO >> /home/linaro/startStat.txt
# cd /opt/monitor
# /usr/bin/python leo_ui.py &>> /home/linaro/startStat.txt
# /usr/bin/python leo_ui.py & >> /home/linaro/pylog.txt 2>&1
cd /opt/monitor
echo Start RUNNING >> /home/linaro/startStat.txt
/usr/local/bin/gunicorn --bind unix:/tmp/nginx.sock leo_ui:app --error-logfile /var/log/gunicorn-err.log & >> /home/linaro/pylog.txt 2>&1

echo Done LEO Core Start >> /home/linaro/startStat.txt

# Start LEO Process Watchdog
echo Start LEO Proc Wdog >> /home/linaro/startStat.txt
cd /opt/monitor
/usr/bin/python leoProcWdog.py & >> /home/linaro/startStat.txt 2>&1
echo Done LEO Proc Wdog >> /home/linaro/startStat.txt
