import cherrypy 
from wx.lib.pubsub import Publisher as pub

class DataListener(object):
    def __init__(self):
        pass
    
    @cherrypy.expose
    def index(self, **kwargs):
        if 'monitor_name' not in kwargs:
            raise Exception('Data name not found')
        monitor_name = kwargs.pop('monitor_name')
        pub.sendMessage('DATA', (monitor_name, kwargs))
            
    def _cp_dispatch(self, vpath):
        assert(len(vpath) == 1)
        cherrypy.request.params['monitor_name'] = vpath.pop()
        return self

        
        #return "Hello world!"

def start_listening(servercfg):
    cherrypy.config.update(servercfg)
    dl = DataListener()
    cherrypy.quickstart(dl)
    return dl