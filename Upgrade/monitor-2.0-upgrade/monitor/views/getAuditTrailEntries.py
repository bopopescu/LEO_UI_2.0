from flask_restful import Resource
from flask import session, jsonify

import leoObject
import networkConstants

class getAuditTrailEntries(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      try:
        x = jsonify( self.gLeonardo.directory.getSystemObject().getAuditTrailEntries() )
        return x
      except:
        return None
