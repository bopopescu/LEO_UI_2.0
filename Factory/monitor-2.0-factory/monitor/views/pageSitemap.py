from flask_restful import Resource
from flask import render_template, Response, session, current_app as app
import LeoFlaskUtils
import leoObject
import os

class pageSitemap(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def get(self):
#        print "**** HIT sitemap.PY ****, Session = ", session

      ctx = LeoFlaskUtils.prepareContext("pageSitemap")
      template = 'pageSitemap.html'
      session['localhost'] = ctx['localhost']

#        print "Client Type: ", ctx['clienttype'], "template: ", template
#        print "ctx: ", ctx
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
