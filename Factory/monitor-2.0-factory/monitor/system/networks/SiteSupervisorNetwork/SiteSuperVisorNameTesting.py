import threading
import sqlite3

import httplib
import json
from xml.etree import ElementTree

SiteIPAddress = "10.1.10.59"

def GetSiteNameFromIPAddress(SiteIPAddress):
    retSiteName = ""
    #    print "GetSiteNameFromIPAddress IP=", E2IPAddress

    # Yes, this is a hack. Let's quickly send a message to the IP address and see if we can get the controller name.
    try:
        print(SiteIPAddress)
        SiteConnection = httplib.HTTPConnection(SiteIPAddress, timeout=20)
        print(SiteConnection)
    except Exception, e:
        E2Connection = None
        print("Error")

    if SiteConnection is not None:
        try:
            jsonRequest = {"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}
            SiteConnection.request("GET", 'http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":"1"}')
            #print(SiteConnection.request('GET', '/cgi-bin/mgw.cgi?m={"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}',headers={""}))
            #SiteConnection.request("http://10.1.10.59/cgi-bin/mgw.cgi?m={%22jsonrpc%22:%222.0%22,%22method%22:%22GetSessionID%22,%22id%22:%221%22}")
            jsonResponse = SiteConnection.getresponse()
            jsonData = jsonResponse.read()
            print(jsonData)
            jsonReturn = json.loads(jsonData)
            sessionID = str(jsonReturn["result"]["sid"])
            print(sessionID)
            # jsonRequest = '{"jsonrpc": "2.0", "method":"GetSystemInventory", ' \
            #               '"params":{"sid":"' + sessionID+'"}, "id": "8"}'

            SiteConnection.request("GET", 'http://' + SiteIPAddress + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSystemInventory","id":"1"}')

            # SiteConnection.request("GET", "http://" + SiteIPAddress +
            #                        "/cgi-bin/mgw.cgi?m={'jsonrpc':'2.0','method':'GetSystemInventory','params':{'sid':'" + sessionID + "'}, 'id':'1'}")

            # print('http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m='+ jsonRequest)
            # requestURL = 'http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m=' + jsonRequest
            # SiteConnection.request('GET', str(requestURL))
            jsonResponse = SiteConnection.getresponse()
            jsonData = jsonResponse.read()
            print jsonData
            jsonReturn = json.loads(jsonData)
            dataValues = jsonReturn["result"]["aps"]
            for i in dataValues:
                if (i["apptype"] == "SystemSettings"):
                    iid = i["iid"]
                    break
            print(iid)
            # jsonRequest = '{"jsonrpc": "2.0", "method": "GetPointValues", "params": {"sid":"'+ sessionID+'","points": [{"ptr":"'+ iid +':SiteName"},{"ptr":"'+ iid +':UnitName"},{"ptr":"'+iid +':UnitNumber"}]},"id": "178"}'
            jsonRequest = '{"jsonrpc":"2.0","method":"GetPointValues","params":{"sid":"'+sessionID+'","points":[{"ptr":"'+ iid +':SiteName"},{"ptr":"'+ iid +':UnitName"},{"ptr":"'+iid +':UnitNumber"}]},"id":"178"}'

            SiteConnection.request('GET', 'http://'+SiteIPAddress+'/cgi-bin/mgw.cgi?m='+jsonRequest)
            jsonResponse = SiteConnection.getresponse()
            jsonData = jsonResponse.read()
            jsonReturn = json.loads(jsonData)
            dataValues = jsonReturn["result"]["points"]
            ptrVal = iid + ":UnitName"
            for i in dataValues:
                if (i["ptr"] == ptrVal):
                    deviceName = i["val"]
                    print("Site Supervisor Name")
                    print(deviceName)
                    jsonReturn["result"] = deviceName
                    break

        except Exception, e:
            strExcept = "Could not get controller name: {}".format(str(e))
            print(strExcept)
            # Remove the port information...
            ipOnlyAddr = SiteIPAddress[:SiteIPAddress.find(":")]
            strBuf = "Site Supervisor Device Did Not Respond at {}".format(ipOnlyAddr)
            jsonReturn = {'result': strBuf}

        SiteConnection.close()

        if len(jsonReturn) > 0:
            retSiteName = jsonReturn['result']
    request = {}
    request['method'] = "GetAlarmSummary"
    request['addr'] = SiteIPAddress
    _transact(SiteConnection, request)

    return retSiteName

def _transact( connection, request):
    jsonRequest = json.dumps(request)

    # if the method is GetAlarmList, we have to clean up the JSON because if we don't the E2 blows chunks.
    if request['method'] == 'GetAlarmSummary':
      print("Inside Site Supervisor Alarm Summary Request")
      print(request['addr'])
      # Change Request from "[\"E2 DEMO\", false]" to ["E2 DEMO", false]
      connection.request("GET",'http://' + request['addr'] + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":"1"}')
      # print(connection.request('GET', '/cgi-bin/mgw.cgi?m={"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}',headers={""}))
      # connection.request("http://10.1.10.59/cgi-bin/mgw.cgi?m={%22jsonrpc%22:%222.0%22,%22method%22:%22GetSessionID%22,%22id%22:%221%22}")
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      print(jsonData)
      jsonReturn = json.loads(jsonData)
      sessionID = str(jsonReturn["result"]["sid"])
      print(sessionID)
      jsonRequest = '{"jsonrpc":"2.0","method":"GetAlarms","params":{"sid":"' + sessionID + '"},"id":"178"}'

      connection.request('GET', 'http://' + request['addr'] + '/cgi-bin/mgw.cgi?m=' + jsonRequest)
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      jsonReturn = json.loads(jsonData)
      print (jsonReturn)
      #dataValues = jsonReturn["result"]["alarms"]
      print("SiteSupervisor Transact - " + request['method'])


    elif request['method'] == 'GetThisControllerName':
      print("Inside Site Supervisor GetThisControllerName Request")
      print(request['addr'])
      try:
        jsonRequest = {"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}
        connection.request("GET",'http://' + request['addr'] + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSessionID","id":"1"}')
        # print(connection.request('GET', '/cgi-bin/mgw.cgi?m={"jsonrpc": "2.0", "method": "GetSessionID", "id": "1"}',headers={""}))
        # connection.request("http://10.1.10.59/cgi-bin/mgw.cgi?m={%22jsonrpc%22:%222.0%22,%22method%22:%22GetSessionID%22,%22id%22:%221%22}")
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        print(jsonData)
        jsonReturn = json.loads(jsonData)
        sessionID = str(jsonReturn["result"]["sid"])
        print(sessionID)
        # jsonRequest = '{"jsonrpc": "2.0", "method":"GetSystemInventory", ' \
        #               '"params":{"sid":"' + sessionID+'"}, "id": "8"}'

        connection.request("GET",'http://' + request['addr'] + '/cgi-bin/mgw.cgi?m={"jsonrpc":"2.0","method":"GetSystemInventory","id":"1"}')

        # connection.request("GET", "http://" + request['addr'] +
        #                        "/cgi-bin/mgw.cgi?m={'jsonrpc':'2.0','method':'GetSystemInventory','params':{'sid':'" + sessionID + "'}, 'id':'1'}")

        # print('http://'+request['addr']+'/cgi-bin/mgw.cgi?m='+ jsonRequest)
        # requestURL = 'http://'+request['addr']+'/cgi-bin/mgw.cgi?m=' + jsonRequest
        # connection.request('GET', str(requestURL))
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        print(jsonData)
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["aps"]
        for i in dataValues:
          if (i["apptype"] == "SystemSettings"):
            iid = i["iid"]
            break
        print(iid)
        # jsonRequest = '{"jsonrpc": "2.0", "method": "GetPointValues", "params": {"sid":"'+ sessionID+'","points": [{"ptr":"'+ iid +':SiteName"},{"ptr":"'+ iid +':UnitName"},{"ptr":"'+iid +':UnitNumber"}]},"id": "178"}'
        jsonRequest = '{"jsonrpc":"2.0","method":"GetPointValues","params":{"sid":"' + sessionID + '","points":[{"ptr":"' + iid + ':SiteName"},{"ptr":"' + iid + ':UnitName"},{"ptr":"' + iid + ':UnitNumber"}]},"id":"178"}'

        connection.request('GET', 'http://' + request['addr'] + '/cgi-bin/mgw.cgi?m=' + jsonRequest)
        jsonResponse = connection.getresponse()
        jsonData = jsonResponse.read()
        jsonReturn = json.loads(jsonData)
        dataValues = jsonReturn["result"]["points"]
        ptrVal = iid + ":UnitName"
        for i in dataValues:
          if (i["ptr"] == ptrVal):
            deviceName = i["val"]
            print("Site Supervisor Name")
            print(deviceName)
            jsonReturn["result"] = deviceName
            break
        print(jsonReturn)
      except Exception, e:
        print( "Entered SiteSupervisor GetThisControllerName - {0}".format(e) )

    else:
      connection.request('POST', '/JSON-RPC', jsonRequest, headers={"Content-type": "application/json"})
      jsonResponse = connection.getresponse()
      jsonData = jsonResponse.read()
      #print(jsonData)
      jsonReturn = json.loads(jsonData)
    return jsonReturn



if __name__ == "__main__":
    GetSiteNameFromIPAddress("10.1.10.59")