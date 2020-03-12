from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class setDevices(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "setDevices LEO Mem=", self.gLeonardo

#      print "ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      dictNewSettings = jsonDict['params'][0]
#      print "newSettingsDict->", dictNewSettings

      return jsonify( self.gLeonardo.directory.getDeviceManager().setDevices(dictNewSettings) )

