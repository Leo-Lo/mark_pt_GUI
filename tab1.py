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



class tab1():

	def __init__(self,spline_color = '#52fffc'):
		

		self.xrange_text = TextInput(title="X Range max:", value="1",width=100)
		self.yrange_text = TextInput(title="Y Range max:", value="1",width=100)

		self.color_palette_menu = Select(title="Plot color palette:", value='Viridis', \
                    options=['Viridis','Cividis','Inferno','Magma','Plasma'],width=150)
		self.cross_color_pick = ColorPicker(color=spline_color, title="Cross color:", width=70)
		self.spline_color_pick = ColorPicker(color=spline_color, title="Spline color:", width=70)
		self.line_menu = Select(title="Line type:", value='I', options=['I','J','IJ'],width=150)
		self.line_number_text = TextInput(title="Line #:", value="0",width=50)

		self.color_text = Div(text="""<b>Color bar range:</b>""", width=120, height=20)
		self.color_range_min = TextInput(title="Min:", value="0",width=50)
		self.color_range_max = TextInput(title="Max:", value="1",width=50)

		self.spline_text = Div(text="""<b>Spline:</b>""", width=120, height=20)
		self.plot_spline_button = Button(label="Plot", button_type="primary",width=80)
		self.clear_spline_button = Button(label="Clear previous", button_type="warning",width=100)
		self.save_spline_button = Button(label="Save & Next", button_type="primary",width=80)
		self.save_all_button = Button(label="Save all", button_type="success",width=150)
		self.save_folder_text = TextInput(title="Save folder name:", value="my_folder",width=300)

		self.IJ_text = Div(text="""<b>Input I+J line?</b>""", width=120, height=20)
		self.IJ_radio_button = RadioButtonGroup(labels=["Yes", "No"], active=1,width=100)










