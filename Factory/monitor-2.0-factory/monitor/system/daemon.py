#!/usr/bin/env python

import sys, os, time, atexit, errno
from signal import SIGINT, SIGTERM

class Daemon:
  """
  A generic daemon class.
  
  Usage: subclass the Daemon class and override the run() method
  """
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    self.stdin = stdin
    self.stdout = stdout
    self.stderr = stderr
    self.pidfile = pidfile
  
  def daemonize(self):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced 
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    """
    try: 
      pid = os.fork()
      if pid > 0:
        # exit first parent
        sys.exit(0) 
    except OSError, e: 
      sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1)
  
    # decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 
  
    # do second fork
    try: 
      pid = os.fork() 
      if pid > 0:
        # exit from second parent
        sys.exit(0) 
    except OSError, e: 
      sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1) 
  
    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = file(self.stdin, 'r')
    so = file(self.stdout, 'a+')
    se = file(self.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
  
    # write pidfile
    atexit.register(self.delpid)
    pid = str(os.getpid())
    file(self.pidfile,'w+').write("%s\n" % pid)
  
  def delpid(self):
    if os.path.exists(self.pidfile):
      os.remove(self.pidfile)

  def start(self):
    """
    Start the daemon
    """
    # Check for a pidfile to see if the daemon already runs
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None


    if pid:
      try:
        os.kill(pid, 0)
      except OSError:
        err = sys.exc_info()[1]
        if err.errno == errno.ESRCH:
          # ESRCH == No such process
          message = "pidfile %s already exist but no active process.\n"
          sys.stderr.write(message % self.pidfile)
          self.delpid()
      else:
        message = "pidfile %s already exist. Daemon already running?\n"
        sys.stderr.write(message % self.pidfile)
        sys.exit(1)
  
    # Start the daemon
    self.daemonize()
    self.run()

  def stop(self):
    """
    Stop the daemon
    """
    # Get the pid from the pidfile
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None
  
    if not pid:
      message = "pidfile %s does not exist. Daemon not running?\n"
      sys.stderr.write(message % self.pidfile)
      return # not an error in a restart

    # Try killing the daemon process  
    self.delpid()
    try:
      os.kill(pid, SIGINT)
      count = 0
      while count < 50:
        os.kill(pid, 0)
        time.sleep(0.1)
        count = count + 1
      os.kill(pid, SIGTERM)
    except OSError:
      err = sys.exc_info()[1]
      if err.errno != errno.ESRCH:
        print "OS Error", err,
        sys.exit(1)
    


  def restart(self):
    """
    Restart the daemon
    """
    self.stop()
    self.start()
    
  def status(self):
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None

    if pid:
      try:
        os.kill(pid, 0)
      except OSError:
        err = sys.exc_info()[1]
        if err.errno != errno.ESRCH:
          sys.stdout.write("Daemon is running.\n")
          sys.exit(0)
      else:
        sys.stdout.write("Daemon is running.\n")
        sys.exit(0)

    sys.stderr.write("Daemon is not running.\n")
    sys.exit(1)
          
  def run(self):
    """
    You should override this method when you subclass Daemon. It will be called after the process has been
    daemonized by start() or restart().
    """
