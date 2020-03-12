from flask_restful import Resource, request
from flask import session, jsonify

import leoObject
import networkConstants
import deviceConstants

class getE2StatusScreenData(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def _GetE2NetworkObject(self) :

      networkDict = self.gLeonardo.directory.getNetworkManager().getNetworks()
      if networkDict != None :
        # Since orderedDict, netrec will only be key into NetworkDict.
        for netrec in networkDict :
          # Look for E2 Network - there will only be 1.
          if networkDict[netrec]['typeName'].find( networkConstants.networkE2NetText ) == 0 :
            E2NetObject = self.gLeonardo.directory.getDeviceManager().getNetworkObjectByName( networkDict[netrec]['name'])
            return E2NetObject

        return None

    def post(self):
#      print "getE2StatusScreenData LEO Mem=", self.gLeonardo
      returnDict = {}

      E2NetworkObject = self._GetE2NetworkObject()

      # The POST must send: objType:E2Network OR E2Device. If E2Device, then E2DevName must be set with either one or many E2 device names in a list.
      jsonDict = request.json
      paramsList = jsonDict['params']
      paramsDict = paramsList[0]
      reqType = paramsDict['reqType'] # "E2Network", "E2Devices", "E2Static"
      devName = paramsDict['E2DevNames']

      # Get list of devices
      devicesDict = self.gLeonardo.directory.getDeviceManager().getDevices()

      E2DevNames = []
      if reqType == "E2Network" or reqType == "E2Devices": # We want ALL E2 devices' information

        if reqType == "E2Network" : # We want a single E2 devices' information
          for devName in devicesDict :
            if devicesDict[devName]['deviceTypeName'] == deviceConstants.deviceE2ExecutionText :
              E2DevNames.append( devName )
        elif reqType == "E2Devices" : # We want a single E2 devices' information
          E2DevNames.append( paramsDict['E2DevNames'] )

        for E2Name in E2DevNames : # Just need to get single E2 device. Find it in the device list.
          # Now, look for E2 Devices - there could be many...
          if E2Name in devicesDict :
            E2DeviceObject = self.gLeonardo.directory.getDeviceManager().getDeviceObjectByName( E2Name )
            if E2DeviceObject != None:
              returnDict[E2Name] = E2DeviceObject.getE2StatusScreenData()

      elif reqType == "E2CellTypeInfo" or reqType == "E2AppInfo" :
        E2DevNames = paramsDict['E2DevNames'] # Single E2 device name
        E2DeviceObject = self.gLeonardo.directory.getDeviceManager().getDeviceObjectByName( E2DevNames )
        if E2DeviceObject != None:
          if reqType == "E2CellTypeInfo" :   # We want the "statically" defined information for a single E2
              returnDict = E2DeviceObject.GetE2DataStructs( "E2CellTypeInfo" )
          elif reqType == "E2AppInfo" :
              returnDict = E2DeviceObject.GetE2DataStructs( "E2AppInfo" )

      if len( returnDict ) > 0 :
        return jsonify( returnDict )
      else :
        return None
