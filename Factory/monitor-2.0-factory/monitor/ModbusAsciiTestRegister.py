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

connection.debug = False # Change to True to debug serial communications
readWrite = "Read"

while 1:
   try: 
      connection.address = 6
      strPrompt = "{0} - Enter a register number. 0=Exit--> ".format( readWrite )
      reg = input(strPrompt)
      if reg == 0 :
        exit()
      elif reg == 500 :
        # swtich modes between read and write 
        if readWrite.find( "Read" ) >=  0 :
          readWrite = "Write"
        else :
          readWrite = "Read"
      else :
        if readWrite.find( "Write" ) >= 0 :
          # Before Write, read register current value
          response = connection.read_registers(reg, 1)
          strPrompt = 'Enter the value to write to reg {0} (curr Value:{1})-->'.format( reg, response )
          value = input(strPrompt)
          connection.write_register(reg, value)
          print "Good Write"
        else :
          response = connection.read_registers(reg, 1)
          print "Read Payload:", response

   except Exception, e:
      strEx = '***** Error ***** {0}'.format( str(e) )
      print "Exception: ", strEx
      print "Reg:", reg, "response = ", response

