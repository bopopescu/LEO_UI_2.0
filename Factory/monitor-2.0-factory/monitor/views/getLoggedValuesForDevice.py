from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getLoggedValuesForDevice(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getLoggedValuesForDevice. JSON= ", request.json
      jsonDict = request.json
      deviceKey = jsonDict['params']
#      print "deviceKey->", deviceKey

      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().getLoggedValuesForDevice(deviceKey) )
      except:
        return None
