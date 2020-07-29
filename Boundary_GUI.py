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
import helper


#Data used
######################################################################################################
global data, source, line_source, spline_folder_name, I_dict, J_dict, IJ_dict,I_spline_dict, J_spline_dict, IJ_spline_dict,previous_line, spline_color
spline_folder_name = "my_folder"
spline_color = '#52fffc'
cross_width = 3
I_dict= {}
J_dict= {}
IJ_dict = {}
I_spline_dict= {}
J_spline_dict= {}
IJ_spline_dict = {}

# Widgets instantiation
######################################################################################################

# header widgets
header = helper.header()
title,file_text,file_input,previous_spline_text,spline_file_input,mark_text = vars(header).values()
space1 = Div(text="""  """, width=200, height=40)
space2 = Div(text="""  """, width=200, height=20)
space3 = Div(text="""  """, width=200, height=20)
space4 = Div(text="""  """, width=200, height=20)

# tab 1 widgets
tab1 = helper.tab1(spline_color = spline_color)
xrange_text,yrange_text,color_palette_menu,cross_color_pick,spline_color_pick,line_menu,\
line_number_text,color_text,color_range_min,color_range_max,spline_text,plot_spline_button,clear_spline_button,\
save_spline_button,save_all_button,save_folder_text,IJ_text,IJ_radio_button = vars(tab1).values()

# tab 2 widgets
tab2 = helper.tab2()
complete_mat_text,mat_file_input,line_type_radio_button,line_value_text,\
change_value_button,invert_button = vars(tab2).values()

# plot widgets
global line_source
plotter = helper.plotter(spline_color = spline_color,cross_width = cross_width)
color_mapper,figure1,img,range_slider,source,line_source,table = vars(plotter).values()



# tab 1 interactions
######################################################################################################
def change_IJ_mode(attr,old,new):
    if IJ_radio_button.active==1:
        print('option 1, No')
        do_IpJ = 0
    if IJ_radio_button.active==0:
        print('option 0, Yes')
IJ_radio_button.on_change('active',change_IJ_mode)

def set_folder_name(attr,old,new):
    global spline_folder_name
    spline_folder_name = new
save_folder_text.on_change('value',set_folder_name)

def reset_index(attr,old,new):
    line_type = new
    try:
        spline_dict = helper.open_pickle(line_type+'_spline_dict.pickle')
        previous_index = max(int(k) for k, v in spline_dict.items())
        line_number_text.value = str(previous_index+1)
    except: 
        line_number_text.value = str(0)
line_menu.on_change('value',reset_index)

def save_all(): 
    spline_folder_name = save_folder_text.value
    if not os.path.exists(spline_folder_name):
        os.makedirs(spline_folder_name)

    helper.save_to_pickle(spline_folder_name,I_dict,J_dict,IJ_dict,I_spline_dict,J_spline_dict,IJ_spline_dict)

    #save to MATLAB .mat file
    helper.save_as_mat_file(spline_folder_name,I_dict,J_dict, IJ_dict)
save_all_button.on_click(save_all)

def load_previous(attr,old,new):
    file_name = spline_file_input.filename
    spline_dict = helper.open_pickle(file_name)
    line_type = ''
    if file_name=='I_spline_dict.pickle':
        global I_spline_dict
        I_spline_dict.update(spline_dict)
        line_type = 'I'
    elif file_name=='J_spline_dict.pickle':
        global J_spline_dict
        J_spline_dict.update(spline_dict)
        line_type = 'J'
    elif file_name=='IJ_spline_dict.pickle':
        global IJ_spline_dict
        IJ_spline_dict.update(spline_dict)
        line_type = 'IJ'
    else:
        print('load spline file input error')

    #plot each line
    for index in spline_dict:
        x = spline_dict[index][0]
        y = spline_dict[index][1]
        figure1.line(x, y, line_width=2,color=spline_color)
    previous_index = max(int(k) for k, v in spline_dict.items())
    line_number_text.value=str(previous_index+1)

    #display in table
    for index in spline_dict:
        new_data = {
        'type' : [line_type],
        '#' : [int(index)],
        }
        global line_source
        line_source.stream(new_data)    
spline_file_input.on_change('value',load_previous)

def clear_previous_spline():
    p.glyph.line_alpha = 0
    xnew = []
    ynew = []    
clear_spline_button.on_click(clear_previous_spline)

def save_next_spline():
    line_type = line_menu.value
    line_num = line_number_text.value
    
    # user-specified points
    x = source.data['x']
    y = source.data['y']
    # sort x,y
    # x = sorted(x)
    # y = [y for (x,y) in sorted(zip(x,y), key=lambda pair: pair[0])]
    
    #splines
    spline_coordinates = np.stack((xnew,ynew))
    
    coordinates = np.stack((x,y))
    if line_type == 'I':
        I_dict[line_num] = coordinates
        I_spline_dict[line_num] = spline_coordinates
        print('saved')
    elif line_type == 'J':
        J_dict[line_num] = coordinates
        J_spline_dict[line_num] = spline_coordinates
        print('saved')
    elif line_type == 'IJ':
        IJ_dict[line_num] = coordinates
        IJ_spline_dict[line_num] = spline_coordinates
        print('saved')
    else:
        print('error: wrong line_type')
    source.data['x']=[]
    source.data['y']=[]
    
    #Table
    global line_source
    new_data = {
        'type' : [line_type],
        '#' : [int(line_number_text.value)],
    }
    line_source.stream(new_data)
    # line_source.data['type'].append(line_type)
    # line_source.data['#'].append(int(line_number_text.value))
    # line_source.update()
    global table
    table.update()

    #Line number update
    line_number_text.value=str(int(line_number_text.value)+1)
save_spline_button.on_click(save_next_spline)


# tab 2 interactions
######################################################################################################
def shift_line_num():
    shift = int(line_value_text.value)
    global point_source
    point_source.data['line_label']+=shift
change_value_button.on_click(shift_line_num)

def plot_all_spline():
    x = source.data['x']
    y = source.data['y']

    pts=np.array(list(zip(x,y)))
    tck, u = interpolate.splprep(pts.T, u=None, s=0.0, per=1) 
    u_new = np.linspace(u.min(), u.max(), 100)
    global xnew, ynew, p
    xnew, ynew = interpolate.splev(u_new, tck, der=0)
    p = figure1.line(xnew, ynew, line_width=2,color=spline_color)

def prepare_sources(mat):
    # Point data
    line_int = mat['line_integer_val'][0]
    x0_list = []
    y0_list = []
    line_num_list = []
    x_list_one_type = []
    y_list_one_type = []

    typeList =mat['line_type_list']
    indices_of_I = np.where(typeList==1)[1]
    indices_of_J = np.where(typeList==2)[1]
    indices_of_IJ = np.where(typeList==3)[1]
    if line_type_radio_button.active==0:
        indices_of_line_type = indices_of_I
    elif line_type_radio_button.active==1:
        indices_of_line_type = indices_of_J
    else:
        indices_of_line_type = indices_of_IJ

    for i in indices_of_line_type:
        x2d = mat['xpts_list'][0][i]
        x1d = x2d.flatten()
        x = x1d.tolist()
        y2d = mat['ypts_list'][0][i]
        y1d = y2d.flatten()
        y = y1d.tolist()
        #sort the x-coordinates such that all labels start at the same side of the plot
        xlist = sorted(x)
        ylist = [y for (x,y) in sorted(zip(x,y), key=lambda pair: pair[0])]
        x0_list.append(xlist[0])
        y0_list.append(ylist[0])
        #line plots
        x_list_one_type.append(xlist)
        y_list_one_type.append(ylist)
        #append line number values
        line_num_list.append(line_int[i])
    
    # Line 
    global one_type_line_source
    one_type_line_source = ColumnDataSource(dict(
            xs=x_list_one_type,
            ys=y_list_one_type,
        )
    )

    #point
    global point_source
    point_source = ColumnDataSource(dict(
            x0s=x0_list,
            y0s=y0_list,
            line_label = line_num_list
        )
    )
    return one_type_line_source, point_source

def plot_mat(attr,old,new):
    file_name = mat_file_input.filename
    global spline_folder_name
    mat = sio.loadmat(spline_folder_name+"/"+file_name)
    one_type_line_source, point_source = prepare_sources(mat)
    glyph = MultiLine(xs="xs", ys="ys", line_color='#52fffc', line_width=2)
    point_glyph = Circle(x='x0s',y='y0s')
    labels = LabelSet(x='x0s',y='y0s',text='line_label',source=point_source,text_font_size="8pt",
                      render_mode='canvas', border_line_alpha=1,background_fill_alpha=1)
    figure1.add_glyph(one_type_line_source, glyph)
    figure1.add_glyph(point_source, point_glyph)
    figure1.add_layout(labels)
mat_file_input.on_change('value',plot_mat)

# line_type_radio_button.on_change('value',plot_mat)


# Plotting interactions
######################################################################################################
range_callback = CustomJS(args=dict(img=img), code='''
                        img.glyph.color_mapper.low = cb_obj.value[0];
                        img.glyph.color_mapper.high = cb_obj.value[1];
                        ''')
range_slider.js_on_change('value',range_callback)

def update_figure(attr, old, new):
    img.glyph.global_alpha = 0
    
    file_name = file_input.filename
    metadata,data = helper.gsf_read(file_name)
    data = np.flipud(data)
    xrange_text.value = str(metadata['XReal']*1e9)
    yrange_text.value = str(metadata['YReal']*1e9)
    
    figure1.xaxis.axis_label = 'x (nm)'
    figure1.yaxis.axis_label = 'y (nm)'
    
    img2 = figure1.image(image=[data], color_mapper=color_mapper,
                   dh=[metadata['YReal']*1e9], dw=[metadata['XReal']*1e9], 
                   x=[-metadata['XReal']*1e9/2], y=[-metadata['YReal']*1e9/2])
    range_slider.start = data.min()
    range_slider.end = data.max()
    range_slider.value = data.min(),data.max()
    renderer = figure1.cross(x='x', y='y', source=source, color=spline_color, size=10,line_width=cross_width)
file_input.on_change('value',update_figure)

#change plot range
callback_x = CustomJS(args=dict(x_range=figure1.x_range), code="""
    x_range.setv({"start": -cb_obj.value*0.55, "end": cb_obj.value*0.55})
     """)
callback_y = CustomJS(args=dict(y_range=figure1.y_range), code="""
    y_range.setv({"start": -cb_obj.value*0.55, "end": cb_obj.value*0.55})
    """)
xrange_text.js_on_change('value',callback_x)
yrange_text.js_on_change('value',callback_y)

def update_color_palette(attr,old,new):
    color_mapper.palette = new+'256'
color_palette_menu.on_change('value',update_color_palette)

def update_color_min(attr, old, new):
    range_slider.start = float(new)
color_range_min.on_change('value',update_color_min)

def update_color_max(attr, old, new):
    range_slider.end = float(new)
color_range_max.on_change('value',update_color_max)

def update_spline_color(attr,old,new):
    global spline_color
    spline_color = new
    p.glyph.line_color=new
    renderer = figure1.cross(x='x', y='y', source=source, color=new, size=10,line_width=cross_width)
spline_color_pick.on_change('color',update_spline_color)

def plot_spline():
    x = source.data['x']
    y = source.data['y']

    pts=np.array(list(zip(x,y)))
    tck, u = interpolate.splprep(pts.T, u=None, s=0.0, per=1) 
    u_new = np.linspace(u.min(), u.max(), 100)
    global xnew, ynew, p
    xnew, ynew = interpolate.splev(u_new, tck, der=0)


    # x_sorted = sorted(x)
    # y_sorted = [y for (x,y) in sorted(zip(x,y), key=lambda pair: pair[0])]
    # tck = interpolate.splrep(x_sorted, y_sorted, s=0)
    # global xnew, ynew, p
    # xnew = np.arange(min(x), max(x), (max(x)-min(x))/500)
    # ynew = interpolate.splev(xnew, tck, der=0)
    p = figure1.line(xnew, ynew, line_width=2,color=spline_color)
    previous_line = p    
plot_spline_button.on_click(plot_spline)


# Layout
######################################################################################################
plot = column(row(xrange_text,yrange_text),space2,
                                     row(color_palette_menu,spline_color_pick),
                                     row(color_text,color_range_min,color_range_max),range_slider,space3,spline_text,
                                     row(line_menu,line_number_text),
                                     row(IJ_text,IJ_radio_button),
                                     row(plot_spline_button,clear_spline_button,save_spline_button),
                                     row(save_all_button),
                                     save_folder_text,table)
tab1_layout=Panel(child=plot,title='Mark points')
adjust = column(complete_mat_text,mat_file_input,line_type_radio_button,line_value_text,\
                change_value_button,invert_button)
tab2=Panel(child=adjust,title='Edit spline label')
tabs = Tabs(tabs=[tab1_layout,tab2],active=0)

all_layout = column(title,space1,row(column(row(file_text,file_input),previous_spline_text,\
                    spline_file_input,mark_text,space4,tabs),figure1))


curdoc().add_root(all_layout)
curdoc().title = "Point selection GUI"
