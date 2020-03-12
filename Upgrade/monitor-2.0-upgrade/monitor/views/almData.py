from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

# This class is to handle "real-time" alarm related JSON calls from Leo - not necessarily related to web "pages" or web page transitions.
class almData(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "POST usrData ", self.gLeonardo
#      print "ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      if jsonDict['id'].find("snoozeAlarmChime") == 0  :
#        print "Snooze the alarm"
        timeRemainingSecs = self.gLeonardo.directory.getAlarmManager().snoozeAlarm()
        result = {}
        result['success'] = True
        result['timeRemainingSecs'] = timeRemainingSecs
        return jsonify( result )

      else :
#       print "Undefined Message ", request.method
        return None

