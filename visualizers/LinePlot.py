from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub
from numpy.lib.function_base import append

class LinePlotPanel(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        wx.Panel.__init__(self, parent)
        self.figure = figure 
        pub.subscribe(self.on_figure_changed, 'FIGURE_CHANGED')
        self.canvas = FigureCanvas(self, -1, self.figure.get_figure())
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizerAndFit(self.sizer)
        self.Fit()

    def add_point(self, y, x=None, z=1):
        self.figure.add_point(y, x, z)
            
    def draw(self):
        self.figure.draw()
        self.canvas.draw()
    
    def save(self, output_dir):
        self.figure.save(output_dir)
        
    def on_figure_changed(self, message):
        if message.data == self.figure:
            self.draw()



class LinePlotFigure(wx.Panel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        #data container
        #self.data = defaultdict(list)
        #plotted lines
        self.line = {}
        #gui stuff
        self.figure = Figure((6,3))
        self.axes = self.figure.add_subplot(111)
        if 'scale' in kwargs:
            self.axes.set_yscale(kwargs['scale'])
    
    def accept_data(self, **kwargs):
        '''
        Handles a request from the HTTP server
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        #don't really know if this is necessary anymore
        wx.CallAfter(self.add_point, **kwargs)

    
    def get_figure(self):
        return self.figure

    def add_point(self, y, x=None, z=1):
        y = float(y)
        print(y)
        #take note of the data
        #self.data[z].append((x,y))
        #plot it
        if not x:
            print z in self.line
            if z in self.line:
                x = self.line[z].get_xdata()[-1] + 1
            else:
                x = 1
            print(x)
            
        try:
            self.line[z].set_xdata(append(self.line[z].get_xdata(), x))
            self.line[z].set_ydata(append(self.line[z].get_ydata(), y))
        except KeyError:
            self.line[z], = self.axes.plot([x],[y])
        
        pub.sendMessage('FIGURE_CHANGED', self)
    
    def draw(self):
        self.axes.relim()
        self.axes.autoscale_view()
        
    
    def save(self, output_dir):
        pass
