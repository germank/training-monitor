from plugin_mgr import FigureFactory
#from wx.lib.pubsub import Publisher as pub
from signalslot.signal import Signal
import os
from utils import mkdir_p
import datetime
from utils import get_logger
logger = get_logger('model.sessions')


class DataThreadMonitor(object):
    '''
    Contains and represents the a visualizing block for
    a data thread
    '''
    def __init__(self, cfg):
        figure_factory = FigureFactory()
        self.figure = figure_factory.build(cfg)
    
    def get_figure(self):
        return self.figure
    
    def accept_data(self, **kwargs):
        self.figure.accept_data(**kwargs)
        self.figure.draw()
        
    def save(self, outfile):
        self.figure.save(outfile)
        
    def ghost_clone(self, other):
        self.figure.ghost_clone(other.figure)


class SessionManager():
    ''' A Session consist of a collection of DataMonitors
    The SessionManager connects to a DataListener (dl) and sends
    all data that it receives to the corresponding DataThreadMonitor
    in the active Session. 
    '''
    def __init__(self, cfg, dl):
        #signals
        self.session_new = Signal(['session_id', 'session_monitors'])
        self.session_switch = Signal(['session_id'])
        
        self.cfg = cfg
        self.session_counter = 0
        self.sessions = {}
        self.session_id_format = "{uniq_id} - {date} - {time}"
        dl.data_updated.connect(self.on_data_arrived)
        
    def switch_new_session(self):
        self.switch_session(self.new_session())
        
        
    def new_session(self):
        self.session_counter = self.session_counter + 1
        session_id = self.session_id_format.format(uniq_id=self.session_counter,
                                                   date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                                   time=datetime.datetime.now().strftime("%H:%M"))
        self.sessions[session_id] = {} 
        for monitor_name, data_cfg in self.cfg['elements'].iteritems():
                self.sessions[session_id][monitor_name] = DataThreadMonitor(data_cfg) 
        
        #pub.sendMessage("SESSION NEW", (session_id, 
        #                                self.get_session_monitors(session_id)))
        self.session_new.emit(session_id=session_id,
                              session_monitors=self.get_session_monitors(session_id))
        
        return session_id
    
    def get_session_monitors(self, session_id):
        return self.sessions[session_id]
    
    def current_session(self):
        return self.sessions[self.current_session_id]
    
    def switch_session(self, session_id):
        self.current_session_id = session_id
        #pub.sendMessage("SESSION SWICH", session_id)
        self.session_switch.emit(session_id=session_id)
        return session_id
    
    def clone_session(self, session_id):
        other_session = self.get_session_monitors(session_id)
        for monitor_name, monitor in self.current_session().iteritems():
            monitor.ghost_clone(other_session[monitor_name])
    
    def on_data_arrived(self, monitor_name, args, **kwargs):
        try:
            self.current_session()[monitor_name].accept_data(**args)
        except KeyError:
            logger.error('Monitor {0} not found'.format(monitor_name))
        
    def save(self, out_dir):
        for session_id, monitors in self.sessions.iteritems():
                session_out_dir = os.path.join(out_dir, str(session_id))
                mkdir_p(session_out_dir)
                for monitor_name, monitor in monitors.iteritems():
                    monitor.save(os.path.join(session_out_dir, monitor_name+'.png'))