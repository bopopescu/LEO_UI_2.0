from flask_restful import Resource
from flask import session, jsonify, request
import leoObject
import logsystem
log = logsystem.getLogger()


class getDeviceValueDescriptions(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getDeviceValueDescriptions LEO Mem=", self.gLeonardo
#        print "JSON= ", request.json
        jsonDict = request.json
        deviceKey = jsonDict['params']
#        print "getDeviceValueDescriptions - Device Key = ", deviceKey

        try:
          return jsonify( self.gLeonardo.directory.getDeviceObject(deviceKey).getValueDescriptions() )
        except Exception, e:
          strEx = '***** Error in getDeviceValueDescriptions ***** {0}'.format(str(e))
          log.exception(strEx)
          return None

