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

deviceType = "EVCO-EV3224"
deviceTypeName = "EVCO-EV3224"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

valueDescriptions = OrderedDict()


#  Analog Inputs - Dedicated Register value 
valueDescriptions["Probe 1"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"Probe 1","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["Probe 2"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"Probe 2","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["Probe 3"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"Probe 3","unitType":unitTypeTemperature, "defaultLog":"true"}

#Digital Inputs 101
valueDescriptions["DoorDigitalInput"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Door Status", "defaultLog":"true"}
valueDescriptions["MultifunctionDigitalInput"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Mute", "false": "-"},"valueType":valueTypeOutput,"displayName":"MultifunctionDigitalInput"}

# OUTPUT - Status Flag bits
# 100 - Status flag
#valueDescriptions["ALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Alarm"}
valueDescriptions["DEFROST Phase"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"0":"Off", "1": "On"},"valueType":valueTypeOutput,"displayName":"DEFROST Phase", "defaultLog":"true"}
valueDescriptions["Status Light"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"0":"Off", "1": "On"},"valueType":valueTypeOutput,"displayName":"Status Light", "defaultLog":"true"}
valueDescriptions["Status Aux"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"0":"Off", "1": "On"},"valueType":valueTypeOutput,"displayName":"Status Aux", "defaultLog":"true"}
valueDescriptions["Status Resistors"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"0":"Off", "1": "On"},"valueType":valueTypeOutput,"displayName":"Status Resistors", "defaultLog":"true"}
valueDescriptions["Set point"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"Probe 3","unitType":unitTypeTemperature, "defaultLog":"true"}

# 101 - Alarm flag
# valueDescriptions["T1PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T1 Probe Alarm","description":"T1 Probe Alarm"}
# valueDescriptions["T2PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T2 Probe Alarm","description":"T2 Probe Alarm"}
# valueDescriptions["T3PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T3 Probe Alarm","description":"T3 Probe Alarm"}
# valueDescriptions["HIGHTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Temp Alarm","description":"High Temp Alarm"}
# valueDescriptions["LOWTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Low Temp Alarm","description":"Low Temp Alarm"}
# valueDescriptions["HIGHCONDALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Generic Alarm","description":"Generic Alarm"}
# valueDescriptions["HIGHPRESALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Pressure Alarm","description":"High Pressure Alarm"}
# valueDescriptions["DOOROPENALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Door Open Alarm","description":"Door Open Alarm"}
# valueDescriptions["CONDCLEANALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Condenser Clean Alarm","description":"Condenser Clean Alarm"}

# 181 - Output Digital flag
valueDescriptions["Output K1"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Output K1", "defaultLog":"true"}
valueDescriptions["Output K2"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Output K2", "defaultLog":"true"}
valueDescriptions["Output K3"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Output K3", "defaultLog":"true"}
valueDescriptions["Output K4"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Output K4", "defaultLog":"true"}


# Configuration Registers
# valueDescriptions["IT"] = {"displayName":"IT","description":"Integral Output Cycle time (10-500 sec)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"90"}
# valueDescriptions["AO1L"] = {"displayName":"AO1L","description":"Econ 1 Volt Low Offset (1=0.04v)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["AO1H"] = {"displayName":"AO1H","description":"Econ 1 Volt High Offset (1=0.04v)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"-10"}
# valueDescriptions["AO2L"] = {"displayName":"AO2L","description":"VS Fan, 1 Volt Low Offset (1=0.04v)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["AO2H"] = {"displayName":"AO2H","description":"VS FAn, 1 Volt High Offset (1=0.04v)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"-10"}
# valueDescriptions["OFST"] = {"displayName":"OFST","description":"Built-In Space Temp 1 Offset (-18.0~18.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"0"}
# valueDescriptions["PB"] = {"displayName":"PB","description":"Proportional Band (0.0~18.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"0"}
# valueDescriptions["DIFF"] = {"displayName":"DIFF","description":"Stage Differential (0.1~2.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"1"}
# valueDescriptions["LOC"] = {"displayName":"LOC","description":"Disabling Front Button Selection","dataType":dataTypeList,"dataList":{"0":"Unlock All Button","249":"UP & Down Setpoint","255":"Lock All Button"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["RE1"] = {"displayName":"RE1","description":"Econ AO1 Direct/Reverse Control Output","dataType":dataTypeList,"dataList":{"0":"Direct","1":"Reverse"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["RE2"] = {"displayName":"RE2","description":"VS Fan AO2 Direct/Reverse Control Output","dataType":dataTypeList,"dataList":{"0":"Direct","1":"Reverse"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["RS"] = {"displayName":"RS","description":"Control Temperature Source","dataType":dataTypeList,"dataList":{"0":"Space Temp 1","1,":"Space Temp","2":"Average Space T 1 & 2"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["SP"] = {"displayName":"SP","description":"Thermostat LCD Display Options","dataType":dataTypeList,"dataList":{"0":"Temp/Time","1":"SP/Time","2":"Temp/RH","3":"SP/RH","4":"Temp/Dewpt","5":"Dewpt/Time","6":"Temp/Time-RH","7":"Supply Temp","8":"Time/Rotate"},"valueType":valueTypeConfig,"default":"8"}
# valueDescriptions["BAUD"] = {"displayName":"BAUD","description":"Modbus Baud Rate Speed","dataType":dataTypeList,"dataList":{"1":"2400 bps","2":"4800 bps","3":"9600 bps","5":"19200 bps","6":"38400 bps","7":"57600 bps","8":"115200 bps"},"valueType":valueTypeConfig,"default":"5"}
# valueDescriptions["PRTY"] = {"displayName":"PRTY","description":"Modbus Parity Data/Stop Bits","dataType":dataTypeList,"dataList":{"0":"Even81","1":"Odd81","2":"none82","3":"none81"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["ID"] = {"displayName":"ID","description":"Modbus Node ID","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1"}
# valueDescriptions["RHOF"] = {"displayName":"RHOF","description":"Humidity Reading Offset (-30.0~30.0)","dataType":dataTypeFloat,"unitType": "Percent","valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["DST"] = {"displayName":"DST","description":"USA Daylight Savings Enable","dataType":dataTypeList,"dataList":{"0":"Disable","1":"Enable"},"valueType":valueTypeConfig,"default":"1"}
# valueDescriptions["FAN"] = {"displayName":"FAN","description":"Fan Type Selection","dataType":dataTypeList,"dataList":{"0":"Single Speed","1":"Variable Speed"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["HFAN"] = {"displayName":"HFAN","description":"Fan Off Delay for Heat Mode (0~300 sec)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"120"}
# valueDescriptions["CFAN"] = {"displayName":"CFAN","description":"Fan Off Delay for Cool Mode (0~300 sec)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["OFAN"] = {"displayName":"OFAN","description":"Fan Mode For Occupied Period","dataType":dataTypeList,"dataList":{"0":"Automatic","1":"Continuous"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["UFAN"] = {"displayName":"UFAN","description":"Fan Mode For Unoccupied Period","dataType":dataTypeList,"dataList":{"0":"Automatic","1":"Continuous"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["H1F"] = {"displayName":"H1F","description":"Fan % Output for Heat Stage 1","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"40"}
# valueDescriptions["H2F"] = {"displayName":"H2F","description":"Fan % Output for Heat Stage 2","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"80"}
# valueDescriptions["C1F"] = {"displayName":"C1F","description":"Fan % Output for Cool Stage 1","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"60"}
# valueDescriptions["C2F"] = {"displayName":"C2F","description":"Fan % Output for Cool Stage 2","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"100"}
# valueDescriptions["IDF"] = {"displayName":"IDF","description":"Fan % Output for Idle Time","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"30"}
# valueDescriptions["DHF"] = {"displayName":"DHF","description":"Fan% For Dehum When No Heat Or Cool","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"50"}
# valueDescriptions["HDLY"] = {"displayName":"HDLY","description":"Inter-Stage Heat Delay (1~10 mins)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1"}
# valueDescriptions["CDLY"] = {"displayName":"CDLY","description":"Inter-Stage Cool Delay (1~10 mins)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1"}
# valueDescriptions["RHOP"] = {"displayName":"RHOP","description":"Dehumidification Control Options","dataType":dataTypeList,"dataList":{"0":"Monitor Only","1":"Cool and Heat","2":"Dehumidify"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["OHSP"] = {"displayName":"OHSP","description":"RH Occupied Cut-In (0~100)","dataType":dataTypeFloat, "unitType": "Percent","valueType":valueTypeConfig,"default":"55"}
# valueDescriptions["OHDF"] = {"displayName":"OHDF","description":"RH Occupied Cut-Out Differential (0~50)","dataType":dataTypeFloat, "unitType": "Percent","valueType":valueTypeConfig,"default":"5"}
# valueDescriptions["UHSP"] = {"displayName":"UHSP","description":"RH Unoccupied Cut-In (0~100)","dataType":dataTypeFloat, "unitType": "Percent","valueType":valueTypeConfig,"default":"60"}
# valueDescriptions["UHDF"] = {"displayName":"UHDF","description":"RH Unoccupied Cut-Out Differential (0~50)","dataType":dataTypeFloat, "unitType": "Percent","valueType":valueTypeConfig,"default":"5"}
# valueDescriptions["SPLY"] = {"displayName":"SPLY","description":"Supply Temperature Sensor Enable","dataType":dataTypeList,"dataList":{"0":"Disable","1":"Enable"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["ECO"] = {"displayName":"ECO","description":"Economizer Function","dataType":dataTypeList,"dataList":{"0":"Disable","1":"Enable"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["ECDO"] = {"displayName":"ECDO","description":"Economizer Command","dataType":dataTypeList,"dataList":{"0":"Off","1":"On"},"valueType":valueTypeConfig,"default":"0"}
# valueDescriptions["ECON"] = {"displayName":"ECON","description":"Econimizer ON Output Level (0~100%)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"80"}
# valueDescriptions["ECOF"] = {"displayName":"ECOF","description":"Econimizer OFF Output Level (0~100%)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"10"}
# valueDescriptions["SPDT"] = {"displayName":"SPDT","description":"Temporary Temp Setpt Range (2.0~20.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"2"}
# valueDescriptions["SPT"] = {"displayName":"SPT","description":"Temporary Temp Setpt Duration (15~120 mins)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"60"}
# valueDescriptions["HTSP"] = {"displayName":"HTSP","description":"Dehumification Reheat Setpoint (32.0~122.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"65"}
# valueDescriptions["RSOF"] = {"displayName":"RSOF","description":"Remote Temperature Offset (-18.0~18.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"0"}
# valueDescriptions["SSOF"] = {"displayName":"SSOF","description":"Supply Temperature Offset (-18.0~18.0)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeDeltaTemperature,"significantDigits":1,"default":"0"}

# Configuration Schedule Registers
# Sunday
# valueDescriptions["SUNOCC"] = {"displayName":"Sunday Occupied","description":"Sunday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["SUNOCCSETCL"] = {"displayName":"Sunday OCC Cool","description":"Sunday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["SUNOCCSETHT"] = {"displayName":"Sunday OCC Heat","description":"Sunday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["SUNUNOCC"] = {"displayName":"Sunday Unoccupied","description":"Sunday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["SUNUNOCCSETCL"] = {"displayName":"Sunday Unocc Cool","description":"Sunday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["SUNUNOCCSETHT"] = {"displayName":"Sunday Unocc Heat","description":"Sunday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Monday
# valueDescriptions["MONOCC"] = {"displayName":"Monday Occupied","description":"Monday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["MONOCCSETCL"] = {"displayName":"Monday OCC Cool","description":"Monday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["MONOCCSETHT"] = {"displayName":"Monday OCC Heat","description":"Monday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["MONUNOCC"] = {"displayName":"Monday Unoccupied","description":"Monday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["MONUNOCCSETCL"] = {"displayName":"Monday Unocc Cool","description":"Monday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["MONUNOCCSETHT"] = {"displayName":"Monday Unocc Heat","description":"Monday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Tuesday
# valueDescriptions["TUEOCC"] = {"displayName":"Tuesday Occupied","description":"Tuesday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["TUEOCCSETCL"] = {"displayName":"Tuesday OCC Cool","description":"Tuesday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["TUEOCCSETHT"] = {"displayName":"Tuesday OCC Heat","description":"Tuesday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["TUEUNOCC"] = {"displayName":"Tuesday Unoccupied","description":"Tuesday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["TUEUNOCCSETCL"] = {"displayName":"Tuesday Unocc Cool","description":"Tuesday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["TUEUNOCCSETHT"] = {"displayName":"Tuesday Unocc Heat","description":"Tuesday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Wednesday
# valueDescriptions["WEDOCC"] = {"displayName":"Wednesday Occupied","description":"Wednesday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["WEDOCCSETCL"] = {"displayName":"Wednesday OCC Cool","description":"Wednesday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["WEDOCCSETHT"] = {"displayName":"Wednesday OCC Heat","description":"Wednesday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["WEDUNOCC"] = {"displayName":"Wednesday Unoccupied","description":"Wednesday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["WEDUNOCCSETCL"] = {"displayName":"Wednesday Unocc Cool","description":"Wednesday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["WEDUNOCCSETHT"] = {"displayName":"Wednesday Unocc Heat","description":"Wednesday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Thursday
# valueDescriptions["THUOCC"] = {"displayName":"Thursday Occupied","description":"Thursday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["THUOCCSETCL"] = {"displayName":"Thursday OCC Cool","description":"Thursday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["THUOCCSETHT"] = {"displayName":"Thursday OCC Heat","description":"Thursday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["THUUNOCC"] = {"displayName":"Thursday Unoccupied","description":"Thursday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["THUUNOCCSETCL"] = {"displayName":"Thursday Unocc Cool","description":"Thursday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["THUUNOCCSETHT"] = {"displayName":"Thursday Unocc Heat","description":"Thursday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Friday
# valueDescriptions["FRIOCC"] = {"displayName":"Friday Occupied","description":"Friday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["FRIOCCSETCL"] = {"displayName":"Friday OCC Cool","description":"Friday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["FRIOCCSETHT"] = {"displayName":"Friday OCC Heat","description":"Friday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["FRIUNOCC"] = {"displayName":"Friday Unoccupied","description":"Friday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["FRIUNOCCSETCL"] = {"displayName":"Friday Unocc Cool","description":"Friday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["FRIUNOCCSETHT"] = {"displayName":"Friday Unocc Heat","description":"Friday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}
# Saturday
# valueDescriptions["SATOCC"] = {"displayName":"Saturday Occupied","description":"Saturday Occupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"800"}
# valueDescriptions["SATOCCSETCL"] = {"displayName":"Saturday OCC Cool","description":"Saturday Occupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"26.1"}
# valueDescriptions["SATOCCSETHT"] = {"displayName":"Saturday OCC Heat","description":"Saturday Occupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"21.1"}
# valueDescriptions["SATUNOCC"] = {"displayName":"Saturday Unoccupied","description":"Saturday Unoccupied Time (0~2359)","dataType":dataTypeInt,"valueType":valueTypeConfig,"default":"1800"}
# valueDescriptions["SATUNOCCSETCL"] = {"displayName":"Saturday Unocc Cool","description":"Saturday Unoccupied Cool (5~98.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"29.4"}
# valueDescriptions["SATUNOCCSETHT"] = {"displayName":"Saturday Unocc Heat","description":"Saturday Unoccupied Heat (4~89.5)","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"16.6"}


# ALARMS
alarmDescriptions = OrderedDict()



class Device(deviceObject.NetworkDeviceObject):
  def __init__(self, deviceManager, name, description, network, networkAddress, image, method = ""):
    deviceObject.NetworkDeviceObject.__init__(self, deviceManager, name, description, network, networkAddress, deviceType, deviceTypeName, image)

    self._valueDescriptions = valueDescriptions
    self._alarmDescriptions = alarmDescriptions

    self.loadValuesFromDatabase()
    self.loadAdvisoriesFromDatabase()

    self.configModbusList = []
                      # ["1","IT",7],
                      # ["1","AO1L",8],
                      # ["1","AO1H",9],
                      # ["2","AO2L",10],
                      # ["2","AO2H",11],
                      # ["2","OFST",12],
                      # ["3","PB",13],
                      # ["3","DIFF",14],
                      # ["3","LOC",15],
                      # ["4","RE1",16],
                      # ["4","RE2",17],
                      # ["4","RS",18],
                      # ["5","SP",19],
                      # ["5","BAUD",20],
                      # ["5","PRTY",21],
                      # ["6","ID",22],
                      # ["6","RHOF",23],
                      # ["6","DST",24],
                      # ["7","FAN",25],
                      # ["7","HFAN",26],
                      # ["7","CFAN",27],
                      # ["8","OFAN",28],
                      # ["8","UFAN",29],
                      # ["8","H1F",30],
                      # ["9","H2F",31],
                      # ["9","C1F",32],
                      # ["9","C2F",33],
                      # ["10","IDF",34],
                      # ["10","DHF",35],
                      # ["10","HDLY",36],
                      # ["11","CDLY",37],
                      # ["11","RHOP",38],
                      # ["11","OHSP",39],
                      # ["12","OHDF",40],
                      # ["12","UHSP",41],
                      # ["12","UHDF",42],
                      # ["13","SPLY",43],
                      # ["13","ECO",44],
                      # ["13","ECDO",45],
                      # ["14","ECON",46],
                      # ["14","ECOF",47],
                      # ["14","SPDT",48],
                      # ["15","SPT",49],
                      # ["15","HTSP",50],
                      # ["15","RSOF",51],
                      # ["16","SSOF",52],
                      # ["16","SUNOCC",61],
                      # ["16","SUNOCCSETCL",75],
                      # ["17","SUNOCCSETHT",76],
                      # ["17","SUNUNOCC",62],
                      # ["17","SUNUNOCCSETCL",77],
                      # ["18","SUNUNOCCSETHT",78],
                      # ["18","MONOCC",63],
                      # ["18","MONOCCSETCL",79],
                      # ["19","MONOCCSETHT",80],
                      # ["19","MONUNOCC",64],
                      # ["19","MONUNOCCSETCL",81],
                      # ["20","MONUNOCCSETHT",82],
                      # ["20","TUEOCC",65],
                      # ["20","TUEOCCSETCL",83],
                      # ["21","TUEOCCSETHT",84],
                      # ["21","TUEUNOCC",66],
                      # ["21","TUEUNOCCSETCL",85],
                      # ["22","TUEUNOCCSETHT",86],
                      # ["22","WEDOCC",67],
                      # ["22","WEDOCCSETCL",87],
                      # ["23","WEDOCCSETHT",88],
                      # ["23","WEDUNOCC",68],
                      # ["23","WEDUNOCCSETCL",89],
                      # ["24","WEDUNOCCSETHT",90],
                      # ["24","THUOCC",69],
                      # ["24","THUOCCSETCL",91],
                      # ["25","THUOCCSETHT",92],
                      # ["25","THUUNOCC",70],
                      # ["25","THUUNOCCSETCL",93],
                      # ["26","THUUNOCCSETHT",94],
                      # ["26","FRIOCC",71],
                      # ["26","FRIOCCSETCL",95],
                      # ["27","FRIOCCSETHT",96],
                      # ["27","FRIUNOCC",72],
                      # ["27","FRIUNOCCSETCL",97],
                      # ["28","FRIUNOCCSETHT",98],
                      # ["28","SATOCC",73],
                      # ["28","SATOCCSETCL",99],
                      # ["29","SATOCCSETHT",100],
                      # ["29","SATUNOCC",74],
                      # ["29","SATUNOCCSETCL",101],
                      # ["30","SATUNOCCSETHT",102]
  # ]


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

      newConfigValue = self._newDeviceConfigurationValues[key]

     # LEO sending data to Device
      if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
        if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
          newConfigValue = self._convertC2F(newConfigValue)
        elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
          newConfigValue = self._convertDeltaC2F(newConfigValue)
        newConfigValue = newConfigValue
        value = self._convertFromFloatValue(newConfigValue * 10)
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


  def _prepareLoggingTransactions(self, valueToLog):
    if len(valueToLog) == 0:
      return None

    networkTrans = NetworkTransaction("Logging")

    if "ACTIVE SETPT" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(1, 1), "ACTIVE SETPT"))

    if "CONTROL TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(0, 1), "CONTROL TEMP"))

    if "COOL SETPT" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(0, 1), "COOL SETPT"))

    if "HEAT SETPT" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(1, 1), "HEAT SETPT"))

    if "SPACE TEMP 1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(6, 1), "SPACE TEMP 1"))

    if "SPACE TEMP 2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(7, 1), "SPACE TEMP 2"))

    if "SUPPLY TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(8, 1), "SUPPLY TEMP"))

    if "ROOM RH%" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(4, 1), "ROOM RH%"))

    if "DEW POINT" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(5, 1), "DEW POINT"))

    if "MODE" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(0), "MODE"))

    if "OCCUPANCY" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(9, 1), "OCCUPANCY"))

    if "FAN STATUS" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(5), "FAN STATUS"))

    if "VS FAN SPEED" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(3, 1), "VS FAN SPEED"))

    if "HEAT STAGE1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(3), "HEAT STAGE1"))

    if "HEAT STAGE2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(4), "HEAT STAGE2"))

    if "COOL STAGE1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(1), "COOL STAGE1"))

    if "COOL STAGE2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(2), "COOL STAGE2"))

    if "DEHUM STATUS" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readDiscreteInputRegisters(6), "DEHUM STATUS"))

    if "DAMPER POS" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readInputRegisters(2, 1), "DAMPER POS"))

    return [ networkTrans ]


  def _prepareUpdateStatusTransactions(self):
    statusList = [
            ["1","Probe 1",201],
            ["1","Probe 2",202],
            ["1","Probe 3",203],
            ["2","181_bitfield",181],
            ["2","101_bitfield",101],
            #["3","DEFROST Phase",557],
            ["4","Status Light",502],
            ["4","Status Aux",503],
            ["5","Status Resistors",504],
            ["5","Set point",558]
            ]
    return  self._prepareListOfTransactions(statusList, "Status")


  def _executeTransaction(self, networkTrans):
    if not networkTrans.online:
      self._nullOutputValues()
    else:

      for transaction in networkTrans.transactions:
        with self.lock:
          if isinstance(transaction.response, readHoldingRegistersResponse):
            value = transaction.response.registers[0]

            if transaction.tag == "101_bitfield":
              # log.debug("Got Status Flag")
              self._values["DoorDigitalInput"] = ((value & 0x4) > 0)
              #self._alarm = self._values["ALARM"]
              #self._values["MUTE"] = ((value & 0x2) > 0)
              #self._values["DEFROST"] = ((value & 0x4) > 0)
              self._values["MultifunctionDigitalInput"] = ((value & 0x8) > 0)
              self.ProcessVirtualProps( transaction.tag )

            # elif transaction.tag == "101_bitfield":
              # # log.debug("Got Alarm Flag")
              # self._values["DoorDigitalInput"] = ((value & 0x1) > 0)
              # self.checkBooleanAdvisory("T1PROBEALARM", self._values["T1PROBEALARM"])
              # self._values["T2PROBEALARM"] = ((value & 0x2) > 0)
              # self.checkBooleanAdvisory("T2PROBEALARM", self._values["T2PROBEALARM"])
              # self._values["T3PROBEALARM"] = ((value & 0x4) > 0)
              # self.checkBooleanAdvisory("T3PROBEALARM", self._values["T3PROBEALARM"])
              # self._values["HIGHTEMPALARM"] = ((value & 0x8) > 0)
              # self.checkBooleanAdvisory("HIGHTEMPALARM", self._values["HIGHTEMPALARM"])
              # self._values["LOWTEMPALARM"] = ((value & 0x10) > 0)
              # self.checkBooleanAdvisory("LOWTEMPALARM", self._values["LOWTEMPALARM"])
              # self._values["HIGHCONDALARM"] = ((value & 0x20) > 0)
              # self.checkBooleanAdvisory("HIGHCONDALARM", self._values["HIGHCONDALARM"])
              # self._values["HIGHPRESALARM"] = ((value & 0x40) > 0)
              # self.checkBooleanAdvisory("HIGHPRESALARM", self._values["HIGHPRESALARM"])
              # self._values["DOOROPENALARM"] = ((value & 0x80) > 0)
              # self.checkBooleanAdvisory("DOOROPENALARM", self._values["DOOROPENALARM"])
              # self._values["CONDCLEANALARM"] = ((value & 0x100) > 0)
              # self.checkBooleanAdvisory("CONDCLEANALARM", self._values["CONDCLEANALARM"])
              # self.ProcessVirtualProps( transaction.tag )

            elif transaction.tag == "181_bitfield":
              # log.debug("Got Output Flag")
              self._values["Output K1"] = ((value & 0x10) > 0)
              self._values["Output K2"] = ((value & 0x20) > 0)
              self._values["Output K3"] = ((value & 0x40) > 0)
              self._values["Output K4"] = ((value & 0x80) > 0)

            # elif transaction.tag == "CFG_1":
              # self._values["T2"] = ((value & 0x1) > 0)
              # self._values["FID"] = ((value & 0x20) > 0)
              # self._values["LOC"] = ((value & 0x40) > 0)
              # self._values["STBY"] = ((value & 0x80) > 0)

            # elif transaction.tag == "CFG_2":
              # self._values["DS"] = ((value & 0x1) > 0)
              # self._values["C-H"] = ((value & 0x2) > 0)
              # self._values["INP"] = ((value & 0x40) > 0)
              # self._values["LIGHTS"] = ((value & 0x20) > 0)
              # self._values["SB"] = ((value & 0x80) > 0)

            # elif transaction.tag == "DEFROST Phase":
             # value1 = ((value & 0x2560) > 0)
             # value2 = ((value & 0x5120) > 0)
             # value3 = ((value & 0x10240) > 0)
             # value4 = ((value & 0x20480) > 0)
             # self._values["STANDBY"] = ((value & 0x80) > 0)

            # elif transaction.tag == "CMD_1":
              # self._values["MDEF"] = ((value & 0x4) > 0)

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

	

      #This below code is under execute transactions

      # for transaction in networkTrans.transactions:
        # with self.lock:
          # if isinstance(transaction.response, readHoldingRegistersResponse) :
            # value = transaction.response.registers[0]
            # decimalDivide = 0
            # key = transaction.tag
            # if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
              # if decimalDivide == 0:
                # self._values[key] = self._convertToFloatValue(value)/10
              # else:
                # self._values[key] = value
              # if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                # self._values[key] = self._convertF2C(self._values[key])
              # elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                # self._values[key] = self._convertDeltaF2C(self._values[key])
              # self._values[key] = self._values[key]
            # elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
              # self._values[key] = False if value == 0 else True
            # else:
             # # log.debug(key) ###########################################
              # self._values[key] = self._convertToIntValue(value)

          # elif isinstance(transaction.response, readInputRegistersResponse) :
            # value = transaction.response.registers[0]
            # decimalDivide = 0
            # key = transaction.tag
            # if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
              # if decimalDivide == 0:
                # self._values[key] = self._convertToFloatValue(value)/10
              # else:
                # self._values[key] = value
              # if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                # self._values[key] = self._convertF2C(self._values[key])
              # elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                # self._values[key] = self._convertDeltaF2C(self._values[key])
              # self._values[key] = self._values[key]
            # elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
              # self._values[key] = False if value == 0 else True
            # else:
             # # log.debug(key) ###########################################
              # self._values[key] = self._convertToIntValue(value)

          # elif isinstance(transaction.response, readDiscreteInputRegistersResponse) :
            # value = transaction.response.registers
            # decimalDivide = 0
            # key = transaction.tag
            # if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
              # if decimalDivide == 0:
                # self._values[key] = self._convertToFloatValue(value)/10
              # else:
                # self._values[key] = value
              # if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                # self._values[key] = self._convertF2C(self._values[key])
              # elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                # self._values[key] = self._convertDeltaF2C(self._values[key])
              # self._values[key] = self._values[key]
            # elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
              # self._values[key] = False if value == 0 else True
            # else:
             # # log.debug(key) ###########################################
              # self._values[key] = self._convertToIntValue(value)

          # elif isinstance(transaction.response, readCoilsRegistersResponse) :
            # value = transaction.response.registers
            # decimalDivide = 0
            # key = transaction.tag
            # if self._valueDescriptions[key]["dataType"] == dataTypeFloat:
              # if decimalDivide == 0:
                # self._values[key] = self._convertToFloatValue(value)/10
              # else:
                # self._values[key] = value
              # if self._valueDescriptions[key]["unitType"] == unitTypeTemperature:
                # self._values[key] = self._convertF2C(self._values[key])
              # elif self._valueDescriptions[key]["unitType"] == unitTypeDeltaTemperature:
                # self._values[key] = self._convertDeltaF2C(self._values[key])
              # self._values[key] = self._values[key]
            # elif self._valueDescriptions[key]["dataType"] == dataTypeBool:
              # self._values[key] = False if value == 0 else True
            # else:
             # # log.debug(key) ###########################################
              # self._values[key] = self._convertToIntValue(value)


