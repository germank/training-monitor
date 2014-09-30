#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')

import threading
import yaml
import argparse

#dynamically load visualizing classes from the visualizers package
from plugin_mgr import load_plugins, FigurePanelFactory, FigureMemoryPanelFactory
load_plugins('visualizers')

from listening_service import start_listening, stop_listening, \
    server_block, DataListener
from model.sessions import SessionManager

import wx
#from wx.lib.pubsub import Publisher as pub


class GUISessionController(object):
    def __init__(self, parent, cfg, dl):
        self.parent  = parent
        self.session_listbook = wx.Listbook(self.parent)
        self.parent.sizer.Add(self.session_listbook, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        self.cfg = cfg
        self.session_manager = SessionManager(cfg, dl)
        self.session_manager.session_new.connect(self.on_session_new)
        self.session_manager.switch_new_session()
    
    def on_session_new(self, session_id, session_monitors, **kwargs):
        panel = wx.Panel(self.parent)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetBackgroundColour((0,0,0))
        self.session_listbook.AddPage(panel, str(session_id))
        #for monitor_name, action_cfg in self.cfg.iteritems():
        for monitor_name, monitor in session_monitors.iteritems():
            monitor_cfg = self.cfg['elements'][monitor_name]
            panel_factory = FigurePanelFactory()
            p = panel_factory.build(panel, monitor.get_figure(), monitor_cfg)
            panel.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        panel.SetSizer(panel.sizer)
    


class GUIController(object):
    def __init__(self, app, cfg, dl):
        fr = wx.Frame(None, title='Training Monitor')
        panel = wx.Panel(fr)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = fr.CreateToolBar()
        new_session_btn = toolbar.AddLabelTool(wx.ID_ANY, 'New Session', wx.Bitmap('img/plus.png'))
        toolbar.Realize()

        #self.Bind(wx.EVT_TOOL, self.OnQuit, qtool)
        self.session_controller = GUISessionController(panel, cfg, dl)
        
        #handlers = {}
        #for monitor_name, cfg in config['elements'].iteritems():
        #    h, p = create_panel(panel, cfg)
        #    handlers[monitor_name] = h
        panel.SetSizerAndFit(panel.sizer)
        fr.Show()
        fr.Maximize()
        
    def save(self, outdir):
        self.session_manager.save(outdir)
        

class ConsoleController(object):
    def __init__(self, cfg, dl):
        self.cfg = cfg
        self.session_manager = SessionManager(cfg, dl)
        self.session_manager.session_new.connect(self.on_session_new)
        self.session_manager.switch_new_session()
        
    def save(self, outdir):
        self.session_manager.save(outdir)
        
    def on_session_new(self, session_id, session_monitors, **kwargs):
        #for monitor_name, action_cfg in self.cfg.iteritems():
        for monitor_name, monitor in session_monitors.iteritems():
            monitor_cfg = self.cfg['elements'][monitor_name]
            panel_factory = FigureMemoryPanelFactory()
            p = panel_factory.build(monitor.get_figure(), monitor_cfg)
            #we throw away p?

if __name__ == "__main__":
    ap = argparse.ArgumentParser('Training Monitor')
    ap.add_argument('config_yml', help='yml file with the monitor configuration')
    ap.add_argument('-G', '--no-gui', action='store_true', default=False)
    ap.add_argument('-s', '--save-output', default=None)
    
    args = ap.parse_args()
    
    config = yaml.load(file(args.config_yml))
    
    


    dl = DataListener()
    
    #Start the HTTP server
    start_listening(config.get('cherrypy',{}),dl)
    
    controller = None
    try:
        if args.no_gui:
            controller = ConsoleController(config, dl)
            server_block()
        else:
            app = wx.PySimpleApp()
            controller = GUIController(app, config, dl)
            app.MainLoop()
    finally:
        #Close the HTTP connection
        stop_listening()
        
        if args.save_output and controller:
            print "Saving graphics to {0}...".format(args.save_output),
            controller.save(args.save_output)
            print "Done"
    
    
    
