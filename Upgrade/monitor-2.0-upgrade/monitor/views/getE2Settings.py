from flask_restful import Resource
from flask import session, jsonify
import networkConstants

import leoObject

class getE2Settings(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def _GetE2NetworkObject(self) :
      networkDict = self.gLeonardo.directory.getNetworkManager().getNetworks()
      if networkDict != None :
        # Since orderedDict, netrec will only be key into NetworkDict.
        for netrec in networkDict :
          if networkDict[netrec]['typeName'].find( networkConstants.networkE2NetText ) == 0 :
            return self.gLeonardo.directory.getDeviceManager().getNetworkObjectByName( networkDict[netrec]['name'])
        return None

    def post(self):

        try:
          E2NetObject = self._GetE2NetworkObject()
          if E2NetObject != None :
            return jsonify( E2NetObject.getE2Settings() )
          else :
            return jsonify( "No E2 Devices Detected" )
        except Exception, e:
          strError = 'getE2Settings Exception={0}'.format(str(e))
          return jsonify(strError)

