from flask_restful import Resource, request
from flask import jsonify

import leoObject

class setEnunciatedAlarmFilters(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      jsonDict = request.json
      dictEnunciatedAlarmFilters = jsonDict['params'][0] # EnunciatedAlarmsActive settings
      EnunciatedAlarmsActive = jsonDict['params'][1] # Enunciatedalarmfilters
      reInit = False
      if len(jsonDict['params']) > 2 :
        if jsonDict['params'][2] > 0 :
          reInit = True

      try:
        self.gLeonardo.directory.getAlarmManager().setEnunciatedAlarmFilters( dictEnunciatedAlarmFilters, EnunciatedAlarmsActive, reInit )

      except Exception, e:
        print "*** Error in setEnunciatedAlarmFilters *** " + str(e)
        return None
