

E2ControllerNames = [ "Rack A", "Rack B", "Rack C", "Rack D", "Rack E" ]

def E2SimResponse( request, E2Name ) :

  print "E2SimResponse - Request: ", request

  if request['method'] == 'E2.GetThisControllerName' :
    return { "result": E2Name, "unitnum": 2,"id": "E2IP Network" }

  elif request['method'] == 'E2.GetAlarmList' :
    print request
    return {
        "result": {
          "data": [
            { "advid": 981733113, "advcode": 214, "timestamp": "12-22-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00", "priority": 20, "rtntimestamp": "12-22-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733111, "advcode": 214, "timestamp": "12-22-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm",
              "alarm": True, "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False,  "rtn": True, "ackuser": "", "acktimestamp": "  0:00", "priority": 20, "rtntimestamp": "12-22-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            {  "advid": 981733109, "advcode": 214, "timestamp": "12-22-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm",
              "alarm": True, "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False,  "rtn": True, "ackuser": "", "acktimestamp": "  0:00", "priority": 20, "rtntimestamp": "12-22-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733107, "advcode": 214, "timestamp": "12-22-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00", "priority": 20, "rtntimestamp": "12-22-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733105, "advcode": 214, "timestamp": "12-22-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00", "priority": 20, "rtntimestamp": "12-22-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733103, "advcode": 214, "timestamp": "12-22-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733101, "advcode": 214, "timestamp": "12-22-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733099, "advcode": 214, "timestamp": "12-22-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733097, "advcode": 214, "timestamp": "12-22-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733095, "advcode": 214, "timestamp": "12-22-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733093, "advcode": 214, "timestamp": "12-22-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733091, "advcode": 214, "timestamp": "12-22-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733089, "advcode": 214, "timestamp": "12-22-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733087, "advcode": 214, "timestamp": "12-22-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733085, "advcode": 214, "timestamp": "12-22-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733083, "advcode": 214, "timestamp": "12-22-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733081, "advcode": 214, "timestamp": "12-22-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-22-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733079, "advcode": 214, "timestamp": "12-21-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733077, "advcode": 214, "timestamp": "12-21-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733075, "advcode": 214, "timestamp": "12-21-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733073, "advcode": 214, "timestamp": "12-21-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733071, "advcode": 214, "timestamp": "12-21-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733069, "advcode": 214, "timestamp": "12-21-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733067, "advcode": 214, "timestamp": "12-21-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733065, "advcode": 214, "timestamp": "12-21-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733063, "advcode": 214, "timestamp": "12-21-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733061, "advcode": 214, "timestamp": "12-21-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733059, "advcode": 214, "timestamp": "12-21-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733057, "advcode": 214, "timestamp": "12-21-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733055, "advcode": 214, "timestamp": "12-21-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733053, "advcode": 214, "timestamp": "12-21-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733051, "advcode": 214, "timestamp": "12-21-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733049, "advcode": 214, "timestamp": "12-21-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733047, "advcode": 214, "timestamp": "12-21-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733045, "advcode": 214, "timestamp": "12-21-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733043, "advcode": 214, "timestamp": "12-21-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733041, "advcode": 214, "timestamp": "12-21-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733039, "advcode": 214, "timestamp": "12-21-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733037, "advcode": 214, "timestamp": "12-21-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733035, "advcode": 214, "timestamp": "12-21-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733033, "advcode": 214, "timestamp": "12-21-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-21-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733031, "advcode": 214, "timestamp": "12-20-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733029, "advcode": 214, "timestamp": "12-20-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733027, "advcode": 214, "timestamp": "12-20-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733025, "advcode": 214, "timestamp": "12-20-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733023, "advcode": 214, "timestamp": "12-20-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733021, "advcode": 214, "timestamp": "12-20-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733019, "advcode": 214, "timestamp": "12-20-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733017, "advcode": 214, "timestamp": "12-20-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733015, "advcode": 214, "timestamp": "12-20-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733013, "advcode": 214, "timestamp": "12-20-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733011, "advcode": 214, "timestamp": "12-20-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733009, "advcode": 214, "timestamp": "12-20-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733007, "advcode": 214, "timestamp": "12-20-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733005, "advcode": 214, "timestamp": "12-20-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733003, "advcode": 214, "timestamp": "12-20-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981733001, "advcode": 214, "timestamp": "12-20-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732999, "advcode": 214, "timestamp": "12-20-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732997, "advcode": 214, "timestamp": "12-20-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732995, "advcode": 214, "timestamp": "12-20-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732993, "advcode": 214, "timestamp": "12-20-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732991, "advcode": 214, "timestamp": "12-20-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732989, "advcode": 214, "timestamp": "12-20-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732987, "advcode": 214, "timestamp": "12-20-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732985, "advcode": 214, "timestamp": "12-20-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-20-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732983, "advcode": 214, "timestamp": "12-19-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732981, "advcode": 214, "timestamp": "12-19-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732979, "advcode": 214, "timestamp": "12-19-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732977, "advcode": 214, "timestamp": "12-19-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732975, "advcode": 214, "timestamp": "12-19-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732973, "advcode": 214, "timestamp": "12-19-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732971, "advcode": 214, "timestamp": "12-19-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732969, "advcode": 214, "timestamp": "12-19-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732967, "advcode": 214, "timestamp": "12-19-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732965, "advcode": 214, "timestamp": "12-19-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732963, "advcode": 214, "timestamp": "12-19-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732961, "advcode": 214, "timestamp": "12-19-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732959, "advcode": 214, "timestamp": "12-19-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732957, "advcode": 214, "timestamp": "12-19-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732955, "advcode": 214, "timestamp": "12-19-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732953, "advcode": 214, "timestamp": "12-19-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732951, "advcode": 214, "timestamp": "12-19-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732949, "advcode": 214, "timestamp": "12-19-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732947, "advcode": 214, "timestamp": "12-19-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732945, "advcode": 214, "timestamp": "12-19-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732943, "advcode": 214, "timestamp": "12-19-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732941, "advcode": 214, "timestamp": "12-19-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732939, "advcode": 214, "timestamp": "12-19-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732937, "advcode": 214, "timestamp": "12-19-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-19-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732935, "advcode": 214, "timestamp": "12-18-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732933, "advcode": 214, "timestamp": "12-18-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732931, "advcode": 214, "timestamp": "12-18-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732929, "advcode": 214, "timestamp": "12-18-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732927, "advcode": 214, "timestamp": "12-18-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732925, "advcode": 214, "timestamp": "12-18-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732923, "advcode": 214, "timestamp": "12-18-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732921, "advcode": 214, "timestamp": "12-18-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732919, "advcode": 214, "timestamp": "12-18-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732917, "advcode": 214, "timestamp": "12-18-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732915, "advcode": 214, "timestamp": "12-18-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732913, "advcode": 214, "timestamp": "12-18-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732911, "advcode": 214, "timestamp": "12-18-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732909, "advcode": 214, "timestamp": "12-18-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732907, "advcode": 214, "timestamp": "12-18-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732905, "advcode": 214, "timestamp": "12-18-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732903, "advcode": 214, "timestamp": "12-18-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732901, "advcode": 214, "timestamp": "12-18-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732899, "advcode": 214, "timestamp": "12-18-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732897, "advcode": 214, "timestamp": "12-18-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732895, "advcode": 214, "timestamp": "12-18-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732893, "advcode": 214, "timestamp": "12-18-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732891, "advcode": 214, "timestamp": "12-18-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732889, "advcode": 214, "timestamp": "12-18-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-18-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732887, "advcode": 214, "timestamp": "12-17-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732885, "advcode": 214, "timestamp": "12-17-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732883, "advcode": 214, "timestamp": "12-17-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732881, "advcode": 214, "timestamp": "12-17-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732879, "advcode": 214, "timestamp": "12-17-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732877, "advcode": 214, "timestamp": "12-17-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732875, "advcode": 214, "timestamp": "12-17-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732873, "advcode": 214, "timestamp": "12-17-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732871, "advcode": 214, "timestamp": "12-17-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732869, "advcode": 214, "timestamp": "12-17-16 14:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 14:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732867, "advcode": 214, "timestamp": "12-17-16 13:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 13:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732865, "advcode": 214, "timestamp": "12-17-16 12:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 12:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732863, "advcode": 214, "timestamp": "12-17-16 11:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 11:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732861, "advcode": 214, "timestamp": "12-17-16 10:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16 10:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732859, "advcode": 214, "timestamp": "12-17-16  9:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  9:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732857, "advcode": 214, "timestamp": "12-17-16  8:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  8:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732855, "advcode": 214, "timestamp": "12-17-16  7:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  7:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732853, "advcode": 214, "timestamp": "12-17-16  6:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  6:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732851, "advcode": 214, "timestamp": "12-17-16  5:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  5:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732849, "advcode": 214, "timestamp": "12-17-16  4:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  4:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732847, "advcode": 214, "timestamp": "12-17-16  3:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  3:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732845, "advcode": 214, "timestamp": "12-17-16  2:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  2:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732843, "advcode": 214, "timestamp": "12-17-16  1:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  1:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732841, "advcode": 214, "timestamp": "12-17-16  0:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-17-16  0:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732839, "advcode": 214, "timestamp": "12-16-16 23:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 23:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732837, "advcode": 214, "timestamp": "12-16-16 22:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 22:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732835, "advcode": 214, "timestamp": "12-16-16 21:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 21:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732833, "advcode": 214, "timestamp": "12-16-16 20:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 20:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732831, "advcode": 214, "timestamp": "12-16-16 19:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 19:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732829, "advcode": 214, "timestamp": "12-16-16 18:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 18:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732827, "advcode": 214, "timestamp": "12-16-16 17:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 17:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732825, "advcode": 214, "timestamp": "12-16-16 16:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 16:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732823, "advcode": 214, "timestamp": "12-16-16 15:00", "state": "N-ALM*", "source": "RACK A   :0IG SENSOR001 :COMMAND OUT", "text": "Digital Sensor Alarm", "alarm": True,
              "notice": False, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": True, "ackuser": "", "acktimestamp": "  0:00","priority": 20, "rtntimestamp": "12-16-16 15:05", "reportvalue": "ON", "limit": "ON", "engUnits": "ON_OFF"
            },
            { "advid": 981732816, "advcode": 9046, "timestamp": "12-16-16 11:34", "state": "NOTCE*", "source": "RACK A   :NetSetup      :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732815, "advcode": 9046, "timestamp": "12-16-16 11:33", "state": "NOTCE*", "source": "E2 Unit02:GENERAL SERV  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732485, "advcode": 9049, "timestamp": "12-09-16 15:39", "state": "NOTCE*", "source": "E2 Unit02:TIME SCHED001 :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732484, "advcode": 9046, "timestamp": "12-09-16 15:38", "state": "NOTCE*", "source": "E2 Unit02:TIME SCHED001 :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732483, "advcode": 9046, "timestamp": "12-09-16 15:38", "state": "NOTCE*", "source": "E2 Unit02:GLOBAL DATA   :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732481, "advcode": 9048, "timestamp": "12-09-16 15:34", "state": "NOTCE*", "source": "E2 Unit02:TIME SCHED001 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732359, "advcode": 9040, "timestamp": "12-07-16  9:31", "state": "NOTCE*", "source": "E2 Unit02:System        :", "text": "Controller startup", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 50, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732358, "advcode": 9039, "timestamp": "12-07-16  9:10", "state": "NOTCE*", "source": "E2 Unit02:System        :", "text": "Controller shutdown", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 50, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732354, "advcode": 9046, "timestamp": "12-07-16  8:20", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.08  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732353, "advcode": 9048, "timestamp": "12-07-16  8:20", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.08  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732352, "advcode": 9049, "timestamp": "12-07-16  8:19", "state": "NOTCE*", "source": "E2 Unit02:INLET PRES.SOL:", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732351, "advcode": 9046, "timestamp": "12-07-16  8:19", "state": "NOTCE*", "source": "E2 Unit02:TEST DIGITAL16:", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732350, "advcode": 9048, "timestamp": "12-07-16  8:18", "state": "NOTCE*", "source": "E2 Unit02:DIG SENSOR003 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732349, "advcode": 9046, "timestamp": "12-07-16  8:17", "state": "NOTCE*", "source": "E2 Unit02:TEST ANALOG 15:", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732347, "advcode": 9046, "timestamp": "12-07-16  8:15", "state": "NOTCE*", "source": "E2 Unit02:TEST ALARM    :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732345, "advcode": 9048, "timestamp": "12-07-16  8:13", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.16  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981732310, "advcode": 9051, "timestamp": "12-06-16 15:32", "state": "NOTCE*", "source": "E2 Unit02:ADVISORY SERV :", "text": "Alarm(s) were reset", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730313, "advcode": 9049, "timestamp": "10-27-16 16:21", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.01  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730304, "advcode": 9049, "timestamp": "10-27-16 16:15", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.16  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730295, "advcode": 9046, "timestamp": "10-27-16 15:42", "state": "NOTCE*", "source": "E2 Unit02:1DIGDEMAN     :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730293, "advcode": 9048, "timestamp": "10-27-16 15:40", "state": "NOTCE*", "source": "E2 Unit02:DIG SENSOR002 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730291, "advcode": 9046, "timestamp": "10-27-16 15:40", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.01  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730290, "advcode": 9048, "timestamp": "10-27-16 15:40", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.01  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730271, "advcode": 9046, "timestamp": "10-27-16 10:15", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.04  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730270, "advcode": 9048, "timestamp": "10-27-16 10:15", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.04  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730269, "advcode": 9049, "timestamp": "10-27-16 10:15", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.04  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730268, "advcode": 9046, "timestamp": "10-27-16 10:15", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.04  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730267, "advcode": 9049, "timestamp": "10-27-16 10:14", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.01  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730259, "advcode": 9046, "timestamp": "10-27-16 10:12", "state": "NOTCE*", "source": "E2 Unit02:LOW TEMP      :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730251, "advcode": 9046, "timestamp": "10-27-16 10:09", "state": "NOTCE*", "source": "E2 Unit02:SATELITE      :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730248, "advcode": 9046, "timestamp": "10-27-16 10:08", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.16  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730246, "advcode": 9048, "timestamp": "10-27-16 10:08", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.16  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730236, "advcode": 9049, "timestamp": "10-27-16 10:04", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.16  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730224, "advcode": 9046, "timestamp": "10-27-16 10:01", "state": "NOTCE*", "source": "E2 Unit02:ACCESS SERVICE:", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981730176, "advcode": 9049, "timestamp": "10-26-16 11:04", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.03  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729940, "advcode": 9046, "timestamp": "10-21-16 16:16", "state": "NOTCE*", "source": "E2 Unit02:0IM SCHEDULE  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729742, "advcode": 9046, "timestamp": "10-17-16 14:10", "state": "NOTCE*", "source": "E2 Unit02:15 DR ORGANC  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729735, "advcode": 9046, "timestamp": "10-17-16 13:21", "state": "NOTCE*", "source": "E2 Unit02:0IG SENSOR001 :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729731, "advcode": 9046, "timestamp": "10-17-16 13:13", "state": "NOTCE*", "source": "E2 Unit02:INLET PRES.SOL:", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729730, "advcode": 9046, "timestamp": "10-17-16 13:13", "state": "NOTCE*", "source": "E2 Unit02:SIM SCHEDULE  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729729, "advcode": 9049, "timestamp": "10-17-16 13:12", "state": "NOTCE*", "source": "E2 Unit02:TIME SCHED001 :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729728, "advcode": 9048, "timestamp": "10-17-16 13:11", "state": "NOTCE*", "source": "E2 Unit02:TIME SCHED001 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729724, "advcode": 9046, "timestamp": "10-17-16 13:04", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.10  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729723, "advcode": 9048, "timestamp": "10-17-16 13:04", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.10  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729722, "advcode": 9048, "timestamp": "10-17-16 13:03", "state": "NOTCE*", "source": "E2 Unit02:DIG SENSOR001 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729695, "advcode": 9049, "timestamp": "09-29-16 16:33", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729694, "advcode": 9046, "timestamp": "09-29-16 16:32", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729691, "advcode": 9048, "timestamp": "09-29-16 15:45", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729687, "advcode": 9049, "timestamp": "09-29-16 15:09", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729686, "advcode": 9046, "timestamp": "09-29-16 14:53", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729684, "advcode": 9048, "timestamp": "09-29-16 11:25", "state": "NOTCE*", "source": "E2 Unit02:EN SUC GRP003 :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729667, "advcode": 9049, "timestamp": "08-30-16 11:06", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.08  :", "text": "Application was deleted", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729666, "advcode": 9046, "timestamp": "08-30-16  9:17", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.08  :", "text": "Application config has changed", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            },
            { "advid": 981729664, "advcode": 9048, "timestamp": "08-30-16  9:17", "state": "NOTCE*", "source": "E2 Unit02:.AI.02.01.08  :", "text": "Application was created", "alarm": False,
              "notice": True, "fail": False, "unacked": True, "acked": False, "reset": False, "rtn": False, "ackuser": "", "acktimestamp": "  0:00","priority": 99, "rtntimestamp": "  0:00", "reportvalue": "", "limit": "", "engUnits": "NONE"
            }
          ]
        },
        "id": 0
      }


  elif request['method'] == 'E2.GetCellList' :
    print request
    return { "result":
     {
         "data": [
        { "controller": "RACK A ", "cellname": ".AI.02.01.02", "celllongname": "", "celltype": 1, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.04", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.05", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.06", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.07", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.08", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.09", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.10", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.11", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.12", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.13", "celllongname": "", "celltype": 1, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".AI.02.01.15", "celllongname": "", "celltype": 1, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.01", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.02", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.03", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.04", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.05", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.06", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.07", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": ".RO.02.01.08", "celllongname": "", "celltype": 33, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "0IG SENSOR001", "celllongname": "", "celltype": 96, "celltypename": "???"},
        { "controller": "RACK A ", "cellname": "0IM SCHEDULE", "celllongname": "Circuit 01", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "15 DR ORGANC", "celllongname": "Circuit 02", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "16AI_001", "celllongname": "", "celltype": 165, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "1DIGDEMAN", "celllongname": "", "celltype": 96, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "22DR ICE CR", "celllongname": "Circuit 10", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "28DR FRZ FD", "celllongname": "Circuit 07", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "3-FRZ ENDCPS", "celllongname": "Circuit 03", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "32DR FRZ FD", "celllongname": "Circuit 06", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "8RO_001", "celllongname": "", "celltype": 166, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "ACCESS LOG", "celllongname": "", "celltype": 236, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "ACCESS SERVICE", "celllongname": "", "celltype": 226, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "ADVISORY SERV", "celllongname": "", "celltype": 225, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "Advisory Log", "celllongname": "", "celltype": 234, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "BASE LOG", "celllongname": "", "celltype": 73, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "Condenser 1", "celllongname": "Condenser 01", "celltype": 129, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "DEVICE SUMM", "celllongname": "", "celltype": 89, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "RACK A ", "celllongname": "", "celltype": 74, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "GENERAL SERV", "celllongname": "", "celltype": 227, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "GLOBAL DATA", "celllongname": "", "celltype": 91, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "GROC FRZ", "celllongname": "Circuit 09", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "ISLE MEAT", "celllongname": "Circuit 04", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "LOW TEMP", "celllongname": "Suction Group 01", "celltype": 162, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "NOTE PAD", "celllongname": "", "celltype": 224, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "NV HANDLER", "celllongname": "", "celltype": 230, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "NetworkService", "celllongname": "", "celltype": 229, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "OVERRIDE LOG", "celllongname": "", "celltype": 237, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "REMOTE DIAL", "celllongname": "", "celltype": 233, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "RXSetupWizard", "celllongname": "", "celltype": 238, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "SATELITE", "celllongname": "Suction Group 02", "celltype": 162, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "SIM SCHEDULE", "celllongname": "", "celltype": 94, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "STD CIRCUIT010", "celllongname": "", "celltype": 131, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "TEST ALARM", "celllongname": "", "celltype": 2, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "TEST ANALOG 15", "celllongname": "Sensor 01", "celltype": 94, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "TEST DIGITAL16", "celllongname": "", "celltype": 96, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "TIME SERVICES", "celllongname": "", "celltype": 228, "celltypename": "???" },
        { "controller": "RACK A ", "cellname": "UG LEAK DETECT", "celllongname": "Sensor 04", "celltype": 94, "celltypename": "???" }
      ]
    },
  "id": "E2IP Network"
  }

  elif request['method'] == 'E2.GetConfigValues' :
    if request['params'][0][0].find( 'TIME SERVICES:Time Zone' ) >= 0 :    # Time zone request
      return { 'result':
        {
          'data': [
          {'valueBin': '80', 'value': '-05:00 Eastern', 'prop': 'E2 DEMO:TIME SERVICES:Time Zone'}
          ]
        },
      'id': u'E2IP Network'
      }
    else :
      print request
      return { "result":
        {
          "data": [
          { "prop": "RACK A :0IM SCHEDULE:Name", "value": "0IM SCHEDULE", "alarm": False, "notice": False, "fail": False, "override": False, "ovtime": "", "ovtype": 0, "engUnits": "NONE", "dataType": 0, "bypasstime": "" },
          { "prop": "RACK A :0IM SCHEDULE:Long Name", "value": "Circuit 01", "alarm": False, "notice": False, "fail": False, "override": False, "ovtime": "", "ovtype": 0, "engUnits": "NONE", "dataType": 0, "bypasstime": "" },
          { "prop": "RACK A :0IM SCHEDULE:CASE TEMP STPT", "value": "57.00", "alarm": False, "notice": False, "fail": False, "override": False, "ovtime": "0:00:00", "ovtype": 0, "engUnits": "DF", "dataType": 1, "bypasstime": "" }
          ]
        },
        "id": "E2IP Network"
      }

  elif request['method'] == 'E2.GetMultiExpandedStatus' :
    print request
    return {}


  