from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getAllLoggedValues(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getAllLoggedValues LEO Mem=", self.gLeonardo
        context = {
                  }

        try:
          return jsonify( self.gLeonardo.directory.getLoggingManager().getAllLoggedValues() )
        except:
          return None
