from flask_restful import Resource
from flask import session, jsonify, request

import leoObject

import logsystem
log = logsystem.getLogger()

class getMultiDeviceInfo(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def post(self):
      # log.debug( "getMultiDeviceInfo . JSON= ", request.json )
      # Handle either postman (form) or JSON call.
      if request.is_json is True :
        # Properties are in the following list: --> [ { 'device':<deviceName>,'valueKey1':<valueKey1> } ,{ 'device':<deviceName>,'valueKey2':<valueKey2> } ]
        jsonDict = request.json
        multiDeviceInfoList = jsonDict['params']
      else :
        multiDeviceInfoList = []
        for entry in request.form:
            multiDeviceInfoList.append( eval(request.form[entry]))

      try:
        returnInfo = {}
        tempValuesDict = {}

        # Loop through each of the dicts.
        for multiDeviceEntry in multiDeviceInfoList:
          deviceName = multiDeviceEntry['device']

          deviceObj = self.gLeonardo.directory.getDeviceObject(deviceName)
          # If the device is found
          if deviceObj is not None and deviceName is not None :
            # If the device's descriptors and values are not yet stored
            if deviceName not in returnInfo:
              # Our goal is to return a dict in the following format:
              # returnInfo = { <deviceName1>:{ "valueDesc":<valueDescription>, "values":[<value1>,<value2>],...] },
              #                <deviceName2>:{ "valueDesc":<valueDescription>, "values":[<value1>,<value2>],...] },

              # If this device is not yet in the return dict, add it.
              returnInfo[deviceName] = {'deviceInfo': deviceObj.getDeviceInformation(), 'values': {}, 'valuesDescr': {}, 'dynamicImages': {} }
              tempValuesDict[deviceName] = deviceObj.getValues()

            # Loop in case there are multiple values
            for keyName in multiDeviceEntry['values']:
              # Now, let's add the value.
              # if the return dict does not yet contain the value we are looking for, add it.
              if keyName not in returnInfo[deviceName]['values'].keys():
                # Add the value
                if keyName not in tempValuesDict[deviceName].keys() :
                  keyNameValue = 'ERROR'
                else:
                  keyNameValue = tempValuesDict[deviceName][keyName]
                  if keyNameValue is None:
                    keyNameValue = '--'
                returnInfo[deviceName]['values'][keyName] = keyNameValue
                # Add the descriptor
                returnInfo[deviceName]['valuesDescr'][keyName] = deviceObj.getValueDescriptionByKey(keyName)
                returnInfo[deviceName]['dynamicImages'][keyName] = deviceObj.getDynamicImagesByKey(keyName)

        return jsonify( returnInfo )

      except Exception, e:
        log.exception("*** getMultiDeviceInfo Error: " + str(e))
        return {}

