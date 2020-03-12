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

deviceType = "LAE AR2-5C14W-BG"
deviceTypeName = "LAE AR2-5C14W-BG"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

timeList = OrderedDict()
timeListWithSkip = OrderedDict()
for idx in xrange(144):
  timeList[str(idx)] = "%s:%s0" % (str(idx / 6), str(idx % 6))
  timeListWithSkip[str(idx)] = "%s:%s0" % (str(idx / 6), str(idx % 6))
timeListWithSkip['144'] = '---'

valueDescriptions = OrderedDict()
# OUTPUTS - Dedicated Register value
valueDescriptions["T1 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T1-Air Probe","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T2 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T2-Evap Probe","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T3 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T3 Temp","unitType":unitTypeTemperature, "defaultLog":"true"}
# OUTPUT - Status Flag bits
# 100 - Status flag
valueDescriptions["ALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Alarm"}
valueDescriptions["MUTE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Mute", "false": "-"},"valueType":valueTypeOutput,"displayName":"Mute"}
valueDescriptions["DEFROST"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost Status", "defaultLog":"true"}
valueDescriptions["DOOR"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Door Status", "defaultLog":"true"}
# 101 - Alarm flag
valueDescriptions["T1PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T1 Probe Alarm","description":"T1 Probe Alarm"}
valueDescriptions["T2PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T2 Probe Alarm","description":"T2 Probe Alarm"}
valueDescriptions["T3PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T3 Probe Alarm","description":"T3 Probe Alarm"}
valueDescriptions["HIGHTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Temp Alarm","description":"High Temp Alarm"}
valueDescriptions["LOWTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Low Temp Alarm","description":"Low Temp Alarm"}
valueDescriptions["HIGHCONDALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Generic Alarm","description":"Generic Alarm"}
valueDescriptions["HIGHPRESALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Pressure Alarm","description":"High Pressure Alarm"}
valueDescriptions["DOOROPENALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Door Open Alarm","description":"Door Open Alarm"}
valueDescriptions["CONDCLEANALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Condenser Clean Alarm","description":"Condenser Clean Alarm"}
# 102 - Output flag
valueDescriptions["AUX1 RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Aux 1", "defaultLog":"true"}
valueDescriptions["COMP RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Compressor", "defaultLog":"true"}
valueDescriptions["DEF RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost", "defaultLog":"true"}
valueDescriptions["FAN RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Evaporator Fan", "defaultLog":"true"}
# Virtual (function to load value)
valueDescriptions["MDEF"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeConfig,"displayName":"MDEF","description":"Turn On Manual Defrost"}
valueDescriptions["STANDBY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeOutput,"displayName":"Standby Status"}
valueDescriptions["DIG Input 2"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Active", "false": "NotAct"},"valueType":valueTypeOutput,"displayName":"Digital Input 2", "defaultLog":"true","default":"0"}
# CONFIG
#CFG REGISTERS
valueDescriptions["SCL"] = {"displayName":"SCL","description":"Readout scale","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"1°C","1":"2°C","2":"°F"},"default":"0"}
valueDescriptions["SPL"] = {"displayName":"SPL","description":"Minimum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-25.0"}
valueDescriptions["SPH"] = {"displayName":"SPH","description":"Maximum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"25.0"}
valueDescriptions["SP"] = {"displayName":"SP","description":"Setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["C-H"] = {"dataType":dataTypeBool,"dataList":{"true":"HEA", "false": "REF"},"valueType":valueTypeConfig,"displayName":"C-H","description":"Refrigerating or heating mode"}
valueDescriptions["HYS"] = {"displayName":"HYS","description":"Thermostat off to on differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"3.0"}
valueDescriptions["CRT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRT","description":"Compressor rest time","unitText":"min","default":"1"}
valueDescriptions["CT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT1","description":"Output run when probe T1 is faulty","unitText":"min","default":"3"}
valueDescriptions["CT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT2","description":"Output stop when probe T1 is faulty","unitText":"min","default":"6"}
valueDescriptions["CSD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSD","description":"Stop delay after door has opened","unitText":"min","default":"1"}
valueDescriptions["DFM"] = {"displayName":"DFM","description":"Default start mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TIM","2":"FRO"},"default":"0"}
valueDescriptions["DFT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DFT","description":"Timer value for automatic defrost to start","unitText":"hrs","default":"6"}
valueDescriptions["DH1"] = {"displayName":"DH1","description":"Defrost time 1","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH2"] = {"displayName":"DH2","description":"Defrost time 2","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH3"] = {"displayName":"DH3","description":"Defrost time 3","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH4"] = {"displayName":"DH4","description":"Defrost time 4","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH5"] = {"displayName":"DH5","description":"Defrost time 5","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH6"] = {"displayName":"DH6","description":"Defrost time 6","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DLI"] = {"displayName":"DLI","description":"Defrost end temperature","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"10.0"}
valueDescriptions["DTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DTO","description":"Maximum defrost duration","unitText":"min","default":"30"}
valueDescriptions["DTY"] = {"displayName":"DTY","description":"Defrost type","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"ELE","2":"GAS"},"default":"0"}
valueDescriptions["DPD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DPD","description":"Pump down time","unitText":"sec","default":"0"}
valueDescriptions["DRN"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DRN","description":"Drip time","unitText":"min","default":"3"}
valueDescriptions["DDM"] = {"displayName":"DDM","description":"Display defrost mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"RT","1":"LT","2":"SP","3":"DEF"},"default":"3"}
valueDescriptions["DDY"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DDY","description":"Display delay","unitText":"min","default":"10"}
valueDescriptions["FID"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"FID","description":"Fans active during defrost","default":"false"}
valueDescriptions["FDD"] = {"displayName":"FDD","description":"Fan restart temperature after defrost","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-5.0"}
valueDescriptions["FTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FTO","description":"Maximum fan stop after defrost","unitText":"min","default":"0"}
valueDescriptions["FCM"] = {"displayName":"FCM","description":"Fan mode during thermostatic control","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["FDT"] = {"displayName":"FDT","description":"Evap-air temp difference to turn OFF fans","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"-2.0"}
valueDescriptions["FDH"] = {"displayName":"FDH","description":"Temp differential for fan restart","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"3.0"}
valueDescriptions["FT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT1","description":"Fan stop delay after stop","unitText":"sec","default":"30"}
valueDescriptions["FT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT2","description":"Timed fan stop","unitText":"min","default":"3"}
valueDescriptions["FT3"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT3","description":"Timed fan run","unitText":"min","default":"0"}
valueDescriptions["ATM"] = {"displayName":"ATM","description":"Alarm threshold management","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ABS","2":"REL"},"default":"0"}
valueDescriptions["ALA"] = {"displayName":"ALA","description":"Low temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-50.0"}
valueDescriptions["AHA"] = {"displayName":"AHA","description":"High temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"120.0"}
valueDescriptions["ALR"] = {"displayName":"ALR","description":"Low temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["AHR"] = {"displayName":"AHR","description":"High temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["ATI"] = {"displayName":"ATI","description":"Probe used for temperature alarm detection","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"T2","2":"T3"},"default":"0"}
valueDescriptions["ATD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ATD","description":"Delay before alarm termperature warning","unitText":"min","default":"60"}
valueDescriptions["ADO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ADO","description":"Door alarm delay","unitText":"min","default":"5"}
valueDescriptions["AHM"] = {"displayName":"AHM","description":"High condenser alarm operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["AHT"] = {"displayName":"AHT","description":"Condensation temp alarm","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"60.0"}
valueDescriptions["ACC"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ACC","description":"Condenser periodic cleaning","unitText":"weeks","default":"0"}
valueDescriptions["IISM"] = {"displayName":"IISM","description":"Switchover mode to second param set","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"HDD","3":"DI"},"default":"0"}
valueDescriptions["IISL"] = {"displayName":"IISL","description":"Minimum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-25.0"}
valueDescriptions["IISH"] = {"displayName":"IISH","description":"Maximum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"25.0"}
valueDescriptions["IISP"] = {"displayName":"IISP","description":"Setpoint [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-20.0"}
valueDescriptions["IIHY"] = {"displayName":"IIHY","description":"Thermostat off to on differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"4.0"}
valueDescriptions["IIFC"] = {"displayName":"IIFC","description":"Fan mode during thermostatic control [II]","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["HDS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"HDS","description":"Sensibility econ > heavy duty","default":"3"}
valueDescriptions["IIDF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDF","description":"Timer value for automatic defrost to start [II]","unitText":"hrs","default":"6"}
valueDescriptions["SB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"SB","description":"Standby button enable","default":"true"}
valueDescriptions["DS"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"DS","description":"Door enabled","default":"false"}
valueDescriptions["DI2"] = {"displayName":"D12","description":"DI2 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"HPS","2":"IISM","3":"RDS","4":"DSY"},"default":"0"}
valueDescriptions["LSM"] = {"displayName":"LSM","description":"Light control mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"DOR"},"default":"0"}
valueDescriptions["OA1"] = {"displayName":"OA1","description":"AUX 1 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"0-1","2":"LGT","3":"2CU","4":"2EU","5":"ALO","6":"AL1"},"default":"0"}
valueDescriptions["2CD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"2CD","description":"Aux compressor start delay","unitText":"sec","default":"3"}
valueDescriptions["INP"] = {"displayName": "INP", "description": "Probe type selection", "dataType": dataTypeBool, "valueType": valueTypeConfig, "dataList":{"true": "SNT1", "false": "SN4"},"default":"false"}
valueDescriptions["OS1"] = {"displayName":"OS1","description":"Probe T1 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["T2"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"T2","description":"Probe T2 enable","default":"false"}
valueDescriptions["OS2"] = {"displayName":"OS2","description":"Probe T2 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["T3"] = {"displayName":"T3","description":"Probe 3 operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DSP","2":"CND","3":"2EU"},"default":"0"}
valueDescriptions["OS3"] = {"displayName":"OS3","description":"Probe T3 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["TLD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"TLD","description":"Delay for min and max temp logging","unitText":"min","default":"5"}
# valueDescriptions["TDS"] = {"displayName":"TDS","description":"Selects temp probe to display","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"1-2","2":"T3"},"default":"0"}
valueDescriptions["SIM"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SIM","description":"Display slowdown","default":"3"}
#272 CFG_1 BITS
valueDescriptions["LOC"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LOC","description":"Keyboard lock"}
valueDescriptions["STBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeConfig,"displayName":"STBY","description":"Standby"}
#273 CFG_2 BITS
valueDescriptions["LIGHTS"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LIGHTS","description":"Manual lights"}
# ALARM
alarmDescriptions = OrderedDict()
alarmDescriptions["T1PROBEALARM"] = {"description": "T1 Probe Alarm"}
alarmDescriptions["T2PROBEALARM"] = {"description": "T2 Probe Alarm"}
alarmDescriptions["T3PROBEALARM"] = {"description": "T3 Probe Alarm"}
alarmDescriptions["HIGHTEMPALARM"] = {"description": "High Temp Alarm"}
alarmDescriptions["LOWTEMPALARM"] = {"description": "Low Temp Alarm"}
alarmDescriptions["HIGHCONDALARM"] = {"description": "Generic Alarm"}
alarmDescriptions["HIGHPRESALARM"] = {"description": "High Pressure Alarm"}
alarmDescriptions["DOOROPENALARM"] = {"description": "Door Open Alarm"}
alarmDescriptions["CONDCLEANALARM"] = {"description": "Condenser Clean Alarm"}



class Device(deviceObject.NetworkDeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, image, method = ""):
    deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image)

    self._valueDescriptions = valueDescriptions
    self._alarmDescriptions = alarmDescriptions

    self.loadValuesFromDatabase()
    self.loadAdvisoriesFromDatabase()

    self.userAction = None

    self.configModbusList = [
            ["1","SPL",200],
            ["1","IISL",201],
            ["1","SPH",202],
            ["2","IISH",203],
            ["2","SP",204],
            ["2","IISP",205],
            ["3","DLI",206],
            ["3","FDD",207],
            ["3","ALA",208],
            ["4","AHA",209],
            ["4","AHT",210],
            ["5","HYS",214],
            ["5","IIHY",215],
            ["5","CRT",216],
            ["6","CT1",217],
            ["6","CT2",218],
            ["6","CSD",219],
            ["7","2CD",220],
            ["7","DFM",221],
            ["7","DFT",222],
            ["8","IIDF",223],
            ["8","DTO",224],
            ["8","DTY",225],
            ["9","DPD",226],
            ["9","DRN",227],
            ["9","DDM",228],
            ["10","DDY",229],
            ["10","FTO",230],
            ["10","FCM",231],
            ["11","IIFC",232],
            ["11","FDT",233],
            ["11","FDH",234],
            ["12","FT1",235],
            ["12","FT2",236],
            ["12","FT3",237],
            ["13","ATM",238],
            ["13","ALR",239],
            ["13","AHR",240],
            ["14","ATI",241],
            ["14","ATD",242],
            ["14","ADO",243],
            ["15","AHM",244],
            ["15","ACC",245],
            ["15","HDS",246],
            ["16","IISM",247],
            ["16","LSM",248],
            ["16","OA1",249],
            ["17","T3",250],
            ["17","DI2",251],
            ["17","TLD",252],
            ["18","SCL",253],
            ["18","SIM",254],
            ["19","OS1",256],
            ["19","OS2",257],
            ["19","OS3",258],
            ["20","CFG_1",272],
            ["20","CFG_2",273],
            ["20","DH1",274],
            ["21","DH2",275],
            ["21","DH3",276],
            ["21","DH4",277],
            ["22","DH5",278],
            ["22","DH6",279],
            ["23","CMD_1",100]
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

      if len(self._newDeviceConfigurationValues) == 1:
        value = 0
        value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value
        networkTrans.transactions.append(NetworkMessage(writeHoldingRegister(100, 0x04), "MDEF"))
        break

      if key == "CMD_1":
        value = 0
        if "MDEF" in self._newDeviceConfigurationValues:
          value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value

      elif key == "CFG_1":
        value = 0
        value = value | 0x1 if self._newDeviceConfigurationValues["T2"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["FID"] else value
        value = value | 0x40 if self._newDeviceConfigurationValues["LOC"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["STBY"] else value


      elif key == "CFG_2":
        value = 0
        value = value | 0x1 if self._newDeviceConfigurationValues["DS"] else value
        value = value | 0x2 if self._newDeviceConfigurationValues["C-H"] else value
        value = value | 0x4 if self._newDeviceConfigurationValues["INP"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["LIGHTS"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["SB"] else value

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

  def _prepareListOfTransactions(self, modbusList, tagPrefix):
    retval = []
    networkTransTag = ""
    networkTrans = None

    for item in modbusList:
      if networkTransTag != item[0]:
        networkTransTag = item[0]
        networkTrans = NetworkTransaction(tagPrefix + networkTransTag)
        retval.append(networkTrans)
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(item[2], 1), item[1]))
    return retval

  def _prepareUpdateDeviceConfigurationTransactions(self):
    return self._prepareListOfTransactions(self.configModbusList, "ReadConfig")


  def _prepareLoggingTransactions(self, valueToLog):
    if len(valueToLog) == 0:
      return None

    networkTrans = NetworkTransaction("Logging")

    if "T1 TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(0, 1), "T1 TEMP"))

    if "T2 TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(1, 1), "T2 TEMP"))

    if "T3 TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(2, 1), "T3 TEMP"))

    # Status flag
    setValueToLog = set(valueToLog)
    setStatusFlag = set(["ALARM","MUTE","DEFROST","DOOR"])
    if len(setValueToLog & setStatusFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "100_bitfield"))

    # Alarm flag
    setAlarmFlag = set(["T1PROBEALARM","T2PROBEALARM","T3PROBEALARM","HIGHTEMPALARM","LOWTEMPALARM","HIGHCONDALARM","HIGHPRESALARM","DOOROPENALARM","CONDCLEANALARM"])
    if len(setValueToLog & setAlarmFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(101, 1), "101_bitfield"))

    # Output flag
    setOutputFlag = set(["AUX1 RLY","COMP RLY","DEF RLY","FAN RLY"])
    if len(setValueToLog & setOutputFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "102_bitfield"))

    # Standby flag
    setStandbyFlag = set(["STANDBY"])
    if len(setValueToLog & setStandbyFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(272, 1), "StandbyFlag"))
    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    statusList = [
            ["1","T1 TEMP",0],
            ["1","T2 TEMP",1],
            ["1","T3 TEMP",2],
            ["2","100_bitfield",100],
            ["2","102_bitfield",102],
            ["3","StandbyFlag",272]
            ]
    return self._prepareListOfTransactions(statusList, "Status")


  def _prepareUpdateAlarmsTransactions(self):
    alarmList = [
            ["1","101_bitfield",101]
    ]
    return self._prepareListOfTransactions(alarmList, "Alarm")


  def _executeTransaction(self, networkTrans):
    if not networkTrans.online:
      self._nullOutputValues()
    else:

      for transaction in networkTrans.transactions:
        with self.lock:
          if isinstance(transaction.response, readHoldingRegistersResponse):
            value = transaction.response.registers[0]

            if transaction.tag == "100_bitfield":
              # log.debug("Got Status Flag")
              self._values["ALARM"] = ((value & 0x1) > 0)
              self._alarm = self._values["ALARM"]
              self._values["MUTE"] = ((value & 0x2) > 0)
              self._values["DEFROST"] = ((value & 0x4) > 0)
              self._values["DOOR"] = ((value & 0x8) > 0)
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "101_bitfield":
              # log.debug("Got Alarm Flag")
              self._values["T1PROBEALARM"] = ((value & 0x1) > 0)
              self.checkBooleanAdvisory("T1PROBEALARM", self._values["T1PROBEALARM"])
              self._values["T2PROBEALARM"] = ((value & 0x2) > 0)
              self.checkBooleanAdvisory("T2PROBEALARM", self._values["T2PROBEALARM"])
              self._values["T3PROBEALARM"] = ((value & 0x4) > 0)
              self.checkBooleanAdvisory("T3PROBEALARM", self._values["T3PROBEALARM"])
              self._values["HIGHTEMPALARM"] = ((value & 0x8) > 0)
              self.checkBooleanAdvisory("HIGHTEMPALARM", self._values["HIGHTEMPALARM"])
              self._values["LOWTEMPALARM"] = ((value & 0x10) > 0)
              self.checkBooleanAdvisory("LOWTEMPALARM", self._values["LOWTEMPALARM"])
              self._values["HIGHCONDALARM"] = ((value & 0x20) > 0)
              self.checkBooleanAdvisory("HIGHCONDALARM", self._values["HIGHCONDALARM"])
              self._values["HIGHPRESALARM"] = ((value & 0x40) > 0)
              self.checkBooleanAdvisory("HIGHPRESALARM", self._values["HIGHPRESALARM"])
              self._values["DOOROPENALARM"] = ((value & 0x80) > 0)
              self.checkBooleanAdvisory("DOOROPENALARM", self._values["DOOROPENALARM"])
              self._values["CONDCLEANALARM"] = ((value & 0x100) > 0)
              self.checkBooleanAdvisory("CONDCLEANALARM", self._values["CONDCLEANALARM"])
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "102_bitfield":
              # log.debug("Got Output Flag")
              self._values["AUX1 RLY"] = ((value & 0x10) > 0)
              self._values["COMP RLY"] = ((value & 0x20) > 0)
              self._values["DEF RLY"] = ((value & 0x40) > 0)
              self._values["FAN RLY"] = ((value & 0x80) > 0)

            elif transaction.tag == "CFG_1":
              self._values["T2"] = ((value & 0x1) > 0)
              self._values["FID"] = ((value & 0x20) > 0)
              self._values["LOC"] = ((value & 0x40) > 0)
              self._values["STBY"] = ((value & 0x80) > 0)

            elif transaction.tag == "CFG_2":
              self._values["DS"] = ((value & 0x1) > 0)
              self._values["C-H"] = ((value & 0x2) > 0)
              self._values["INP"] = ((value & 0x40) > 0)
              self._values["LIGHTS"] = ((value & 0x20) > 0)
              self._values["SB"] = ((value & 0x80) > 0)

            elif transaction.tag == "StandbyFlag":
             self._values["STANDBY"] = ((value & 0x80) > 0)

            elif transaction.tag == "CMD_1":
              self._values["MDEF"] = ((value & 0x4) > 0)

            else:    # LEO reading up from Device
              key = transaction.tag
              if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
                self._values[key] = self._convertToFloatValue(value)
                if int(self._values["SCL"]) == 2:
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

  def performUserAction(self, data):
    self.userAction = data
    return data

  def _prepareActionTransactions(self):
    retval = []
# FUTURE
#    if self.userAction is not None:
#      if self.userAction['command'] == 'defrost':
#        networkTrans = NetworkTransaction('defrost')
#        retval.append(networkTrans)
#        networkTrans.transactions.append(NetworkMessage(writeHoldingRegister(100, 0x04), 'defrost'))
#      self.userAction = None
    return retval


  # The purpose of this function is to look at one property value settings and update one or more "virtual" properties. In the case of the AR2-5, we want to look
  # at the DI2 parameter and set the DIG Input 2 "virtual" property value "On" or "Off" based upon the DI2 parameter configuration function.
  def ProcessVirtualProps(self,transaction):
    if transaction == "100_bitfield":
      if self._values["DI2"] == 3 or self._values["DI2"] == 4:
        self._values["DIG Input 2"] = self._values["DEFROST"]
    if transaction == "101_bitfield":
      if self._values["DI2"] == 1:
        self._values["DIG Input 2"] = self._values["HIGHPRESALARM"]


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

