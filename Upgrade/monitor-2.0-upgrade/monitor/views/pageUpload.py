from flask_restful import Resource
from flask import render_template, Response, session, current_app as app
import LeoFlaskUtils
import os

class pageUpload(Resource):
    def get(self):

        ctx = LeoFlaskUtils.prepareContext("pageUpload")
        template = 'pageUpload.html'

#        print "session = ", session

        if 'can_access_files' in session and session['can_access_files'] == True:
            # Get list of DEVICE image files - need full path.
            urlImagePath = '/static/uimg/devices'
            imgFilelist = os.listdir( app.root_path + urlImagePath )
#            print "urlImage", urlImagePath
#            print "UPLOAD - Files = ", imgFilelist
            urlCustImagePath = '/static/local/img'
            imgCustFilelist = os.listdir( app.root_path + urlCustImagePath )
            return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, imageFiles=imgFilelist, imagePath=urlImagePath,  imageCustFiles=imgCustFilelist, imageCustPath=urlCustImagePath, mimetype='text/html' ) )
        else :
            # If we get here, we have a problem. Refresh the browser by going to the logout html - where we do a reload page.
            return Response(render_template(ctx['clienttype'] + '/' + 'pageLogout.html', mimetype='text/html'  ) )




