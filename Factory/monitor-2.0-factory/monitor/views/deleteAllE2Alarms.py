from flask_restful import Resource
from flask import session, jsonify

import leoObject

class deleteAllE2Alarms(Resource):
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
        # print "deleteAllE2Alarms LEO Mem=", self.gLeonardo
        context = {
                  }

        E2NetObject = self._GetE2NetworkObject()
        if E2NetObject != None :
          return jsonify( E2NetObject.deleteAllE2Alarms() )
        else :
          return None
