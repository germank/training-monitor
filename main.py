#!/usr/bin/env python
from numpy import arange, sin, pi, append
import matplotlib
import threading
import cherrypy 
import logging
import yaml
import argparse
from collections import defaultdict
from wx.lib.pubsub import Publisher as pub


matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

import wx

class ActionHandler(object):
    def save(self, output_dir):
        self.panel.save(output_dir)
        
class LinePlotPanel(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        wx.Panel.__init__(self, parent)
        self.figure = figure 
        self.canvas = FigureCanvas(self, -1, self.figure.get_figure())
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizerAndFit(self.sizer)
        self.Fit()

    def add_point(self, y, x=None, z=1):
        self.figure.add_point(y, x, z)
        
            
    def draw(self):
        self.figure.draw()
        self.canvas.draw()
    
    def save(self, output_dir):
        self.figure.save(output_dir)


        
class LinePlotHandler(ActionHandler):
    def __init__(self, panel):
        self.panel = panel
        
    def handle_request(self, **kwargs):
        '''
        Handles a request from the HTTP server
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        wx.CallAfter(self.panel.add_point, **kwargs)
    
        

class LinePlotFigure(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        #data container
        #self.data = defaultdict(list)
        #plotted lines
        self.line = {}
        #gui stuff
        self.figure = Figure((6,3))
        self.axes = self.figure.add_subplot(111)
        if 'scale' in kwargs:
            self.axes.set_yscale(kwargs['scale'])
    
    def get_figure(self):
        return self.figure

    def add_point(self, y, x=None, z=1):
        y = float(y)
        print(y)
        #take note of the data
        #self.data[z].append((x,y))
        #plot it
        if not x:
            print z in self.line
            if z in self.line:
                x = self.line[z].get_xdata()[-1] + 1
            else:
                x = 1
            print(x)
            
        try:
            self.line[z].set_xdata(append(self.line[z].get_xdata(), x))
            self.line[z].set_ydata(append(self.line[z].get_ydata(), y))
        except:
            #xs,ys = zip(*self.data[z])
            self.line[z], = self.axes.plot([x],[y])
    
    def draw(self):
        self.axes.relim()
        self.axes.autoscale_view()
        
    
    def save(self, output_dir):
        pass

class DataListener(object):
    def __init__(self):
        pass
    
    @cherrypy.expose
    def index(self, **kwargs):
        if 'data_name' not in kwargs:
            raise Exception('Data name not found')
        data_name = kwargs.pop('data_name')
        pub.sendMessage('DATA', (data_name, kwargs))
            
    def _cp_dispatch(self, vpath):
        assert(len(vpath) == 1)
        cherrypy.request.params['data_name'] = vpath.pop()
        return self

        
        #return "Hello world!"

def start_listening(servercfg):
    cherrypy.config.update(servercfg)
    dl = DataListener()
    cherrypy.quickstart(dl)
    return dl


def create_panel(parent, cfg):
    assert 'type' in cfg, "type keyword missing "\
        "(use to specify the type of panel)"
    #if not offline:
    f = globals()[cfg['type'] + 'Figure'](**(cfg['args'] if 'args' in cfg else {}))
    p = globals()[cfg['type'] + 'Panel'](parent,f, **(cfg['args'] if 'args' in cfg else {}))
    parent.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
    #else:
    #   
    h = globals()[cfg['type'] + 'Handler'](p)
    return h, p


class DataMonitor(object):
    def __init__(self, cfg):
        self.figure = globals()[cfg['type'] + 'Figure'](**(cfg['args'] if 'args' in cfg else {}))
        self.handler = globals()[cfg['type'] + 'Handler'](self.figure) 

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
        for data_name, data_cfg in self.cfg.iteritems():
                self.sessions[session_id][data_name] = DataMonitor(data_cfg) 
        
        pub.sendMessage("SESSION NEW", session_id)
        return session_id
    
    def switch_session(self, session_id):
        self.current_session = session_id
        pub.sendMessage("SESSION SWICH", session_id)
        return session_id
    
    def on_data_arrived(self, message):
        action_name, kwargs = message.data
        
        

class GUISessionController(object):
    def __init__(self, parent, cfg):
        self.parent  = parent
        self.session_listbook = wx.Listbook(self.parent)
        self.cfg = cfg
        self.session_manager = SessionManager(cfg)
        pub.subscribe(self.on_session_new, "SESSION NEW")
        pub.subscribe(self.on_session_switch, "SESSION SWITCH")
    
    def on_session_new(self, message):
        session_id = message.data
        panel = wx.Panel(self.parent)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        self.session_listbook.AddPage(panel, str(session_id))
        for data_name, action_cfg in self.cfg.iteritems():
            panel.sizer.add(create_panel(self.session_listbook, action_cfg), 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND) 
        return session_id
    
    def on_session_switch(self, message):
        #do nothing
        pass
    
    def on_data_arrived(self, message):
        tid, 
        
class GUIController(object):
    def __init__(self, app, cfg):
        fr = wx.Frame(None, title='Training Monitor')
        panel = wx.Panel(fr)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.session_controller = GUISessionController(panel, cfg)
        
        handlers = {}
        for data_name, cfg in config['elements'].iteritems():
            h, p = create_panel(panel, cfg)
            handlers[data_name] = h
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
                        args=(config['cherrypy'] if 'cherrypy' in config 
                                                 else {}))
    thread.setDaemon(True)
    thread.start()
    
    try:
        app.MainLoop()
    except KeyboardInterrupt:
        controller.save(args.output_dir)
    
    
    
