#from wx.lib.pubsub import Publisher as pub
from numpy.lib.function_base import append
from numpy import asarray, arange
from visualizers.Base import BasePanel, BaseFigure, BaseMemoryPanel
import matplotlib

class HistogramPanel(BasePanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        BasePanel.__init__(self, parent, figure)
        

class HistogramMemoryPanel(BaseMemoryPanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, figure, **kwargs):
        BaseMemoryPanel.__init__(self, figure)
        
class HistogramFigure(BaseFigure):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        BaseFigure.__init__(self)
        #plotted lines
        self.line = {}
        self.bins = kwargs.get('bins', None)
        self.range = kwargs.get('range', None)
        self.binwidth = kwargs.get('binwidth', None)
        
    
    def do_accept_data(self, **kwargs):
        '''
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        cells = map(float, kwargs['cells'].split(','))
        M = asarray(cells)
        print "Histogram data"
        print repr(M)
        self.update_matrix(M)
        #self.axes.relim()
        #self.axes.autoscale_view()
    
    def get_figure(self):
        return self.figure

    def update_matrix(self, M):
        self.axes.cla()
        args = {}
        if self.bins:
            args['bins'] = self.bins
        if self.range and self.binwidth:
            args['bins'] = arange(self.range[0], self.range[1] + self.binwidth, self.binwidth)
        self.axes.hist(M, rwidth=1)
        self.axes.get_xaxis().get_major_formatter().set_useOffset(False)
        self.axes.get_yaxis().get_major_formatter().set_useOffset(False)
        
    def save(self, output_file):
        self.figure.savefig(output_file)

    def ghost_clone(self, other):
        pass
