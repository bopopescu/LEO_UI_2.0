from flask_restful import Resource
from flask import jsonify, request

import leoObject
import authentication

class usrData(Resource):
    def __init__(self):
      self.gLeonardo = leoObject.getLeoObject()

    def post(self):
#      print "POST usrData ", self.gLeonardo
      print "ID = ", request.json['id'], "REQ->", request.json
      jsonDict = request.json

      if jsonDict['id'].find("addUser") == 0  :
        userName = jsonDict['params'][0]
        fullName = jsonDict['params'][1]
        roles = jsonDict['params'][2]
        password = jsonDict['params'][3]

        # Returns the updated userlist.
        return jsonify( authentication.auth_add_user( userName, fullName, roles, password ) )

      elif jsonDict['id'].find( "setUserInfo" ) == 0  :
        userName = jsonDict['params'][0]
        fullName = jsonDict['params'][1]
        roles = jsonDict['params'][2]

        retVal = authentication.auth_set_user_info( userName, fullName, roles )
#        print "setUserInfo RETURN ", retVal
        return jsonify( retVal )

      elif jsonDict['id'].find( "setUserPassword" ) == 0 :
        userName = jsonDict['params'][0]
        password = jsonDict['params'][1]

        return jsonify( authentication.auth_set_user_password( userName, password ) )

      elif jsonDict['id'].find( "deleteUsers" ) == 0  :
        delUserList = jsonDict['params'][0]
        return jsonify( authentication.auth_delete_users( delUserList ) )

      else :
#        print "Undefined Message ", request.method
        return None

