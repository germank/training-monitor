#!/usr/bin/env python
from numpy import arange, sin, pi, append
import matplotlib
matplotlib.use('WXAgg')
import threading
import cherrypy 
import logging
import yaml
import argparse
from collections import defaultdict
from wx.lib.pubsub import Publisher as pub

#Import pluggable visualizers
from visualizers.LinePlot import *



import wx

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


#def create_panel(parent, cfg):
#    assert 'type' in cfg, "type keyword missing "\
#        "(use to specify the type of panel)"
#    #if not offline:
#    f = globals()[cfg['type'] + 'Figure'](**(cfg['args'] if 'args' in cfg else {}))
#    
#    #else:
#    #   
#    #h = globals()[cfg['type'] + 'Handler'](p)
#    return p


class DataMonitor(object):
    def __init__(self, cfg):
        self.figure = globals()[cfg['type'] + 'Figure'](**(cfg['args'] if 'args' in cfg else {}))
    
    def get_figure(self):
        return self.figure
    
    def accept_data(self, **kwargs):
        self.figure.accept_data(**kwargs) 

class SessionListbook(wx.Listbook):
    def __init__(self, parent):
        wx.Listbook.__init__(self, parent)


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
        

class GUISessionController(object):
    def __init__(self, parent, cfg):
        pub.subscribe(self.on_session_new, "SESSION NEW")
        pub.subscribe(self.on_session_switch, "SESSION SWITCH")
        self.parent  = parent
        self.session_listbook = wx.Listbook(self.parent)
        self.parent.sizer.Add(self.session_listbook, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        self.cfg = cfg
        self.session_manager = SessionManager(cfg)
    
    def on_session_new(self, message):
        session_id,session_monitors = message.data  
        panel = wx.Panel(self.parent)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetBackgroundColour((0,0,0))
        self.session_listbook.AddPage(panel, str(session_id))
        #for monitor_name, action_cfg in self.cfg.iteritems():
        for monitor_name, monitor in session_monitors.iteritems():
            print monitor_name
            monitor_cfg = self.cfg['elements'][monitor_name]
            p = globals()[monitor_cfg['type'] + 'Panel'](panel, 
                                                 monitor.get_figure(),
                                                  **(monitor_cfg.get('args',{})))
            panel.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        panel.SetSizer(panel.sizer)
        return session_id
    
    def on_session_switch(self, message):
        #do nothing
        pass
    
    def on_data_arrived(self, message):
        pass
        
class GUIController(object):
    def __init__(self, app, cfg):
        fr = wx.Frame(None, title='Training Monitor')
        panel = wx.Panel(fr)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = fr.CreateToolBar()
        new_session_btn = toolbar.AddLabelTool(wx.ID_ANY, 'New Session')
        toolbar.Realize()

        #self.Bind(wx.EVT_TOOL, self.OnQuit, qtool)
        self.session_controller = GUISessionController(panel, cfg)
        
        #handlers = {}
        #for monitor_name, cfg in config['elements'].iteritems():
        #    h, p = create_panel(panel, cfg)
        #    handlers[monitor_name] = h
        panel.SetSizerAndFit(panel.sizer)
        fr.Show()
        fr.Maximize()
        

    

if __name__ == "__main__":
    ap = argparse.ArgumentParser('Training Monitor')
    ap.add_argument('config_yml', help='yml file with the monitor configuration')
    ap.add_argument('--offline', action='store_true', default=False)
    ap.add_argument('--output-dir', default='.')
    
    args = ap.parse_args()
    
    config = yaml.load(file(args.config_yml))
    
     
    #Create the GUI
    app = wx.PySimpleApp()
    if args.offline:
        controller = ConsoleController(app)
    else:
        controller = GUIController(app, config)
        
    #Start the HTTP server
    thread=threading.Thread(target=start_listening, 
                        args=(config.get('cherrypy',{}),))
    thread.setDaemon(True)
    thread.start()
    
    try:
        app.MainLoop()
    except KeyboardInterrupt:
        controller.save(args.output_dir)
    
    
    
