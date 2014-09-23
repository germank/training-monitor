from plugin_mgr import FigureFactory
from wx.lib.pubsub import Publisher as pub

class DataMonitor(object):
    def __init__(self, cfg):
        figure_factory = FigureFactory()
        self.figure = figure_factory.build(cfg)
    
    def get_figure(self):
        return self.figure
    
    def accept_data(self, **kwargs):
        self.figure.accept_data(**kwargs)
        self.figure.draw()


class SessionManager():
    def __init__(self, cfg):
        self.cfg = cfg
        self.session_counter = 0
        self.sessions = {}
        self.switch_session(self.new_session())
        pub.subscribe(self.on_data_arrived, 'DATA')
        
        
    def new_session(self):
        self.session_counter = self.session_counter + 1
        session_id = self.session_counter
        self.sessions[session_id] = {} 
        for monitor_name, data_cfg in self.cfg['elements'].iteritems():
                self.sessions[session_id][monitor_name] = DataMonitor(data_cfg) 
        
        pub.sendMessage("SESSION NEW", (session_id,
                                        self.get_session_monitors(session_id)))
        return session_id
    
    def get_session_monitors(self, session_id):
        return self.sessions[session_id]
    
    def current_session(self):
        return self.sessions[self.current_session_id]
    
    def switch_session(self, session_id):
        self.current_session_id = session_id
        pub.sendMessage("SESSION SWICH", session_id)
        return session_id
    
    def on_data_arrived(self, message):
        action_name, kwargs = message.data
        self.current_session()[action_name].accept_data(**kwargs)