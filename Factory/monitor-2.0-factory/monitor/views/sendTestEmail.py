from flask_restful import Resource
from flask import session, jsonify, request

import leoObject
import networkConstants

class sendTestEmail(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "sendTestEmail LEO Mem=", self.gLeonardo
      jsonDict = request.json
      paramsDict = jsonDict['params']
  
      if len( paramsDict['toaddress'] ) > 0 :
        self.gLeonardo.directory.getAlarmManager().setTestEmailInfo( paramsDict['emailtype'], paramsDict['toaddress'], paramsDict['emailservername'] )
        return jsonify( "Wait a couple of minutes and see the auditTrail for status" )
      else :
        return jsonify( "No email address provided (toaddress parameter)" )
