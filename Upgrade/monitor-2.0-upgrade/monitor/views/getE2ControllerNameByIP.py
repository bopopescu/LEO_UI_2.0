from flask_restful import Resource
from flask import session, jsonify, request
import httplib
import json

class getE2ControllerNameByIP(Resource):

    def post(self):
        retE2Name = ""
        jsonDict = request.json
        E2IPAddress = jsonDict['E2IPAddress']
        # print "getE2ControllerNameByIP. IP=", E2IPAddress

        # Yes, this is a hack. Let's quickly send message to the IP address and see if we can get the controller name.
        try:
            E2Connection = httplib.HTTPConnection(E2IPAddress, timeout=2)
        except Exception, e:
            retE2Name = "--NETWORK ERROR--"
            E2Connection = None

        if E2Connection != None:
            jsonRequest = json.dumps( {'id': 'E2IP Network', 'method': 'E2.GetThisControllerName', 'params': '[[]]'} )
            E2Connection.request('POST', '/JSON-RPC', jsonRequest, headers={"Content-type": "application/json"})
            jsonResponse = E2Connection.getresponse()
            jsonData = jsonResponse.read()
            jsonReturn = json.loads(jsonData)

            if len(jsonReturn) > 0:
                retE2Name = jsonReturn['result']

        return jsonify( retE2Name )
