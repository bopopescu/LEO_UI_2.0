#! /usr/bin/python

import threading
from collections import OrderedDict
import logsystem
log = logsystem.getLogger()

# This class is just a lookup of objects of a specific type
# it is thread safe
class ObjectDirectory:
  def __init__(self):
    self.lock = threading.RLock()

    self.systemObject = None
    self.alarmManager = None
    self.E2AlarmManager = None
    self.loggingManager = None
    self.networkManager = None
    self.deviceManager = None

    self.resetDirectory()

  def resetDirectory(self):
    with self.lock:
      self.networkObjects = OrderedDict()
      self.networkObjectTypes = OrderedDict()
      self.deviceObjects = OrderedDict()
      self.deviceObjectTypes = OrderedDict()

  ################################
  # Alarm Objects
  ################################
  def getAlarmManager(self):
    return self.alarmManager

  def setAlarmManager(self, alarmManager):
    self.alarmManager = alarmManager

  ################################
  # Logging Object
  ################################
  def getLoggingManager(self):
    return self.loggingManager

  def setLoggingManager(self, loggingManager):
    self.loggingManager = loggingManager

  ################################
  # System Object
  ################################
  def getSystemObject(self):
    return self.systemObject

  def setSystemObject(self, systemObject):
    self.systemObject = systemObject

  ################################
  # Network Manager
  ################################
  def getNetworkManager(self):
    return self.networkManager

  def setNetworkManager(self, networkManager):
    self.networkManager = networkManager

  ################################
  # Device Manager
  ################################
  def getDeviceManager(self):
    return self.deviceManager

  def setDeviceManager(self, deviceManager):
    self.deviceManager = deviceManager

  ################################
  # Network Objects
  ################################
  # This will make thread safe calls but will in lock itself
  # do not use this internal - this is meant for JSON
  def getNetworkObjects(self):
    retval = OrderedDict()
    keys = self.getNetworkObjectKeys()
    for key in keys:
      network = self.getNetworkObject(key)
      if network is not None:
        retval[key] = network
    return retval

  def getNetworkObjectKeys(self):
    with self.lock:
      return self.networkObjects.keys()

  def getNetworkObject(self, id):
    with self.lock:
      if id in self.networkObjects:
        return self.networkObjects[id]
      return None

  def addNetworkObject(self, id, obj):
    with self.lock:
      if not id in self.networkObjects:
        self.networkObjects[id] = obj
      else:
        raise KeyError

  def removeNetworkObject(self, id):
    with self.lock:
      if id in self.networkObjects:
        del self.networkObjects[id]
      else:
        raise KeyError

  ################################
  # Network Object Types
  ################################
  def getNetworkObjectTypes(self):
    with self.lock:
      return self.networkObjectTypes;

  def addNetworkObjectType(self, id, obj):
    with self.lock:
      if not id in self.networkObjectTypes:
        self.networkObjectTypes[id] = obj
      else:
        raise KeyError

  def removeNetworkObjectType(self, id):
    with self.lock:
      if id in self.networkObjectTypes:
        del self.networkObjectTypes[id]
      else:
        raise KeyError

  ################################
  # Device Objects
  ################################
  # This will make thread safe calls but will in lock itself
  # do not use this internal - this is meant for JSON
  def getDeviceObjects(self):
    retval = OrderedDict()
    keys = self.getDeviceObjectKeys()
    for key in keys:
      device = self.getDeviceObject(key)
      if device is not None:
        retval[key] = device
    return retval

  def getDeviceObjectKeys(self):
    with self.lock:
      return self.deviceObjects.keys()

  def getDeviceObject(self, id):
    with self.lock:
      if id in self.deviceObjects:
        return self.deviceObjects[id]
      return None

  def addDeviceObject(self, id, obj):
    with self.lock:
      if not id in self.deviceObjects:
        self.deviceObjects[id] = obj
      else:
        raise KeyError

  def removeDeviceObject(self, id):
    with self.lock:
      if id in self.deviceObjects:
        del self.deviceObjects[id]
      else:
        raise KeyError

  ################################
  # Device Object Types
  ################################
  def getDeviceObjectTypes(self):
    with self.lock:
      return self.deviceObjectTypes;

  def addDeviceObjectType(self, id, obj):
    with self.lock:
      if not id in self.deviceObjectTypes:
        self.deviceObjectTypes[id] = obj
      else:
        raise KeyError

  def removeDeviceObjectType(self, id):
    with self.lock:
      if id in self.deviceObjectTypes:
        del self.deviceObjectTypes[id]
      else:
        raise KeyError





