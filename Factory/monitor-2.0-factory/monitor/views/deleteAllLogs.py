from flask_restful import Resource
from flask import session, jsonify

import leoObject

class deleteAllLogs(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "deleteAllLogs LEO Mem=", self.gLeonardo
        context = {
                  }
        try:
          return jsonify( self.gLeonardo.directory.getLoggingManager().deleteAllLogs() )
        except:
          return None

