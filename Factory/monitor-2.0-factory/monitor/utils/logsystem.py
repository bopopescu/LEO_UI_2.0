#! /usr/bin/python

import logging
import logging.handlers
import os
import sys

# The purpose of this class is to try to get the crash "dumps" into the leonardo log file. So we will redirect all
# stdout AND stderr through logger.
# class StreamToLogger(object):
#   """
#   Fake file-like stream object that redirects writes to a logger instance.
#   """
#   def __init__(self, logger, log_level=logging.INFO):
#      self.logger = logger
#      self.log_level = log_level
#      self.linebuf = ''
#
#   def write(self, buf):
#      for line in buf.rstrip().splitlines():
#         self.logger.log(self.log_level, line.rstrip())


# create logger
_logger = logging.getLogger('')

_logger.setLevel(logging.DEBUG)

# We need to make sure the log folder actually exists.

# create file handler which logs even debug messages
strLeoLogPath = '{0}/log'.format( sys.path[0] )

if os.path.exists( strLeoLogPath ) == False:
  oldUmask = os.umask( 0 )
  os.mkdir( strLeoLogPath, 0777 )
  os.umask( oldUmask )

strLeoLogFile = "{0}/leonardo.log".format( strLeoLogPath )
_fileHandler = logging.handlers.RotatingFileHandler(strLeoLogFile, maxBytes=1000000, backupCount=10)
_fileHandler.setLevel(logging.NOTSET)

# create console handler with a higher log level
_consoleHandler = logging.StreamHandler()
_consoleHandler.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
# logging.basicConfig(format="%(threadName)s:%(message)s")
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(threadName)s:%(filename)s:%(funcName)s:%(lineno)d %(message)s')
# formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d %(message)s')
_fileHandler.setFormatter(_formatter)
_consoleHandler.setFormatter(_formatter)

# add the handlers to the logger
_logger.addHandler(_fileHandler)
_logger.addHandler(_consoleHandler)

# To Redirect STDOUT - For debugging on actual LEO
# stdout_logger = logging.getLogger('STDOUT')
# sl = StreamToLogger(stdout_logger, logging.WARN)
# sys.stdout = sl

# Do not redirect STDERR in PYCHARM
#if not "PYCHARM_HOSTED" in os.environ:
#  stderr_logger = logging.getLogger('STDERR')
#  sl = StreamToLogger(stderr_logger, logging.ERROR)
#  sys.stderr = sl

def getLogger():
  return _logger

def shutdown():
  logging.shutdown()
