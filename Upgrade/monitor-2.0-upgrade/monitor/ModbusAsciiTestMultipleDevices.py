#! /usr/bin/python

import serial
import testModbus 
import os
# import system.networks.modbusConstants

import time

port = '/dev/ttySAC4'
baudrate = 9600
parity = serial.PARITY_EVEN
bytesize = 7
stopbits = serial.STOPBITS_ONE
timeout = 1

connection = testModbus.modbus(port, baudrate=baudrate, parity=parity, bytesize=bytesize, stopbits=stopbits, timeout=timeout, mode=testModbus.MODE_ASCII)

strDebug = "Initializing Port: {0}, Baud:{1}, Parity:{2}, Size:{3}, stopbits:{4}, timeout:{5}".format( port, baudrate, parity, bytesize, stopbits, timeout )

print strDebug 

connection.debug = True # Change to True to debug serial communications

while 1:
   try: 
      connection.address = 2
      response = connection.read_registers(200, 1)
      time.sleep(.5)
      connection.address = 3
      response = connection.read_registers(200, 1)
      time.sleep(.5)
      connection.address = 4
      response = connection.read_registers(200, 1)
      time.sleep(.5)
      connection.address = 5
      response = connection.read_registers(200, 1)
      time.sleep(.5)
      connection.address = 6
      response = connection.read_registers(200, 1)
      time.sleep(.5)
#      print "Response: ", response
#      print "Good Response", ":".join("{:02x}".format(ord(c)) for c in response)

   except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      print "Exception: ", strEx
      payload = strEx[strEx.find("is: "):]
      print "My response = ", payload, "Length:", len(payload)
      print ":".join("{:02x}".format(ord(c)) for c in payload)

   time.sleep(1)

