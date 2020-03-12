from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

import logsystem
log = logsystem.getLogger()

class setScreenBrightness(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
        jsonDict = request.json
        paramsList = jsonDict['params']
        paramsDict = paramsList[0]
        percent = paramsDict['brightPct']
#        print "setScreenBrightness=", percent, " LEO Mem=", self.gLeonardo

        try:
          return jsonify( self.gLeonardo.directory.getSystemObject().setScreenBrightness(percent) )
        except:
          return None

