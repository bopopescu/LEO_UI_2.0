#! /usr/bin/python

import imp
import os
import sys

def getPlugins(pluginDirectory):
  plugins = []
  pluginDirectory = os.path.join(sys.path[0], pluginDirectory)
  possibleplugins = os.listdir(pluginDirectory)
  for folder in possibleplugins:
    location = os.path.join(pluginDirectory, folder)
    if os.path.isdir(location) : # If a folder
      namedLoadableFile = "__{0}__.py".format( folder ) # Default to a file named the same as the folder (__folder__.py)
      moduleName = ""
      if namedLoadableFile in os.listdir(location) :
        moduleName = "__{0}__".format( folder )
      elif "__init__.py" in os.listdir(location) : # if no named loadable module, look for __init__.py
        moduleName = "__init__"
      if len( moduleName ) > 0 :
        info = imp.find_module(moduleName, [location])
    #    print "Location: ", [location]
        plugins.append({"name": folder, "info": info, "moduleName": moduleName })
#    info[0].close()
  return plugins

def loadPlugin(plugin):
  fp = plugin['info'][0]
  path = plugin['info'][1]
  description = plugin['info'][2]
#  fp, path, description = imp.find_module("__init__", path )
#  tmp = imp.load_source("__init__", os.path.dirname(path) )
#  strDebug = "loadPlugin; plugin-->{0}".format( plugin )
#  print strDebug
  imp.acquire_lock()
  tmp = imp.load_module(plugin['moduleName'], fp, path, description )
  imp.release_lock()
#  tmp = imp.load_module("__init__", *plugin["info"])
#  plugin["info"][0].close()
#  print "Plugin Info: ", plugin['info']
  return tmp
