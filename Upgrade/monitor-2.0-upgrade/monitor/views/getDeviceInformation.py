from flask_restful import Resource
from flask import session, jsonify, request

import leoObject
import logsystem
log = logsystem.getLogger()

class getDeviceInformation(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
        # print "getDeviceInformation LEO Mem=", self.gLeonardo
        # print "Request-->", request, "JSON= ", request.json
        deviceKey = ""
        if request.json is None:
            # Let's see if the form is filled.
            f = request.form
            if len(f) > 0 :
              for key in f.keys():
                for value in f.getlist(key):
                  deviceKey = value
            else:
              return "No device specified."
        else: # it is a json dict. Parse...
          jsonDict = request.json
          deviceKey = jsonDict['params']

        try:
          if len( deviceKey ) > 0 :
            return self.gLeonardo.directory.getDeviceObject(deviceKey).getDeviceInformation()
          else:
            return ""

        except Exception, e:
          strEx = '***** Error in getDeviceInformation ***** {0}'.format(str(e))
          log.exception(strEx)
          return strEx

