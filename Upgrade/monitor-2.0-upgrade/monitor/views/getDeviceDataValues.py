from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

import logsystem
log = logsystem.getLogger()

class getDeviceDataValues(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getDeviceDataValues Mem=", self.gLeonardo

      try:

        deviceKey = ""
        if request.json is None:
          # Let's see if the form is filled.
          f = request.form
          if len(f) > 0:
            for key in f.keys():
              for value in f.getlist(key):
                deviceKey = value
          else:
            return "No device specified."
        else:  # it is a json dict. Parse...
          jsonDict = request.json
          deviceKey = jsonDict['params']

        if len(deviceKey) > 0:
          device = self.gLeonardo.directory.getDeviceObject(deviceKey)
          self.gLeonardo.directory.getSystemObject().statusWatch(deviceKey)
          return jsonify( device.getDataValues() )
        else:
          return ""

      except Exception, e:
        log.exception("*** getDeviceDataValues Error: " + str(e))
        return None

