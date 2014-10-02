import wx
from plugin_mgr import FigurePanelFactory

class MainFrame(wx.Frame):
    def __init__(self, app):
        wx.Frame.__init__(self, None, title='Training Monitor')
        self.main_panel = wx.Panel(self)
        self.main_panel.sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = self.CreateToolBar()
        new_session_ID = wx.NewId()
        self.new_session_btn = toolbar.AddLabelTool(new_session_ID, 'New Session', wx.Bitmap('img/plus.png'))
        save_session_ID = wx.NewId()
        self.save_session_btn = toolbar.AddLabelTool(save_session_ID, 'Save Session', wx.Bitmap('img/save.png'))
        switch_session_ID = wx.NewId()
        self.switch_session_btn = toolbar.AddLabelTool(switch_session_ID, 'Switch Session', wx.Bitmap('img/switch.png'))
        clone_session_ID = wx.NewId()
        self.clone_session_btn = toolbar.AddLabelTool(clone_session_ID, 'Clone Session', wx.Bitmap('img/clone.png'))
        toolbar.AddSeparator()
        start_server_ID = wx.NewId()
        self.start_server_btn = toolbar.AddLabelTool(start_server_ID, 'Start Server', wx.Bitmap('img/play.png'))
        stop_server_ID = wx.NewId()
        self.stop_server_btn = toolbar.AddLabelTool(stop_server_ID, 'Stop Server', wx.Bitmap('img/stop.png'))
        toolbar.Realize()
        self.toolbar = toolbar
        
        self.session_listbook = wx.Listbook(self.main_panel)
        
        il = wx.ImageList(16,16)
        il.Add(wx.Bitmap('img/ball_red.png'))
        il.Add(wx.Bitmap('img/ball_green.png'))
        self.session_listbook.AssignImageList(il)
        
        self.main_panel.sizer.Add(self.session_listbook, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        
        
        self.main_panel.SetSizerAndFit(self.main_panel.sizer)
        
        
    def get_selection(self):
        return self.session_listbook.GetSelection()
    
    def select_active_session(self, page_id):
        for i in range(self.session_listbook.GetPageCount()):
            self.session_listbook.SetPageImage(i, 1 if i == page_id else 0)
        self.session_listbook.SetSelection(page_id)
        
    
    def new_session_panel(self, text):
        panel = wx.Panel(self.main_panel)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        self.session_listbook.AddPage(panel, text, imageId=0)
        page_id = self.session_listbook.GetPageCount()-1
        return panel, page_id
    
    def add_monitor(self, session_panel, monitor_cfg, monitor_figure, default_name):
        panel_factory = FigurePanelFactory()
        #Create the Panel 
        p = panel_factory.build(session_panel, monitor_figure, monitor_cfg)
        #Define the panel label
        s = wx.StaticText(session_panel,-1,monitor_cfg.get('label', default_name))
        session_panel.sizer.Add(s, 0)
        session_panel.sizer.Add(p, 1, wx.LEFT | wx.TOP | wx.GROW| wx.EXPAND)
        session_panel.SetSizer(session_panel.sizer)    
