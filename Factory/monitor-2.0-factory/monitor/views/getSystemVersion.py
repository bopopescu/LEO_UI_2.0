from flask_restful import Resource
from flask import session, jsonify
import version
import os

import leoObject

class getSystemVersion(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#        print "getSystemVersion", self.gLeonardo
        result = {}

        # First, get the Leo python version.
        # print "Version: ", version.versionInfo
        result['swVersion'] = version.versionInfo
        # Next, get the OS version.
        result['osInfo'] = self.gLeonardo.directory.getSystemObject().getOsInfo()

        return jsonify( result )


