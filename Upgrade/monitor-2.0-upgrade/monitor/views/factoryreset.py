from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

# This function provides a JSON service to remotely completely reset the settings in LEO to their factory default
# Factory Reset Types: 0 = Do Nothing, 1 = Reset ALL & Set IP Information to blank, 2 = Reset All EXCEPT IP Information
class factoryreset(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "factoryreset LEO Mem=", self.gLeonardo
#        print "JSON= ", request.json
        jsonDict = request.json

        factoryResetType = jsonDict['resetType']
#        print "factoryResetType->", factoryResetType

        try:
#            print "gLeonardo = ", self.gLeonardo
            return jsonify(self.gLeonardo.directory.getSystemObject().factoryReset(factoryResetType) )
        except:
            return None
