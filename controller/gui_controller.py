import wx
from view.main_frame import MainFrame
from model.sessions import SessionManager
from listening_service import DataListener, ListeningService


class GUIController(object):
    def __init__(self, app, cfg):
        self.frame = MainFrame(app)
        self.cfg = cfg
        self.session_id2page = {}
        self.page2session_id = {}
        
        #Event Bindings
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_save_session, 
                  id=self.frame.save_session_btn.GetId())
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_new_session, 
                  id=self.frame.new_session_btn.GetId()) 
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_switch_session, 
                  id=self.frame.switch_session_btn.GetId()) 
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_clone_session, 
                  id=self.frame.clone_session_btn.GetId())
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_start_server, 
                  id=self.frame.start_server_btn.GetId())
        self.frame.Bind(wx.EVT_TOOL, self.on_btn_stop_server, 
                  id=self.frame.stop_server_btn.GetId())
        
        #Service that handles HTTP requests
        dl = DataListener()
    
        #Start the HTTP server
        self.ls = ListeningService(cfg.get('cherrypy',{}), dl)
        self.ls.server_started.connect(self.on_server_started)
        self.ls.server_stopped.connect(self.on_server_stopped)
        self.ls.start()
         
        self.session_manager = SessionManager(cfg, dl)
        self.session_manager.session_new.connect(self.on_session_new)
        self.session_manager.session_switch.connect(self.on_session_switch)
        self.session_manager.switch_new_session()
        
        self.frame.Bind(wx.EVT_CLOSE, self.on_quit)

        self.frame.Show()
        self.frame.Maximize()
        
    def on_quit(self, event):
        self.ls.stop()
        self.ls.exit()
        event.Skip()
        
    def on_server_started(self, **kwargs):
        self.frame.toolbar.EnableTool(self.frame.start_server_btn.GetId(), False)
        self.frame.toolbar.EnableTool(self.frame.stop_server_btn.GetId(), True)
    
    def on_server_stopped(self, **kwargs):
        self.frame.toolbar.EnableTool(self.frame.start_server_btn.GetId(), True)
        self.frame.toolbar.EnableTool(self.frame.stop_server_btn.GetId(), False)
        
    def on_btn_save_session(self, event):
        dir_dialog = wx.DirDialog(self.frame, "Select the output directory")
        if dir_dialog.ShowModal() == wx.ID_OK:
            self.save(dir_dialog.GetPath())
        event.Skip()
    
    def on_btn_new_session(self, event):
        self.session_manager.new_session()
        event.Skip()
        
    def on_btn_switch_session(self, event):
        page_id = self.frame.get_selection()
        session_id = self.page2session_id[page_id]
        self.session_manager.switch_session(session_id)
        event.Skip()
        
    def on_btn_clone_session(self, event):
        page_id = self.frame.get_selection()
        session_id = self.page2session_id[page_id]
        self.session_manager.clone_session(session_id)
        event.Skip()
            
    def on_btn_start_server(self, event):
        self.ls.start()
        event.Skip()
        
    def on_btn_stop_server(self, event):
        self.ls.stop()
        event.Skip()
        
    def save(self, outdir):
        self.session_manager.save(outdir)
    
    def on_session_switch(self, session_id, **kwargs):
        page_id = self.session_id2page[session_id]
        self.frame.select_active_session(page_id)
    
        
    def on_session_new(self, session_id, session_monitors, **kwargs):
        session_panel, page_id = self.frame.new_session_panel(session_id)
        self.session_id2page[session_id] = page_id
        self.page2session_id[page_id] = session_id
        for monitor_name, monitor in session_monitors.iteritems():
            monitor_cfg = self.cfg['elements'][monitor_name]
            monitor_figure = monitor.get_figure()
            self.frame.add_monitor(session_panel, monitor_cfg, 
                                   monitor_figure, monitor_name)
    