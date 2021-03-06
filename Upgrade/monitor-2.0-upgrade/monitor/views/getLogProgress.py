from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getLogProgress(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      jsonDict = request.json
      id = jsonDict['params'][0]

      try:
        return jsonify( self.gLeonardo.directory.getLoggingManager().getLogProgress(id) )
      except:
        return None
