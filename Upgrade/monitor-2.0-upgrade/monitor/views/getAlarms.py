from flask_restful import Resource
from flask import jsonify, request
import datetime
import logsystem
log = logsystem.getLogger()
import leoObject

class getAlarms(Resource):
  def __init__(self):
    self.gLeonardo = leoObject.getLeoObject()

  def post(self):
    jsonDict = request.json
    dictSettings = jsonDict['params'][0]
    strAlarmType = dictSettings['alarmList']

    try:
      alarmMgrObj = self.gLeonardo.directory.getAlarmManager()
      allAlms = {}
      if strAlarmType == 'enunciated' :
        # Call with None - so method can get active alarms internally.
        allAlms['active'] = alarmMgrObj.getLeoActiveAlarms()
        allAlms['enunciated'] = alarmMgrObj.getLeoEnunciatedAlarms( allAlms['active'])
        enunciatedIds = {d["E2advid"] for d in allAlms['enunciated']}
        filteredAlarms = [x for x in allAlms['active'] if x["E2advid"] not in enunciatedIds]
        allAlms['active'] = filteredAlarms
        return jsonify( allAlms )

      elif strAlarmType == 'active' :
        allAlms['active'] = alarmMgrObj.getLeoActiveAlarms()
        return jsonify( allAlms )

      elif strAlarmType == 'history' :
        # Because history alarms can be the largest list of alarms, we will make a slight filter here - but only
        # for the frontend browser. If we are the frontend browser, we will see if the lastest LEO alarm
        # is newer than latest alarm that was sent to the frontend - OR - if it's been some period of time, we
        # will also return a boat load of alarm listings.

        # See if web server requested cache/filter bypass
        if "clearHistoryAlarmCache" in dictSettings:
          blClearHistoryAlarmCache = dictSettings['clearHistoryAlarmCache']
        else:
          blClearHistoryAlarmCache = False
          
        # Only when the request is from the local browser AND no clear cache request is indicated, use the filter.
        if ('localhost' in request.host or '127.0.0.1' in request.host) and blClearHistoryAlarmCache is False:
          dictLatestHistoryAlarmEntry = alarmMgrObj.getLeoAlarmLatestHistoryAlarm()
          if alarmMgrObj.autoGetHistoryAlarmsTimer.hasElapsed() or \
                 dictLatestHistoryAlarmEntry != alarmMgrObj.prevdictLatestHistoryAlarmEntry :
            # There is a newer historical alarm. Get the full buffer and return it.
            alarmMgrObj.prevdictLatestHistoryAlarmEntry = dictLatestHistoryAlarmEntry
            allAlms['history'] = alarmMgrObj.getLeoAlarmHistory()
            alarmMgrObj.autoGetHistoryAlarmsTimer.reset()
          else :
            allAlms['history'] = "NoNewAlarms"
        else:
          # If we're not local browser, get the full list everytime.
          allAlms['history'] = alarmMgrObj.getLeoAlarmHistory()

        return jsonify( allAlms )

      elif strAlarmType == 'all' :
        allAlms['active'] = alarmMgrObj.getLeoActiveAlarms()
        allAlms['enunciated'] = alarmMgrObj.getLeoEnunciatedAlarms( allAlms['active']) # Pass in active alarms as optimization
        allAlms['history'] = alarmMgrObj.getLeoAlarmHistory()
        return jsonify( allAlms )

    except Exception, e:
      print "***** getAlarms EXCEPTION *****" + str(e)
      return None
