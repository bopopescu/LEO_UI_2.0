from flask_restful import Resource
from flask import session, jsonify

import leoObject

# The purpose of this interface is to get ALL devices in the system's associated status. These status are currently PRE-DEFINED.
# This interface will loop through all devices from the device list and provide the latest information for each device so that
# there can be specific information viewed for the entire system.
# The selections are:
#   - "type":"SYSTEM_SUMMARY" - return all devices (name, online/offline, alarm state, network, address, deviceType )
class getSystemDeviceStatus(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      devMgg = self.directory.getDeviceManager()
      sysObj = self.gLeonardo.directory.getSystemObject()
      retval = {}
      retval = dict(sysObj.getSiteInfo().items() + self.gLeonardo.directory.getAlarmManager().getAlarmStatus().items())
      retval["timeInfo"] = sysObj.getCurrentTime()
      retval["alarmChimeSnoozeTimeRemaining"] = int( self.gLeonardo.directory.getAlarmManager().getAlarmChimeSnoozeTimeRemaining() )
      retval["alarmChimeSnoozeEnable"] = self.gLeonardo.directory.getAlarmManager().getAlarmChimeSnoozeEnable()
      retval["strTestEmailMsg"] = self.gLeonardo.directory.getAlarmManager().getTestEmailMsg()
      return jsonify( retval )
