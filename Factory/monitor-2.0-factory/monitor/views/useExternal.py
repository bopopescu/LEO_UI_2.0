from flask_restful import Resource, request
from flask import jsonify
from flask import session, current_app as app
import os
import leoObject
import subprocess
import auditTrail
from LeoFlaskUtils import getSessionUsername
import logsystem
log = logsystem.getLogger()

class useExternal(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "deleteAllAlarms LEO Mem=", self.gLeonardo
        result = {}
        jsonDict = request.json

        dictNewSettings = jsonDict['params']
        method = dictNewSettings['method']
        if method == "external":
          log.debug("Inside External")
          try:
            os.system("cp /opt/monitor/asound.conf  /etc/")
            log.debug("After Subprocess")
            result['success'] = True
            strAuditOperation = " Use External Speaker"
            strAudit = '{0} SUCCESS - {1}. System Is Rebooting To Make The Changes.'.format( getSessionUsername( session ), strAuditOperation )
            auditTrail.AuditTrailAddEntry( strAudit )
            os.system('sudo shutdown -r now')
          except Exception, e:
            print "*** Error in useExternal Speaker *** " + str(e)
            log.debug(str(e))
            result["success"] = False
        elif method == "internal":
          try:
            os.system("rm /etc/asound.conf" )
            result['success'] = True
            strAuditOperation = " Use Internal Speaker"
            strAudit = '{0} SUCCESS - {1}. System Is Rebooting To Make The Changes.'.format( getSessionUsername( session ), strAuditOperation )
            auditTrail.AuditTrailAddEntry( strAudit )
            os.system('sudo shutdown -r now')
          except Exception, e:
            print "*** Error in useExternal Speaker *** " + str(e)
            log.debug(str(e))
            result["success"] = False
        return result