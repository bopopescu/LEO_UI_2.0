from flask_restful import Resource
from flask import session, jsonify

import leoObject

class deleteAllAlarms(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "deleteAllAlarms LEO Mem=", self.gLeonardo

#         try:
        return jsonify( self.gLeonardo.directory.getAlarmManager().deleteAllAlarms() )
#         except:
#          return None
