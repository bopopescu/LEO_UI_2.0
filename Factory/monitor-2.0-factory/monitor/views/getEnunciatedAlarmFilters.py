from flask_restful import Resource
from flask import session, jsonify
import networkConstants

import leoObject

class getEnunciatedAlarmFilters(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      try:
        return jsonify( self.gLeonardo.directory.getAlarmManager().getEnunciatedAlarmFilters() )
      except Exception, e:
        print "*** Error in getEnunciatedAlarmFilters *** " + str(e)
        return None

