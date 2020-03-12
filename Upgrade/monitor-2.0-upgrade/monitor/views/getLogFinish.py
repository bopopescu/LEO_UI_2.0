from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getLogFinish(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getLogFinish JSON= ", request.json
      jsonDict = request.json
      id = jsonDict['params'][0]

      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().getLogFinish(id) )
      except:
        return None
