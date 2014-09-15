#!/usr/bin/env python
from numpy import arange, sin, pi
import matplotlib
import threading
import cherrypy 
import logging
import yaml
import argparse
from collections import defaultdict
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

import wx


class LinePlotPanel(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #data container
        self.data = defaultdict(list)
        #plotted lines
        self.line = {}
        #gui stuff
        self.figure = Figure((6,3))
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizerAndFit(self.sizer)
        self.Fit()

    def add_point(self, x, y, z=1):
        #take note of the data
        self.data[z].append((x,y))
        #plot it
        try:
            self.line[z].set_data(*zip(*self.data[z]))
        except:
            xs,ys = zip(*self.data[z])
            self.line[z], = self.axes.plot(xs,ys)
        #refresh view
        self.axes.relim()
        self.axes.autoscale_view()
        self.canvas.draw()
        
    def handle_request(self, **kwargs):
        '''
        Handles a request from the HTTP server
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        wx.CallAfter(self.add_point, **kwargs)
        

class DataListener(object):
    def __init__(self, init_handlers=None):
        self.handlers = {}
        if init_handlers:
            self.handlers.update(init_handlers);
    
    def add_handler(self, action_name, handler):
        self.handlers[action_name] = handler
        
    @cherrypy.expose
    def index(self, **kwargs):
        if 'action_name' not in kwargs:
            raise Exception('Action name not found')
        action_name = kwargs.pop('action_name')
        if action_name not in self.handlers:
            raise Exception('No handler registered for ' + action_name)
        
        self.handlers[action_name].handle_request(**kwargs)
            
    def _cp_dispatch(self, vpath):
        assert(len(vpath) == 1)
        cherrypy.request.params['action_name'] = vpath.pop()
        return self

        
        #return "Hello world!"

def start_listening(handlers, servercfg):
    cherrypy.config.update(servercfg)
    cherrypy.quickstart(DataListener(handlers))


def create_panel(parent, cfg):
    assert 'type' in cfg, "type keyword missing "\
        "(use to specify the type of panel)"
    return globals()[cfg['type']](parent)


if __name__ == "__main__":
    ap = argparse.ArgumentParser('Training Monitor')
    ap.add_argument('config_yml', help='yml file with the monitor configuration')
    
    args = ap.parse_args()
    
    config = yaml.load(file(args.config_yml))
    
    
    #Create the GUI
    app = wx.PySimpleApp()
    fr = wx.Frame(None, title='Training Monitor')
    panel = wx.Panel(fr)#LinePlotPanel(fr)
    panel.sizer = wx.BoxSizer(wx.VERTICAL)
    handlers = {}
    for action_name, cfg in config['elements'].iteritems():
        p = create_panel(panel, cfg)
        handlers[action_name] = p
        panel.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
    panel.SetSizerAndFit(panel.sizer)
    fr.Show()
    fr.Maximize()
    
    #Start the HTTP server
    thread=threading.Thread(target=start_listening, 
                            args=(handlers,
                                  config['cherrypy'] if 'cherrypy' in config 
                                                     else {}))
    thread.setDaemon(True)
    thread.start()
    
    #Go!
    app.MainLoop()
    
    
