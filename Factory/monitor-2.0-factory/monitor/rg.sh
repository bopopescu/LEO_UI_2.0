ps aux | grep leo
pkill -HUP -o gunicorn
echo Waiting for process to restart.
sleep 2
ps aux | grep leo
