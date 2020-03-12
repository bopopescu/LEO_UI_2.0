from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageAuditTrail(Resource):
    def get(self):
      ctx = LeoFlaskUtils.prepareContext("pageAuditTrail")

      template = 'pageAuditTrail.html'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
