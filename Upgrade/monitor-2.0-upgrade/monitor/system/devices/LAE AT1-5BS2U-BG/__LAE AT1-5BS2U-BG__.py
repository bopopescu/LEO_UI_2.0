#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append( os.path.join(sys.path[0], 'system/networks') )
sys.path.append( os.path.join(sys.path[0], 'system/devices') )

from deviceConstants import *
import deviceObject

from networkConstants import *

from modbusConstants import *
# import modbusConstants

import copy
from collections import OrderedDict


import logsystem
log = logsystem.getLogger()

deviceType = "LAE AT1-5BS2U-BG"
deviceTypeName = "LAE AT1-5BS2U-BG"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

valueDescriptions = OrderedDict()

# OUTPUTS - Dedicated Register value
valueDescriptions["T1 TEMP"] = {"displayName": "T1-Air Probe", "dataType": dataTypeFloat, "unitType": unitTypeTemperature, "valueType": valueTypeOutput, "significantDigits": 1, "defaultLog":"true"}
valueDescriptions["T2 TEMP"] = {"displayName": "T2-Evap Probe", "dataType": dataTypeFloat, "unitType": unitTypeTemperature, "valueType": valueTypeOutput, "significantDigits": 1, "defaultLog":"true"}

# OUTPUT - Address 100 Status Flag bits
valueDescriptions["ALARM"] = {"displayName": "General Alarm", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["MUTE"] = {"displayName": "Alarm Mute", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["DEFROST"] = {"displayName": "Defrost Status", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"}, "defaultLog":"true" }
valueDescriptions["DOOR"] = {"displayName": "Door Status", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "Open", "false": "Closed"}, "defaultLog":"true" }

# OUTPUT - Address 101 Alarm Flag bits
valueDescriptions["T1FAILUREALARM"] = {"displayName": "T1 Probe FAILUREALARM", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["T2FAILUREALARM"] = {"displayName": "T2 Probe FAILUREALARM", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["HIGHTEMPALARM"] = {"displayName": "High Temp Alarm", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["LOWTEMPALARM"] = {"displayName": "Low Temp Alarm", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["CONDCLEANALARM"] = {"displayName": "Dirty Condenser", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }
valueDescriptions["DOOROPENALARM"] = {"displayName": "Door Open Alarm", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"} }

# OUTPUT - Address 102 Output Flag bits
valueDescriptions["COMP RLY"] = {"displayName": "Compressor", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"}, "defaultLog":"true"}
valueDescriptions["AUX RLY"] = {"displayName": "AUX", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "On", "false": "Off"}, "defaultLog":"true"}

# Virtual (function to load value)
# valueDescriptions["MDEF"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeConfig,"displayName":"MDEF","description":"Turn On Manual Defrost"}
valueDescriptions["STANDBY"] = {"displayName": "Standby Status", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeOutput, "dataList": {"true": "Standby", "false": "No"} }

# CONFIG
valueDescriptions["SCL"] = {"displayName": "SCL", "description": "Readout scale", "dataType": dataTypeList, "valueType": valueTypeConfig, "dataList": {"0": "1°C", "1": "2°C", "2": "°F"},"default":"0"}
valueDescriptions["SPL"] = {"displayName": "SPL", "description": "Minimum setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"-25.0"}
valueDescriptions["SPH"] = {"displayName": "SPH", "description": "Maximum setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"25.0"}
valueDescriptions["SP"] = {"displayName": "SP", "description": "Setpoint", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"0.0"}
valueDescriptions["CHHEATCOOL"] = {"displayName": "C-H", "description": "Refrigerating or heating mode", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeConfig, "dataList": {"true": "Heating", "false": "Cooling"},"default":"true"}
valueDescriptions["HYS"] = {"displayName": "HYS", "description": "Hysteresis", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1,"default":"3.0"}
valueDescriptions["CRT"] = {"displayName": "CRT", "description": "Compressor rest time", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"1"}
valueDescriptions["CT1"] = {"displayName": "CT1", "description": "Compressor run with sensor T1 failure", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"3"}
valueDescriptions["CT2"] = {"displayName": "CT2", "description": "Compressor stop with T1 failure", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"6"}
valueDescriptions["CSD"] = {"displayName": "CSD", "description": "Compressor stop delay after door open", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"1"}
valueDescriptions["DFR"] = {"displayName": "DFR", "description": "Defrost frequency", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "2.5 minute increments","default":"0"}
valueDescriptions["DLI"] = {"displayName": "DLI", "description": "Defrost end temperature", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"10.0"}
valueDescriptions["DTO"] = {"displayName": "DTO", "description": "Maximum defrost duration", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"30"}
valueDescriptions["DTY"] = {"displayName": "DTY", "description": "Defrost type", "dataType": dataTypeList, "valueType": valueTypeConfig, "dataList": {"14": "OFF", "15": "ELE", "16": "GAS"},"default":"14"}
valueDescriptions["DDY"] = {"displayName": "DDY", "description": "Display controls during defrost", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"0"}
valueDescriptions["ATM"] = {"displayName": "ATM", "description": "Alarm threshold management", "dataType": dataTypeList, "valueType": valueTypeConfig, "dataList": {"11": "NON", "12": "ABS", "13": "REL"},"default":"11"}
valueDescriptions["ALA"] = {"displayName": "ALA", "description": "Low temperature alarm", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"-50.0"}
valueDescriptions["AHA"] = {"displayName": "AHA", "description": "High temperature alarm", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeTemperature, "significantDigits": 1,"default":"120.0"}
valueDescriptions["ALR"] = {"displayName": "ALR", "description": "Low alarm differential", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1,"default":"0.0"}
valueDescriptions["AHR"] = {"displayName": "AHR", "description": "High alarm differential", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1,"default":"0.0"}
valueDescriptions["ATD"] = {"displayName": "ATD", "description": "Temperature alarm delay", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"60"}
valueDescriptions["ADO"] = {"displayName": "ADO", "description": "Door alarm delay", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"5"}
valueDescriptions["ACC"] = {"displayName": "ACC", "description": "Condenser cleaning", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "weeks","default":"0"}
valueDescriptions["STANDBYBUTTONENABLE"] = {"displayName": "SB","description":"Standby button enable", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"},"default":"true"}
valueDescriptions["DSDOORENABLE"] = {"displayName": "DS", "description": "Door Enable", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"},"default":"false"}
valueDescriptions["OAU"] = {"displayName": "OAU", "description": "Auxiliary output control mode", "dataType": dataTypeList, "valueType": valueTypeConfig, "dataList": {"17": "NON", "18": "O-I", "19": "DEF", "20": "LGT", "21": "ALR"},"default":"17"}
valueDescriptions["INP"] = {"displayName": "INP", "description": "Probe type selection", "dataType": dataTypeList, "valueType": valueTypeConfig, "dataList": {"3": "SN4", "4": "ST1"},"default":"3"}
valueDescriptions["OS1"] = {"displayName": "OS1", "description": "Probe T1 offset", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"0.0"}
valueDescriptions["ENABLET2"] = {"displayName": "T2", "description": "Probe T2 Enable", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"},"default":"false"}
valueDescriptions["OS2"] = {"displayName": "OS2", "description": "Probe T2 offset", "dataType": dataTypeFloat, "valueType": valueTypeConfig, "unitType": unitTypeDeltaTemperature, "significantDigits": 1,"default":"0.0"}
valueDescriptions["TLD"] = {"displayName": "TLD", "description": "Delay for min/max temperature storage", "dataType": dataTypeInt, "valueType": valueTypeConfig, "unitText": "minutes","default":"5"}
valueDescriptions["SIM"] = {"displayName": "SIM", "description": "Display slowdown", "dataType": dataTypeInt, "valueType": valueTypeConfig,"default":"3"}

# Cfg_1 Address 229
valueDescriptions["LOCKKEYBOARD"] = {"displayName": "LOC", "description": "Lock Keyboard", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeConfig, "dataList": {"true": "Yes", "false": "No"}}
valueDescriptions["STBY"] = {"displayName": "STBY", "description": "Standby", "dataType": dataTypeBool,"unitType":"OnOff", "valueType": valueTypeConfig, "dataList": {"true": "Standby", "false": "No"}}

# ALARMS
alarmDescriptions = OrderedDict()
alarmDescriptions["T1FAILUREALARM"] = {"description": "T1 Probe Failure" }
alarmDescriptions["T2FAILUREALARM"] = {"description": "T2 Probe Failure" }
alarmDescriptions["HIGHTEMPALARM"] = {"description": "High Temp" }
alarmDescriptions["LOWTEMPALARM"] = {"description": "Low Temp" }
alarmDescriptions["CONDCLEANALARM"] = {"description": "Dirty Condenser" }
alarmDescriptions["DOOROPENALARM"] = {"description": "Door Open Alarm" }


class Device(deviceObject.NetworkDeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, image, method = ""):
    deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image)

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
                      ["11", "CFG_1", 229]
               #       ["12","CMD_1",100]
    ]


  def _prepareSetDeviceConfigurationTransactions(self):
    if self._newDeviceConfigurationValues is None:
      return None

    retval = []
    networkTransTag = ""
    networkTrans = None


    for configItem in self.configModbusList:
      # [0] = MessageGroup/Tag; [1] = actual parameter, [2] = register address
      if networkTransTag != configItem[0]:
        networkTransTag = configItem[0]
        networkTrans = NetworkTransaction("WriteConfig" + networkTransTag)
        retval.append(networkTrans)

      key = configItem[1]

   #   if len(self._newDeviceConfigurationValues) == 1:
   #     value = 0
   #     value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value
   #     networkTrans.transactions.append(NetworkMessage(writeHoldingRegister(100, 0x04), "MDEF"))
   #     break

   #   if key == "CMD_1":
   #     value = 0
   #     if "MDEF" in self._newDeviceConfigurationValues:
   #       value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value

      if key == "CFG_1":
        value = 0
        value = value | 0x01 if self._newDeviceConfigurationValues["DSDOORENABLE"] else value
        value = value | 0x02 if self._newDeviceConfigurationValues["CHHEATCOOL"] else value
        value = value | 0x04 if self._newDeviceConfigurationValues["ENABLET2"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["LOCKKEYBOARD"] else value
        value = value | 0x40 if self._newDeviceConfigurationValues["STBY"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["STANDBYBUTTONENABLE"] else value

      else:
        newConfigValue = self._newDeviceConfigurationValues[key]

     # LEO sending data to Device
        if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
          if (self._newDeviceConfigurationValues["SCL"]) == "2" or (self._newDeviceConfigurationValues["SCL"]) == 2:
            if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
              newConfigValue = self._convertC2F(newConfigValue)
            elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
              newConfigValue = self._convertDeltaC2F(newConfigValue)
          elif (self._newDeviceConfigurationValues["SCL"]) == "0" or (self._newDeviceConfigurationValues["SCL"]) == 0:
            newConfigValue = newConfigValue * 10.0
          value = self._convertFromFloatValue(newConfigValue)
        elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
          value = 0 if newConfigValue == False else 1
        else:
          value = self._convertFromIntValue(newConfigValue)
      networkTrans.transactions.append(NetworkMessage(writeHoldingRegister(configItem[2], value), configItem[1]))
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
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(configItem[2], 1), configItem[1]))
    return retval

  def _prepareLoggingTransactions(self, valueToLog):
    if len(valueToLog) == 0:
      return None

    networkTrans = NetworkTransaction("Logging")

    if "T1 TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(0, 1), "T1 TEMP"))

    if "T2 TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(1, 1), "T2 TEMP"))

    setValueToLog = set(valueToLog)
    setStatusFlag = set(["ALARM", "MUTE", "DEFROST", "DOOR"])
    if len(setValueToLog & setStatusFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "StatusFlag"))

    # Alarm flag
    setAlarmFlag = set(["T1FAILUREALARM", "T2FAILUREALARM", "HIGHTEMPALARM", "LOWTEMPALARM", "CONDCLEANALARM", "DOOROPENALARM"])
    if len(setValueToLog & setAlarmFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(101, 1), "AlarmFlag"))

    # Output flag
    setOutputFlag = set(["COMP RLY", "AUX RLY"])
    if len(setValueToLog & setOutputFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "OutputFlag"))

    # Standby flag
    setStandbyFlag = set(["STANDBY"])
    if len(setValueToLog & setStandbyFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(229, 1), "StandbyFlag"))

    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    networkTrans = NetworkTransaction("Status1")
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(0, 1), "T1 TEMP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(1, 1), "T2 TEMP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(203, 1), "SP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "StatusFlag"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "OutputFlag"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(229, 1), "StandbyFlag"))
    return [ networkTrans ] + self._prepareUpdateAlarmsTransactions()


  def _prepareUpdateAlarmsTransactions(self):
    networkTrans = NetworkTransaction("Alarms")
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(101, 1), "AlarmFlag")) # function 3
    return [ networkTrans ]


  def _executeTransaction(self, networkTrans):
    if not networkTrans.online:
      self._nullOutputValues()
    else:

      for transaction in networkTrans.transactions:
        with self.lock:
          if isinstance(transaction.response, readHoldingRegistersResponse):
            value = transaction.response.registers[0]

            if transaction.tag == "StatusFlag":
              self._values["ALARM"] = ((value & 0x01) > 0)
              self._alarm = self._values["ALARM"]
              self._values["MUTE"] = ((value & 0x02) > 0)
              self._values["DEFROST"] = ((value & 0x04) > 0)
              self._values["DOOR"] = ((value & 0x08) > 0)

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

            elif transaction.tag == "OutputFlag":
              self._values["COMP RLY"] = ((value & 0x01) > 0)
              self._values["AUX RLY"] = ((value & 0x02) > 0)

            elif transaction.tag == "StandbyFlag":
              self._values["STANDBY"] = ((value & 0x40) > 0)

            elif transaction.tag == "CFG_1":
              self._values["DSDOORENABLE"] = ((value & 0x01) > 0)
              self._values["CHHEATCOOL"] = ((value & 0x02) > 0)
              self._values["ENABLET2"] = ((value & 0x04) > 0)
              self._values["LOCKKEYBOARD"] = ((value & 0x20) > 0)
              self._values["STBY"] = ((value & 0x40) > 0)
              self._values["STANDBYBUTTONENABLE"] = ((value & 0x80) > 0)

        #    elif transaction.tag == "CMD_1":
        #      self._values["MDEF"] = ((value & 0x4) > 0)

            else:    # LEO reading up from Device
              key = transaction.tag
              if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
                self._values[key] = self._convertToFloatValue(value)
                if self._values["SCL"] == 2:
                  if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                    self._values[key] = self._convertF2C(self._values[key])
                  elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                    self._values[key] = self._convertDeltaF2C(self._values[key])
                elif self._values["SCL"] == 0:
                  self._values[key] = self._values[key] / 10.0
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


