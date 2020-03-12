from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class getEmailSettings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
        try:
          jsonDict = request.json
          version = jsonDict['version']
  
          return jsonify( self.gLeonardo.directory.getSystemObject().getEmailSettings( version ) )
        except:
          return None

