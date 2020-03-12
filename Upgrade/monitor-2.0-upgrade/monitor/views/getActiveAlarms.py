from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getActiveAlarms(Resource):
  def __init__(self):
    self.gLeonardo = leoObject.getLeoObject()

  def post(self):
    try:
      return jsonify( self.gLeonardo.directory.getAlarmManager().getLeoActiveAlarms() )
    except:
      return None
