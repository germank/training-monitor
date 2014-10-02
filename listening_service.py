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

class ListeningService(object):
    def __init__(self, servercfg, dl):
        self.server_started = Signal()
        self.server_stopped = Signal()
        
        self.servercfg = servercfg
        self.dl = dl
        
        cherrypy.engine.subscribe('start', self.on_start)
        cherrypy.engine.subscribe('stop', self.on_stop)
    
    def on_start(self):
        self.server_started.emit()
    
    def on_stop(self):
        self.server_stopped.emit()
        
    def start(self):
        cherrypy.config.update(self.servercfg)
        cherrypy.tree.mount(self.dl, "", None)
        
        if hasattr(cherrypy.engine, "signal_handler"):
            cherrypy.engine.signal_handler.subscribe()
        if hasattr(cherrypy.engine, "console_control_handler"):
            cherrypy.engine.console_control_handler.subscribe()
        
        cherrypy.engine.start()
    

    def stop(self):
        cherrypy.engine.stop()
        
    def exit(self):
        cherrypy.engine.exit()

    def block(self):
        cherrypy.engine.block()