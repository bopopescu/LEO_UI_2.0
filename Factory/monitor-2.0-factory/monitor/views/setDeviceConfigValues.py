from flask_restful import Resource, request
from flask import session, jsonify

import leoObject

class setDeviceConfigValues(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "setDeviceConfigValues LEO Mem=", self.gLeonardo

#      print "ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      deviceName = jsonDict['params'][0]
      configSettings = jsonDict['params'][1]
#      print "Device Name->", deviceName, " Config Settings->", configSettings

      try:
          return jsonify( self.gLeonardo.directory.getDeviceObject(deviceName).setConfigValues(configSettings) )
      except:
          return None


