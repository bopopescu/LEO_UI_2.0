# include "showerrors.inc";
from flask import session, jsonify, request
import subprocess
import auditTrail

import logsystem
log = logsystem.getLogger()
import dbUtils
import os
import hashlib

import logsystem
log = logsystem.getLogger()
import authentication

NO_SESSION_ROLE       = 0
CONFIGURE_DEVICE_ROLE = 1
EDIT_LOGGING_ROLE     = 2
ACTION_COMMANDS_ROLE  = 3
EDIT_SYSTEM_ROLE      = 4
ACCESS_FILES_ROLE     = 5
EDIT_USERS_ROLE       = 6

SERVER = {}

LeoRolesList = [
    { 'role': 'NO_SESSION_ROLE',       'dbRole' : 'None',            'UIrole': 'None' },
    { 'role': 'CONFIGURE_DEVICE_ROLE', 'dbRole' : 'configureDevice', 'UIrole': 'Configure' },
    { 'role': 'EDIT_LOGGING_ROLE',     'dbRole' : 'editLogging',     'UIrole': 'Logged Values' },
    { 'role': 'ACTION_COMMANDS_ROLE',  'dbRole' : 'actionCommands',  'UIrole': 'Action Commands' },
    { 'role': 'EDIT_SYSTEM_ROLE',      'dbRole' : 'editSystem',      'UIrole': 'System' },
    { 'role': 'ACCESS_FILES_ROLE',     'dbRole' : 'accessFiles',     'UIrole': 'Files (Images, Backup/Restore)' },
    { 'role': 'EDIT_USERS_ROLE',       'dbRole' : 'editUsers',       'UIrole': 'Users' }
]

# Function to get data from database in standard Python dict format
def dictFactory(cursor, row):
    retDict = {}
    for idx, col in enumerate(cursor.description):
        retDict[col[0]] = row[idx]
    return retDict

# This MUST only be used for READ ONLY operations. There is no "commit" in this function
def auth_query_database( strSQL ) :
  try :
    conn = dbUtils.getAuthDatabaseConnection()
    conn.row_factory = dictFactory # function to translate to SQL results to dict
    cur = conn.cursor()
#    print "auth_query_database - SQL=", strSQL
    cur.execute( strSQL )
    retval = cur.fetchall()
#    for user in cur.fetchall():
#      dict = dbUtils.dictFromRow(user)
#      retval.append(dict)
#    print "retval =", retval
    conn.close()
    return retval

    #    strReturn = cur.fetchall()

  except:
    log.exception( "Error with database query" )
    retval  = None

  return retval

def md5Password( password ) :
  return ( hashlib.md5( password ).hexdigest() )

def auth_hash_password( password ) :
  return md5Password( password.strip() )

def auth_get_users() :
  # Database query returns in list of orderedDict of records
  return auth_query_database('select name,fullName,roles from users where hidden=0');


###########################################
# Authorization Database Blue-R
def setAuthDatabaseToFactorySettings() :
  conn = dbUtils.getAuthDatabaseConnection()
  cur = conn.cursor()
  # Clear all user records.
  cur.execute('delete from users')
  conn.commit()
  conn.close()
  dbUtils.vacuumDatabase( dbUtils.authDatabasePath ) # Compress database

  # Add back superuser login
  auth_add_superuser()

  # Add back default user login
  _auth_add_default_user()

def _auth_add_default_user() :
  # First delete what is there.
  _auth_delete_default_user()

  # Add default login
  strRoles = ""
  for roleRec in LeoRolesList :
    if roleRec['dbRole'] != "None" :
      strRoles = "{0}{1},".format( strRoles, roleRec['dbRole'] )
  auth_add_user( 'hl',  'Default Admin', strRoles, 'pass' )
  auth_add_user( 'user1',  'Level 1 Access', 'actionCommands', 'pass' )
  auth_add_user( 'user2',  'Level 2 Access', 'configureDevice,actionCommands,editLogging', 'pass' )
  auth_add_user( 'user3',  'Level 3 Access', 'configureDevice,actionCommands,editLogging,editSystem', 'pass' )
  auth_add_user( 'user4',  'Level 4 Access', 'configureDevice,actionCommands,editLogging,editSystem,accessFiles', 'pass' )
  auth_add_user( 'Virtual',  'Remote Login', '', 'remote' )

def _auth_delete_default_user() :
  # Add default login
  conn = dbUtils.getAuthDatabaseConnection()
  cur = conn.cursor()
  strSQL = 'delete from users where name="hl"'
  try:
    cur = conn.cursor()
    cur.execute( strSQL )
    conn.commit()
  except:
    log.exception( "Error removing default user" )

  conn.close()


# Update a user in the database.
def auth_set_user_info( name, fullName, roles) :

  conn = dbUtils.getAuthDatabaseConnection()
  cur = conn.cursor()

  try:
    strSQL = 'update users set fullName="{0}", roles="{1}" where name="{2}" and hidden=0'.format( fullName, roles, name )

#    print "SetUserInfo->", strSQL
    cur = conn.cursor()
    cur.execute( strSQL )
    conn.commit()
    conn.close()
  except:
      log.exception( "Error with set user operation" )
  conn.close()

  return auth_get_users();


def auth_set_user_password( name, password) :
  if len( password ) > 0 :
    conn = dbUtils.getAuthDatabaseConnection()
    cur = conn.cursor()
    try :
      password_hash = auth_hash_password( password )
      strSQL = 'update users set password="{0}" where name="{1}"'.format( password_hash, name )
      cur = conn.cursor()
      cur.execute( strSQL )
      conn.commit()

    except:
      log.exception( "Error with set user operation", e.message )

    conn.close()
  return auth_get_users();


def auth_add_user( name,  fullName, roles, password) :
  if len( password ) > 0 and len( name ) > 0 :
    conn = dbUtils.getAuthDatabaseConnection()
    cur = conn.cursor()
    try:
      strSQL = "select name from users where name='{0}'".format( name )
      cur = conn.cursor()
      cur.execute( strSQL )
      user = cur.fetchall()

    except:
      user = None

    # If the user does not exist
    if len(user) == 0 :
      password_hash = auth_hash_password(password);
      try:
        strSQL = 'INSERT INTO users (name,fullname,roles,password,hidden) VALUES ( "{0}","{1}","{2}","{3}", 0)'.format( name, fullName, roles, password_hash )
#        print strSQL
        cur = conn.cursor()
        cur.execute( strSQL )
        conn.commit()
      except:
        log.exception( "Error adding user" )

    conn.close()
  return auth_get_users();

# Delete admin user ...Should only be called during backup
def auth_delete_superuser() :
  conn = dbUtils.getAuthDatabaseConnection()
  cur = conn.cursor()
  strSQL = 'delete from users where hidden=1;'
  try:
    cur = conn.cursor()
    cur.execute( strSQL )
    conn.commit()
  except:
    log.exception( "Error removing default user" )

  conn.close()

# Add admin user (admin)...Should only be called during backup
def auth_add_superuser() :

  # First kill current admin
  auth_delete_superuser()

  # Next we need to build up a string of all the permissions
  strRoles = ""
  for roleRec in LeoRolesList :
    if roleRec['dbRole'] != "None" :
      strRoles = "{0}{1},".format( strRoles, roleRec['dbRole'] )

  if len( strRoles ) > 0 :
    # Remove last comma
    strRoles = strRoles[0:strRoles.rfind(",")]

  # Now, update the database with the new superuser username and password
  conn = dbUtils.getAuthDatabaseConnection()
  cur = conn.cursor()

  password_hash = auth_hash_password('Hunt3rL!berty53')
  try:
    strKeys = 'name,fullname,roles,password,hidden'
    strValues = '"huntlib","Hunter Liberty","{0}","{1}",1'.format( strRoles, password_hash )
    strValues = '"huntlib","Hunter Liberty","{0}","{1}",1'.format( strRoles, password_hash )
    strSQL = 'INSERT INTO users ( {0} ) VALUES ( {1} )'.format( strKeys, strValues )
    cur.execute( strSQL )
    conn.commit()

  except:
      log.exception( "Error adding superuser" )

  conn.close()
  return 0

def auth_delete_users( nameArray ) :
#  print "Hit auth_delete_users->", nameArray

  conn = dbUtils.getAuthDatabaseConnection()

  for name in nameArray :
    try :
      strSQL = 'delete from users where name="{0}" and hidden=0'.format( name )
      cur = conn.cursor()
      cur.execute( strSQL )
      conn.commit()
    except:
      log.exception( "Error deleting user(s)" )

  conn.close()
  return auth_get_users()

def auth_verify_user( name, password ) :

#  print "Hit auth_verify_user->", name, password
  conn = dbUtils.getAuthDatabaseConnection()
  conn.row_factory = dictFactory  # function to translate to SQL results to dict
  cur = conn.cursor()

  strReturn = ''

  password_hash = auth_hash_password( password )
#  print "password_hash->", password_hash

  try :
    strSQL = 'select name,fullName,roles,hidden from users where name="{0}" and password="{1}"'.format( name, password_hash )
#    print strSQL
    cur.execute( strSQL )
    strReturn = cur.fetchall()
#    print "strReturn->", strReturn

  except:
    log.exception( "Error verifying users")

  conn.close()
#  print "strReturn", strReturn
  if len(strReturn) > 0 :
    return strReturn
  else :
    return ""


def auth_verify_remote_user( name, password ) :
  # log.debug(name)
  # log.debug(password)
  if len(name) == 0 or len(password) == 0 :
    return False

#  print "Hit auth_verify_user->", name, password
  conn = dbUtils.getAuthDatabaseConnection()
  conn.row_factory = dictFactory  # function to translate to SQL results to dict
  cur = conn.cursor()

  strReturn = ''

  password_hash = auth_hash_password( password )
#  print "password_hash->", password_hash

  try :
    strSQL = 'select name,fullName,roles,hidden from users where name="{0}" and password="{1}"'.format( name, password_hash )
#    print strSQL
    cur.execute( strSQL )
    strReturn = cur.fetchall()
    val= {}
   # log.debug(strReturn)
  except:
    log.exception( "Error verifying Remote Login users")

  conn.close()
#  print "strReturn", strReturn
  if len(strReturn) > 0 :
    #val["success"] = True
    return True
  else :
    #val["success"] = False
    return  False


def session_authenticate_user( name, password) :

#  print "!!! Hit session_authenticate_user->", name, password

  # Test the username and password parameters
  if len(name) == 0 or len(password) == 0 :
    return False

  user = auth_verify_user(name, password)
  if len( user ) == 0 :
    return False

  # Register the loginUsername
  dictUser = user[0]
  session["loginUsername"] = dictUser["fullName"]
  session["loginRoles"] = dictUser["roles"]
  session["loginHidden"] = dictUser["hidden"]
#  print "Hit session_authenticate_user - RETURN TRUE"

  strAudit = '{0} Logged in'.format( name )
  auditTrail.AuditTrailAddEntry( strAudit )

  return True


# Connects to a session and checks that the user has
# authenticated and that the remote IP address matches
# the address used to create the session.
def session_page_authenticate() :

#  print "Hit session_page_authenticate"

  # Check if the user hasn't logged in
  if len(session["loginUsername"]) == 0 :
    # The request does not identify a session
    session["message"] = "You are not authorized to access the URL {0}".format( SERVER["REQUEST_URI"] )
#    print("Logged Out");


  # Check if the request is from a different IP address to previously
  if len( session["sessionIP"] ) == 0 or ( session["sessionIP"] != SERVER["REMOTE_ADDR"]) :

    # The request did not originate from the machine
    # that was used to create the session.
    # THIS IS POSSIBLY A session HIJACK ATTEMPT
    session["message"] = 'You are not authorized to access the URL {0} from the address {1}'.format( SERVER["REQUEST_URI"], SERVER["REMOTE_ADDR"] )
#    print("Logged Out");


# Connects to a session and checks that the user has
# authenticated and that the remote IP address matches
# the address used to create the session.
def session_is_authenticated( ) :
  if len( session["loginUsername"]) > 0 and len(session["sessionIP"]) > 0 and (session["sessionIP"] == SERVER["REMOTE_ADDR"]) :
#    print "Hit session_is_authenticated->TRUE"
    return True
  else :
#    print "Hit session_is_authenticated->FALSE"
    return False

def auth_set_sessionIP() :
#  print "Hit auth_set_sessionIP"

  if len( session["sessionIP"]) == 0 :
    # Register the IP address that started this session
    session["sessionIP"] = SERVER["REMOTE_ADDR"];

def auth_check_sessionIP() :
  # Check if the request is from a different IP address to previously
  if len( session["sessionIP"] ) > 0 or ( session["sessionIP"] != SERVER["REMOTE_ADDR"]) :
    print('HTTP/1.0 404 Not Found');
    # Destroy the session.
#    TODO session.delete()

def session_username( ) :
  if len(session["loginUsername"]) > 0 :
    return session["loginUsername"]
  else :
    return ""

def session_role( role ) :
  if len( session["loginHidden"]) > 0 and len( session["loginHidden"] ) > 0 :
    return True

  if len(session["loginRoles"]) > 0 :
    if session["loginRoles"].find( role ) < 0 :
      return False
    return True
  else :
    return False

def session_can_edit_device() :
  return session_role(LeoRolesList[CONFIGURE_DEVICE_ROLE]['role'])

def session_can_edit_logging() :
  return session_role(LeoRolesList[EDIT_LOGGING_ROLE]['role'])

def session_can_action_command() :
  return session_role(LeoRolesList[ACTION_COMMANDS_ROLE]['role'])

def session_can_edit_system() :
  return session_role(LeoRolesList[EDIT_SYSTEM_ROLE]['role'])

def session_can_access_files():
  return session_role(LeoRolesList[ACCESS_FILES_ROLE]['role'])

def session_can_edit_users() :
  return session_role(LeoRolesList[EDIT_USERS_ROLE]['role'])

