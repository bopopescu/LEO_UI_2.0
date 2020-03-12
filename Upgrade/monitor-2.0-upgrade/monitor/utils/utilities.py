#! /usr/bin/python

import time
import datetime


def compareLists(old, new):
  oldset = set(old)
  addlist = [x for x in new if x not in oldset]

  newset = set(new)
  dellist = [x for x in old if x not in newset]
  
  samelist = [x for x in old if x in newset]
  return (addlist, dellist, samelist)
  
def getCurrentUTCOffsetSeconds():  
  ts = time.time()
  return (datetime.datetime.fromtimestamp(ts) - 
          datetime.datetime.utcfromtimestamp(ts)).total_seconds()
  
def getCurrentUTCOffsetMinutes():
  return getCurrentUTCOffsetSeconds() / 60
  
def iso8601ToDateTime(dateval):
  # 2015-02-25T05:00:00.000Z
  try:
    dtsplit = dateval.split('T')
    datestr = dtsplit[0].split('-')  
    timestr = dtsplit[1].split(':')
    return datetime.datetime(int(datestr[0]), int(datestr[1]), int(datestr[2]), int(timestr[0]), int(timestr[1]))
  except:
    return None

#################################################################
# This function simply gets the current UTC time and formats it
# using the following format: 2017-10-23 17:00:00
#################################################################

def getUTCnowFormatted(appendStr=""):
  strUTCnow = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
  if len(appendStr) > 0 :
    strUTCnow = "{0} {1}".format( strUTCnow, appendStr )
  return strUTCnow

