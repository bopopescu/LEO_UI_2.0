#! /usr/bin/python



class readHoldingRegisters:
  def __init__(self, startingRegister, count):
    self.startingRegister = startingRegister
    self.count = count

class readHoldingRegistersResponse:
  def __init__(self):
    self.registers = []

class readCoilsRegisters:
  def __init__(self, startingRegister):
    self.startingRegister = startingRegister
    #self.functioncode = functioncode      #01

class readCoilsRegistersResponse:
  def __init__(self):
    self.registers = 0

class readDiscreteInputRegisters:
  def __init__(self, startingRegister):
    self.startingRegister = startingRegister
    #self.functioncode = functioncode      #02

class readDiscreteInputRegistersResponse:
  def __init__(self):
    self.registers = 0

class readInputRegisters:
  def __init__(self, startingRegister, count):
    self.startingRegister = startingRegister
    self.count = count
    #self.functioncode = functioncode      #04

class readInputRegistersResponse:
  def __init__(self):
    self.registers = 0.0

class writeHoldingRegister:
  def __init__(self, register, value):
    self.register = register
    self.value = value

class writeHoldingRegisterResponse:  
  def __init__(self):
    pass

class writeCoilsRegister:
  def __init__(self, register, value):
    self.register = register
    self.value = value

class writeCoilsRegisterResponse:  
  def __init__(self):
    pass