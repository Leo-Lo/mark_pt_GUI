from bokeh.io import *
from bokeh.layouts import *
from bokeh.plotting import *
from bokeh.models.renderers import *
from bokeh.palettes import *
from bokeh.models.widgets import *
from bokeh.models import *
from scipy import interpolate
import scipy.io as sio
import numpy as np
import os
from matplotlib import pyplot as plt
from bokeh.plotting import figure, show, Column


class plotter():

	def __init__(self,spline_color = '#52fffc',cross_width = 3):

		data = np.random.rand(200,200)
		self.color_mapper = LinearColorMapper(palette="Viridis256", low=0, high=1)
		self.figure1 = figure(x_range=(-0.05*1,1.05*1), y_range=(-0.05*1,1.05*1))
		color_bar = ColorBar(color_mapper=self.color_mapper, ticker= BasicTicker(),
		                     location=(0,0))
		self.figure1.add_layout(color_bar, 'right')

		self.img = self.figure1.image(image=[data], color_mapper=self.color_mapper,
		                   dh=[1.0*1], dw=[1.0*1], x=[0], y=[0])

		self.range_slider = RangeSlider(start=data.min(), end=data.max(),
		                           value=(data.min(), data.max()),
		                           step=0.01, title="range", width=300)


		self.source = ColumnDataSource({'x': [], 'y': []})
		renderer = self.figure1.cross(x='x', y='y', source=self.source, color=spline_color, size=10,line_width=cross_width)

		#table
		
		self.line_source = ColumnDataSource({'type': [], '#': []})
		columns = [TableColumn(field="#", title="Line number")]
		self.table = DataTable(source=self.line_source, columns=columns, editable=False, height=200,width=300)

		self.figure1.toolbar.logo = None
		self.figure1.toolbar.tools = [PanTool(),SaveTool(),UndoTool(),RedoTool(),BoxZoomTool()]

		draw_tool = PointDrawTool(renderers=[renderer])
		cross_hair_tool = CrosshairTool()
		zoom_tool = WheelZoomTool()
		self.figure1.add_tools(draw_tool,cross_hair_tool,zoom_tool)
		self.figure1.toolbar.active_tap = draw_tool
		self.figure1.toolbar.active_scroll = zoom_tool


	    