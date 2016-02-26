import logging
import sys
import threading
import time

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT, stream=sys.stderr)

logger = logging.getLogger('test')

_GLOBAL_LOCK = threading.Lock()
print('Global Lock: {}'.format(_GLOBAL_LOCK))


class Process(object):
    
    def __init__(self, a):
        self.a = a
        
    def add(self, value):
        with _GLOBAL_LOCK:
            logger.info("Adding {} to {}".format(value, self.a))
            print("{}: Adding {} to {}".format(time.asctime(), value, self.a))
            self.a += value
            time.sleep(2)
            
    def subtract(self, value):
        
        with _GLOBAL_LOCK:
            logger.info("Subtracting {} from {}".format(value, self.a))
            print("{}: Subtracting {} from {}".format(time.asctime(), value, self.a))
            self.a -= value
            time.sleep(2)