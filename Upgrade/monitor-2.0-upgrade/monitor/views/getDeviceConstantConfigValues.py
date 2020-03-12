from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getDeviceConstantConfigValues(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getDeviceConfigValues LEO Mem=", self.gLeonardo
#      print "JSON= ", request.json
      jsonDict = request.json
      deviceKey = jsonDict['params']

      try:
        return jsonify( self.gLeonardo.directory.getDeviceObject(deviceKey).getConstantConfigValues() )
      except:
        return None
