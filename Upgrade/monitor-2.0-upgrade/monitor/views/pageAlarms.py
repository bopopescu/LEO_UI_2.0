from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageAlarms(Resource):
    def get(self):
        ctx = LeoFlaskUtils.prepareContext("pageAlarms")

        template = 'pageAlarms.html'
        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
