from flask_restful import Resource
from flask import session, jsonify

import leoObject

class getNetworkTypes(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
        return jsonify( self.gLeonardo.directory.getNetworkManager().getNetworkTypes() )

