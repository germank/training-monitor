import pkgutil
import sys

def load_plugins(package_name):
    '''Loads the Panel and Figure class from the each module in the given package'''
    for module_loader, module_name, ispkg in pkgutil.iter_modules([package_name]):
        if module_name not in sys.modules:
            # Import module
            tmp = __import__(package_name+"."+module_name, globals(), locals(), [module_name+'Panel',module_name+'Figure'])
            globals()[module_name+'Panel'] = tmp.__dict__[module_name+'Panel']
            globals()[module_name+'Figure'] = tmp.__dict__[module_name+'Figure']

class FigureFactory():
    def build(self, cfg):
        return globals()[cfg['type'] + 'Figure'](**(cfg['args'] if 'args' in cfg else {}))

class FigurePanelFactory(object):
    def build(self, panel, figure, cfg):
        return globals()[cfg['type'] + 'Panel'](panel, 
                                        figure,
                                        **(cfg.get('args',{})))
        