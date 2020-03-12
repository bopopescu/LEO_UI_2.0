from flask_restful import Resource
from flask import render_template, Response
import deviceConstants

import leoObject
import LeoFlaskUtils

class pageE2alarms(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      ctx = LeoFlaskUtils.prepareContext("pageE2alarms")
      template = 'pageE2alarms.html'

      # Get the E2 device list.
      deviceDict = dict( self.gLeonardo.directory.getDeviceManager().getDevices() )
      E2deviceNameList = []
      E2deviceDictList = []
      E2dev = {}
      for devName in deviceDict :
        if deviceDict[devName]['deviceTypeName'].find( deviceConstants.deviceE2ExecutionText ) == 0 :
          E2dev['devName'] = devName
          E2dev['devType'] = deviceDict[devName]['deviceTypeName']
          E2deviceDictList.append( E2dev )
          E2deviceNameList.append( devName )

      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, E2deviceNameList=E2deviceNameList, E2deviceDictList=E2deviceDictList, mimetype='text/html' ) )
      