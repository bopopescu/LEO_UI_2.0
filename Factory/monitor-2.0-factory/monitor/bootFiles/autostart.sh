#/bin/sh

# Give the LEO system time to get initialized.
sleep 7

date >> /home/linaro/bootup.txt

READY_FILE=/home/linaro/LeoReady

x=0
while [ "$x" -lt 200 -a ! -e $READY_FILE ]; do
   x=$((x+1))
   sleep .1
done
if [ -e $READY_FILE ]
then
   echo "Found: $READY_FILE Time:$x" >> /home/linaro/bootup.txt
else
   echo "File $READY_FILE not found within time limit!" >> /home/linaro/bootup.txt
fi

date >> /home/linaro/bootup.txt
# delete the "ready" file
rm $READY_FILE

# NOW Start the browser

# The following line starts the browser in full screen
/usr/bin/chromium-browser --disable-session-crashed-bubble --disable-infobars --incognito  --touch-devices=9 --kiosk http://localhost

# The following line starts the browser like a normal browser for dev/debug.
#/usr/bin/chromium-browser  http://localhost

# The following line starts the browser for remote debugging. Use with remdebug.sh
# /usr/bin/chromium-browser --remote-debugging-port=9222 http://localhost

