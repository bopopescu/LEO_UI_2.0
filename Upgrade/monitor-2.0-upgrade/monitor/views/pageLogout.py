from flask import render_template, Response, session
from flask_restful import Resource
import LeoFlaskUtils
import leoObject

class pageLogout(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def get(self):

        ctx = LeoFlaskUtils.prepareContext("pageLogout")

        LeoFlaskUtils.endSession()

        ctx['siteStatus'] = dict( self.gLeonardo.directory.getSystemObject().getSiteInfo().items() )

        session['localhost'] = ctx['localhost']
        template = 'pageLogout.html'
        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )


