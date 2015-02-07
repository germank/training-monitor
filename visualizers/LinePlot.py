#from wx.lib.pubsub import Publisher as pub
import wx
from numpy import mean
from numpy.lib.function_base import append
from visualizers.Base import BasePanel, BaseFigure, BaseMemoryPanel

class LinePlotPanel(BasePanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, parent, figure, **kwargs):
        BasePanel.__init__(self, parent, figure)
        
    
         # create a long tooltip with newline to get around wx bug (in v2.6.3.3)
        # where newlines aren't recognized on subsequent self.tooltip.SetTip() calls
#        self.tooltip = wx.ToolTip(tip='tip with a long %s line and a newline\n' % (' '*100))
#        self.SetToolTip(None)
#        self.tooltip.Enable(False)
#        self.tooltip.SetDelay(0)
#        self.canvas.mpl_connect('motion_notify_event', self.onMotion)
#    
#    def onMotion(self, event):
#        collisionFound = False
#        if event.xdata != None and event.ydata != None: # mouse is inside the axes
#            for z, line in self.figure.line.iteritems():
#                xdata = line.get_xdata()
#                ydata = line.get_ydata()
#                for x,y in zip(xdata,ydata):
#                    radius = 0.01
#                    if abs(event.xdata - x) < radius and abs(event.ydata - y) < radius:
#                        if not self.GetToolTip():
#                            tip='x=%f;y=%f' % (event.xdata, event.ydata)
#                            self.tooltip.SetTip(tip) 
#                            self.tooltip.Enable(True)
#                            self.SetToolTip(self.tooltip)
#                            collisionFound = True
#                            break
#        if not collisionFound:
#            self.tooltip.Enable(False)
#            self.SetToolTip(None)
        

class LinePlotMemoryPanel(BaseMemoryPanel):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, figure, **kwargs):
        BaseMemoryPanel.__init__(self, figure)
        
class LinePlotFigure(BaseFigure):
    '''
    A Panel with a line plot in it
    '''
    def __init__(self, **kwargs):
        BaseFigure.__init__(self)
        #plotted lines
        self.line = {}
        if 'scale' in kwargs:
            self.axes.set_yscale(kwargs['scale'])
        self.range = kwargs.get('range',None)
        self.ls = kwargs.get('ls', kwargs.get('linestyle', "-"))
        self.marker = kwargs.get('marker', None)
        self.grid = kwargs.get('grid', False)
        self.smoothing = kwargs.get('smoothing', 1)
        self.moving_history = []
        if self.grid:
                self.axes.grid()
    
    def do_accept_data(self, **kwargs):
        '''
        @keyword x: x-value for the point
        @keyword y: t-value for the point
        @keyword z: line index in the plot 
        '''
        #don't really know if this is necessary anymore
        self.add_point(**kwargs)
        self.axes.relim()
        if self.range:
            self.axes.set_ylim(self.range)
        self.axes.autoscale_view()
    
    def get_figure(self):
        return self.figure

    def add_point(self, y, x=None, z=1):
        y = float(y)
        self.moving_history.append(y)
        self.moving_history = self.moving_history[-self.smoothing:]
        print(self.moving_history)
        y = mean(self.moving_history)
        print y
        if not x:
            if z in self.line:
                x = self.line[z].get_xdata()[-1] + 1
            else:
                x = 1
        print x
        try:
            self.line[z].set_xdata(append(self.line[z].get_xdata(), x))
            self.line[z].set_ydata(append(self.line[z].get_ydata(), y))
        except KeyError:
            self.line[z], = self.axes.plot([x],[y], linestyle=str(self.ls), marker=str(self.marker))
            
        
    
    def save(self, output_file):
        self.figure.savefig(output_file)

    def ghost_clone(self, other):
        for line in other.line.itervalues():
            self.axes.plot(line.get_xdata(), line.get_ydata(), alpha=0.5)