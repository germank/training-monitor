from plugin_mgr import FigureMemoryPanelFactory
from model.sessions import SessionManager
from listening_service import  DataListener, ListeningService
from view.console import CommandConsole

class ConsoleController(object):
    def __init__(self, cfg):
        #Service that handles HTTP requests
        dl = DataListener()
    
        #Start the HTTP server
        cp_cfg = cfg.get('cherrypy',{})
        cp_cfg['log.screen'] = cp_cfg.get('log.screen', False)
        self.ls = ListeningService(cp_cfg, dl)
        self.ls.server_started.connect(self.on_server_started)
        self.ls.server_stopped.connect(self.on_server_stopped)
        self.ls.start()
        
        self.cfg = cfg
        self.session_manager = SessionManager(cfg, dl)
        self.session_manager.session_new.connect(self.on_session_new)
        self.session_manager.switch_new_session()
        
        self.command_console = CommandConsole()
        self.command_console.quit_command.connect(self.on_quit_command)
        self.command_console.save_command.connect(self.on_save_command)
    
    def cmdloop(self):
        self.command_console.cmdloop()
    
    def on_server_started(self, **kwargs):
        print "HTTP Server Started"
    
    def on_server_stopped(self, **kwargs):
        print "HTTP Server Stopped"    
    
    def on_quit_command(self, **kwargs):
        self.ls.exit()
    
    def on_save_command(self, output_dir, **kwargs):
        self.session_manager.save(output_dir)
        
    def start_server(self):
        self.ls.start()
        
    def on_session_new(self, session_id, session_monitors, **kwargs):
        #for monitor_name, action_cfg in self.cfg.iteritems():
        for monitor_name, monitor in session_monitors.iteritems():
            monitor_cfg = self.cfg['elements'][monitor_name]
            panel_factory = FigureMemoryPanelFactory()
            p = panel_factory.build(monitor.get_figure(), monitor_cfg)
            #we throw away p?