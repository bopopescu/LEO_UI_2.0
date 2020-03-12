mkdir /opt/debugfil
mkdir /opt/debugfil/log
cp /opt/monitor/log/*.* /opt/debugfil/log
mkdir /opt/debugfil/data
cp /opt/monitor/data/*.* /opt/debugfil/data
mkdir /opt/debugfil/nginx
cp /var/log/nginx/*.* /opt/debugfil/nginx
cp /var/log/gunicorn-err.log /opt/debugfil
cp /var/log/kern.log /opt/debugfil
cp /var/log/auth.log /opt/debugfil
cp /var/log/syslog /opt/debugfil
cp /home/linaro/*.txt /opt/debugfil

