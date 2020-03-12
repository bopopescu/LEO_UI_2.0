from flask_restful import Resource
from flask import render_template, Response
import LeoFlaskUtils

class pageTestStatus(Resource):
    def get(self):
        ctx = LeoFlaskUtils.prepareContext("pageTestStatus")

        template = 'pageTestStatus.html'
        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html' ) )
