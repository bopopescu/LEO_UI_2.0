from flask_restful import Resource
from flask import session, jsonify, request
import version
import os

import leoObject

# This class get the software modules in the system (e.g. pip and apt) and maybe in the future other areas of the system so that
# we be sure that LEO devices are consistent. This web service call does take quite a while to return.
class getSWMVersion(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getSWMVersion", self.gLeonardo

        sysVersion = {}

        # Call must pass in: "PIP" (installed python modules). "APT" Installed Linux packages. "LEOSW" installed LEOSW file listing.
        jsonDict = request.json
        paramsList = jsonDict['params']
        paramsDict = paramsList[0]
        strSelect = paramsDict['SWM']
#        print "getSWMVersion->", strSelect

        sysVersion['swm'] = self.gLeonardo.directory.getSystemObject().getSoftwareModulesVersion( strSelect )
        # print "Software Modules Version-->", sysVersion['swm']

        return jsonify( sysVersion )


