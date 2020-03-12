#! /usr/bin/python

import networkConstants
import networkObject

import modbusConstants

import serial
import basicModbus
import os

import logsystem
log = logsystem.getLogger()


import time

networkType = networkConstants.networkModbusASCII
networkTypeName = networkConstants.networkModbusASCIIText

class Network(networkObject.NetworkObject):
  def __init__(self, networkManager, name, description, connectionInfo):
    networkObject.NetworkObject.__init__(self, networkManager, name, description, connectionInfo, networkType, networkTypeName)
    strInfo = "Loaded network type:{0}, name:{1}, description:{2}".format( networkTypeName, name, description )
    log.info( strInfo )

    self.port = '/dev/null'
    self.baudrate = 9600
    self.parity = serial.PARITY_EVEN
    self.bytesize = 7
    self.stopbits = serial.STOPBITS_ONE
    self.timeout = 1

    # WE allow hard-coding...But not recommeneded...
    connectionParts = connectionInfo.split(',')
    connectionPartsCount = len(connectionParts)
    if connectionPartsCount > 0:
      self.port = connectionParts[0].strip()
      if self.port.find("COM4") >= 0 :
        self.port = '/dev/ttySAC3'
      elif self.port.find("COM5") >= 0 :
        self.port = '/dev/ttySAC4'
    if connectionPartsCount > 1:
      self.baudrate = int(connectionParts[1].strip())
    if connectionPartsCount > 2:
      parityBit = connectionParts[2].strip()
      if parityBit == 'E':
        self.parity = serial.PARITY_EVEN
      elif parityBit == 'O':
        self.parity = serial.PARITY_ODD
      elif parityBit == 'N':
        self.parity = serial.PARITY_NONE
      elif parityBit == 'M':
        self.parity = serial.PARITY_MARK
      elif parityBit == 'S':
        self.parity = serial.PARITY_SPACE
    if connectionPartsCount > 3:
      self.bytesize = int(connectionParts[3].strip())
    if connectionPartsCount > 4:
      stopbit = connectionParts[4].strip()
      if stopbit == '1':
        self.stopbits = serial.STOPBITS_ONE
      elif stopbit == '1.5':
        self.stopbits = serial.STOPBITS_ONE_POINT_FIVE
      elif stopbit == '2':
        self.stopbits = serial.STOPBITS_TWO
    if connectionPartsCount > 5:
      self.timeout = float(connectionParts[5].strip())


  def run(self):
    if os.name == 'nt' : # adjust this when running on PC.
      if self.port == '/dev/ttySAC3' or self.port == '/dev/ttySAC4' : # Com2,4,5 RS-485
        self.port = 'COM3' # Where USB serial port shows on my laptop...

    try:
      strDebug = "Initializing Port [{0}]: {1}, Baud:{2}, Parity:{3}, Size:{4}, stopbits:{5}, timeout:{6}".format( self.name, self.port, self.baudrate, self.parity, self.bytesize, self.stopbits, self.timeout )
      log.info( strDebug )
      connection = basicModbus.modbus(self.port, baudrate=self.baudrate, parity=self.parity, bytesize=self.bytesize, stopbits=self.stopbits, timeout=self.timeout, mode=basicModbus.MODE_ASCII)
      connection.debug = False # Change to True to debug serial communications
    except:
      connection = None
      log.exception("Error creating " + self.name + " on port " + self.port)

    while not self.stopNetwork:
      with self.lock:
        if self.requestQueue.empty():
          networkTrans = None
        else:
          networkTrans = self.requestQueue.get()

      if networkTrans is None:
        time.sleep(1)
      else:
        if connection is None:
          networkTrans.online = False
          networkTrans.offlineMessage = "Error connecting to port {0}".format( self.port )
        else:
          # do the transactions
          for transaction in networkTrans.transactions:
            if self.stopNetwork:
              break

            request = transaction.request
            response = None
            if isinstance(request, modbusConstants.readHoldingRegisters):
              response = modbusConstants.readHoldingRegistersResponse()
              try:
                connection.address = int(networkTrans.networkAddress)
                response.registers = connection.read_registers(request.startingRegister, request.count)
              except:
                networkTrans.online = False
                networkTrans.offlineMessage = "Network:{0}, Device at address:{1} not responding.  Check address or cabling.".format( self.port, connection.address )
                break

            elif isinstance(request, modbusConstants.writeHoldingRegister):
              # response has nothing to do - so this is blank
              response = modbusConstants.writeHoldingRegisterResponse()
              try:
                connection.address = int(networkTrans.networkAddress)
                connection.write_register(request.register, request.value)
              except:
                networkTrans.online = False
                networkTrans.offlineMessage = "Device at address '" + str(connection.address) + "' not responding.  Check address or cabling."
                break

            else:
              log.debug("Invalid modbus request is unknown or unimplemented: " + str(type(request)))
              networkTrans.online = False
              networkTrans.offlineMessage = "Unknown modbus request-{0}".format( request )
              break

            transaction.response = response

            time.sleep(0.02)


        with self.lock:
          self.completedQueue.put(networkTrans)




