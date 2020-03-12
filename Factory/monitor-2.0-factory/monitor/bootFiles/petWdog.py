#! /usr/bin/python

import sys
import time
import os
import subprocess
import threading

def petWatchdog():

    # This method simply sits in a loop and keeps petting the watchdog.
    wDogFile = open('/dev/watchdog','w')
    wDogFile.write('j')
    wDogFile.flush() # Make sure it is not buffered.

    # Every 15 seconds, pet the dog
    while 1 :

        # Pet the watchdog so he does not reboot the system.
        wDogFile.write('j')
        wDogFile.flush() # Make sure it is not buffered.
        time.sleep( 15 )

petWatchdog()
