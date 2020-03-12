from flask import render_template, Response
from flask_restful import Resource
import leoObject
import deviceConstants
import LeoFlaskUtils


class pageService(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      dataDevices = dict( self.gLeonardo.directory.getDeviceManager().getDevices() )

      activeDeviceTypes = []
      for device in dataDevices:
        # If we haven't added this device type name to the list, add it
        devTypeName = dataDevices[device]['deviceTypeName']
        if  devTypeName not in activeDeviceTypes :
          activeDeviceTypes.append( devTypeName )

      ctx = LeoFlaskUtils.prepareContext("pageService")
      template = 'pageService.html'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, activeDeviceTypes=activeDeviceTypes, mimetype='text/html' ) )
