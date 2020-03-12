#! /usr/bin/python

import threading
# import sqlite3

import networkConstants
import dbUtils
import plugins
from collections import OrderedDict

import logsystem
log = logsystem.getLogger()
# import copy
import time

class NetworkManager:
  def __init__(self, directory):
    self.lock = threading.RLock()
    self.directory = directory

    self.plugins = {}

    i = 0
    pluginsList = plugins.getPlugins("system/networks")
    strNetTypeNames = "Loading {0} Network Type Plugins: ".format( len( pluginsList) )
    while i < len( pluginsList ) :
      strNetTypeNames = "{0}{1}, ".format( strNetTypeNames, pluginsList[i]['name'] )
      i = i + 1
    log.info( strNetTypeNames )

    # Load network types. Add new supported networks as they come
    for plugin in plugins.getPlugins("system/networks"):
      try:
        loadedPlugin = plugins.loadPlugin(plugin)
        self.plugins[loadedPlugin.networkType] = { 'plugin' : plugin, 'loadedPlugin' : loadedPlugin }
        self.directory.addNetworkObjectType(loadedPlugin.networkType, loadedPlugin.networkTypeName)
      except Exception, e:
        strBuf = "ERROR - Loading network from directory {0}. Error:{1})".format(plugin["name"], e )
        log.exception(strBuf)
    log.debug(self.plugins)
    self.loadNetworks()


  def loadNetworks(self):
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("select * from networks")
    for networkInfo in cur.fetchall():
      networkType = networkInfo["networkType"]
      if networkType in self.plugins :
        plugin = plugins.loadPlugin(self.plugins[networkType]['plugin'])
        strDebug = "Starting NetworkInfo: {0}, {1}, {2}, {3}".format( networkInfo["networkType"], networkInfo["name"], networkInfo["description"], networkInfo["connectionInfo"] )
        log.info( strDebug )
        network = plugin.Network(self, networkInfo['name'], networkInfo['description'], networkInfo['connectionInfo'] )
        if network is not None:
          self.directory.addNetworkObject(network.getName(), network)
      else :
        strError = "Error starting network: {0},{1}".format( networkInfo['networkType'], networkInfo['name'] )
        log.exception( strError )
    conn.close()

  def getNetworkTypes(self):
    retval = {}
    retval['types'] = dict( self.directory.getNetworkObjectTypes() )
    retval['ports'] = networkConstants.networkPortSettings
    return retval

  def getNetworks(self):
    with self.lock:
      keys = self.directory.getNetworkObjectKeys()
      retval = OrderedDict()
      for key in keys:
        network = self.directory.getNetworkObject(key)
        if network is not None:
          retval[key] = { "typeName": network.getNetworkTypeName(),
                          "name": network.getName(),
                          "connection": network.getConnectionInfo(),
                          "description": network.getDescription() }
      return retval

  def setNetworks(self, newNetworks):
    uniqueNames = []

    # update database
    conn = dbUtils.getSystemDatabaseConnection()
    try:
      cur = conn.cursor()
      cur.execute("delete from networks")
      for network in newNetworks:

        # guarantee name uniqueness
        if network["name"] in uniqueNames:
          continue
        uniqueNames.append(network["name"])

        networkTypes = self.directory.getNetworkObjectTypes()
        networkType = ""
        for key in networkTypes.keys():
          if networkTypes[key] == network["typeName"]:
            networkType = key
            break

        cur.execute("INSERT INTO networks VALUES (?, ?, ?, ?)", (networkType, network["name"], network["connection"], network["description"]))

      conn.commit()

      self.directory.getSystemObject().reinitialize() # restarts the system
    except:
      log.exception("Error in setNetworks")
    finally:
      conn.close()
