from flask_restful import Resource
from flask import session, jsonify

import leoObject

class deleteAllAuditTrailEntries(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):

        try:
          return jsonify( self.gLeonardo.directory.getSystemObject().deleteAllAuditTrailEntries() )
        except Exception, e:
          return 'Error Deleting Audit Trail Entries: {0}'.format(str(e))

