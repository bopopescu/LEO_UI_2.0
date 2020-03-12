from flask_restful import Resource
from flask import session, jsonify, request
import datetime

import leoObject
import elapsedTimer

import logsystem
log = logsystem.getLogger()

class getSiteStatus(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "self.gLeonardo = ", self.gLeonardo
#        print "leoObject.getLeoObject() = ", leoObject.getLeoObject()
#      strDebug = "self.gLeonardo:{0}, leoObject.getLeoObject:{1}".format( self.gLeonardo, leoObject.getLeoObject() )
#      log.debug( strDebug )

      try:
        # Reset browser watchdog - only when localhost is reqeusting. This is so that if the local browser crashes, the system will reboot.
        # However, we should NOT reset the watchdog timer when the get site status message comes in remotely.
        # watchdog timer is initialized and checked in LeoObject - init and execute
        # print "START GetSiteStatus {0} ".format(datetime.datetime.utcnow())
        if 'localhost' in request.host or '127.0.0.1' in request.host:
          self.gLeonardo.browserWatchdogTimer.reset()

        retval = {}
        # If the directory is initialized and system object is configured properly, call it.
        if hasattr(self.gLeonardo, 'directory') :
          if hasattr(self.gLeonardo.directory, 'getSystemObject') :
            sysObj = self.gLeonardo.directory.getSystemObject()
            # If the alarm manager is initialized.
            if hasattr(self.gLeonardo.directory, 'getSystemObject') and \
               hasattr(self.gLeonardo.directory.getAlarmManager(), 'getAlarmStatus') :
              retval = dict(sysObj.getSiteInfo().items() + self.gLeonardo.directory.getAlarmManager().getAlarmStatus().items())
              retval["timeInfo"] = sysObj.getCurrentTime()
              retval["alarmChimeSnoozeTimeRemaining"] = int( self.gLeonardo.directory.getAlarmManager().getAlarmChimeSnoozeTimeRemaining() )
              retval["alarmChimeSnoozeEnable"] = self.gLeonardo.directory.getAlarmManager().getAlarmChimeSnoozeEnable()
              retval["strTestEmailMsg"] = self.gLeonardo.directory.getAlarmManager().getTestEmailMsg()
      except Exception, e:
        log.exception("*** getSiteStatus Exception: " + str(e))
        retval = {}

      return jsonify( retval )

