import os, errno
import logging

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    f = logging.FileHandler('monitor.log')
    f.setLevel(logging.INFO)
    #stream = logging.StreamHandler()
    #stream.setLevel(logging.INFO)
    logger.addHandler(f)
    return logger