#! /usr/bin/python

import Queue

class RRPriorityQueue(Queue.Queue):
  '''Variant of Queue that retrieves open entries in priority order (lowest first)
  but allows highest priorities to be skipped.

  '''
  
  def _init(self, priorityOrder):
    if priorityOrder is None:
      raise TypeError

    self._queue = []
    
    self._priorityOrder = priorityOrder
    self._orderIdx = len(self._priorityOrder) + 1
  
  def _qsize(self, len=len):
    return len(self._queue)
  
  def _put(self, item):
    # This restricts the input to only unique items
    for queueItem in self._queue:
      if queueItem == item:
        # however, if the new request has a higher priority, update it
        if queueItem.priority < item.priority:
          queueItem.priority = item.priority
        return
    self._queue.append(item)
  
  def _get(self):
    if (len(self._queue) == 0):
      raise IndexError
    
    retVal = None
  
    # change the order index for the priority order list  
    self._orderIdx = self._orderIdx + 1
    if self._orderIdx >= len(self._priorityOrder):
      self._orderIdx = 0
      
    # the priority we are interested in and the highest value
    # in case we don't find one at our priority 
    filterPriority = self._priorityOrder[self._orderIdx]
    highest = self._queue[0]
    
    # look for one of our priority but saving highest priority (lowest number)
    for item in self._queue:
      priority = item.priority
      if priority == filterPriority:
        # we found our item
        retVal = item
        break
      if highest.priority > item.priority:
        highest = item
        
    # if we didn't find our item, the return the highest
    if retVal is None:
      retVal = highest
    
    self._queue.remove(retVal)
    return retVal
