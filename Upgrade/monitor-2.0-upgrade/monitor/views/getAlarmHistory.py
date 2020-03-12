from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getAlarmHistory(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getAlarmHistory LEO Mem=", self.gLeonardo
        context = {
                  }

        try:
          return jsonify( self.gLeonardo.directory.getAlarmManager().getLeoAlarmHistory() )
        except:
          return None
