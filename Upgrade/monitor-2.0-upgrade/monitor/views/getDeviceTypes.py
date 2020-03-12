from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getDeviceTypes(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getDeviceTypes LEO Mem=", self.gLeonardo

        return jsonify( self.gLeonardo.directory.getDeviceManager().getDeviceTypes() )
