from flask_restful import Resource
from flask import render_template, Response, session, current_app as app
import LeoFlaskUtils
import leoObject
import os
import subprocess
import logsystem
log = logsystem.getLogger()

class pageIndex(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def get(self):
      blDirNone = False
      if self.gLeonardo.directory is None:
        blDirNone = True

      #debugBuf = "**** HIT INDEX.PY ****, Session:{0}, Directory:{1}, Dir Is None:".format( session, self.gLeonardo.directory, blDirNone )
      #print debugBuf

      ctx = LeoFlaskUtils.prepareContext("pageIndex")
      ctx['siteStatus'] = dict( self.gLeonardo.directory.getSystemObject().getSiteInfo().items() )

      session['localhost'] = ctx['localhost']
      out = subprocess.Popen("postqueue -p  | grep -v empty | grep -c '^[0-9A-Z]'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
      ctx["emailsInQueue"] = out

      # Here we handle the customer logo image. If there is an image in the uimg folder, then this is the customer logo; otherwise use the default image.
      usrImgCustLogo = 'static/uimg/custlogo.png'
      if os.path.exists( usrImgCustLogo ) == False:
        usrImgCustLogo = 'static/local/img/custlogo.png'

      template = 'pageIndex.html'
      return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html', logoImage=usrImgCustLogo ) )
