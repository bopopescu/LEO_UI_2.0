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

deviceType = "LAE BIT25B1S3WH-8TM"
deviceTypeName = "LAE BIT25B1S3WH-8TM"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

valueDescriptions = OrderedDict()

# OUTPUTS - Dedicated Register value
valueDescriptions["T1 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T1-Air Probe","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T2 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T2-Evap Probe","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T3 TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T3 Temp","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["THI"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"HACCP High Temp","unitType":unitTypeTemperature}
valueDescriptions["TLO"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"HACCP Low Temp","unitType":unitTypeTemperature}
valueDescriptions["CND"] = {"dataType":dataTypeInt,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"CND","unitText":"weeks", "hide":"true"}
valueDescriptions["LOCSTAT"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Locked", "false": "Unlocked"},"valueType":valueTypeOutput,"displayName":"Keypad Lock Status"}
valueDescriptions["DIG Input 1"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital Input 1","defaultLog":"true"}
valueDescriptions["DIG Input 2"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital Input 2","defaultLog":"true"}
# OUTPUT - Status Flag bits
# 100 - Status flag
valueDescriptions["ALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Alarm Status"}
valueDescriptions["MUTE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Mute", "false": "No"},"valueType":valueTypeOutput,"displayName":"Mute", "hide":"true"}
valueDescriptions["DEFROST"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost Status", "defaultLog":"true"}
valueDescriptions["DOOR"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Door Status"}
valueDescriptions["TESTMODE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Test Mode", "hide":"true"}
valueDescriptions["STANDBY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeOutput,"displayName":"Standby Status"}
# 101 - Alarm flag
valueDescriptions["T1PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T1 Probe Alarm","description":"T1 Probe Alarm"}
valueDescriptions["T2PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T2 Probe Alarm","description":"T2 Probe Alarm"}
valueDescriptions["T3PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T3 Probe Alarm","description":"T3 Probe Alarm"}
valueDescriptions["LOWTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Low Temp Alarm","description":"Low Temp Alarm"}
valueDescriptions["HIGHTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Temp Alarm","description":"High Temp Alarm"}
valueDescriptions["HIGHCONDALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Condenser Temp","description":"High Condenser Alarm"}
valueDescriptions["GENERICALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Generic Alarm","description":"Generic Alarm"}
valueDescriptions["DOOROPENALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Door Open Alarm","description":"Door Open Alarm"}
valueDescriptions["CONDCLEANALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Condenser Clean Alarm","description":"Condenser Clean Alarm"}
# 102 - Output flag
valueDescriptions["COMP RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Compressor","defaultLog":"true"}
valueDescriptions["AUX1 RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"AUX 1","defaultLog":"true"}
valueDescriptions["AUX2 RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"AUX 2","defaultLog":"true"}
# Virtual (function to load value)
valueDescriptions["LIGHTS"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Lights"}
valueDescriptions["MDEF"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeConfig,"displayName":"MDEF","description":"Turn On Manual Defrost"}

# CONFIG
#CFG REGISTERS
valueDescriptions["SPL"] = {"displayName":"SPL","description":"Minimum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["SPH"] = {"displayName":"SPH","description":"Maximum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"5.0"}
valueDescriptions["SP"] = {"displayName":"SP","description":"Setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"2.0"}
valueDescriptions["HY0"] = {"displayName":"HY0","description":"Thermostat off to on differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"2.0"}
valueDescriptions["HY1"] = {"displayName":"HY1","description":"Thermostat on to off differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"2.0"}
valueDescriptions["CRT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRT","description":"Compressor rest time","unitText":"min","default":"4"}
valueDescriptions["CMT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CMT","description":"Compressor minimum ON Time","unitText":"min","default":"4"}
valueDescriptions["CT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT1","description":"Output run when probe T1 is faulty","unitText":"min","default":"10"}
valueDescriptions["CT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT2","description":"Output stop when probe T1 is faulty","unitText":"min","default":"10"}
valueDescriptions["CSD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSD","description":"Stop delay after door has opened","unitText":"min","default":"4"}
valueDescriptions["HT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"HT","description":"Door Heater ON time","unitText":"min","default":"10"}
valueDescriptions["DFM"] = {"displayName":"DFM","description":"Default start mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TIM","2":"FRO"},"default":"2"}
valueDescriptions["DFT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DFT","description":"Timer value for automatic defrost to start","unitText":"hrs","default":"4"}
valueDescriptions["DFB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"DFB","description":"Defrost timer backup","default":"true"}
valueDescriptions["LTD"] = {"displayName":"LTD","description":"Low Temperature for defrost start","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-11.0"}
valueDescriptions["DDS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DDS","description":"Delay between defrost","unitText":"hrs","default":"1"}
valueDescriptions["DLI"] = {"displayName":"DLI","description":"Defrost end temperature","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"5.0"}
valueDescriptions["DTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DTO","description":"Maximum defrost duration","unitText":"min","default":"40"}
valueDescriptions["DTY"] = {"displayName":"DTY","description":"Defrost type","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"ELE","2":"GAS"},"default":"0"}
valueDescriptions["DSO"] = {"displayName":"DSO","description":"Defrost start optimization","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"LO","2":"HI"},"default":"1"}
valueDescriptions["SOD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SOD","description":"Start optimization delay","unitText":"min","default":"30"}
valueDescriptions["DPD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DPD","description":"Pump down time","unitText":"sec","default":"0"}
valueDescriptions["DRN"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DRN","description":"Drip time","unitText":"min","default":"0"}
valueDescriptions["DDM"] = {"displayName":"DDM","description":"Display defrost mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"RT","1":"LT","2":"SP","3":"DEF"},"default":"3"}
valueDescriptions["DDY"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DDY","description":"Display delay","unitText":"min","default":"15"}
valueDescriptions["FID"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"FID","description":"Fans active during defrost","default":"true"}
valueDescriptions["FDD"] = {"displayName":"FDD","description":"Fan restart temperature after defrost","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["FTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FTO","description":"Maximum fan stop after defrost","unitText":"min","default":"1"}
valueDescriptions["FCM"] = {"displayName":"FCM","description":"Fan mode during thermostatic control","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TMP","2":"TIM"},"default":"2"}
valueDescriptions["FDT"] = {"displayName":"FDT","description":"Evap-air temp difference to turn OFF fans","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["FDH"] = {"displayName":"FDH","description":"Temp differential for fan restart","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.6"}
valueDescriptions["FT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT1","description":"Fan stop delay after stop","unitText":"sec","default":"0"}
valueDescriptions["FT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT2","description":"Timed fan stop","unitText":"min","default":"5"}
valueDescriptions["FT3"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT3","description":"Timed fan run","unitText":"min","default":"1"}
valueDescriptions["FMS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FMS","description":"Fan Minimum Stop","unitText":"sec","default":"5"}
valueDescriptions["ATM"] = {"displayName":"ATM","description":"Alarm threshold management","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ABS","2":"REL"},"default":"0"}
valueDescriptions["ALA"] = {"displayName":"ALA","description":"Low temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-7.8"}
valueDescriptions["AHA"] = {"displayName":"AHA","description":"High temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"10.0"}
valueDescriptions["ALR"] = {"displayName":"ALR","description":"Low temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"0.0"}
valueDescriptions["AHR"] = {"displayName":"AHR","description":"High temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"0.0"}
valueDescriptions["ATI"] = {"displayName":"ATI","description":"Probe used for temperature alarm detection","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"T2","2":"T3"},"default":"0"}
valueDescriptions["ATD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ATD","description":"Delay before alarm termperature warning","unitText":"min","default":"10"}
valueDescriptions["ADO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ADO","description":"Door alarm delay","unitText":"min","default":"4"}
valueDescriptions["AHM"] = {"displayName":"AHM","description":"High condenser alarm operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["AHT"] = {"displayName":"AHT","description":"Condensation temp alarm","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"82.0"}
valueDescriptions["ACC"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ACC","description":"Condenser periodic cleaning","unitText":"weeks","default":"0"}
valueDescriptions["IISM"] = {"displayName":"IISM","description":"Switchover mode to second param set","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"DI2"},"default":"0"}
valueDescriptions["IISL"] = {"displayName":"IISL","description":"Minimum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["IISH"] = {"displayName":"IISH","description":"Maximum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"5.0"}
valueDescriptions["IISP"] = {"displayName":"IISP","description":"Setpoint [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"2.0"}
valueDescriptions["IIH0"] = {"displayName":"IIH0","description":"Thermostat off to on differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"2.0"}
valueDescriptions["IIH1"] = {"displayName":"IIH1","description":"Thermostat on to off differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"2.0"}
valueDescriptions["IIHT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIHT","description":"Door Heater ON time in mode 2","unitText":"min","default":"10"}
valueDescriptions["IIFC"] = {"displayName":"IIFC","description":"Fan mode during thermostatic control [II]","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TMP","2":"TIM"},"default":"2"}
valueDescriptions["IIDF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDF","description":"Timer value for automatic defrost to start [II]","unitText":"hrs","default":"4"}
valueDescriptions["SB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"SB","description":"Standby button enable","default":"true"}
valueDescriptions["DI1"] = {"displayName":"DI1","description":"DI1 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"RDS"},"default":"0"}
valueDescriptions["DI2"] = {"displayName":"DI2","description":"DI2 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"RDS","4":"IISM","5":"T3","6":"PSP"},"default":"0"}
valueDescriptions["T3M"] = {"displayName":"T3","description":"Probe 3 operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"DSP","1":"CND","3":"DTP"},"default":"0"}
valueDescriptions["OS3"] = {"displayName":"OS3","description":"Probe T3 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["PSL"] = {"displayName":"PSL","description":"Minimum setpoint adjusted via potentiometer","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["PSR"] = {"displayName":"PSR","description":"Range of setpoint adusted via potentiometer","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature, "significantDigits":1,"default":"5.0"}
valueDescriptions["LSM"] = {"displayName":"LSM","description":"Light control mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"D1O","3":"D2O","4":"D2C"},"default":"1"}
valueDescriptions["OA1"] = {"displayName":"OA1","description":"AUX 1 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"FAN","2":"DEF","3":"LGT","4":"0-1","5":"ALO","6":"ALC","7":"HTR"},"default":"1"}
valueDescriptions["OA2"] = {"displayName":"OA2","description":"AUX 2 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"FAN","2":"DEF","3":"LGT","4":"0-1","5":"ALO","6":"ALC","7":"HTR"},"default":"3"}
valueDescriptions["OS1"] = {"displayName":"OS1","description":"Probe T1 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["T2E"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"T2","description":"Probe T2 enable","default":"true"}
valueDescriptions["OS2"] = {"displayName":"OS2","description":"Probe T2 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["TLD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"TLD","description":"Delay for min and max temp logging","unitText":"min","default":"5"}
valueDescriptions["SCL"] = {"displayName":"SCL","description":"Readout scale","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"1°C","1":"2°C","2":"°F"},"default":"0"}
valueDescriptions["SIM"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SIM","description":"Display slowdown","default":"100"}
valueDescriptions["ABE"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"ABE","description":"Alarm Buzzer Enable","default":"true"}
# The following entries are not visible from the display device of the BIT25
valueDescriptions["LOC"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Locked", "false": "Unlocked"},"valueType":valueTypeConfig,"displayName":"LOC","description":"Keypad lock"}
valueDescriptions["STBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeConfig,"displayName":"STBY","description":"Standby Mode"}

# ALARM
alarmDescriptions = OrderedDict()
alarmDescriptions["T1PROBEALARM"] = {"description": "T1 Probe Alarm"}
alarmDescriptions["T2PROBEALARM"] = {"description": "T2 Probe Alarm"}
alarmDescriptions["T3PROBEALARM"] = {"description": "T3 Probe Alarm"}
alarmDescriptions["LOWTEMPALARM"] = {"description": "Low Temp Alarm"}
alarmDescriptions["HIGHTEMPALARM"] = {"description": "High Temp Alarm"}
alarmDescriptions["HIGHCONDALARM"] = {"description": "High Condenser Alarm"}
alarmDescriptions["GENERICALARM"] = {"description": "Generic Alarm"}
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
            ["1","SCL",200],
            ["1","SPL",201],
            ["1","SPH",202],
            ["2","SP",203],
            ["2","HY0",204],
            ["2","CRT",205],
            ["3","CT1",206],
            ["3","CT2",207],
            ["3","CSD",208],
            ["4","DFM",209],
            ["4","DFT",210],
            ["4","DLI",211],
            ["5","DTO",212],
            ["5","DTY",213],
            ["5","DPD",214],
            ["6","DRN",215],
            ["6","DDM",216],
            ["6","DDY",217],
            ["7","FDD",218],
            ["7","FTO",219],
            ["7","FCM",220],
            ["8","FDT",221],
            ["8","FDH",222],
            ["8","FT1",223],
            ["9","FT2",224],
            ["9","FT3",225],
            ["9","ATM",226],
            ["10","ALA",227],
            ["10","AHA",228],
            ["10","ALR",229],
            ["11","AHR",230],
            ["11","ATI",231],
            ["11","ATD",232],
            ["12","ADO",233],
            ["12","AHM",234],
            ["12","AHT",235],
            ["13","ACC",236],
            ["13","IISM",237],
            ["13","IISL",238],
            ["14","IISH",239],
            ["14","IISP",240],
            ["14","IIH0",241],
            ["15","IIFC",242],
            ["15","IIDF",243],
            ["15","DI1",244],
            ["16","DI2",245],
            ["16","T3M",246],
            ["16","OS3",247],
            ["17","PSL",248],
            ["17","PSR",249],
            ["17","LSM",250],
            ["18","OA1",251],
            ["18","OA2",252],
            ["18","OS1",253],
            ["19","OS2",254],
            ["19","TLD",255],
            ["19","SIM",256],
            ["20","LTD",263],
            ["20","DDS",264],
            ["20","HY1",265],
            ["21","IIH1",266],
            ["21","FMS",267],
            ["21","HT",268],
            ["22","IIHT",269],
            ["22","DSO",270],
            ["22","SOD",271],
            ["23","CMT",272],
            ["24","CFG_1",258],
            ["26","CMD_1",100]
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
        value = value | 0x0001 if self._newDeviceConfigurationValues["STBY"] else value
        value = value | 0x0002 if self._newDeviceConfigurationValues["SB"] else value
        value = value | 0x0008 if self._newDeviceConfigurationValues["LOC"] else value
        value = value | 0x0010 if self._newDeviceConfigurationValues["DFB"] else value
        value = value | 0x0020 if self._newDeviceConfigurationValues["FID"] else value
        value = value | 0x0040 if self._newDeviceConfigurationValues["T2E"] else value
        value = value | 0x0400 if self._newDeviceConfigurationValues["ABE"] else value

      else:
        newConfigValue = self._newDeviceConfigurationValues[key]

        if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
          # This unit is always C
          #if "unitType" in self._valueDescriptions[key] and self._values["SCL"] == 2:# this is deliberate as SCL will be set as the first one
          #  if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
          #    newConfigValue = self._convertC2F(newConfigValue)
          #  elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
          #    newConfigValue = self._convertDeltaC2F(newConfigValue)
          value = self._convertFromFloatValue(newConfigValue * 10.0)

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

    if "THI" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(259, 1), "THI"))

    if "TLO" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(260, 1), "TLO"))

    # Status flag
    setValueToLog = set(valueToLog)
    setStatusFlag = set(["ALARM","MUTE","DEFROST","DOOR","TESTMODE","STANDBY"])
    if len(setValueToLog & setStatusFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "StatusFlag"))

    # Alarm flag
    setAlarmFlag = set(["T1PROBEALARM","T2PROBEALARM","T3PROBEALARM","LOWTEMPALARM","HIGHTEMPALARM","HIGHCONDALARM","GENERICALARM","DOOROPENALARM","CONDCLEANALARM"])
    if len(setValueToLog & setAlarmFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(101, 1), "AlarmFlag"))

    # Output flag
    setOutputFlag = set(["COMP RLY","AUX1 RLY","AUX2 RLY"])
    if len(setValueToLog & setOutputFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "OutputFlag"))

    # Input flag
    setInputFlag = set(["DIG Input 1","DIG Input 2"])
    if len(setValueToLog & setInputFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(004, 1), "InputFlag"))

    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    # log.debug("Preparing Update Status Transactions" );
    networkTrans = NetworkTransaction("Status1")
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(0, 1), "T1 TEMP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(1, 1), "T2 TEMP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(2, 1), "T3 TEMP"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(260, 1), "TLO"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(259, 1), "THI"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(261, 1), "CND"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "StatusFlag"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "OutputFlag"))
    networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(004, 1), "InputFlag"))
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
              # log.debug("Got Status Flag")
              self._values["ALARM"] = ((value & 0x1) > 0)
              self._alarm = self._values["ALARM"]
              self._values["MUTE"] = ((value & 0x2) > 0)
              self._values["DEFROST"] = ((value & 0x4) > 0)
              self._values["DOOR"] = ((value & 0x8) > 0)
              self._values["TESTMODE"] = ((value & 0x10) > 0)
              self._values["STANDBY"] = ((value & 0x20) > 0)
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "AlarmFlag":
              # log.debug("Got Alarm Flag")
              self._values["T1PROBEALARM"] = ((value & 0x1) > 0)
              self.checkBooleanAdvisory("T1PROBEALARM", self._values["T1PROBEALARM"])
              self._values["T2PROBEALARM"] = ((value & 0x2) > 0)
              self.checkBooleanAdvisory("T2PROBEALARM", self._values["T2PROBEALARM"])
              self._values["T3PROBEALARM"] = ((value & 0x4) > 0)
              self.checkBooleanAdvisory("T3PROBEALARM", self._values["T3PROBEALARM"])
              self._values["LOWTEMPALARM"] = ((value & 0x8) > 0)
              self.checkBooleanAdvisory("LOWTEMPALARM", self._values["LOWTEMPALARM"])
              self._values["HIGHTEMPALARM"] = ((value & 0x10) > 0)
              self.checkBooleanAdvisory("HIGHTEMPALARM", self._values["HIGHTEMPALARM"])
              self._values["HIGHCONDALARM"] = ((value & 0x20) > 0)
              self.checkBooleanAdvisory("HIGHCONDALARM", self._values["HIGHCONDALARM"])
              self._values["GENERICALARM"] = ((value & 0x40) > 0)
              self.checkBooleanAdvisory("GENERICALARM", self._values["GENERICALARM"])
              self._values["DOOROPENALARM"] = ((value & 0x80) > 0)
              self.checkBooleanAdvisory("DOOROPENALARM", self._values["DOOROPENALARM"])
              self._values["CONDCLEANALARM"] = ((value & 0x100) > 0)
              self.checkBooleanAdvisory("CONDCLEANALARM", self._values["CONDCLEANALARM"])
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "OutputFlag":
              # log.debug("Got Output Flag")
              self._values["COMP RLY"] = ((value & 0x1) > 0)
              self._values["AUX1 RLY"] = ((value & 0x2) > 0)
              self._values["AUX2 RLY"] = ((value & 0x4) > 0)
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "InputFlag":
              # log.debug("Got Input Flag")
              self._values["DIG Input 1"] = ((value & 0x1) > 0)
              self._values["DIG Input 2"] = ((value & 0x2) > 0)
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "CFG_1":
              # log.debug("Got CFG_1 Flag")
              self._values["STBY"] = ((value & 0x0001) > 0)
              self._values["SB"] = ((value & 0x0002) > 0)
              self._values["LOC"] = ((value & 0x0008) > 0)
              self._values["LOCSTAT"] = self._values["LOC"] # LOC is config, LOCSTAT is status - Showing same value
              self._values["DFB"] = ((value & 0x0010) > 0)
              self._values["FID"] = ((value & 0x0020) > 0)
              self._values["T2"] = ((value & 0x0040) > 0)
              self._values["ABE"] = ((value & 0x0400) > 0)
              self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "CMD_1":
              self._values["MDEF"] = ((value & 0x4) > 0)
              self.ProcessVirtualProps( transaction.tag )

            else:
              key = transaction.tag
              # print "Transaction.tag=", transaction.tag
              if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
                self._values[key] = self._convertToFloatValue(value) / 10.0
                # This unit is always C
                #if "unitType" in self._valueDescriptions[key] and self._values["SCL"] == 2:
                #  if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                #    self._values[key] = self._convertF2C(self._values[key])
                #  elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                #    self._values[key] = self._convertDeltaF2C(self._values[key])

              elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
                self._values[key] = False if value == 0 else True
              else:
                self._values[key] = self._convertToIntValue(value)

              self.ProcessVirtualProps( transaction.tag )

      if "ReadConfig" in networkTrans.tag:
        self.saveValuesToDatabase()
      elif "WriteConfig" in networkTrans.tag:
        self.updateDeviceConfiguration()

  def performUserAction(self, data):
    self.userAction = data
    return data

  # The purpose of this function is to look at one property and update one or more "virtual" properties. In the case of the BIT25, we want to look
  # at the door switch and set a lights property "On" or "Off" based upon the door switch.
  def ProcessVirtualProps( self, transactionTag ) :
    if transactionTag == "StatusFlag" :
      self._values["LIGHTS"] = self._values["DOOR"] # "Virtual" Lights property...


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


