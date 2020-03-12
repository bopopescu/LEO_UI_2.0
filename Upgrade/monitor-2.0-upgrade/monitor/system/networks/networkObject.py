#! /usr/bin/python

import threading
import Queue

import datetime
from collections import OrderedDict
import dbUtils
import auditTrail

import logsystem
log = logsystem.getLogger()

import networkConstants
import RRPriorityQueue

# TODO: switch this from a thread is a to a thread has a relationship
class NetworkObject():
  def __init__(self, networkManager, name, description, connectionInfo, networkType, networkTypeName ):
    self.networkManager = networkManager
    self.name = name
    self.connectionInfo = connectionInfo
    self.description = description
    self.networkType = networkType
    self.networkTypeName = networkTypeName

    self.lock = threading.RLock()
    self.requestQueue = RRPriorityQueue.RRPriorityQueue([1,2,1,3,1,2,1,4,1,2,1,3,1,2,1])
    self.completedQueue = Queue.Queue()


    self.stopNetwork = False
    strThreadName = '{0}'.format( name )
    self.thread = threading.Thread(target=self.run,name=strThreadName)

    self._alarms = OrderedDict()


  def __del__(self):
    self.stop();

  def getNetworkManager(self):
    return self.networkManager

  def getName(self):
    return self.name

  def getDescription(self):
    return self.description

  def getConnectionInfo(self):
    return self.connectionInfo

  def getNetworkType(self):
    return self.networkType

  def getNetworkTypeName(self):
    return self.networkTypeName

  def putNetworkTransaction(self, transaction):
    with self.lock:
      self.requestQueue.put(transaction)

  def getCompletedNetworkTransaction(self):
    with self.lock:
      if self.completedQueue.empty():
        return None
      return self.completedQueue.get()

  def start(self):
    self.stopNetwork = False
    strThreadName = '{0}'.format( self.name )
    self.thread = threading.Thread(target=self.run,name=strThreadName)
    # print "Network Object START = {0}".format(self.thread.getName())
    self.thread.start()

  def stop(self):
    if self.thread is not None:
      if self.thread.isAlive():
        log.info("Stopping " + self.name)
        self.stopNetwork = True
        try:
          self.thread.join()
        except Exception:
          log.exception("Exception when stopping thread " + self.name)


  def restart(self):
    self.stop()
    self.start()

  def run(self):
    raise NotImplementedError

