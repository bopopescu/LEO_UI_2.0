from flask_restful import Resource, request
from flask import session, jsonify

import leoObject

class setLoggedValuesForDevice(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "setLoggedValuesForDevice ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      deviceName = jsonDict['params'][0]
      loggedValues = jsonDict['params'][1]
      setValue = jsonDict['params'][2]
#      print "Device Name->", deviceName, " Config Settings->", loggedValues

      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().setLoggedValuesForDevice(deviceName, loggedValues, setValue) )
      except:
        return None
