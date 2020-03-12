#!/usr/bin/env python

import sys
from daemon import Daemon

import main

class LeonardoDaemon(Daemon):
  def run(self):
    argv = sys.argv
    argc = len(argv)

    leonardo = main.Leonardo()
    leonardo.execute(argc, argv)

if __name__ == "__main__":
  stderrLog = '{0}/log/leoDaemonStderr.log'.format( sys.path[0] )
  stdoutLog = '{0}/log/leoDaemonStdout.log'.format( sys.path[0] )
  daemon = LeonardoDaemon('/var/run/leonardo.pid', '/dev/null', stdoutLog, stderrLog )
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    elif 'status' == sys.argv[1]:
      daemon.status()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart|status" % sys.argv[0]
    sys.exit(2)

