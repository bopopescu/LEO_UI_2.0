from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getSystemSettings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getSystemSettings LEO Mem=", self.gLeonardo
        context = {
                  }

        try:
          return jsonify( self.gLeonardo.directory.getSystemObject().getSystemSettings() )
        except:
          return None
