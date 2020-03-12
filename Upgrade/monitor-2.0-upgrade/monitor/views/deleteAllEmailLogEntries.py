from flask_restful import Resource
from flask import session, jsonify

import leoObject

class deleteAllEmailLogEntries(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):

        try:
          self.gLeonardo.directory.getAlarmManager().setEmailDatabaseToFactorySettings()
          return "All Email Log Entries Have Been Deleted"

        except Exception, e:
          return 'Error Deleting Email Log Entries: {0}'.format(str(e))
