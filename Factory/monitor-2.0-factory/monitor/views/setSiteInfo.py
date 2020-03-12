from flask_restful import Resource, request
from flask import session, jsonify

import leoObject

class setSiteInfo(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "setSiteInfo LEO Mem=", self.gLeonardo

      jsonDict = request.json
#      print "ID = ", request.json['id'], "REQ->", request.json, "Params->", jsonDict['params']

      dictSiteInfo = jsonDict['params'][0]
#      print "dictSiteInfo->", dictSiteInfo

      return jsonify( self.gLeonardo.directory.getSystemObject().setSiteInfo(dictSiteInfo) )
