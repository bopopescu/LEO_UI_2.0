from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

import leoObject

class pageDevices(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      ctx = LeoFlaskUtils.prepareContext("pageDevices")

      deviceNameList = []
      deviceDictList = []
      # Get the device list.
      deviceDict = dict( self.gLeonardo.directory.getDeviceManager().getDevices() )
      if len(deviceDict) > 0 :
#        print "deviceDict = ", deviceDict
        dev = {}
        for devName in deviceDict :
          deviceDictList.append( { 'devName':devName, 'devType': deviceDict[devName]['deviceTypeName'] } )
          deviceNameList.append( devName )
        deviceName = deviceNameList[0]
      else :
        deviceName = ""

      template = 'pageDevices.html'
      deviceImagesRoot = 'templates/local/devices'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, deviceNameList=deviceNameList, deviceName=deviceName, deviceDictList=deviceDictList, deviceImagesRoot=deviceImagesRoot, mimetype='text/html' ) )
