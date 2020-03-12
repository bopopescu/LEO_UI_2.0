from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getDatabaseBackup(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getDatabaseBackup LEO Mem=", self.gLeonardo
#        print "ID = ", request.json['id'], "REQ->", request.json

        jsonDict = request.json

        dictNewSettings = jsonDict['params'][0]
#        print "dictNewSettings->", dictNewSettings

        try:
          return jsonify( self.directory.getSystemObject().getDatabaseBackup(database, directory) )
        except:
          return None
