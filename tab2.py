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


class tab2():
	
	def __init__(self):

		self.complete_mat_text = Div(text="""<b>Load complete splines:</b> (only .mat format)""", width=400, height=20)
		self.mat_file_input = FileInput(accept=".mat")
		self.line_type_radio_button = RadioButtonGroup(labels=["I", "J","I+J"], active=0,width=200)
		self.line_value_text = TextInput(title="Change all line # of by (can be negative):", value="0",width=100)
		self.change_value_button = Button(label="Confirm change", button_type="primary",width=150)
		self.invert_button = Button(label="Invert sign of all line numbers", button_type="warning",width=150)









