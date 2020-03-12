from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getLogCancel(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "getLogCancel. JSON= ", request.json
      jsonDict = request.json
      id = jsonDict['params'][0]

      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().getLogCancel(id) )
      except:
        return None
