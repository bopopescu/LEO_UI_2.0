from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

class setEthernetSettings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
        jsonDict = request.json
        settings = jsonDict['params'][0]

        return jsonify( self.gLeonardo.directory.getSystemObject().setEthernetSettings(settings) )

