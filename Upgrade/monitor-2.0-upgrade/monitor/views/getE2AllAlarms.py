from flask_restful import Resource
from flask import session, jsonify, request

import leoObject
import deviceConstants

class getE2AllAlarms(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def _GetE2DeviceObject(self, LeoE2ControllerName ) :
      deviceDict = self.gLeonardo.directory.getDeviceManager().getDevices()
      if deviceDict != None :
        # Since orderedDict, netrec will only be key into NetworkDict.
        for devrec in deviceDict :
          if deviceDict[devrec]['deviceTypeName'].find( deviceConstants.deviceE2ExecutionText ) == 0 :
            devName = deviceDict[devrec]['name']
            if devName == LeoE2ControllerName :
              return self.gLeonardo.directory.getDeviceManager().getDeviceObjectByName( deviceDict[devrec]['name'])
        return None

    def post(self):
#        print "getE2AllAlarms LEO Mem=", self.gLeonardo
        jsonDict = request.json
        LeoE2ControllerName = jsonDict['LeoE2Name']
        E2DevObject = self._GetE2DeviceObject( LeoE2ControllerName )
        if E2DevObject != None :
          return jsonify( E2DevObject.getE2AllAlarms() )
        else :
          return jsonify( "Invalid Name - No E2 Device Found" )
