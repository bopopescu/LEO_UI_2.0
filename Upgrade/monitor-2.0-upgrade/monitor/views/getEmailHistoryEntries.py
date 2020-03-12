from flask_restful import Resource
from flask import jsonify, request

import leoObject

class getEmailHistoryEntries(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      # try:
        jsonDict = request.json
        dictSettings = jsonDict['params'][0]
        #    print "dictSettings->", dictSettings
        transType = dictSettings['transType']
        if "EBrecId" in dictSettings:
          EBrecId = dictSettings['EBrecId']
        else:
          EBrecId = -1
        if "ETrecId" in dictSettings:
          ETrecId = dictSettings['ETrecId']
        else:
          ETrecId = -1

      # print "transType:{0}, ETrecId{1}, EBrecId:{2}".format( transType, ETrecId, EBrecId )
  
        retValue = self.gLeonardo.directory.getAlarmManager().getEmailHistoryEntries( transType, ETrecId, EBrecId )
        return jsonify( retValue )

    # except Exception, e:
        # strError = 'getEmailHistoryEntries exception={0} {1}'.format(e, str(e) )
        # return jsonify(strError)
