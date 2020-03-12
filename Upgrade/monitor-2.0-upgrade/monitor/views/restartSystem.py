from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class restartSystem(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "restartSystem LEO Mem=", self.gLeonardo
        context = {
                  }
        try:
          jsonDict = request.json
          paramsList = jsonDict['params']
          paramsDict = paramsList[0]
          strRestartType = "{0} {1}".format( paramsDict[ 'rebootUser' ], paramsDict['rebootType'] )
          self.gLeonardo.directory.getSystemObject().setScreenBrightness( 100 ) # Turn up the backlight immediately to indicate reset.
          return jsonify( self.gLeonardo.directory.getSystemObject().restartSystem( strRestartType ) )

        except:
#          print "Restart Failed"
          return jsonify( "Restart Failed" )

