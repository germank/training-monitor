#from wx.lib.pubsub import Publisher as pub
import matplotlib.cm as cm
from numpy.lib.function_base import append
from numpy import asarray
from visualizers.Base import BasePanel, BaseFigure, BaseMemoryPanel


import numpy as N
import pylab as P

def _blob(x,y,area,colour):
    """
    Draws a square-shaped blob with the given area (< 1) at
    the given coordinates.
    """
    hs = N.sqrt(area) / 2
    xcorners = N.array([x - hs, x + hs, x + hs, x - hs])
    ycorners = N.array([y - hs, y - hs, y + hs, y + hs])
    P.fill(xcorners, ycorners, colour, edgecolor=colour)

def hinton(W, maxWeight=None):
    """
    Draws a Hinton diagram for visualizing a weight matrix. 
    Temporarily disables matplotlib interactive mode if it is on, 
    otherwise this takes forever.
    """
    reenable = False
    if P.isinteractive():
        P.ioff()
    P.clf()
    height, width = W.shape
    if not maxWeight:
        maxWeight = 2**N.ceil(N.log(N.max(N.abs(W)))/N.log(2))

    P.fill(N.array([0,width,width,0]),N.array([0,0,height,height]),'gray')
    P.axis('off')
    P.axis('equal')
    for x in xrange(width):
        for y in xrange(height):
            _x = x+1
            _y = y+1
            w = W[y,x]
            if w > 0:
                _blob(_x - 0.5, height - _y + 0.5, min(1,w/maxWeight),'white')
            elif w < 0:
                _blob(_x - 0.5, height - _y + 0.5, min(1,-w/maxWeight),'black')
    if reenable:
        P.ion()
    P.show()

class HintonPanel(BasePanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        BasePanel.__init__(self, parent, figure)
        

class HintonMemoryPanel(BaseMemoryPanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, figure, **kwargs):
        BaseMemoryPanel.__init__(self, figure)
        
class HintonFigure(BaseFigure):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        BaseFigure.__init__(self)
        #plotted lines
        self.line = {}
        self.colorbar = None
        self.image = None
        self.range = kwargs.get('range', None)
        
    
    def do_accept_data(self, **kwargs):
        '''
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        cells = map(float, kwargs['cells'].split(','))
        size =  map(float, kwargs['size'].split(','))
        M = asarray(cells).reshape(size)
        if len(size) > 1 and M.shape[0] > M.shape[1]:
            M = M.transpose()
        self.update_matrix(M)
        self.axes.relim()
        self.axes.autoscale_view()

    
    def get_figure(self):
        return self.figure

    def update_matrix(self, M):
        if not self.image:
            self.image = self.axes.imshow(M, cmap = cm.Greys_r, interpolation='none')
            if self.range:
                self.image.set_clim(vmin=self.range[0], vmax=self.range[1])
            self.colorbar = self.figure.colorbar(self.image)
        else:
            self.image.set_array(M)
            #self.image.set_extent([0,M.shape[0],0,M.shape[1]])
            if not self.range:
                self.image.autoscale()
            #self.image.changed()
            #self.image.set_extent()
            #self.image.update(M)
        
        
    
    def save(self, output_file):
        self.figure.savefig(output_file)

    def ghost_clone(self, other):
        pass
