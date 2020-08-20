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
from matplotlib import pyplot as plt
from bokeh.plotting import figure, show, Column
import pickle
from pathlib import Path

root = Path(".")

#helper method
def save_to_pickle(spline_folder_name,pt_dict):

    with open(root / spline_folder_name /'pt_dict.pickle', 'wb') as handle:
        pickle.dump(pt_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

def open_pickle(file_name):
    with open(file_name, 'rb') as handle:
        spline_dict = pickle.load(handle)
    return spline_dict

# Sourced from https://gist.github.com/carlodri/66c471498e6b52caf213
def gsf_read(file_name):
    '''Read a Gwyddion Simple Field 1.0 file format
    http://gwyddion.net/documentation/user-guide-en/gsf.html
    
    Args:
        file_name (string): the name of the output (any extension will be replaced)
    Returns:
        metadata (dict): additional metadata to be included in the file
        data (2darray): an arbitrary sized 2D array of arbitrary numeric type
    '''
    if file_name.rpartition('.')[1] == '.':
        file_name = file_name[0:file_name.rfind('.')]
    
    gsfFile = open(file_name + '.gsf', 'rb')
    
    metadata = {}
    
    # check if header is OK
    if not(gsfFile.readline().decode('UTF-8') == 'Gwyddion Simple Field 1.0\n'):
        gsfFile.close()
        raise ValueError('File has wrong header')
        
    term = b'00'
    # read metadata header
    while term != b'\x00':
        line_string = gsfFile.readline().decode('UTF-8')
        metadata[line_string.rpartition(' = ')[0]] = line_string.rpartition('=')[2]
        term = gsfFile.read(1)
        gsfFile.seek(-1, 1)
    
    gsfFile.read(4 - gsfFile.tell() % 4)
    
    #fix known metadata types from .gsf file specs
    #first the mandatory ones...
    metadata['XRes'] = np.int(metadata['XRes'])
    metadata['YRes'] = np.int(metadata['YRes'])
    
    #now check for the optional ones
    if 'XReal' in metadata:
        metadata['XReal'] = np.float(metadata['XReal'])
    
    if 'YReal' in metadata:
        metadata['YReal'] = np.float(metadata['YReal'])
                
    if 'XOffset' in metadata:
        metadata['XOffset'] = np.float(metadata['XOffset'])
    
    if 'YOffset' in metadata:
        metadata['YOffset'] = np.float(metadata['YOffset'])
    
    data = np.frombuffer(gsfFile.read(),dtype='float32').reshape(metadata['YRes'],metadata['XRes'])
    
    gsfFile.close()
    
    return metadata, data


class tab0():
    
    def __init__(self):

        self.file_text = Div(text="""<b>Load image: </b>(accept .gsf (preferred) or .png format)""", width=200, height=20)
        self.file_input = FileInput(accept=".gsf,.png")
        self.color_group_text = Div(text="(Optional) Specify the color range (R,G,B,A) for extracting value \
                            from input file with format other than .gsf", width=400, height=40)
        self.color_radio_button_group = RadioButtonGroup(labels=['R', 'B','G','A'], active=0,width=300)
        self.previous_spline_text = Div(text="""(Optional) <b>Load previous splines:</b> (only .pickle format)""", width=400, height=20)
        self.spline_file_input = FileInput(accept=".pickle")
        self.mark_text = Div(text="""<b>IMPORTANT: Mark each domain in counter-clockwise order! \
                            And all points need to be within image boundary.</b>""", width=400, height=20)


class tab1():

    def __init__(self,line_color = '#52fffc'):
        

        self.xrange_text = TextInput(title="X Range max:", value="1",width=100)
        self.yrange_text = TextInput(title="Y Range max:", value="1",width=100)

        self.color_palette_menu = Select(title="Plot color palette:", value='Viridis', \
                    options=['Viridis','Cividis','Inferno','Magma','Plasma'],width=150)
        self.cross_color_pick = ColorPicker(color=line_color, title="Cross color:", width=70)
        self.line_color_pick = ColorPicker(color=line_color, title="Line color:", width=70)
        self.line_number_text = TextInput(title="Line index:", value="0",width=100)

        self.color_text = Div(text="""<b>Color bar range:</b>""", width=120, height=20)
        self.color_range_min = TextInput(title="Min:", value="0",width=50)
        self.color_range_max = TextInput(title="Max:", value="1",width=50)

class tab2():

    def __init__(self):

        self.is_boundary_text = Div(text="""<b>Is this domain at the boundary:</b>""", width=200, height=20)
        self.is_boundary_button = RadioButtonGroup(labels=['Yes', 'No'], active=1,width=150)
        self.mirror_text = Div(text="""<b>(If "yes" above) Mirror flip direction:</b>""", width=400, height=20)
        self.mirror_button = RadioButtonGroup(labels=['Left to right', 'Right to left','Up to down','Down to up'], active=0,width=300)

        self.plot_line_button = Button(label="Plot", button_type="primary",width=80)
        self.clear_spline_button = Button(label="Clear previous", button_type="warning",width=100)
        self.save_spline_button = Button(label="Save & Next", button_type="primary",width=80)
        self.save_all_button = Button(label="Save all", button_type="success",width=150)
        self.save_folder_text = TextInput(title="Save folder name:", value="my_folder",width=300)


class plotter():

    def __init__(self,line_color = '#52fffc',cross_width = 3):

        data = np.random.rand(200,200)
        self.color_mapper = LinearColorMapper(palette="Viridis256", low=0, high=1)
        self.figure1 = figure(x_range=(-0.05*1,1.05*1), y_range=(-0.05*1,1.05*1),plot_width=750, plot_height=650)
        color_bar = ColorBar(color_mapper=self.color_mapper, ticker= BasicTicker(),
                             location=(0,0))
        self.figure1.add_layout(color_bar, 'right')

        self.img = self.figure1.image(image=[data], color_mapper=self.color_mapper,
                           dh=[1.0*1], dw=[1.0*1], x=[0], y=[0])

        self.range_slider = RangeSlider(start=data.min(), end=data.max(),
                                   value=(data.min(), data.max()),
                                   step=0.01, title="range", width=300)


        self.source = ColumnDataSource({'x': [], 'y': []})
        renderer = self.figure1.cross(x='x', y='y', source=self.source, color=line_color, size=10,line_width=cross_width)

        #table
        
        self.line_source = ColumnDataSource({'type': [], '#': []})
        columns = [TableColumn(field="#", title="Line number")]

        self.figure1.toolbar.logo = None
        self.figure1.toolbar.tools = [PanTool(),SaveTool(),UndoTool(),RedoTool(),BoxZoomTool()]

        draw_tool = PointDrawTool(renderers=[renderer])
        cross_hair_tool = CrosshairTool()
        zoom_tool = WheelZoomTool()
        self.figure1.add_tools(draw_tool,cross_hair_tool,zoom_tool)
        self.figure1.toolbar.active_tap = draw_tool
        self.figure1.toolbar.active_scroll = zoom_tool


        






