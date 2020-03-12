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

deviceType = "LAE BR1-28"
deviceTypeName = "LAE BR1-28"
executionType = deviceNetworkExecution
executionTypeName = deviceNetworkExecutionText

timeList = OrderedDict()
timeListWithSkip = OrderedDict()
for idx in xrange(144):
  timeList[str(idx)] = "%s:%s0" % (str(idx / 6), str(idx % 6))
  timeListWithSkip[str(idx)] = "%s:%s0" % (str(idx / 6), str(idx % 6))
timeListWithSkip['144'] = '---'

valueDescriptions = OrderedDict()
valueDescriptions["T1TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T1","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T2TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T2","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["T3TEMP"] = {"dataType":dataTypeFloat,"valueType":valueTypeOutput,"significantDigits":1,"displayName":"T3","unitType":unitTypeTemperature, "defaultLog":"true"}
valueDescriptions["ALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Alarm"}
valueDescriptions["MUTE"] = {"dataType":dataTypeBool,"dataList":{"true":"Mute", "false": "-"},"valueType":valueTypeOutput,"displayName":"Mute", "defaultLog":"true"}
valueDescriptions["DEFROST"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost", "defaultLog":"true"}
valueDescriptions["DOOR"] = {"dataType":dataTypeBool,"dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Door", "defaultLog":"true"}
valueDescriptions["TESTMODE"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Test Mode"}
valueDescriptions["STANDBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "-"},"valueType":valueTypeOutput,"displayName":"Standby"}
valueDescriptions["TWOSETACTIVE"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"II-Set Active"}
valueDescriptions["ZIGBEERESET"] = {"dataType":dataTypeBool,"dataList":{"true":"In Progess", "false": "-"},"valueType":valueTypeOutput,"displayName":"Zigbee Reset"}
valueDescriptions["T1PROBEALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T1 Probe Alarm","description":"T1 Probe Alarm"}
valueDescriptions["T2PROBEALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T2 Probe Alarm","description":"T2 Probe Alarm"}
valueDescriptions["T3PROBEALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"T3 Probe Alarm","description":"T3 Probe Alarm"}
valueDescriptions["LOWTEMPALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Low Temp Alarm","description":"Low Temp Alarm"}
valueDescriptions["HIGHTEMPALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Temp Alarm","description":"High Temp Alarm"}
valueDescriptions["HIGHPRESALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"High Pressure Alarm","description":"High Pressure Alarm"}
valueDescriptions["GENERICALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Generic Alarm","description":"Generic Alarm"}
valueDescriptions["DOOROPENALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Door Open Alarm","description":"Door Open Alarm"}
valueDescriptions["CONDCLEANALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Condenser Clean Alarm","description":"Condenser Clean Alarm"}
valueDescriptions["RTCALARM"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Real Time Clock Error","description":"Real Time Clock Error"}
valueDescriptions["COMPOUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Compressor Out", "defaultLog":"true"}
valueDescriptions["EVAPFANOUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Evaporator Fan Out", "defaultLog":"true"}
valueDescriptions["DEFOUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Defrost Out", "defaultLog":"true"}
valueDescriptions["AUX1OUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Aux 1 Out", "defaultLog":"true"}
valueDescriptions["AUX2OUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"Aux 2 Out", "defaultLog":"true"}
valueDescriptions["SSROUT"] = {"dataType":dataTypeBool,"dataList":{"true":"On", "false": "Off"},"valueType":valueTypeOutput,"displayName":"SSR Driver", "defaultLog":"true"}
valueDescriptions["DIGIN1"] = {"dataType":dataTypeBool,"dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital In 1","description":"Digital Input 1", "defaultLog":"true"}
valueDescriptions["DIGIN2"] = {"dataType":dataTypeBool,"dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital In 2","description":"Digital Input 2", "defaultLog":"true"}
valueDescriptions["DIGIN3"] = {"dataType":dataTypeBool,"dataList":{"true":"Open", "false": "Closed"},"valueType":valueTypeOutput,"displayName":"Digital In 3","description":"Digital Input 3", "defaultLog":"true"}
valueDescriptions["SCL"] = {"displayName":"SCL","description":"Readout scale","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"1°C","1":"2°C","2":"°F"},"default":"0"}
valueDescriptions["SPL"] = {"displayName":"SPL","description":"Minimum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["SPH"] = {"displayName":"SPH","description":"Maximum setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["SP"] = {"displayName":"SP","description":"Setpoint [I]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["HY0"] = {"displayName":"HY0","description":"Thermostat off to on differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["HY1"] = {"displayName":"HY1","description":"Thermostat on to off differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["CRT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CRT","description":"Compressor rest time","unitText":"min"}
valueDescriptions["CT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT1","description":"Output run when probe T1 is faulty","unitText":"min"}
valueDescriptions["CT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CT2","description":"Output stop when probe T1 is faulty","unitText":"min"}
valueDescriptions["DFM"] = {"displayName":"DFM","description":"Default start mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"TIM","2":"FRO"},"default":"0"}
valueDescriptions["DFT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DFT","description":"Timer value for automatic defrost to start","unitText":"hrs"}
valueDescriptions["DLI"] = {"displayName":"DLI","description":"Defrost end temperature","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["DTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DTO","description":"Maximum defrost duration","unitText":"min"}
valueDescriptions["DTY"] = {"displayName":"DTY","description":"Defrost type","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"ELE","2":"GAS"},"default":"0"}
valueDescriptions["DSO"] = {"displayName":"DSO","description":"Defrost start optimization","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"OFF","1":"LO","2":"HI"},"default":"0"}
valueDescriptions["SOD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SOD","description":"Start optimization delay","unitText":"min"}
valueDescriptions["DPD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DPD","description":"Drain pump down","unitText":"sec"}
valueDescriptions["DRN"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DRN","description":"Drain down time","unitText":"min"}
valueDescriptions["DDM"] = {"displayName":"DDM","description":"Display defrost mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"RT","1":"LT","2":"SP","3":"DEF"},"default":"0"}
valueDescriptions["DDY"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DDY","description":"Display delay","unitText":"min"}
valueDescriptions["FDD"] = {"displayName":"FDD","description":"Fan restart temperature after defrost","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["FTO"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FTO","description":"Maximum fan stop after defrost","unitText":"min"}
valueDescriptions["FCM"] = {"displayName":"FCM","description":"Fan mode during thermostatic control","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["FDT"] = {"displayName":"FDT","description":"Evap-air temp difference to turn OFF fans","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["FDH"] = {"displayName":"FDH","description":"Temp differential for fan restart","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["FT1"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT1","description":"Fan stop delay after stop","unitText":"sec"}
valueDescriptions["FT2"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT2","description":"Timed fan stop","unitText":"min"}
valueDescriptions["FT3"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"FT3","description":"Timed fan run","unitText":"min"}
valueDescriptions["ATM"] = {"displayName":"ATM","description":"Alarm threshold management","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ABS","2":"REL"},"default":"0"}
valueDescriptions["ALA"] = {"displayName":"ALA","description":"Low temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["AHA"] = {"displayName":"AHA","description":"High temp alarm threshold","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["ALR"] = {"displayName":"ALR","description":"Low temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["AHR"] = {"displayName":"AHR","description":"High temp alarm differential","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["ATI"] = {"displayName":"ATI","description":"Probe used for temperature alarm detection","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"T2","2":"T3"},"default":"0"}
valueDescriptions["ATD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ATD","description":"Delay before alarm termperature warning","unitText":"min"}
valueDescriptions["ACC"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ACC","description":"Condenser periodic cleaning","unitText":"weeks"}
valueDescriptions["IISM"] = {"displayName":"IISM","description":"Switchover mode to second param set","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"ECO","3":"DI"},"default":"0"}
valueDescriptions["IISL"] = {"displayName":"IISL","description":"Minimum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["IISH"] = {"displayName":"IISH","description":"Maximum temperature [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["IISP"] = {"displayName":"IISP","description":"Setpoint [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["IIH0"] = {"displayName":"IIH0","description":"Thermostat off to on differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["IIH1"] = {"displayName":"IIH1","description":"Thermostat on to off differential [II]","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["IIFC"] = {"displayName":"IIFC","description":"Fan mode during thermostatic control [II]","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"MON","1":"TMP","2":"TIM"},"default":"0"}
valueDescriptions["ECS"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"ECS","description":"Controller switchover sensitivity"}
valueDescriptions["IIDF"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"IIDF","description":"Timer value for automatic defrost to start [II]","unitText":"hrs"}
valueDescriptions["DSM"] = {"displayName":"DSM","description":"Door switch input mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["DAD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"DAD","description":"Delay before door opening alarm","unitText":"min"}
valueDescriptions["CSD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"CSD","description":"Stop delay after door has opened","unitText":"min"}
valueDescriptions["D1O"] = {"displayName":"D1O","description":"DI1 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"IISM","4":"RDS"},"default":"0"}
valueDescriptions["D2O"] = {"displayName":"D2O","description":"DI2 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"IISM","4":"RDS"},"default":"0"}
valueDescriptions["D3O"] = {"displayName":"D3O","description":"DI3 digital input operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DOR","2":"ALR","3":"IISM","4":"RDS","5":"DSY"},"default":"0"}
valueDescriptions["LSM"] = {"displayName":"LSM","description":"Light control mode","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"MAN","2":"ECO","3":"DI1","4":"DI2","5":"DI3","6":"RTC"},"default":"0"}
valueDescriptions["OA1"] = {"displayName":"OA1","description":"AUX 1 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"LGT","2":"0-1","3":"2CU","4":"2EU","5":"ALO","6":"ALC"},"default":"0"}
valueDescriptions["OA2"] = {"displayName":"OA2","description":"AUX 2 output operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"LGT","2":"0-1","3":"2CU","4":"2EU","5":"ALO","6":"ALC"},"default":"0"}
valueDescriptions["2CD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"2CD","description":"Aux compressor start delay","unitText":"sec"}
valueDescriptions["OS1"] = {"displayName":"OS1","description":"Probe T1 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["OS2"] = {"displayName":"OS2","description":"Probe T2 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["T3"] = {"displayName":"T3","description":"Probe 3 operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"DSP","2":"CND","3":"2EU"},"default":"0"}
valueDescriptions["OS3"] = {"displayName":"OS3","description":"Probe T3 Offset","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType": unitTypeDeltaTemperature,"significantDigits":1}
valueDescriptions["AHM"] = {"displayName":"AHM","description":"High condenser alarm operation","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"NON","1":"ALR","2":"STP"},"default":"0"}
valueDescriptions["AHT"] = {"displayName":"AHT","description":"Condensation temp alarm","dataType":dataTypeFloat,"valueType":valueTypeConfig,"unitType":unitTypeTemperature,"significantDigits":1}
valueDescriptions["TLD"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"TLD","description":"Delay for min and max temp logging","unitText":"min"}
valueDescriptions["TDS"] = {"displayName":"TDS","description":"Selects temp probe to display","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":{"0":"T1","1":"1-2","2":"T3"},"default":"0"}
valueDescriptions["AVG"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"AVG","description":"Relative weight of T2 on T1","unitText":"%"}
valueDescriptions["SIM"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"SIM","description":"Display slowdown"}
valueDescriptions["SB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"SB","description":"Standby button enable"}
valueDescriptions["STDBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "-"},"valueType":valueTypeConfig,"displayName":"STDBY","description":"Standby"}
valueDescriptions["LOC"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LOC","description":"Keyboard lock"}
valueDescriptions["DFB"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"DFB","description":"Defrost timer backup"}
valueDescriptions["FID"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"FID","description":"Fans active during defrost"}
valueDescriptions["T2"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"T2","description":"Probe T2 enable"}
valueDescriptions["MANUALSTBY"] = {"dataType":dataTypeBool,"dataList":{"true":"Standby", "false": "-"},"valueType":valueTypeConfig,"displayName":"MANUALSTBY","description":"Manual standby"}
valueDescriptions["LIGHTS"] = {"dataType":dataTypeBool,"dataList":{"true":"Yes", "false": "No"},"valueType":valueTypeConfig,"displayName":"LIGHTS","description":"Manual lights"}
valueDescriptions["C-H"] = {"dataType":dataTypeBool,"dataList":{"true":"HEA", "false": "REF"},"valueType":valueTypeConfig,"displayName":"C-H","description":"Refrigerating or heating mode"}
valueDescriptions["D1A"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"D1A","description":"Digital input 1 activation"}
valueDescriptions["D2A"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"D2A","description":"Digital input 2 activation"}
valueDescriptions["D3A"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"D3A","description":"Digital input 3 activation"}
valueDescriptions["LSA"] = {"dataType":dataTypeBool,"dataList":{"true":"Closed", "false": "Open"},"valueType":valueTypeConfig,"displayName":"LSA","description":"Light activation"}
valueDescriptions["EPT"] = {"dataType":dataTypeInt,"valueType":valueTypeConfig,"displayName":"EPT","description":"Pull down time","unitText":"min"}
valueDescriptions["DH1"] = {"displayName":"DH1","description":"Defrost time 1","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH2"] = {"displayName":"DH2","description":"Defrost time 2","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH3"] = {"displayName":"DH3","description":"Defrost time 3","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH4"] = {"displayName":"DH4","description":"Defrost time 4","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH5"] = {"displayName":"DH5","description":"Defrost time 5","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["DH6"] = {"displayName":"DH6","description":"Defrost time 6","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeListWithSkip,"default":"0"}
valueDescriptions["STT"] = {"displayName":"STT","description":"Start time for timed actions","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeList,"default":"0"}
valueDescriptions["EDT"] = {"displayName":"EDT","description":"Stop time for timed actions","dataType":dataTypeList,"valueType":valueTypeConfig,"dataList":timeList,"default":"0"}


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
  def __init__(self, deviceManager, name, description, network, networkAddress, image):
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
            ["17","D3O",250],
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
            ["25","EDT",279]
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

      if key == "266_bitfield":
        value = 0
        value = value | 0x1 if self._newDeviceConfigurationValues["SB"] else value
        value = value | 0x2 if self._newDeviceConfigurationValues["STDBY"] else value
        value = value | 0x4 if self._newDeviceConfigurationValues["LOC"] else value
        value = value | 0x8 if self._newDeviceConfigurationValues["DFB"] else value
        value = value | 0x10 if self._newDeviceConfigurationValues["FID"] else value
        value = value | 0x20 if self._newDeviceConfigurationValues["T2"] else value
        value = value | 0x40 if self._newDeviceConfigurationValues["MANUALSTBY"] else value
        value = value | 0x80 if self._newDeviceConfigurationValues["LIGHTS"] else value
        value = value | 0x100 if self._newDeviceConfigurationValues["C-H"] else value
        value = value | 0x200 if self._newDeviceConfigurationValues["D1A"] else value
        value = value | 0x400 if self._newDeviceConfigurationValues["D2A"] else value
        value = value | 0x800 if self._newDeviceConfigurationValues["D3A"] else value
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

      networkTrans.transactions.append(NetworkMessage(modbusConstants.writeHoldingRegister(configItem[2], value), configItem[1]))
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
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(item[2], 1), item[1]))
    return retval

  def _prepareUpdateDeviceConfigurationTransactions(self):
    return self._prepareListOfTransactions(self.configModbusList, "ReadConfig")


  def _prepareLoggingTransactions(self, valueToLog):
    if len(valueToLog) == 0:
      return None

    networkTrans = NetworkTransaction("Logging")

    if "T1TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(0, 1), "T1TEMP"))

    if "T2TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(1, 1), "T2TEMP"))

    if "T3TEMP" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(2, 1), "T3TEMP"))

    if "DIGIN1" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(143, 1), "DIGIN1"))

    if "DIGIN2" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(144, 1), "DIGIN2"))

    if "DIGIN3" in valueToLog:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(145, 1), "DIGIN3"))

    setValueToLog = set(valueToLog)
    setFlag = set(["ALARM","MUTE","DEFROST","DOOR","TESTMODE","STANDBY","TWOSETACTIVE","ZIGBEERESET"])
    if len(setValueToLog & setFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(100, 1), "100_bitfield"))

    setFlag = set(["T1PROBEALARM","T2PROBEALARM","T3PROBEALARM","LOWTEMPALARM","HIGHTEMPALARM","HIGHPRESALARM","GENERICALARM","DOOROPENALARM","CONDCLEANALARM","RTCALARM"])
    if len(setValueToLog & setFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(101, 1), "101_bitfield"))

    setFlag = set(["COMPOUT","EVAPFANOUT","DEFOUT","AUX1OUT","AUX2OUT","SSROUT"])
    if len(setValueToLog & setFlag) > 0:
      networkTrans.transactions.append(NetworkMessage(modbusConstants.readHoldingRegisters(102, 1), "102_bitfield"))

    return [ networkTrans ]

  def _prepareUpdateStatusTransactions(self):
    statusList = [
            ["1","T1TEMP",0],
            ["1","T2TEMP",1],
            ["1","T3TEMP",2],
            ["2","100_bitfield",100],
            ["2","102_bitfield",102],
            ["2","DIGIN1",143],
            ["3","DIGIN2",144],
            ["3","DIGIN3",145]
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
          if isinstance(transaction.response, modbusConstants.readHoldingRegistersResponse):
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
              self._values["COMPOUT"] = ((value & 0x1) > 0)
              self._values["EVAPFANOUT"] = ((value & 0x2) > 0)
              self._values["DEFOUT"] = ((value & 0x8) > 0)
              self._values["AUX1OUT"] = ((value & 0x10) > 0)
              self._values["AUX2OUT"] = ((value & 0x20) > 0)
              self._values["SSROUT"] = ((value & 0x40) > 0)

            elif transaction.tag == "266_bitfield":
              self._values["SB"] = ((value & 0x1) > 0)
              self._values["STDBY"] = ((value & 0x2) > 0)
              self._values["LOC"] = ((value & 0x4) > 0)
              self._values["DFB"] = ((value & 0x8) > 0)
              self._values["FID"] = ((value & 0x10) > 0)
              self._values["T2"] = ((value & 0x20) > 0)
              self._values["MANUALSTBY"] = ((value & 0x40) > 0)
              self._values["LIGHTS"] = ((value & 0x80) > 0)
              self._values["C-H"] = ((value & 0x100) > 0)
              self._values["D1A"] = ((value & 0x200) > 0)
              self._values["D2A"] = ((value & 0x400) > 0)
              self._values["D3A"] = ((value & 0x800) > 0)
              self._values["LSA"] = ((value & 0x1000) > 0)

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
    if self.userAction is not None:
      if self.userAction['command'] == 'defrost':
        networkTrans = NetworkTransaction('defrost')
        retval.append(networkTrans)
        networkTrans.transactions.append(NetworkMessage(modbusConstants.writeHoldingRegister(100, 0x04), 'defrost'))
      self.userAction = None
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

