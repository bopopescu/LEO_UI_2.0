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

import datetime
import pytz
from pytz import timezone
from datetime import datetime
import sys
import auditTrail

#################################################################
# Values for the E2 Status Screens parsing functions
#################################################################

# CREATING/ENCODING THE DYNAMIC E2 STATUS SCREEN LAYOUT IN LEO
APP_HEADER = 1
APP_TYPE = 2
SGL_STATUS = 3
DBL_STATUS = 4
SECT_HEADER = 5
STAGES_STATUS = 6
COMMENT_LINE = 7
MULTI_HEADER = 8
MULTI_VALUE = 9

# Ordered by what I beleve will be the ones seen most
dictStatusLineCmds = {'SglStatus': SGL_STATUS, 'DblStatus': DBL_STATUS, 'AppHeader': APP_HEADER,
                      'AppType': APP_TYPE, 'MultiTitle': MULTI_HEADER, 'MultiValue': MULTI_VALUE,
                      'StagesStatus': STAGES_STATUS, 'SectHeader': SECT_HEADER, '#': COMMENT_LINE}



log = logsystem.getLogger()

    #################################################################
    # E2 Status Screens functions
    #
    # The following are functions for managing and obtaining
    # data for the E2 status screen in LEO
    #################################################################


class E2StatusScreen:
  def __init__(self) :
    # object initialization here.
    if os.name == "nt" :
      CONFIG_FILE_NAME = 'static/StatusScreenConfig.txt'
    else :
      CONFIG_FILE_NAME = '{0}/static/StatusScreenConfig.txt'.format( sys.path[0] )
    self.E2realTimeTableName = 'E2RealTimeInfo'

  # Reads the status screen config file and encodes.
  def _initE2AppStatusScreenConfigFile(self) :

#     print "_initE2AppStatusScreenConfigFile"

    # We now will process the new input file and spit out the matching entries
    dictEncStatusLine = []

    iLineCount = 0
#      print "Opening Status Config File"
    # Now let's open the output file and see if we can pick out all of the input and output board and points
    #        try:
    cfgFile = open(CONFIG_FILE_NAME, "r")

    while 1:
        strInLine = cfgFile.readline()  # read line
        if not strInLine: break
#          strInLine = strInLine.replace("\n\r", "")
        strInLine = strInLine.rstrip()          # Remove trailing white spaces.
#          print "Line-->", strInLine

        params = strInLine.split(",")
        iLineCount = iLineCount + 1

        tmpListEncLine = {}
        tmpListEncLine['cmd'] = 'Error'
        # Look for command in line
        try:
          for strCmd, valCmd in dictStatusLineCmds.iteritems():
              if strCmd == params[0]:
                  tmpListEncLine['cmd'] = valCmd

                  if valCmd == SGL_STATUS:
                      # Need to get description and property
                      tmpListEncLine['descStr'] = params[1]
                      tmpListEncLine['Prop'] = params[2]
                      break

                  elif valCmd == DBL_STATUS:
                      # Need to get TWO descriptions and properties
                      tmpListEncLine['descStr'] = params[1]
                      tmpListEncLine['Prop'] = params[2]
                      tmpListEncLine['descStr2'] = params[3]
                      tmpListEncLine['Prop2'] = params[4]
                      break

                  elif valCmd == APP_HEADER:
                      # Need to simply get string
                      tmpListEncLine['descStr'] = params[1]
                      break

                  if valCmd == APP_TYPE:
                      # Need to get description and property
                      tmpListEncLine['appType'] = params[1]
                      tmpListEncLine['appCellNum'] = int(params[2])
                      break

                  elif valCmd == STAGES_STATUS:
                      tmpListEncLine['MaxStages'] = int(params[1])
                      tmpListEncLine['NumStageProp'] = params[2]
                      tmpListEncLine['Prop'] = params[3]
                      break

                  elif valCmd == SECT_HEADER:
                      # Need to simply get string
                      tmpListEncLine['descStr'] = params[1]
                      break

                  elif valCmd == MULTI_HEADER or valCmd == MULTI_VALUE:
                      paramLen = len(params) - 1
                      iColNum = 1
                      while paramLen > 0:
                          strCol = 'col' + str(iColNum)
                          tmpListEncLine[strCol] = params[iColNum]
                          paramLen = paramLen - 1
                          iColNum = iColNum + 1
                      break

                  elif valCmd == COMMENT_LINE:
                      tmpListEncLine.remove(strCmd)
                      break
        except:
            strOut = "ERROR on Line #{0} - Not Processed-->{1}".format( iLineCount, strInLine )
            log.debug( strOut )

        # If there are entries, add  the list to the collection of status lines
        if len(tmpListEncLine) > 0:
          if tmpListEncLine['cmd'] != 'Error':
            dictEncStatusLine.append(tmpListEncLine)
          else:
            strOut = "ERROR on Line #{0} - Not Processed-->{1}".format( iLineCount, strInLine )
            log.debug( strOut )

#      for line in dictEncStatusLine:
#          print line

    cfgFile.close()
    return dictEncStatusLine

  def _createE2AppTypeProperties( self, dictEncStatusLine ) :

    # Let's go through the dictEncStatusLine and pick out the properties that need to be read.
    listAppTypeProperties = {} # Indexed by str(appType)
    strCellNum = '1'
    for dictLine in dictEncStatusLine:
        if dictLine['cmd'] == SGL_STATUS or dictLine['cmd'] == DBL_STATUS:
            listAppTypeProperties[strCellNum].append( dictLine['Prop'] )
            if dictLine['cmd'] == DBL_STATUS:
                listAppTypeProperties[strCellNum].append( dictLine['Prop2'] )
        elif dictLine['cmd'] == STAGES_STATUS:
            count = 0
            while count < dictLine['MaxStages']:
                twoStarLoc = dictLine['Prop'].find("**")
                oneStarLoc = dictLine['Prop'].find("*")
                if twoStarLoc >= 0:
                    # Two stars = leading zero
                    strStageNoStar = dictLine['Prop'][:oneStarLoc]
                    # replace the * with the number - NO leading zero
                    strProp = "{:s}{:02d}".format(strStageNoStar, count+1)
                    listAppTypeProperties[strCellNum].append( strProp )
                elif oneStarLoc >= 0:
                    # one star = no leading zero
                    strStageNoStar = dictLine['Prop'][:oneStarLoc]
                    # replace the * with the number - NO leading zero
                    strProp = "{0}{1}".format(strStageNoStar, str(count+1))
                    listAppTypeProperties[strCellNum].append( strProp )
                count = count + 1
        elif dictLine['cmd'] == APP_TYPE :
          strCellNum = str(dictLine['appCellNum'])
          listAppTypeProperties[strCellNum] = []
        elif dictLine['cmd'] == MULTI_VALUE :
            # Get number of entries. We know there are is one extra property for 'cmd', but the rest are col1 thru col "n"
            iNumCols = len( dictLine ) - 1
            iCol = 1
            while iCol <= iNumCols : # relative 1
                strCol = 'col' + str(iCol)
                listAppTypeProperties[strCellNum].append( dictLine[strCol] )
                iCol = iCol + 1

    return listAppTypeProperties

  def _createE2AppQueryProps( self, listAppPathByType, listAppTypeProperties ) :
  # We now have a list of all the properties to be read for each apptype and a list of app names.
  # Now we have to translate this all into a list of queries for each appName

    MAX_PROPS_PER_MESSAGE = 15

    listAppPathNameQueryProps = {}
    for appCellNum in listAppPathByType:
        for appPath in listAppPathByType[appCellNum]:
            iNumProps = len(listAppTypeProperties[str(appCellNum)])
            #          print iNumProps
            iPropCount = 0
            listTmpMsgProps = []
            listAppPathNameQueryProps[str(appPath)] = []
            for property in listAppTypeProperties[str(appCellNum)]:
                strProps = '{0}:{1}'.format(appPath, property)
                iNumProps = iNumProps - 1
                iPropCount = iPropCount + 1
                listTmpMsgProps.append(strProps)
                if iPropCount % MAX_PROPS_PER_MESSAGE == 0 and iNumProps > 0:
                    # Message is full. Move to next message.
                    # Need to add commas
                    iPropCount = 0
                    listAppPathNameQueryProps[str(appPath)].append(listTmpMsgProps)
                    listTmpMsgProps = []
            if len(listTmpMsgProps) > 0:  # Make sure all props get out.
                listAppPathNameQueryProps[str(appPath)].append(listTmpMsgProps)

    return listAppPathNameQueryProps

  def _createE2AppStatusMemory( self, listAppPathByType, listAppTypeProperties ) :
    # Create memory storage. We start at props and work up to the controller.
    dictAppsByName = {}
    # Loop through apps for the app type
    for appType in listAppPathByType :

        for appPathName in listAppPathByType[appType] :
            colonLoc = appPathName.find(":")
            appBaseName = appPathName[colonLoc+1:]
            dictAppsByName[appBaseName] = { 'fullName': appPathName }
            dictAppsByName[appBaseName] = { 'appType' : appType }

            # First get all properties for this appType - only once for appType
            dictAppsByName[appBaseName]['props'] = {}
            for propName in listAppTypeProperties[appType]:
                dictAppsByName[appBaseName]['props'][propName] = {}

    return dictAppsByName

  def _updateLastStatusUpdate(self, timeStamp) :
    conn = dbUtils.getE2AlarmDatabaseConnection()
    cur = conn.cursor()
    strSQL = 'update {0} set LastStatusUpdateTime={1}'.format( self.E2realTimeTableName, strTimeStamp )
    cur.execute( strSQL )
    conn.commit()
    conn.close()

  def _initE2AppStatusScreenData( self ):

    self.dictEncStatusLine = self._initE2AppStatusScreenConfigFile( )
    self.listAppTypeProperties = self._createE2AppTypeProperties( self.dictEncStatusLine )

    # Let's build up the list of application names for the types of apps that we are interested in.
    # appNames is a list of application names for the application cell type number (as a string)
    # For example: listAppNames['131'] = list of app names for standard circuits (e.g. ['GROC FRZ', 'ISLE MEAT'])
    listAppPathByType = {}

    for appName,cellNum in self.cellTypes.iteritems():
        strCellNum = str(cellNum)
        if strCellNum in self.listAppTypeProperties.keys():
            if not strCellNum in listAppPathByType :
              listAppPathByType[strCellNum] = []
            strCellPath = "{0}:{1}".format( self.e2ControllerName,appName )
            listAppPathByType[strCellNum].append( strCellPath )

    # Now build up a list of the properties required for the status screen by app name
    self.listAppPathNameQueryProps = self._createE2AppQueryProps(listAppPathByType, self.listAppTypeProperties)
#      print "_createE2AppQueryProps OK"

    blPrintResults = False
    if ( blPrintResults is True ) :
      print "listAppTypeProperties->", self.listAppTypeProperties
      print "listAppTypeProperties"
      for appType in self.listAppTypeProperties :
          print appType, "Props-->", self.listAppTypeProperties[appType]
      print "self.cellTypes->", self.cellTypes
      print "listAppPathByType->", listAppPathByType
      print "listAppPathByType"
      for appPath in listAppPathByType :
          print appPath, "Apps-->", listAppPathByType[appPath]
      print "listAppPathNameQueryProps->", self.listAppPathNameQueryProps

    # create the memory for where we will store the status value results for the UI and JSON interface
    self.dictAppsByName = self._createE2AppStatusMemory( listAppPathByType, self.listAppTypeProperties )
#      print "_createE2AppStatusMemory OK"

    self.blInitE2GetStatus = False

    self.e2Time2GetStatusTimer = elapsedTimer.Interval(self.E2Time2GetStatusInterval)
    self.e2Time2GetStatusTimer.elapse()

    return 0

  def sendE2GetStatusMsg(self, conn, dictAppsByName, listAppPathNameQueryProps):

    if len( self.cellTypes ) !=  len(self.prevCellTypes) :
    # We need to reinitialize the status screens due to a change in the number of apps
      self.blInitE2GetStatus = True

    # Send messages out to E2.
    for appPath in listAppPathNameQueryProps :
      params2Send = listAppPathNameQueryProps[appPath]

      doThis = 1
      if doThis > 0 :
          #  "E2IP Network", "method": "E2.GetMultiExpandedStatus"}
          #  print "NEW Get MultiExpanded Status"
          response = self._transact(conn, {'id': 'E2IP Network', 'method': 'E2.GetMultiExpandedStatus', 'params': params2Send })

      if len( response ) > 0 :
          # Get to the payload of the response
          payload = response['result']['data']

          # Read the response and update the status values in memory
          for propertyStatus in payload :
            params = propertyStatus['prop'].split( ":" ) # Param[0] = controller, Param[1] = appName, Param[2] = property
            controller = params[0]
            appName = params[1]
            prop = params[2]
            memProps = dictAppsByName[appName]['props'][prop]
            memProps['value'] = propertyStatus['value']
            memProps['engUnits'] = propertyStatus['engUnits']
            memProps['alarm'] = propertyStatus['alarm']
            memProps['fail'] = propertyStatus['fail']
            memProps['override'] = propertyStatus['override']

      # If we made it here, we have successfully updated the E2 alarms database. Timestamp it.
      # We need to add UTC after the timestamp so we can properly convert it in the javascript
      strUpdateTimestamp = utilities.getUTCnowFormatted()
      self._updateLastStatusUpdate( strUpdateTimestamp )
      print "Updated E2 Status Timestamp-->", strUpdateTimestamp

    return dictAppsByName

  def getE2StatusScreenData(self) :
    # Whenever we get this call, increase the refresh rate. We will
    # change the interval timer back if we do not hit this refresh for 15 times
#        print "getE2StatusScreenData CALLED. Online= ", self.blE2CommOnline
      if self.blE2CommOnline == True :

 #      try:
          self.E2Time2GetStatusInterval = self.E2_GETSTATUS_FAST_UPDATE_SECS
          self.e2Time2GetStatusTimer = elapsedTimer.Interval(self.E2Time2GetStatusInterval)
          self.e2Time2GetStatusTimer.elapse()

          # We also reset the countdown "counter". When this counter gets to zero
          # the E2Time2GetSTatusInterval will be set back to the default value (e.g. not fast update)
          self.E2StatusFastUpdateResetCounter = self.E2_GETSTATUS_NUM_INTERVALS_TO_RESET_FAST_UPDATE
  #       print "Status Screen Counter = ", self.E2StatusFastUpdateResetCounter, "Interval = ", self.E2Time2GetStatusInterval
#            print "Online???-->", self.blE2CommOnline
          self.E2StatusScreenData['dictAppsByName'] = self.dictAppsByName
          self.E2StatusScreenData['blE2CommOnline'] = self.blE2CommOnline
#           print "E2 PY Status Screend Data ", self.E2StatusScreenData
          return self.E2StatusScreenData
      else :
#            print "getE2StatusScreenData Returned NONE"
          return None
  #      except:
  #       print "getE2StatusScreenData except"
  #        return None


