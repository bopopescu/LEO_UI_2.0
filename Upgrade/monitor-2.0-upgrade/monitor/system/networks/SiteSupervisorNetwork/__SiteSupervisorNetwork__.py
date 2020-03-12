#! /usr/bin/python

import networkConstants
import networkObject

import httplib
import json
import os

import logsystem
import dbUtils

from collections import OrderedDict
from collections import Counter

import elapsedTimer
import time

import re
import datetime
import pytz
from pytz import timezone
from datetime import datetime
import sys
import auditTrail

log = logsystem.getLogger()

_transactMsgs = {}

###################################
# E2 NETWORK
# The E2 Settings are at the Network level so that the user does not need to edit the E2 settings for each E2. It is
# done centrally; instead it is done at the E2 Network level.
###################################
networkType = networkConstants.networkSiteSupervisorNet
networkTypeName = networkConstants.networkSiteSupervisorNetText

class Network(networkObject.NetworkObject):
  def __init__(self, networkManager, name, description, connectionInfo):
    networkObject.NetworkObject.__init__(self, networkManager, name, description, connectionInfo, networkType,
                                           networkTypeName)
    self.HTTPConnectionTimeout = 2 # 2 seconds wait for response.
    self.blSuspendTransactions = False
    # Get copy of dictSettings
    self.E2Settings = self.getE2Settings()
    self.GetThisControllerName = {}
  def run(self):

    strInfo = "Starting:{}, NetType:{}, Description:{}".format( self.name, networkTypeName, self.description )
    log.info( strInfo )
    
    connection = None
    connectionFailure = False  # this is to clear out other connection failures
    connectionFailureMessage = "Error connecting to Site Supervisor - Check IP address, port or network connection"
    currConnectionE2IPAddress = None
    self.debugComm = False
    # log.debug( "E2 Network PID:{0}".format( os.getpid() ) )

    while not self.stopNetwork:
#      print "E2 Network run method Hit"

      with self.lock:
        if self.requestQueue.empty():
          networkTrans = None
        else:
          networkTrans = self.requestQueue.get()

      # This network handles multiple E2 device connections.
      if networkTrans is not None and not self.stopNetwork :
        # process the transactions
        if self.debugComm is True:
          if len( networkTrans.transactions ) > 0 :
            log.debug( "Number of Messages in Site Supervisor Network Run: {0}".format( len( networkTrans.transactions ) ) )

        for transaction in networkTrans.transactions:
          if self.stopNetwork:
            break

          request = transaction.request
          # Added a parameter to request to pass the network IP address for the E2

          # print "***** Request (TYPE: ", type( request ), " Request:", request
          if isinstance(request, dict) and request['method'].find('Get') == 0:
            msgE2IPAddress = request['addr']
            #del request['addr']
          else :
            strRequest = "BAD addr in Site Supervisor Network:{0}".format( request )
            log.debug( strRequest )
            msgE2IPAddress = ''
            # Read it and then delete this addr key.

          #
          # OPEN HTTP CONNECTION
          #
          # If we have a valid IP Address from the transaction AND we do not want to stop processing
          if len( msgE2IPAddress ) > 0 :
            if self.blSuspendTransactions is False:
              # See if we need to open a different E2 connection.
              if connection is None or msgE2IPAddress != currConnectionE2IPAddress :
                # close the connection
                if currConnectionE2IPAddress is not None and connection is not None:
                  connection.close()
                  connection = None
                # Open with the new address
                try:
                  connection = httplib.HTTPConnection(msgE2IPAddress, timeout=self.HTTPConnectionTimeout)
                  currConnectionE2IPAddress = msgE2IPAddress
                except Exception, e:
                  print "HTTPConnection Error: ", e
                  connection = None
                  currConnectionE2IPAddress = None
                  networkTrans.online = False
                  networkTrans.offlineMessage = connectionFailureMessage
                  log.exception("Error connecting to Site Supervisor at " + msgE2IPAddress )
            else:
              connection.close()
              connection = None

          #
          # SEND MESSAGE
          #
          # If good connection, try to send the message.
          blCommGood = True # Assume good until determine otherwise...
          if connection is not None:
            try:
              response = self._transact(connection, request)
              transaction.response = response
              if response is None:
                blCommGood = False
                if self.debugComm is True :
                  strInfo = "SEND ERROR - {}".format( request )
                  log.debug( strInfo )
              else: # We got a response.
                if self.debugComm is True :
                  strInfo = "GOOD SEND - {}, {}, {}".format( transaction, len(response), request )
                  log.debug( strInfo )
            except Exception, e:
              if self.debugComm is True:
                strBuf = "Json failure in transaction to SiteSupervisor for host {}-{}-{})".format(msgE2IPAddress, request, e)
                log.debug( strBuf )
              connectionFailure = True
              blCommGood = False
              connection.close()
              connection = None
              break
          else:
            # We are not connected. Assume offline.
            blCommGood = False

          # Update network transaction status
          if blCommGood is False :
            connectionFailure = True
            networkTrans.online = False
            networkTrans.offlineMessage = connectionFailureMessage
            if connection is not None :
              connection.close()
              connection = None
          else:
            connectionFailure = False
            networkTrans.online = True
            networkTrans.offlineMessage = None

          time.sleep( float(self.E2Settings['E2DelayBetweenMsgsMS']) / 500.0 )

        if networkTrans is not None:
          with self.lock:
              self.completedQueue.put(networkTrans)
      else :
        # Sleep for a period if there are no messages instead of looping like a crazy person.
        time.sleep(2)

  def _transact(self, connection, request):
    jsonRequest = json.dumps(request)
    #log.debug(request)
    requestIP = request['addr']
    if request['method'] == 'GetAlarmSummary':
      connection.connect()
      connection.request('GET','http://' + requestIP + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":""}')
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      #log.debug(jsonData)
      jsonReturn = json.loads(jsonData)
      sessionID = str(jsonReturn["result"]["sid"])
      #log.debug(sessionID)
      jsonRequest = '{"jsonrpc":"2.0","method":"GetAlarms","params":{"sid":"' + sessionID + '"},"id":""}'
      connection.connect()
      connection.request('GET', 'http://' + requestIP + '/cgi-bin/mgw.cgi?m=' + jsonRequest)
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      jsonReturn = json.loads(jsonData)
      #log.debug(jsonReturn)
      #dataValues = jsonReturn["result"]["alarms"]
      #log.debug("SiteSupervisor Transact - " + request['method'])


    elif request['method'] == 'GetThisControllerName':
      try:
        jsonRequest = {"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}
        connection.connect()
        connection.request('GET','http://'+ requestIP + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":"1"}')
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        #log.debug(jsonData)
        jsonReturn = json.loads(jsonData)
        sessionID = str(jsonReturn["result"]["sid"])
        #log.debug(sessionID)
        connection.connect()
        connection.request('GET','http://'+requestIP+'/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSystemInventory","id":"1"}')
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        #log.debug(jsonData)
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["aps"]
        for i in dataValues:
          if (i["apptype"] == "SystemSettings"):
            iid = i["iid"]
            break
        jsonRequest = '{"jsonrpc":"2.0","method":"GetPointValues","params":{"sid":"' + sessionID + '","points":[{"ptr":"' + iid + ':SiteName"},{"ptr":"' + iid + ':UnitName"},{"ptr":"' + iid + ':UnitNumber"}]},"id":"1"}'
        connection.connect()
        connection.request('GET', 'http://' + requestIP + '/cgi-bin/mgw.cgi?m='+jsonRequest)
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["points"]
        ptrVal = iid + ":UnitName"
        for i in dataValues:
          if (i["ptr"] == ptrVal):
            deviceName = i["val"]
            #log.debug("Site Supervisor Name")
            #log.debug(deviceName)
            jsonReturn["result"] = deviceName
            self.GetThisControllerName[requestIP] = deviceName
            break
        #log.debug(jsonReturn)
      except Exception, e:
        log.exception( "Entered SiteSupervisor GetThisControllerName - {0}".format(e) )
        jsonReturn["result"] = None #self.GetThisControllerName[requestIP]
        return jsonReturn["result"]

    else:
      connection.request('POST', '/JSON-RPC', jsonRequest, headers={"Content-type": "application/json"})
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      #log.debug(jsonData)
      jsonReturn = json.loads(jsonData)
    return json.dumps(jsonReturn)

  def getE2Settings(self):
    # no lock needed here as we are writing to the database
    dictE2Settings = ""
    conn = dbUtils.getE2AlarmDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("select * from E2Settings")
      dictE2Settings = dbUtils.dictFromRow(cur.fetchone())
      self.E2Settings = dictE2Settings
    except Exception, e:
      strBuf = "Error in setE2Settings - {0}".format(e)
      log.exception(strBuf)
    finally:
      conn.close()
      return dictE2Settings

  def setE2Settings(self, newSettings):
    conn = dbUtils.getE2AlarmDatabaseConnection()
    try:

      cur = conn.cursor()
      # print "setE2Settings-->", newSettings

      cur.execute("update E2Settings set E2GetAlarms=?, E2alarmCycleTime=?, E2GetAdvisoryOrAnnunciatorLog=?, " \
              "E2AlarmPriorityFilter=?, E2AlarmFilterNotice=?, E2AlarmFilterFail=?, E2AlarmFilterAlarm=?, " \
              "E2AlarmFilterRTN=?, " \
              "E2DevOfflineAlmDelay=?, E2DevOfflineRTNDelay=?, E2MaxValsPerMsg=?,  E2DelayBetweenMsgsMS=?",
          (newSettings["E2GetAlarms"],
          newSettings["E2alarmCycleTime"],
          newSettings["E2GetAdvisoryOrAnnunciatorLog"],
          newSettings["E2AlarmPriorityFilter"],
          newSettings["E2AlarmFilterNotice"],
          newSettings["E2AlarmFilterFail"],
          newSettings["E2AlarmFilterAlarm"],
          newSettings["E2AlarmFilterRTN"],
          newSettings["E2DevOfflineAlmDelay"],
          newSettings["E2DevOfflineRTNDelay"],
          newSettings["E2MaxValsPerMsg"],
          newSettings["E2DelayBetweenMsgsMS"]))
      conn.commit()
      conn.close()

      self.E2Settings = newSettings  # Update the E2 Network E2settings.
      
    except Exception, e:
      log.exception( "Error in setE2Settings - {0}".format(e) )
      return False

  ###########################################
  # E2 Settings Blue-R Reset To Factory Settings.
  ###########################################
  def setE2SettingsToFactorySettings(self) :
    factoryE2Settings = {  "E2GetAlarms":1,
                           "E2alarmCycleTime":30,
                           "E2GetAdvisoryOrAnnunciatorLog":0,
                           "E2AlarmPriorityFilter":20,
                           "E2AlarmFilterNotice":1,
                           "E2AlarmFilterFail":0,
                           "E2AlarmFilterAlarm":0,
                           "E2AlarmFilterRTN":1,
                           "E2DevOfflineRTNDelay":1,
                           "E2DevOfflineAlmDelay":1,
                           "E2MaxValsPerMsg":10,
                           "E2DelayBetweenMsgsMS":500}

    self.setE2Settings( factoryE2Settings )

    conn = dbUtils.getE2AlarmDatabaseConnection()

    try:
      cur = conn.cursor()
      cur.execute("delete from E2RealTimeInfo")
      cur.execute("delete from E2AlarmEntryTable")
      conn.commit()
      conn.close()
      dbUtils.vacuumDatabase( dbUtils.E2AlarmDatabasePath ) # Compress database

    except Exception, e:
      strBuf = "Error in setE2SettingsToFactorySettings - {0}".format(e)
      log.exception(strBuf)


  ###########################################
  # Suspend Transactions - This function is needed so that when we clear the logs, we do not have values continuing to
  # be written into the database.
  ###########################################
  def suspendTransactions(self) :
    self.blSuspendTransactions = True
