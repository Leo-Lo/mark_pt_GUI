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


class header():

	def __init__(self):

		self.title = Div(text="<h1><b>Moire extraction GUI</b></h1>",width=600, height=30)
		self.file_text = Div(text="""<b>Load image: </b>(only .png format)""", width=200, height=20)
		self.file_input = FileInput(accept=".gsf")
		self.previous_spline_text = Div(text="""(Optional) <b>Load previous splines:</b> (only .pickle format)""", width=400, height=20)
		self.spline_file_input = FileInput(accept=".pickle")




	    