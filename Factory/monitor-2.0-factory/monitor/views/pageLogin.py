from flask_restful import Resource
from flask import render_template, Response, session
import LeoFlaskUtils

class pageLogin(Resource):
    def get(self):
#      print "B4 session", session
      LeoFlaskUtils.startSession()
#      print "After session", session
      ctx = LeoFlaskUtils.prepareContext("pageLogin")

      template = 'pageLogin.html'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
