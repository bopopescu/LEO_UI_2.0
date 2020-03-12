from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageE2status(Resource):
    def get(self):
        ctx = LeoFlaskUtils.prepareContext("pageE2status")

        template = 'pageE2status.html'
        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
