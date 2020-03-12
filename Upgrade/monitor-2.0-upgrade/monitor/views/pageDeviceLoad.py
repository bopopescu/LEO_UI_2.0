from flask_restful import Resource
from flask import Response, request, current_app as app

import urllib
import os

import leoObject

######
# This is a special page. bascially it provides an interface from the .load (jquery) call so that the pageDevices.html can dynamically load content through a specific
# html file (in addition to the "standard" pageDevices.html file.
######
class pageDeviceLoad(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      # Locate the specific device type html file
      deviceTypeName = request.query_string

      doThis = 0
      if doThis > 0 :
        # Read the file contents and send as response.
        strFilePath = "templates/local/devices/{0}/__{0}__.html".format( deviceTypeName  )
#        print "strFilePath(1) = ", strFilePath
        htmlData = urllib.urlopen(strFilePath).read()
#        print "htmlData = ", htmlData

      strDeviceTypeName = urllib.unquote( deviceTypeName )
      strFilePath = "templates/local/devices/{0}/__{0}__.html".format( strDeviceTypeName  )
#      print "strFilePath(2) = ", strFilePath
      strFullFilePath = os.path.join( app.root_path, strFilePath )
      htmlData = urllib.urlopen(strFilePath).read()
#      print "htmlData = ", htmlData

      # return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, deviceNameList=deviceNameList, deviceImagesRoot=deviceImagesRoot, mimetype='text/html' ) )
      return Response( htmlData, mimetype='text/html' )
