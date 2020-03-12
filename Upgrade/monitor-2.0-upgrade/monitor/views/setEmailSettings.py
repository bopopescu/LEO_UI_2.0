from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class setEmailSettings(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):

      jsonDict = request.json

      dictNewSettings = jsonDict['params']
      emailSettings = dictNewSettings['emailSettings']
      if "version" not in emailSettings:
        emailSettings['version'] = 2
      

#      try:
      return self.gLeonardo.directory.getSystemObject().setEmailSettings( emailSettings, emailSettings['version'] )
#      except Exception, e:
#        print 'setEmailSettings ERROR:{0}, {1}'.format( e, Exception )
#        return None
