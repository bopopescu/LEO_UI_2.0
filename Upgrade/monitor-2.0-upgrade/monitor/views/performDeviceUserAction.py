from flask_restful import Resource, request
from flask import session, jsonify

import leoObject

class performDeviceUserAction(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "performDeviceUserAction LEO Mem=", self.gLeonardo

      jsonDict = request.json

      deviceName = jsonDict['params'][0]
      useerAction = jsonDict['params'][1]
#      print "Device Name->", deviceName, " User Action ->", useerAction

      try:
        return jsonify( self.gLeonardo.directory.getDeviceObject(deviceName).performUserAction(useerAction) )
      except:
        return None
