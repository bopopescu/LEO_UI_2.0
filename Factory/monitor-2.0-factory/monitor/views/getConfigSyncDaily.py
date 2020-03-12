from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getConfigSyncDaily(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getDeviceConfigValues LEO Mem=", self.gLeonardo
#      print "JSON= ", request.json
      jsonDict = request.json
      deviceKey = jsonDict['params']

      try:
        return jsonify( self.gLeonardo.directory.getDeviceObject(deviceKey).getSyncDaily() )
      except:
        return None
