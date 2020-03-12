from flask_restful import Resource
from flask import jsonify, request

import leoObject

import logsystem
log = logsystem.getLogger()

class getDeviceAlarms(Resource):
  def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

  def post(self):
    try:
      jsonDict = request.json
      if jsonDict is None:
        jsonDict = request.form['params']

      dictSettings = jsonDict['params'][0]
#      print "dictSettings->", dictSettings
      deviceKey = dictSettings['deviceName']
      strAlarmType = dictSettings['AlarmType']
      return jsonify( self.gLeonardo.directory.getDeviceObject(deviceKey).getDeviceAlarms( strAlarmType ) )
    except Exception, e:
      log.debug("Error in getDeviceAlarms " + str(e))
      return ""
