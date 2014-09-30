import cherrypy 
#from wx.lib.pubsub import Publisher as pub
from signalslot.signal import Signal

class DataListener(object):
    '''
    HTTP Service that listens to requests and forwards them
    upwards through the data_updated Signal
    '''
    def __init__(self):
        self.data_updated = Signal(['monitor_name', 'args'])
    
    @cherrypy.expose
    def index(self, **kwargs):
        if 'monitor_name' not in kwargs:
            raise Exception('Data name not found')
        monitor_name = kwargs.pop('monitor_name')
        #pub.sendMessage('DATA', (monitor_name, kwargs))
        self.data_updated.emit(monitor_name=monitor_name,
                               args=kwargs)
            
    def _cp_dispatch(self, vpath):
        assert(len(vpath) == 1)
        cherrypy.request.params['monitor_name'] = vpath.pop()
        return self

        
        #return "Hello world!"

def start_listening(servercfg, dl):
    cherrypy.config.update(servercfg)
    cherrypy.tree.mount(dl, "", None)
    
    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()
    
    #cherrypy.quickstart(dl)
    cherrypy.engine.start()
    

def stop_listening():
    cherrypy.engine.stop()
    cherrypy.engine.exit()

def server_block():
    cherrypy.engine.block()