from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageEmailHistory(Resource):
    def get(self):
      ctx = LeoFlaskUtils.prepareContext("pageEmailHistory")

      template = 'pageEmailHistory.html'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
