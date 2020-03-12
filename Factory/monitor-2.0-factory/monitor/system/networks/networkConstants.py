#! /usr/bin/python

# These are network type constants
# Each network object should include this and declare its type

# Don't change these ever
networkModbusASCII = "modbusASCII"
networkModbusRTU = "modbusRTU"
networkE2IP = "e2ip"
networkE2Net = "e2Net"
networkSiteSupervisorIP = "siteip"
networkSiteSupervisorNet = "siteNet"

networkAKSC255IP = "sc255ip"
networkAKSC255Net = "sc255Net"
AKSC255_SETTINGS_TABLE_NAME = "AKSC255Settings"
# These are textual representations that can be localized
networkModbusASCIIText = "Modbus ASCII"
networkModbusRTUText = "Modbus RTU"
networkE2NetText = "E2 Network"
networkAKSC255NetText = "AKSC255" #It used to be AK-SC255 Net
networkSiteSupervisorNetText = "SiteSupervisor"

# This must be a dict show ALL network types and port connection options. It will be used as options for the connection information and validated when saved on the
# system configuration page.
networkPortSettings = { "E2 Network" : ["Not Needed"], "Modbus ASCII" : [ "COM4, 9600, E, 7, 1", "COM5, 9600, E, 7, 1" ], "Modbus RTU" : [ "COM4, 9600, E, 8, 1", "COM5, 9600, E, 8, 1" ], "AKSC255" : ["Not Needed"] , "SiteSupervisor" : ["Not Needed"] }

class NetworkTransaction:
  def __init__(self, tag=""):
    self.forLogging = False
    self.tag = tag
    self.transactions = []

    self.name = ""
    self.network = ""
    self.networkAddress = ""
    self.priority = 10

    self.online = True
    self.offlineMessage = ""

  def __eq__(self, other):
    return self.name == other.name and self.tag == other.tag

class NetworkMessage:
  def __init__(self, request, tag=""):
    self.tag = tag
    self.request = request
    self.response = None

