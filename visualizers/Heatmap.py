#from wx.lib.pubsub import Publisher as pub
import matplotlib.cm as cm
from numpy.lib.function_base import append
from numpy import asarray
from visualizers.Base import BasePanel, BaseFigure, BaseMemoryPanel

class HeatmapPanel(BasePanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        BasePanel.__init__(self, parent, figure)
        

class HeatmapMemoryPanel(BaseMemoryPanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, figure, **kwargs):
        BaseMemoryPanel.__init__(self, figure)
        
class HeatmapFigure(BaseFigure):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        BaseFigure.__init__(self)
        #plotted lines
        self.line = {}
        self.axes = self.figure.add_subplot(111)
    
    def do_accept_data(self, **kwargs):
        '''
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        cells = map(float, kwargs['cells'].split(','))
        size =  map(float, kwargs['size'].split(','))
        M = asarray(cells).reshape(size)
        self.update_matrix(M)

    
    def get_figure(self):
        return self.figure

    def update_matrix(self, M):
        self.axes.cla()
        self.axes.imshow(M, cmap = cm.Greys_r, interpolation='none')
        
    def draw(self):
        self.axes.relim()
        self.axes.autoscale_view()
    
    def save(self, output_file):
        self.figure.savefig(output_file)

    def ghost_clone(self, other):
        pass
