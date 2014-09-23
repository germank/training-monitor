#!/usr/bin/env python
import matplotlib
matplotlib.use('WXAgg')

import threading
import yaml
import argparse

#dynamically load visualizing classes from the visualizers package
from plugin_mgr import load_plugins, FigurePanelFactory
load_plugins('visualizers')

from listening_service import start_listening
from model.sessions import SessionManager

import wx
from wx.lib.pubsub import Publisher as pub


class GUISessionController(object):
    def __init__(self, parent, cfg):
        pub.subscribe(self.on_session_new, "SESSION NEW")
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
            panel_factory = FigurePanelFactory()
            p = panel_factory.build(panel, monitor.get_figure(), monitor_cfg)
            panel.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        panel.SetSizer(panel.sizer)
        return session_id
    
class GUIController(object):
    def __init__(self, app, cfg):
        fr = wx.Frame(None, title='Training Monitor')
        panel = wx.Panel(fr)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = fr.CreateToolBar()
        new_session_btn = toolbar.AddLabelTool(wx.ID_ANY, 'New Session', wx.Bitmap('img/plus.png'))
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
        

class ConsoleController(object):
    def __init__(self, app, cfg):
        self.cfg = cfg
        self.session_manager = SessionManager(cfg)
        
    def save(self, outdir):
        self.session_manager.save(outdir)

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
        controller = ConsoleController(app, config)
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
    
    
    
