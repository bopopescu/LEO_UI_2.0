#! /usr/bin/python

import sys
import time
import os
import subprocess
import threading

# The purpose of this file is simply a python script to run after killing the leoProcWdog
# It is based on leoProcWdog except simply continues to pet the watchdog - regardless.

def PetWatchdog():

    wDogFile = open('/dev/watchdog','w')
    wDogFile.write('j')
    wDogFile.flush() # Make sure it is not buffered.

    print "Petting the Watchdog."
    while 1 :

        # Pet the watchdog so he does not reboot the system.
        wDogFile.write('j')
        wDogFile.flush() # Make sure it is not buffered.
        time.sleep( 10 )

PetWatchdog()
