#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append( os.path.join(sys.path[0], 'system/networks') )
sys.path.append( os.path.join(sys.path[0], 'system/devices') )

from deviceConstants import *
import deviceObject

from networkConstants import *

import modbusConstants

import copy
from collections import OrderedDict

import logsystem
log = logsystem.getLogger()

deviceType = "LAE AT1-5"
deviceTypeName = "LAE AT1-5"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

valueDescriptions = OrderedDict()

# OUTPUTS - Dedicated Register value
valueDescriptions["T1"] = {"displayName": "T1-Air Probe", "dataType": dataTypeFloat, "unitType": unitTypeTemperature, "valueType": valueTypeOutput, "significantDigits": 1, "defaultLog":"true"}
valueDescriptions["T2"] = {"displayName": "T2-Evaporator Probe", "dataType": dataTypeFloat, "unitType": unitTypeTemperature, "valueType": valueTypeOutput, "significantDigits": 1, "defaultLog":"true"}
valueDescriptions["SPO"] = {"displayName": "Set Point", "dataType": dataTypeFloat, "unitType": unitTypeTemperature, "valueType": valueTypeOutput, "significantDigits": 1, "defaultLog":"true"}

# OUTPUT - Status Flag bits
valueDescriptions["ALARM"] = {"displayName": "General Alarm", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["MUTE"] = {"displayName": "Alarm Mute", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"}, "defaultLog":"true" }
valueDescriptions["DEF"] = {"displayName": "Defrost Active", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"}, "defaultLog":"true" }
valueDescriptions["DOOR"] = {"displayName": "Door Open", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"}, "defaultLog":"true" }

# OUTPUT - Alarm bits
valueDescriptions["T1FAILUREALARM"] = {"displayName": "T1 Probe FAILUREALARM", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["T2FAILUREALARM"] = {"displayName": "T2 Probe FAILUREALARM", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["HIGHTEMPALARM"] = {"displayName": "High Temp Alarm", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["LOWTEMPALARM"] = {"displayName": "Low Temp Alarm", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["CONDCLEANALARM"] = {"displayName": "Dirty Condenser", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["DOOROPENALARM"] = {"displayName": "Door Open Alarm", "dataType": dataTypeBool, "valueType": valueTypeOutput, "dataList": {"true": "Yes", "false": "No"} }

# CONFIG
valueDescriptions["SCL"] = {"displayName": "SCL", "description": "Readout scale", "dataType": dataTypeList, "valueType": valueTypeConfig, "default": "0", "dataList": {"0": "1°C", "1": "2°C", "2": "°F"} }
valueDescriptions["SPL"] = {"displayName": "SPL", "description": "Minimum setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["SPH"] = {"displayName": "SPH", "description": "Maximum setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["SP"] = {"displayName": "SP", "description": "Setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["HYS"] = {"displayName": "HYS", "description": "Hysteresis", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1}
valueDescriptions["CRT"] = {"displayName": "CRT", "description": "Compressor rest time", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["CT1"] = {"displayName": "CT1", "description": "Compressor run with sensor T1 failure", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["CT2"] = {"displayName": "CT2", "description": "Compressor stop with T1 failure", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["CSD"] = {"displayName": "CSD", "description": "Compressor stop delay after door open", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["DFR"] = {"displayName": "DFR", "description": "Defrost frequency", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "2.5 minute increments" }
valueDescriptions["DLI"] = {"displayName": "DLI", "description": "Defrost end temperature", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["DTO"] = {"displayName": "DTO", "description": "Maximum defrost duration", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["DTY"] = {"displayName": "DTY", "description": "Defrost type", "dataType": dataTypeList, "valueType": valueTypeConfig, "default": "14", "dataList": {"14": "OFF", "15": "ELE", "16": "GAS"} }
valueDescriptions["DDY"] = {"displayName": "DDY", "description": "Display controls during defrost", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["ATM"] = {"displayName": "ATM", "description": "Alarm threshold management", "dataType": dataTypeList, "valueType": valueTypeConfig, "default": "0", "dataList": {"11": "NON", "12": "ABS", "13": "REL"} }
valueDescriptions["ALA"] = {"displayName": "ALA", "description": "Low temperature alarm", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["AHA"] = {"displayName": "AHA", "description": "High temperature alarm", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1}
valueDescriptions["ALR"] = {"displayName": "ALR", "description": "Low alarm differential", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1}
valueDescriptions["AHR"] = {"displayName": "AHR", "description": "High alarm differential", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1}
valueDescriptions["ATD"] = {"displayName": "ATD", "description": "Temperature alarm delay", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["ADO"] = {"displayName": "ADO", "description": "Door alarm delay", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["ACC"] = {"displayName": "ACC", "description": "Condenser cleaning", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "weeks" }
valueDescriptions["OAU"] = {"displayName": "OAU", "description": "Auxiliary output control mode", "dataType": dataTypeList, "valueType": valueTypeConfig, "default": "17", "dataList": {"17": "NON", "18": "O-I", "19": "DEF", "20": "LGT", "21": "ALR"} }
valueDescriptions["INP"] = {"displayName": "INP", "description": "Probe type selection", "dataType": dataTypeList, "valueType": valueTypeConfig, "default": "3", "dataList": {"3": "SN4", "4": "ST1"} }
valueDescriptions["OS1"] = {"displayName": "OS1", "description": "Probe T1 offset", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1}
valueDescriptions["OS2"] = {"displayName": "OS2", "description": "Probe T2 offset", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1}
valueDescriptions["TLD"] = {"displayName": "TLD", "description": "Delay for min/max temperature storage", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes" }
valueDescriptions["SIM"] = {"displayName": "SIM", "description": "Display slowdown", "dataType": dataTypeInt, "valueType": valueTypeConfig }


valueDescriptions["DSDOORENABLE"] = {"displayName": "DSDoorEnable", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["CHHEATCOOL"] = {"displayName": "C-H", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Heating", "false": "Cooling"} }
valueDescriptions["ENABLET2"] = {"displayName": "Enable T2 Probe", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["LOCKKEYBOARD"] = {"displayName": "Lock Keyboard", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["STANDBY"] = {"displayName": "Standby", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"} }
valueDescriptions["STANDBYBUTTONENABLE"] = {"displayName": "Standby Button Enable", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"} }

# ALARMS
alarmDescriptions = OrderedDict()
alarmDescriptions["T1FAILUREALARM"] = {"description": "T1 Probe Failure" }
alarmDescriptions["T2FAILUREALARM"] = {"description": "T2 Probe Failure" }
alarmDescriptions["HIGHTEMPALARM"] = {"description": "High Temp" }
alarmDescriptions["LOWTEMPALARM"] = {"description": "Low Temp" }
alarmDescriptions["CONDCLEANALARM"] = {"description": "Dirty Condenser" }
alarmDescriptions["DOOROPENALARM"] = {"description": "Door Open Alarm" }


class Device(deviceObject.NetworkDeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, image ):
    deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image )

    self._valueDescriptions = valueDescriptions
    self._alarmDescriptions = alarmDescriptions

    self.loadValuesFromDatabase()
    self.loadAdvisoriesFromDatabase()

    self.configModbusList = [
                      ["1", "SCL", 200],
                      ["1", "SPL", 201],
                      ["1", "SPH", 202],

                      ["2", "SP",  203],
                      ["2", "HYS", 204],
                      ["2", "CRT", 205],

                      ["3", "CT1", 206],
                      ["3", "CT2", 207],
                      ["3", "CSD", 208],

                      ["4", "DFR", 209],
                      ["4", "DLI", 210],
                      ["4", "DTO", 211],

                      ["5", "DTY", 212],
                      ["5", "DDY", 213],
                      ["5", "ATM", 214],

                      ["6", "ALA", 215],
                      ["6", "AHA", 216],
                      ["6", "ALR", 217],

                      ["7", "AHR", 218],
                      ["7", "ATD", 219],
                      ["7", "ADO", 220],

                      ["8", "ACC", 221],
                      ["8", "OAU", 222],
                      ["8", "INP", 223],

                      ["9", "OS1", 224],
                      ["9", "OS2", 225],
                      ["9", "TLD", 226],

                      ["10", "SIM", 227],
                      ["10", "CFG_1", 229]
                   ]



  def _prepareSetDeviceConfigurationTransactions(self):
    if self._newDeviceConfigurationValues is None:
      return None

    retval = []
    networkTransTag = ""
    networkTrans = None


    for configItem in self.configModbusList:
      if networkTransTag != configItem[0]:
        networkTransTag = configItem[0]
        networkTrans = NetworkTransaction("WriteConfig" + networkTransTag)
        retval.append(networkTrans)


      key = configItem[1]

      if key == "CFG_1":
        value = value | 0x01 if self._newDeviceConfigurationValues["DSDOORENABLE"] else value
        value = value | 0x02 if self._newDeviceConfigurationValues["CHHEATCOOL"] else value
        value = value | 0x04 if self._newDeviceConfigurationValues["ENABLET2"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["LOCKKEYBOARD"] else value
        value = value | 0x40 if self._newDeviceConfigurationValues["STANDBY"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["STANDBYBUTTONENABLE"] else value

      else:
        newConfigValue = self._newDeviceConfigurationValues[key]

        if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
          if int(self._values["SCL"]) == 2:    # this is deliberate as SCL will be set as the first one and we need to see if conversion is neede
            if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
              newConfigValue = self._convertC2F(newConfigValue)
            elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
              newConfigValue = self._convertDeltaC2F(newConfigValue)
          value = self._convertFromFloatValue(newConfigValue)

        elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
          value = 0 if newConfigValue == False else 1
        else:
          value = self._convertFromIntValue(newConfigValue)

      networkTrans.transactions.append(NetworkMessage(modbusConstants.writeHoldingRegister(configItem[2], value), configItem[1]))
    return retval

  def _prepareUpdateDeviceConfigurationTransactions(self):
    retval = []
    networkTransTag = ""
    networkTrans = None

    for configItem in self.configModbusList:
      if networkTransTag != configItem[0]:
        networkTransTag = configItem[0]
        networkTrans = NetworkTransaction("ReadConfig" + networkTransTag)
        retval.append(networkTrans)
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(configItem[2], 1), configItem[1]))
    return retval

  def _prepareLoggingTransactions(self, valueToLog):
    if len(valueToLog) == 0:
      return None

    networkTrans = NetworkTransaction("Logging")

    if "T1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(0, 1), "T1"))  # function 3

    if "T2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(1, 1), "T2")) # function 3

    if "SPO" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(203, 1), "SPO"))  # function 3

    setValueToLog = set(valueToLog)
    setStatusFlag = set(["ALARM", "MUTE", "DEF", "DOOR"])
    setAlarmFlag = set(["T1FAILUREALARM", "T2FAILUREALARM", "HIGHTEMPALARM", "LOWTEMPALARM", "CONDCLEANALARM", "DOOROPENALARM"])

    if len(setValueToLog & setStatusFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(100, 1), "StatusFlag"))  # function 3

    if len(setValueToLog & setAlarmFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(101, 1), "AlarmFlag")) # function 3

    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    networkTrans = NetworkTransaction("Status1")
    networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(0, 1), "T1"))  # function 3
    networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(1, 1), "T2")) # function 3
    networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(203, 1), "SPO")) # function 3
    networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(100, 1), "StatusFlag"))  # function 3
    return [ networkTrans ] + self._prepareUpdateAlarmsTransactions()

  def _prepareUpdateAlarmsTransactions(self):
    networkTrans = NetworkTransaction("Alarms")
    networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(101, 1), "AlarmFlag")) # function 3
    return [ networkTrans ]


  def _executeTransaction(self, networkTrans):
    if not networkTrans.online:
      self._nullOutputValues()
    else:

      for transaction in networkTrans.transactions:
        with self.lock:
          if isinstance(transaction.response, modbusConstants.readHoldingRegistersResponse):
            value = transaction.response.registers[0]

            if transaction.tag == "StatusFlag":
              self._values["ALARM"] = ((value & 0x01) > 0)
              self._values["MUTE"] = ((value & 0x02) > 0)
              self._values["DEF"] = ((value & 0x04) > 0)
              self._values["DOOR"] = ((value & 0x08) > 0)
              self._alarm = self._values["ALARM"]

            elif transaction.tag == "AlarmFlag":
              self._values["T1FAILUREALARM"] = ((value & 0x01) > 0)
              self.checkBooleanAdvisory("T1FAILUREALARM", self._values["T1FAILUREALARM"])
              self._values["T2FAILUREALARM"] = ((value & 0x02) > 0)
              self.checkBooleanAdvisory("T2FAILUREALARM", self._values["T2FAILUREALARM"])
              self._values["HIGHTEMPALARM"] = ((value & 0x04) > 0)
              self.checkBooleanAdvisory("HIGHTEMPALARM", self._values["HIGHTEMPALARM"])
              self._values["LOWTEMPALARM"] = ((value & 0x08) > 0)
              self.checkBooleanAdvisory("LOWTEMPALARM", self._values["LOWTEMPALARM"])
              self._values["CONDCLEANALARM"] = ((value & 0x10) > 0)
              self.checkBooleanAdvisory("CONDCLEANALARM", self._values["CONDCLEANALARM"])
              self._values["DOOROPENALARM"] = ((value & 0x20) > 0)
              self.checkBooleanAdvisory("DOOROPENALARM", self._values["DOOROPENALARM"])

            elif transaction.tag == "CFG_1":
              self._values["DSDOORENABLE"] = ((value & 0x01) > 0)
              self._values["CHHEATCOOL"] = ((value & 0x02) > 0)
              self._values["ENABLET2"] = ((value & 0x04) > 0)
              self._values["LOCKKEYBOARD"] = ((value & 0x20) > 0)
              self._values["STANDBY"] = ((value & 0x40) > 0)
              self._values["STANDBYBUTTONENABLE"] = ((value & 0x80) > 0)

            else:
              key = transaction.tag
              if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
                self._values[key] = self._convertToFloatValue(value)
                if int(self._values["SCL"]) == 2:
                  if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                    self._values[key] = self._convertF2C(self._values[key])
                  elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                    self._values[key] = self._convertDeltaF2C(self._values[key])

              elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
                self._values[key] = False if value == 0 else True
              else:
                self._values[key] = self._convertToIntValue(value)

      if "ReadConfig" in networkTrans.tag:
        self.saveValuesToDatabase()
      elif "WriteConfig" in networkTrans.tag:
        self.updateDeviceConfiguration()


  def _convertF2C(self, value):
    return (value - 32) / 1.8

  def _convertC2F(self, value):
    return (value * 1.8) + 32

  def _convertDeltaF2C(self, value):
    return value / 1.8

  def _convertDeltaC2F(self, value):
    return value * 1.8

  def _convertToFloatValue(self, value):
    if value > 0x7fff:
      return float(value - 0x10000)
    return float(value)

  def _convertFromFloatValue(self, value):
    if value < 0:
      return int(round(value + 0x10000))
    return int(round(value))

  def _convertToIntValue(self, value):
    if value > 0x7fff:
      return int(value - 0x10000)
    return int(value)

  def _convertFromIntValue(self, value):
    if value < 0:
      return int(value + 0x10000)
    return int(value)


