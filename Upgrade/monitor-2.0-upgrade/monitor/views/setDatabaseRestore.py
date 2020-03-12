from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class setDatabaseRestore(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "setDatabaseRestore LEO Mem=", self.gLeonardo
#        print "ID = ", request.json['id'], "REQ->", request.json

        jsonDict = request.json

        dictNewSettings = jsonDict['params'][0]
#        print "newSettingsDict->", dictNewSettings

        try:
          return self.gLeonardo.directory.getSystemObject().setDatabaseRestore(database, directory)
        except:
          return None

