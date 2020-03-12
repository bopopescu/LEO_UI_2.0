from flask_restful import Resource
from flask import session, jsonify, request
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], 'monitor'))
import leoObject

class setSiteCurrentTime(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      jsonDict = request.json

      dictTimeInfo = jsonDict['params'][0]
      # Update the time.
      result = jsonify( self.gLeonardo.directory.getSystemObject().setCurrentTime(dictTimeInfo) )
      # We need to reset the watchdog timer because if we changed the timezone, it may elapse and cause
      # a browser down reboot when moving time "forward" - e.g. going from PST to EST.
      self.gLeonardo.browserWatchdogTimer.reset()
      # return the result.
      return result
      
