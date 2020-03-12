#! /usr/bin/python

import time
import datetime

class Timeout:
  def __init__(self, timeout = 0):
    self.lastReset = time.time()
    self.timeout = timeout

  def getTimeRemainingSecs(self):
    currentTime = time.time()
    timeDiff = ((self.lastReset+self.timeout) - currentTime)
    if ( timeDiff < 0 ) : timeDiff = 0
#    print "getTimeRemaining-->", int(timeDiff), "curr:", currentTime, "lastReset:", self.lastReset, "timeout:", self.timeout
    return ( timeDiff )

  def hasElapsed(self):
    currentTime = time.time()

    # Errant case where the time has changed behind our last review.
    if currentTime < self.lastReset:
      return True

    # if our time has elapsed
    if (self.lastReset + self.timeout) < currentTime:
      return True
    else:
      return False

  def reset(self):
    self.lastReset = time.time()

  def setTimeout(self, timeout):
    self.timeout = timeout

  def elapse(self):
    self.lastReset = 0


class Interval(Timeout):
  def __init__(self, timeout = 0):
    Timeout.__init__(self, timeout)

  def hasElapsed(self):
    retval = Timeout.hasElapsed(self)

    # if our time has elapsed
    if retval:
      self.reset()

    return retval

class DailyEvent:
  def __init__(self, timeOfDay = None):
    self.setTimeOfDay(timeOfDay)
    self.lastCheck = datetime.datetime.min

  def getInfo(self): # For debugging only.
    currentDate = datetime.datetime.now()
    if self.lastCheck <= self.nextEventDate and self.nextEventDate < currentDate:
      tempVal = True
    else:
      tempVal = False
    #print "DailyEvent Info:", str(currentDate), str(self.lastCheck), str(self.nextEventDate), tempVal

  def hasElapsed(self):
    currentDate = datetime.datetime.now()
    #print "checking elapsed", str(currentDate), str(self.lastCheck), str(self.nextEventDate)

    if self.lastCheck <= self.nextEventDate and self.nextEventDate < currentDate:
      self._putNextEventDateIntoFuture()
      retval = True
    else:
      retval = False

    self.lastCheck = currentDate
    return retval

  def setTimeOfDay(self, timeOfDay):
    self.nextEventDate = datetime.datetime.now()
    if timeOfDay is not None:
      self.nextEventDate = self.nextEventDate.replace(hour=timeOfDay.hour, minute=timeOfDay.minute, second=timeOfDay.second)
    self._putNextEventDateIntoFuture()

  def _putNextEventDateIntoFuture(self):
    while self.nextEventDate < datetime.datetime.now():
      self.nextEventDate += datetime.timedelta(1)

  def trigger(self):
    self.nextEventDate -= datetime.timedelta(1)
    self.lastCheck = self.nextEventDate

