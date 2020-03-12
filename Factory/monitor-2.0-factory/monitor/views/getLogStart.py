from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getLogStart(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getLogStart. JSON= ", request.json
      jsonDict = request.json
      dataform = jsonDict['params'][0]
      values = jsonDict['params'][1]
      startdate = jsonDict['params'][2]
      enddate = jsonDict['params'][3]
      dictUnitSetting = jsonDict['params'][4]
      fileNameFormat = jsonDict['params'][5]
      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().getLogStart(dataform, values, startdate, enddate, dictUnitSetting, fileNameFormat ) )
      except:
        return None

