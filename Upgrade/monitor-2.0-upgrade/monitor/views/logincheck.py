from flask_restful import Resource
from flask import session, jsonify, request
import authentication

class logincheck(Resource):
  def post(data):
#    print "loginCheck POST"

    result = {}
    result['success'] = False
    session['loginError'] = True

    jsonDict = request.json
    paramsList = jsonDict['params']
    paramsDict = paramsList[0]

    loginUsername = paramsDict['User']
    loginPassword = paramsDict['Pass']

#    print "Name = ", loginUsername, "Password = ", loginPassword

    if 'Remote' in paramsDict:
      if (authentication.auth_verify_remote_user( loginUsername, loginPassword)) :
        result['success'] = True

    else:
      if (authentication.session_authenticate_user( loginUsername, loginPassword)) :
#      print "Username and Password Correct"
        session['username'] = loginUsername

        session['is_authenticated'] = True

        if 'configureDevice' in session['loginRoles']:
          session['can_edit_device'] = True
        else:
          session['can_edit_device'] = False

        if 'editLogging' in session['loginRoles']:
          session['can_edit_logging'] = True
        else:
          session['can_edit_logging'] = False

        if 'actionCommands' in session['loginRoles']:
            session['can_action_command'] = True
        else:
            session['can_action_command'] = False

        if 'editSystem' in session['loginRoles'] :
            session['can_edit_system'] = True
        else :
            session['can_edit_system'] = False

        if 'accessFiles' in session['loginRoles'] :
            session['can_access_files'] = True
        else :
            session['can_access_files'] = False

        if 'editUsers' in session['loginRoles'] :
            session['can_edit_users'] = True
        else :
            session['can_edit_users'] = False

        result['success'] = True
        session['loginError'] = False

      # Note the login in the audit trail.

      else :
#       print "Username and Password BAD"
        result['success'] = False
        session['loginError'] = True

    return jsonify( result )


