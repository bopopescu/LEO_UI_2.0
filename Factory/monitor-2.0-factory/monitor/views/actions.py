from flask_restful import Resource
from flask import session, jsonify, request

import leoObject
import systemInterface

class actions(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      jsonDict = request.json
      dictNewSettings = jsonDict['params'][0]

      if dictNewSettings['action'] == "PlayAlarmChime" :
        strSoundFile = "/opt/monitor/system/AlarmChime.wav"
        volumeLevel = dictNewSettings['volume']
        systemInterface.soundPlayFile(strSoundFile, volumeLevel )
        
      return jsonify( "Requested Action Completed" )

