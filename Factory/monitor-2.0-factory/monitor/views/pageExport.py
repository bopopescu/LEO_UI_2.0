from flask_restful import Resource
from flask import render_template, Response
import json
import LeoFlaskUtils

import leoObject

class pageExport(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      ctx = LeoFlaskUtils.prepareContext("pageExport")

      # Changed from ordered dict to dict and then to non-unicode representation.
      dataAllLoggedValues =  dict( self.gLeonardo.directory.getLoggingManager().getAllLoggedValues() )
      if len(dataAllLoggedValues) > 0 :
        deviceName = list(dataAllLoggedValues)[0] # Get the name of the first device
      else :
        deviceName = ""

      template = 'pageExport.html'

      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, deviceName=deviceName, allLoggedValues=dataAllLoggedValues, mimetype='text/html' ) )
