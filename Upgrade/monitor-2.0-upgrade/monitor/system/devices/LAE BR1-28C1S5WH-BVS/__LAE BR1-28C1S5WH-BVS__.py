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

deviceType = "LAE BR1-28C1S5WH-BVS"
deviceTypeName = "LAE BR1-28C1S5WH-BVS"
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
valueDescriptions["DIG Input 1"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital Input 1","description":"Digital Input 1", "defaultLog":"true"}
valueDescriptions["DIG Input 2"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital Input 2","description":"Digital Input 2", "defaultLog":"true"}
valueDescriptions["Hz"] = {"dataType":dataTypeInt,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"Hz","unitType":"Hert", "defaultLog":"true"}
# OUTPUT - Status Flag bits
# 100 - Status flag
valueDescriptions["ALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Alarm"}
valueDescriptions["MUTE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Mute", "false": "-"},"valueType":valueTypeOutput,"displayName":"Mute"}
valueDescriptions["DEFROST"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost Status", "defaultLog":"true"}
valueDescriptions["DOOR"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Door Status"}
valueDescriptions["TESTMODE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Test Mode"}
valueDescriptions["STANDBY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeOutput,"displayName":"Standby Status"}
valueDescriptions["TWOSETACTIVE"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"II-Set Active"}
valueDescriptions["ZIGBEERESET"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"In Progess", "false": "-"},"valueType":valueTypeOutput,"displayName":"Zigbee Reset"}
# 101 - Alarm flag
valueDescriptions["T1PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T1 Probe Alarm","description":"T1 Probe Alarm"}
valueDescriptions["T2PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T2 Probe Alarm","description":"T2 Probe Alarm"}
valueDescriptions["T3PROBEALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T3 Probe Alarm","description":"T3 Probe Alarm"}
valueDescriptions["LOWTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Low Temp Alarm","description":"Low Temp Alarm"}
valueDescriptions["HIGHTEMPALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Temp Alarm","description":"High Temp Alarm"}
valueDescriptions["HIGHPRESALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Pressure Alarm","description":"High Pressure Alarm"}
valueDescriptions["GENERICALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Generic Alarm","description":"Generic Alarm"}
valueDescriptions["DOOROPENALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Door Open Alarm","description":"Door Open Alarm"}
valueDescriptions["CONDCLEANALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Condenser Clean Alarm","description":"Condenser Clean Alarm"}
valueDescriptions["RTCALARM"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Real Time Clock Error","description":"Real Time Clock Error"}
# 102 - Output flag
valueDescriptions["COMP RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Compressor", "defaultLog":"true"}
valueDescriptions["FAN RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Evaporator Fan", "defaultLog":"true"}
valueDescriptions["DEF RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost Relay", "defaultLog":"true"}
valueDescriptions["AUX1 RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"AUX 1", "defaultLog":"true"}
valueDescriptions["AUX2 RLY"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"AUX 2", "defaultLog":"true"}
valueDescriptions["SSROUT"] = {"dataType":dataTypeBool,"unitType":"OnOff","dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"SSR Driver"}
# Virtual value
valueDescriptions["MDEF"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeConfig,"displayName":"MDEF","description":"Turn On Manual Defrost"}
valueDescriptions["MISF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"MISF","description":"Minimum Compressor Speed Frequency","unitText":"Hz","default":"85"}
valueDescriptions["MASF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"MASF","description":"Maximum Compressor Speed Frequency","unitText":"Hz","default":"150"}
# CONFIG
#CFG REGISTERS
valueDescriptions["MDL"] = {"displayName":"MDL","description":"Control model","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"SS","1":"VS"},"default":"1"}
valueDescriptions["SPL"] = {"displayName":"SPL","description":"Minimum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-6.7"}
valueDescriptions["SPH"] = {"displayName":"SPH","description":"Maximum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"4.4"}
valueDescriptions["SP"] = {"displayName":"SP","description":"Setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"1.1"}
valueDescriptions["HY0"] = {"displayName":"HY0","description":"Thermostat off to on differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.6"}
valueDescriptions["HY1"] = {"displayName":"HY1","description":"Thermostat on to off differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["PB"] = {"displayName":"PB","description":"Proportional Band for VS","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"5.0"}
valueDescriptions["IT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IT","description":"Integrative Time for VS","unitText":"sec","default":"100"}
valueDescriptions["DT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DT","description":"Derivative Time for VS","unitText":"sec","default":"6"}
valueDescriptions["CT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT","description":"Cycling Time for VS","unitText":"sec","default":"5"}
valueDescriptions["AR"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"AR","description":"Antireset","unitText":"%","default":"70"}
valueDescriptions["CRT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRT","description":"Compressor rest time","unitText":"min","default":"2"}
valueDescriptions["CMS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CMS","description":"Compresor Max Speed","unitText":"%","default":"100"}
valueDescriptions["CRS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRS","description":"Compressor Restart Speed","unitText":"%","default":"57"}
valueDescriptions["CRD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRD","description":"Compressor Restart Duration","unitText":"sec","default":"60"}
valueDescriptions["CDS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CDS","description":"Compresor Defrost Speed","unitText":"%","default":"0"}
valueDescriptions["CSS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSS","description":"Compresor Speed Test,Speed Threshold","unitText":"%","default":"100"}
valueDescriptions["CSO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSO","description":"Compressor Speed Test,Compressor ON Time","unitText":"hrs","default":"0"}
valueDescriptions["CST"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CST","description":"Compressor Speed Test,Time Threshold","unitText":"sec","default":"0"}
valueDescriptions["CT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT1","description":"Output run when probe T1 is faulty","unitText":"min","default":"6"}
valueDescriptions["CT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT2","description":"Output stop when probe T1 is faulty","unitText":"min","default":"4"}
valueDescriptions["DFM"] = {"displayName":"DFM","description":"Default start mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TIM","2":"FRO","3":"RTC"},"default":"0"}
valueDescriptions["DFT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DFT","description":"Timer value for automatic defrost to start","unitText":"hrs","default":"6"}
valueDescriptions["DFB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"DFB","description":"Defrost timer backup","default":"false"}
valueDescriptions["DH1"] = {"displayName":"DH1","description":"Defrost time 1","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
# valueDescriptions["DLY"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DLY","description":"Defrost start delay DFM=RT1","unitText":"min"}
valueDescriptions["DH2"] = {"displayName":"DH2","description":"Defrost time 2","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH3"] = {"displayName":"DH3","description":"Defrost time 3","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH4"] = {"displayName":"DH4","description":"Defrost time 4","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH5"] = {"displayName":"DH5","description":"Defrost time 5","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH6"] = {"displayName":"DH6","description":"Defrost time 6","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DLI"] = {"displayName":"DLI","description":"Defrost end temperature","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"8.9"}
valueDescriptions["DTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DTO","description":"Maximum defrost duration","unitText":"min","default":"30"}
valueDescriptions["DTY"] = {"displayName":"DTY","description":"Defrost type","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"ELE","2":"GAS"},"default":"0"}
valueDescriptions["DSO"] = {"displayName":"DSO","description":"Defrost start optimization","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"LO","2":"HI"},"default":"0"}
valueDescriptions["SOD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SOD","description":"Start optimization delay","unitText":"min","default":"0"}
valueDescriptions["DPD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DPD","description":"Pump down time","unitText":"sec","default":"0"}
valueDescriptions["DRN"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DRN","description":"Drip time","unitText":"min","default":"0"}
# valueDescriptions["RON"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"RON","description":"Resistor On time after defrost termination","unitText":"hrs"}
valueDescriptions["DDM"] = {"displayName":"DDM","description":"Display defrost mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"RT","1":"LT","2":"SP","3":"DEF"},"default":"3"}
valueDescriptions["DDY"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DDY","description":"Display delay","unitText":"min","default":"0"}
valueDescriptions["FID"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"FID","description":"Fans active during defrost","default":"true"}
valueDescriptions["FDD"] = {"displayName":"FDD","description":"Fan restart temperature after defrost","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-1.1"}
valueDescriptions["FTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FTO","description":"Maximum fan stop after defrost","unitText":"min","default":"2"}
valueDescriptions["FCM"] = {"displayName":"FCM","description":"Fan mode during thermostatic control","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["FDT"] = {"displayName":"FDT","description":"Evap-air temp difference to turn OFF fans","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["FDH"] = {"displayName":"FDH","description":"Temp differential for fan restart","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.6"}
valueDescriptions["FT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT1","description":"Fan stop delay after stop","unitText":"sec","default":"0"}
valueDescriptions["FT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT2","description":"Timed fan stop","unitText":"min","default":"0"}
valueDescriptions["FT3"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT3","description":"Timed fan run","unitText":"min","default":"0"}
valueDescriptions["ATM"] = {"displayName":"ATM","description":"Alarm threshold management","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ABS","2":"REL"},"default":"0"}
valueDescriptions["ALA"] = {"displayName":"ALA","description":"Low temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-12.2"}
valueDescriptions["AHA"] = {"displayName":"AHA","description":"High temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"10.0"}
valueDescriptions["ALR"] = {"displayName":"ALR","description":"Low temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"-5.6"}
valueDescriptions["AHR"] = {"displayName":"AHR","description":"High temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"5.6"}
valueDescriptions["ATI"] = {"displayName":"ATI","description":"Probe used for temperature alarm detection","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"T2","2":"T3"},"default":"0"}
valueDescriptions["PAD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"PAD","description":"Delay before alarm termperature warning at power on","unitText":"min","default":"60"}
valueDescriptions["ATD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ATD","description":"Delay before alarm termperature warning","unitText":"min","default":"30"}
valueDescriptions["ACC"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ACC","description":"Condenser periodic cleaning","unitText":"weeks","default":"0"}
valueDescriptions["IISM"] = {"displayName":"IISM","description":"Switchover mode to second param set","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"ECO","3":"DI","4":"RTC"},"default":"0"}
valueDescriptions["IISL"] = {"displayName":"IISL","description":"Minimum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-6.7"}
valueDescriptions["IISH"] = {"displayName":"IISH","description":"Maximum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"4.4"}
valueDescriptions["IISP"] = {"displayName":"IISP","description":"Setpoint [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"1.1"}
valueDescriptions["IIH0"] = {"displayName":"IIH0","description":"Thermostat off to on differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"1.1"}
valueDescriptions["IIH1"] = {"displayName":"IIH1","description":"Thermostat on to off differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"1.1"}
valueDescriptions["IIPB"] = {"displayName":"IIPB","description":"Proportional Band for VS Mode 2","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"5.0"}
valueDescriptions["IIC1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIC1","description":"Compressor/heater output run when probe T1 is faulty, in mode 2","unitText":"min","default":"6"}
valueDescriptions["IIDM"] = {"displayName":"IIDM","description":"Defrost start mode, in mode 2","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TIM","2":"FRO","3":"RT1","4":"RT2"},"default":"1"}
valueDescriptions["IIDF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDF","description":"Timer value for automatic defrost to start [II]","unitText":"hrs","default":"6"}
valueDescriptions["IIDL"] = {"displayName":"IIDL","description":"Defrost end temperature, in mode 2","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"8.9"}
valueDescriptions["IIDO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDO","description":"Maximum defrost duration, in mode 2","unitText":"min","default":"30"}
valueDescriptions["IIDR"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDR","description":"Drip time, in mode 2","unitText":"min","default":"0"}
valueDescriptions["IIFI"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"IIFI","description":"Fans active during defrost, in mode 2","default":"true"}
valueDescriptions["IIFD"] = {"displayName":"IIFD","description":"Fan re-start temperature after defrost, in mode 2","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-1.1"}
valueDescriptions["IIFT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIFT","description":"Maximum fan stop after defrost, in mode 2","unitText":"min","default":"2"}
valueDescriptions["IIFC"] = {"displayName":"IIFC","description":"Fan mode during thermostatic control [II]","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["IIAL"] = {"displayName":"IIAL","description":"Low temperature alarm threshold, in mode 2","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"-12.2"}
valueDescriptions["IIAH"] = {"displayName":"IIAH","description":"High temperature alarm threshold, in mode 2","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"50.0"}
valueDescriptions["ECS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ECS","description":"Controller switchover sensitivity","default":"3"}
valueDescriptions["EPT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"EPT","description":"Pull down time","unitText":"min","default":"30"}
valueDescriptions["SB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"SB","description":"Standby button enable","default":"true"}
valueDescriptions["DSM"] = {"displayName":"DSM","description":"Door switch input mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["DAD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DAD","description":"Delay before door opening alarm","unitText":"min","default":"30"}
valueDescriptions["CSD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSD","description":"Stop delay after door has opened","unitText":"min","default":"5"}
valueDescriptions["D1O"] = {"displayName":"D1O","description":"DI1 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"IISM","4":"RDS","5":"TS1","6":"TS2"},"default":"0"}
valueDescriptions["D1A"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"D1A","description":"Digital input 1 activation","default":"true"}
valueDescriptions["D2O"] = {"displayName":"D2O","description":"DI2 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"IISM","4":"RDS"},"default":"0"}
valueDescriptions["D2A"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"D2A","description":"Digital input 2 activation","default":"false"}
valueDescriptions["LSM"] = {"displayName":"LSM","description":"Light control mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"ECO","3":"DI1","4":"DI2","5":"RTC"},"default":"0"}
valueDescriptions["LSA"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"LSA","description":"Light activation","default":"false"}
valueDescriptions["STT"] = {"displayName":"STT","description":"Start time for timed actions","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeList,"default":"0"}
valueDescriptions["EDT"] = {"displayName":"EDT","description":"Stop time for timed actions","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeList,"default":"0"}
valueDescriptions["OA1"] = {"displayName":"OA1","description":"AUX 1 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"LGT","2":"0-1","3":"2CU","4":"2EU","5":"ALO","6":"ALC"},"default":"0"}
valueDescriptions["OA2"] = {"displayName":"OA2","description":"AUX 2 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"LGT","2":"0-1","3":"2CU","4":"2EU","5":"ALO","6":"ALC"},"default":"0"}
valueDescriptions["2CD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"2CD","description":"Aux compressor start delay","unitText":"sec","default":"0"}
valueDescriptions["OS1"] = {"displayName":"OS1","description":"Probe T1 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["T2"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"T2","description":"Probe T2 enable","default":"false"}
valueDescriptions["OS2"] = {"displayName":"OS2","description":"Probe T2 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["T3"] = {"displayName":"T3","description":"Probe 3 operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DSP","2":"CND","3":"2EU"},"default":"0"}
valueDescriptions["OS3"] = {"displayName":"OS3","description":"Probe T3 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1,"default":"0.0"}
valueDescriptions["AHM"] = {"displayName":"AHM","description":"High condenser alarm operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["AHT"] = {"displayName":"AHT","description":"Condensation temp alarm","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1,"default":"82.0"}
valueDescriptions["TLD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"TLD","description":"Delay for min and max temp logging","unitText":"min","default":"1"}
valueDescriptions["TDS"] = {"displayName":"TDS","description":"Selects temp probe to display","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"1-2","2":"T3"},"default":"0"}
valueDescriptions["AVG"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"AVG","description":"Relative weight of T2 on T1","unitText":"%","default":"0"}
valueDescriptions["SCL"] = {"displayName":"SCL","description":"Readout scale","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"1°C","1":"2°C","2":"°F"},"default":"0"}
valueDescriptions["SIM"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SIM","description":"Display slowdown","default":"0"}
#266 CFG_1 BITS
valueDescriptions["STBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "No"},"valueType":valueTypeConfig,"displayName":"STBY","description":"Standby"}
valueDescriptions["LOC"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LOC","description":"Keyboard lock"}
# valueDescriptions["MANUALSTBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "-"},"valueType":valueTypeConfig,"displayName":"MANUALSTBY","description":"Manual standby"}
valueDescriptions["LIGHTS"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LIGHTS","description":"Manual lights"}
#valueDescriptions["C-H"] = {"dataType":dataTypeBool,"dataList":{"true":"HEA", "false": "REF"},"valueType":valueTypeConfig,"displayName":"C-H","description":"Refrigerating or heating mode"}

# ALARM
alarmDescriptions = OrderedDict()
alarmDescriptions["T1PROBEALARM"] = {"description": "T1 Probe Alarm"}
alarmDescriptions["T2PROBEALARM"] = {"description": "T2 Probe Alarm"}
alarmDescriptions["T3PROBEALARM"] = {"description": "T3 Probe Alarm"}
alarmDescriptions["LOWTEMPALARM"] = {"description": "Low Temp Alarm"}
alarmDescriptions["HIGHTEMPALARM"] = {"description": "High Temp Alarm"}
alarmDescriptions["HIGHPRESALARM"] = {"description": "High Pressure Alarm"}
alarmDescriptions["GENERICALARM"] = {"description": "Generic Alarm"}
alarmDescriptions["DOOROPENALARM"] = {"description": "Door Open Alarm"}
alarmDescriptions["CONDCLEANALARM"] = {"description": "Condenser Clean Alarm"}
alarmDescriptions["RTCALARM"] = {"description": "Real Time Clock Error"}


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
            ["2","HY1",205],
            ["3","CRT",206],
            ["3","CT1",207],
            ["3","CT2",208],
            ["4","DFM",209],
            ["4","DFT",210],
            ["4","DLI",211],
            ["5","DTO",212],
            ["5","DTY",213],
            ["5","DSO",214],
            ["6","SOD",215],
            ["6","DPD",216],
            ["6","DRN",217],
            ["7","DDM",218],
            ["7","DDY",219],
            ["7","FDD",220],
            ["8","FTO",221],
            ["8","FCM",222],
            ["8","FDT",223],
            ["9","FDH",224],
            ["9","FT1",225],
            ["9","FT2",226],
            ["10","FT3",227],
            ["10","ATM",228],
            ["10","ALA",229],
            ["11","AHA",230],
            ["11","ALR",231],
            ["11","AHR",232],
            ["12","ATI",233],
            ["12","ATD",234],
            ["12","ACC",235],
            ["13","IISM",236],
            ["13","IISL",237],
            ["13","IISH",238],
            ["14","IISP",239],
            ["14","IIH0",240],
            ["14","IIH1",241],
            ["15","IIFC",242],
            ["15","ECS",243],
            ["15","IIDF",244],
            ["16","DSM",245],
            ["16","DAD",246],
            ["16","CSD",247],
            ["17","D1O",248],
            ["17","D2O",249],
            ["18","LSM",251],
            ["18","OA1",252],
            ["18","OA2",253],
            ["19","2CD",254],
            ["19","OS1",255],
            ["19","OS2",256],
            ["20","T3",257],
            ["20","OS3",258],
            ["20","AHM",259],
            ["21","AHT",260],
            ["21","TLD",261],
            ["21","TDS",262],
            ["22","AVG",263],
            ["22","SIM",264],
            ["22","266_bitfield",266],
            ["23","EPT",271],
            ["23","DH1",272],
            ["23","DH2",273],
            ["24","DH3",274],
            ["24","DH4",275],
            ["24","DH5",276],
            ["25","DH6",277],
            ["25","STT",278],
            ["25","EDT",279],
            ["26","IIDO",283],
            ["26","IIDR",284],
            ["26","IIFD",285],
            ["27","IIFT",286],
            ["27","IIAL",287],
            ["27","IIAH",288],
            ["28","IIC1",289],
            ["28","PAD",290],
            ["28","IIDM",291],
            ["29","IIDL",292],
            ["29","MISF",293],
            ["29","MASF",294],
            ["30","PB",295],
            ["30","IT",296],
            ["30","DT",297],
            ["31","CT",298],
            ["31","AR",299],
            ["31","CMS",300],
            ["32","CRS",301],
            ["32","CRD",302],
            ["32","CDS",303],
            ["33","CSO",304],
            ["33","CST",305],
            ["33","CSS",306],
            ["34","IIPB",307],
            ["34","MDL",308],
            ["35","IIFI",713],
            ["36","CMD_1",100]
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

      if len(self._newDeviceConfigurationValues) == 1:
        value = 0
        value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value
        networkTrans.transactions.append(NetworkMessage(writeHoldingRegister(100, 0x04), "MDEF"))
        break

      if key == "CMD_1":
        value = 0
        if "MDEF" in self._newDeviceConfigurationValues:
          value = value | 0x04 if self._newDeviceConfigurationValues["MDEF"] else value

      elif key == "266_bitfield":
        value = 0
        value = value | 0x1 if self._newDeviceConfigurationValues["SB"] else value
        value = value | 0x2 if self._newDeviceConfigurationValues["STBY"] else value
        value = value | 0x4 if self._newDeviceConfigurationValues["LOC"] else value
        value = value | 0x8 if self._newDeviceConfigurationValues["DFB"] else value
        value = value | 0x10 if self._newDeviceConfigurationValues["FID"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["T2"] else value
      # value = value | 0x40 if self._newDeviceConfigurationValues["MANUALSTBY"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["LIGHTS"] else value
      # value = value | 0x100 if self._newDeviceConfigurationValues["C-H"] else value
        value = value | 0x200 if self._newDeviceConfigurationValues["D1A"] else value
        value = value | 0x400 if self._newDeviceConfigurationValues["D2A"] else value
        value = value | 0x1000 if self._newDeviceConfigurationValues["LSA"] else value

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

    if "DIG Input 1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(143, 1), "DIG Input 1"))

    if "DIG Input 2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(144, 1), "DIG Input 2"))

    if "Hz" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(105, 1), "Hz"))

    setValueToLog = set(valueToLog)
    setStatusFlag = set(["ALARM","MUTE","DEFROST","DOOR","TESTMODE","STANDBY","TWOSETACTIVE","ZIGBEERESET"])
    if len(setValueToLog & setStatusFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(100, 1), "100_bitfield"))

    setAlarmFlag = set(["T1PROBEALARM","T2PROBEALARM","T3PROBEALARM","LOWTEMPALARM","HIGHTEMPALARM","HIGHPRESALARM","GENERICALARM","DOOROPENALARM","CONDCLEANALARM","RTCALARM"])
    if len(setValueToLog & setAlarmFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(101, 1), "101_bitfield"))

    setOutputFlag = set(["COMP RLY","FAN RLY","DEF RLY","AUX1 RLY","AUX2 RLY","SSROUT"])
    if len(setValueToLog & setOutputFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(readHoldingRegisters(102, 1), "102_bitfield"))

    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    statusList = [
            ["1","T1 TEMP",0],
            ["1","T2 TEMP",1],
            ["1","T3 TEMP",2],
            ["2","100_bitfield",100],
            ["2","102_bitfield",102],
            ["3","Hz",105],
            ["4","DIG Input 1",143],
            ["4","DIG Input 2",144]
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
              self._values["ALARM"] = ((value & 0x1) > 0)
              self._alarm = self._values["ALARM"]
              self._values["MUTE"] = ((value & 0x2) > 0)
              self._values["DEFROST"] = ((value & 0x4) > 0)
              self._values["DOOR"] = ((value & 0x8) > 0)
              self._values["TESTMODE"] = ((value & 0x10) > 0)
              self._values["STANDBY"] = ((value & 0x20) > 0)
              self._values["TWOSETACTIVE"] = ((value & 0x40) > 0)
              self._values["ZIGBEERESET"] = ((value & 0x80) > 0)

            elif transaction.tag == "101_bitfield":
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
              self._values["HIGHPRESALARM"] = ((value & 0x20) > 0)
              self.checkBooleanAdvisory("HIGHPRESALARM", self._values["HIGHPRESALARM"])
              self._values["GENERICALARM"] = ((value & 0x40) > 0)
              self.checkBooleanAdvisory("GENERICALARM", self._values["GENERICALARM"])
              self._values["DOOROPENALARM"] = ((value & 0x80) > 0)
              self.checkBooleanAdvisory("DOOROPENALARM", self._values["DOOROPENALARM"])
              self._values["CONDCLEANALARM"] = ((value & 0x100) > 0)
              self.checkBooleanAdvisory("CONDCLEANALARM", self._values["CONDCLEANALARM"])
              self._values["RTCALARM"] = ((value & 0x200) > 0)
              self.checkBooleanAdvisory("RTCALARM", self._values["RTCALARM"])

            elif transaction.tag == "102_bitfield":
              self._values["COMP RLY"] = ((value & 0x1) > 0)
              self._values["FAN RLY"] = ((value & 0x2) > 0)
              self._values["DEF RLY"] = ((value & 0x4) > 0)
              self._values["AUX1 RLY"] = ((value & 0x10) > 0)
              self._values["AUX2 RLY"] = ((value & 0x20) > 0)
              self._values["SSROUT"] = ((value & 0x40) > 0)

            elif transaction.tag == "266_bitfield":
              self._values["SB"] = ((value & 0x1) > 0)
              self._values["STBY"] = ((value & 0x2) > 0)
              self._values["LOC"] = ((value & 0x4) > 0)
              self._values["DFB"] = ((value & 0x8) > 0)
              self._values["FID"] = ((value & 0x10) > 0)
              self._values["T2"] = ((value & 0x20) > 0)
           #   self._values["MANUALSTBY"] = ((value & 0x40) > 0)
              self._values["LIGHTS"] = ((value & 0x80) > 0)
           #  self._values["C-H"] = ((value & 0x100) > 0)
              self._values["D1A"] = ((value & 0x200) > 0)
              self._values["D2A"] = ((value & 0x400) > 0)
              self._values["LSA"] = ((value & 0x1000) > 0)

            elif transaction.tag == "CMD_1":
              self._values["MDEF"] = ((value & 0x4) > 0)

            else:
              key = transaction.tag
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




  #def _convertF2C(self, value):
  #  return (value - 32) / 1.8

  #def _convertC2F(self, value):
  #  return (value * 1.8) + 32

  #def _convertDeltaF2C(self, value):
  #  return value / 1.8

  #def _convertDeltaC2F(self, value):
  #  return value * 1.8

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

