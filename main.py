#!/usr/bin/env python
import matplotlib
from controller.console_controller import ConsoleController
from controller.gui_controller import GUIController
matplotlib.use('Agg')

import yaml
import argparse
import wx

#dynamically load visualizing classes from the visualizers package
from plugin_mgr import load_plugins
load_plugins('visualizers')


if __name__ == "__main__":
    ap = argparse.ArgumentParser('Training Monitor')
    ap.add_argument('config_yml', help='yml file with the monitor configuration')
    ap.add_argument('-G', '--no-gui', action='store_true', default=False)
    
    args = ap.parse_args()
    
    config = yaml.load(file(args.config_yml))

    
    controller = None
    
    if args.no_gui:
        controller = ConsoleController(config)
        controller.cmdloop()
    else:
        app = wx.PySimpleApp()
        controller = GUIController(app, config)
        app.MainLoop()
