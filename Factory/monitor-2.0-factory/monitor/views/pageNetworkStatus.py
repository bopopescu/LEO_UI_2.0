from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageNetworkStatus(Resource):
    def get(self):
        ctx = LeoFlaskUtils.prepareContext("pageNetworkStatus")

        template = 'pageNetworkStatus.html'
        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
