from flask_restful import Resource, request
from flask import session, jsonify

import leoObject

class setSystemSettings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "setSystemSettings LEO Mem=", self.gLeonardo

        jsonDict = request.json
#        print "ID = ", request.json['id'], "REQ->", request.json, "Params->", jsonDict['params']

        dictSettings = jsonDict['params'][0]
#        print "dictSettings->", dictSettings

        try:
          return jsonify( self.gLeonardo.directory.getSystemObject().setSystemSettings(dictSettings) )
        except:
          return None
