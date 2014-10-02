
import wx
from signalslot.signal import Signal
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg #as FigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


class BasePanel(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        wx.Panel.__init__(self, parent)
        self.figure = figure 
        #pub.subscribe(self.on_figure_changed, 'FIGURE_CHANGED')
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure.get_figure())
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizerAndFit(self.sizer)
        self.Fit()
        
        self.figure.figure_updated.connect(self.on_figure_updated)
    
    def draw(self):
        #forwards the call to the GUI thread
        wx.CallAfter(self.do_draw)
        
    def do_draw(self):
        self.figure.draw()
        self.canvas.draw()
        
    def on_figure_updated(self, figure, **kwargs):
        if figure == self.figure:
            self.draw()
        
class BaseMemoryPanel(object):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, figure, **kwargs):
        self.figure = figure 
        #pub.subscribe(self.on_figure_changed, 'FIGURE_CHANGED')
        self.canvas = FigureCanvasAgg(self.figure.get_figure())
        self.figure.figure_updated.connect(self.on_figure_updated)
    
    def draw(self):
        self.do_draw()
        
    def do_draw(self):
        self.figure.draw()
        self.canvas.draw()
        
    def on_figure_updated(self, figure, **kwargs):
        if figure == self.figure:
            self.draw()
            
            
class BaseFigure(object):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        self.figure_updated = Signal()
        self.figure = Figure()
        
    def accept_data(self, **kwargs):
        '''
        Handles a request from the HTTP server
        '''
        self.do_accept_data(**kwargs)
        self.figure_updated.emit(figure=self)
