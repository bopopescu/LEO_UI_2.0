from flask_restful import Resource, request
from flask import session, jsonify

import leoObject
import networkConstants
import deviceConstants

class setE2Settings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    # E2 settings will be read and written through the E2 network object because it is a singleton for all E2 devices.
    # Each E2 device will go directly to the database to read their settings through the device level E2DeviceSettingsInit method in the device
    # This REST interface will be responsible for making sure each E2 device refreshes its settings when a change is made from here.

    def _GetE2NetworkObject(self) :
      networkDict = self.gLeonardo.directory.getNetworkManager().getNetworks()
      if networkDict != None :
        # Since orderedDict, netrec will only be key into NetworkDict.
        for netrec in networkDict :
          if networkDict[netrec]['typeName'].find( networkConstants.networkE2NetText ) == 0 :
            return self.gLeonardo.directory.getDeviceManager().getNetworkObjectByName( networkDict[netrec]['name'])
        return None

    def post(self):
#      print "setE2Settings LEO Mem=", self.gLeonardo
      jsonDict = request.json
      dictE2Settings = jsonDict['params'][0]
#      print "ID = ", request.json['id'], "REQ->", request.json, "Params->", jsonDict['params']
#      print "dictE2Settings", dictE2Settings

      try:
        E2NetObject = self._GetE2NetworkObject()
        if E2NetObject is not None:
          retVal = jsonify(E2NetObject.setE2Settings(dictE2Settings))
        else:
          return jsonify("No E2 Network Detected")

        # Now go to each E2 device and "refresh" the E2 object's "E2Settings"
        deviceDict = self.gLeonardo.directory.getDeviceManager().getDevices()
        if deviceDict is not None:
          for deviceRec in deviceDict:  # Find E2 device objects
            if deviceDict[deviceRec]['deviceTypeName'].find(deviceConstants.deviceE2ExecutionText) == 0:
              E2DeviceObject = self.gLeonardo.directory.getDeviceManager().getDeviceObjectByName(deviceDict[deviceRec]['name'])
              E2DeviceObject.InitE2DeviceSettings()  # To get device to update latest E2 settings
          return retVal
        else :
          return None
      except Exception, e:
        return None
