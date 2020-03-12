from flask_restful import Resource
from flask import render_template, Response, session
import authentication
import LeoFlaskUtils

class pageUsers(Resource):
    def get(self):

        ctx = LeoFlaskUtils.prepareContext("pageUsers")
        template = 'pageUsers.html'

        dataUserRoles = {}
        for entry in authentication.LeoRolesList :
            dataUserRoles[entry['dbRole']] = entry['UIrole']
#        print "dataUserRoes = ", dataUserRoles

        # returns an OrderedDict of users
        odDataUserList = authentication.auth_get_users()

        # Convert from OrderedDict to standard list of users in standard dict format.
        dataUserList = []
        for userRow in odDataUserList :
          dataUserList.append( dict(userRow) )
#        print "dataUserList = ", dataUserList

#        print "Hit units.py - Session = ", session
#        print "clienttype = ", ctx['clienttype']
#        print "Template = ", template
#        print "userRoles =", dataUserRoles
#        print "userList = ", dataUserList

        return Response(render_template(ctx['clienttype'] + '/' + template, ctx=ctx, mimetype='text/html',
                                        userRoles=dataUserRoles, userList=dataUserList ) )

