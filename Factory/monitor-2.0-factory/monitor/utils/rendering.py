from flask import render_template, Response, request


def render_html(template, context):
    if 'localhost' in request.host:
        clienttype = 'local'
    else:
        clienttype = 'remote'

    return Response(render_template(clienttype+'/'+template, ctx=context), mimetype='text/html')
