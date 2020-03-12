from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class setNetworks(Resource):

    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "setNetworks LEO Mem=", self.gLeonardo

#      print "ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      dictNewSettings = jsonDict['params'][0]
#      print "dictNewSettings->", dictNewSettings

      return jsonify( self.gLeonardo.directory.getNetworkManager().setNetworks(dictNewSettings) )
