from bokeh.io import *
from bokeh.layouts import *
from bokeh.plotting import *
from bokeh.models.renderers import *
from bokeh.palettes import *
from bokeh.models.widgets import *
from bokeh.models import *
from PIL import Image
from scipy import interpolate
import scipy.io as sio
import numpy as np
import os
from matplotlib import pyplot as plt
from bokeh.plotting import figure, show, Column
import helper

#Data used
######################################################################################################

global data, source, line_source, line_folder_name, pt_dict, previous_line, line_color
line_folder_name = "my_folder"
line_color = '#52fffc'
cross_width = 3

class bokeh_object():
    def __init__(self):

        self.pt_dict = {}

        self.data = None
        self.source = None
        self.line_source = None
        self.line_folder_name = "my_folder"
        self.previous_line = None
        self.line_color = '#52fffc'

    def get_pt_dict(self):
        return self.pt_dict

    def my_app(self,doc):

        # Widgets instantiation
        ######################################################################################################

        # tab 0 widgets
        title = Div(text="<h1><b>Domain extraction GUI</b></h1>",width=600, height=30)
        tab0 = helper.tab0()
        file_text,file_input,color_group_text,color_radio_button_group,previous_spline_text,\
            spline_file_input,mark_text = vars(tab0).values()

        space1 = Div(text="""  """, width=200, height=40)
        space2 = Div(text="""  """, width=200, height=20)
        space3 = Div(text="""  """, width=200, height=20)
        space4 = Div(text="""  """, width=200, height=20)
        space5 = Div(text="""  """, width=200, height=20)
        space6 = Div(text="""  """, width=200, height=20)

        # tab 1 widgets
        tab1 = helper.tab1(line_color = line_color)
        xrange_text,yrange_text,color_palette_menu,cross_color_pick,line_color_pick,\
        line_number_text,color_text,color_range_min,color_range_max = vars(tab1).values()

        # tab 2 widgets
        tab2 = helper.tab2()
        is_boundary_text,is_boundary_button,mirror_text,mirror_button,plot_line_button,\
        clear_spline_button,save_spline_button,save_all_button,save_folder_text = vars(tab2).values()

        # plot widgets
        global line_source
        plotter = helper.plotter(line_color = line_color,cross_width = cross_width)
        color_mapper,figure1,img,range_slider,source,line_source = vars(plotter).values()



        # Interactions
        ######################################################################################################

        def set_folder_name(attr,old,new):
            global line_folder_name
            line_folder_name = new
        save_folder_text.on_change('value',set_folder_name)

        def save_all(): 
            line_folder_name = save_folder_text.value
            if not os.path.exists(line_folder_name):
                os.makedirs(line_folder_name)

            helper.save_to_pickle(line_folder_name,pt_dict)

        save_all_button.on_click(save_all)

        def load_previous(attr,old,new):
            file_name = spline_file_input.filename
            line_dict = helper.open_pickle(file_name)
            global pt_dict
            self.pt_dict.update(line_dict)
            pt_dict.update(line_dict)
                
            #plot each line
            for index in line_dict:
                x = line_dict[index][0]
                y = line_dict[index][1]
                figure1.line(x, y, line_width=2,color=line_color)
            previous_index = max(int(k) for k, v in line_dict.items())
            line_number_text.value=str(previous_index+1)

        spline_file_input.on_change('value',load_previous)

        def clear_previous_spline():
            p.glyph.line_alpha = 0
            xnew = []
            ynew = []    
        clear_spline_button.on_click(clear_previous_spline)

        def save_next_line():
            
            x = source.data['x']
            y = source.data['y']
            line_num = line_number_text.value
            coordinates = np.stack((x,y))
            self.pt_dict[line_num] = coordinates
            
            # reset for next line
            source.data['x']=[]
            source.data['y']=[]
            line_number_text.value=str(int(line_number_text.value)+1)
            is_boundary_button.active = 1

            
        save_spline_button.on_click(save_next_line)


        # Mirror operation
        ######################################################################################################
        def mirror_d2u(xs,ys):
            ymax = float(yrange_text.value)/2
            ys_mirror = np.flip(-(ys-ymax)+ymax)
            xs_mirror = np.flip(xs)
            x_total = np.append(xs,xs_mirror)
            y_total = np.append(ys,ys_mirror)
            return x_total,y_total

        def mirror_u2d(xs,ys):
            ymax = float(yrange_text.value)/2
            ys_mirror = np.flip(-(ys+ymax)-ymax)
            xs_mirror = np.flip(xs)
            x_total = np.append(xs,xs_mirror)
            y_total = np.append(ys,ys_mirror)
            return x_total,y_total

        def mirror_l2r(xs,ys):
            xmax = float(xrange_text.value)/2
            xs_mirror = np.flip(-(xs-xmax)+xmax)
            ys_mirror = np.flip(ys)
            x_total = np.append(xs,xs_mirror)
            y_total = np.append(ys,ys_mirror)
            return x_total,y_total

        def mirror_r2l(xs,ys):
            xmax = float(xrange_text.value)/2
            xs_mirror = np.flip(-(xs+xmax)-xmax)
            ys_mirror = np.flip(ys)
            x_total = np.append(xs,xs_mirror)
            y_total = np.append(ys,ys_mirror)
            return x_total,y_total

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
            if file_name[-3:] == 'gsf':
                metadata,data = helper.gsf_read(file_name)
                data = np.flipud(data)
                xrange_text.value = str(metadata['XReal']*1e9)
                yrange_text.value = str(metadata['YReal']*1e9)

                figure1.xaxis.axis_label = 'x'
                figure1.yaxis.axis_label = 'y'

                img2 = figure1.image(image=[data], color_mapper=color_mapper,
                               dh=[metadata['YReal']*1e9], dw=[metadata['XReal']*1e9], 
                               x=[-metadata['XReal']*1e9/2], y=[-metadata['YReal']*1e9/2])
                range_slider.start = data.min()
                range_slider.end = data.max()
                range_slider.value = data.min(),data.max()
                renderer = figure1.cross(x='x', y='y', source=source, color=line_color, size=10,line_width=cross_width)
            else:    # presumbly png or jpeg
                im = Image.open(file_name, 'r')
                pix_val = np.array(im.getdata())
                total_length = len(pix_val)
                N = int(np.sqrt(total_length))
                color_index = int(color_radio_button_group.active)
                Lx,Ly = im.size
                data = np.reshape(pix_val[:,color_index],(Ly,Lx))

                data = np.flipud(data)
                xrange_text.value = str(1)
                yrange_text.value = str(1)

                figure1.xaxis.axis_label = 'x'
                figure1.yaxis.axis_label = 'y'

                figure1.x_range.update(start=-0.55, end=0.55)
                figure1.y_range.update(start=-0.55, end=0.55)

                img2 = figure1.image(image=[data], color_mapper=color_mapper,\
                               dh=[1], dw=[1],x=[-0.5], y=[-0.5])
                range_slider.start = data.min()
                range_slider.end = data.max()
                range_slider.value = data.min(),data.max()
                renderer = figure1.cross(x='x', y='y', source=source, color=line_color, size=10,line_width=cross_width)

            
        file_input.on_change('value',update_figure)
        color_radio_button_group.on_click(update_figure)

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

        def update_line_color(attr,old,new):
            global line_color
            line_color = new
            p.glyph.line_color=new
            renderer = figure1.cross(x='x', y='y', source=source, color=new, size=10,line_width=cross_width)
        line_color_pick.on_change('color',update_line_color)

        def plot_line():

            x = source.data['x']
            y = source.data['y']
            
            x = np.array(x)
            y = np.array(y)
            if is_boundary_button.active == 0:   # is boundary

                if mirror_button.active == 0:      #left to right
                    x,y = mirror_l2r(x,y)
                elif mirror_button.active == 1:    #right to left
                    x,y = mirror_r2l(x,y)
                elif mirror_button.active == 2:    #up to down
                    x,y = mirror_u2d(x,y)
                else:                              #down to up
                    x,y = mirror_d2u(x,y)
            x = list(x)
            y = list(y)
            x.append(x[0])
            y.append(y[0])
            source.data['x'] = x
            source.data['y'] = y
            p = figure1.line(x, y, line_width=2,color=line_color)
            previous_line = p    
        plot_line_button.on_click(plot_line)


        # Layout
        ######################################################################################################
        load = column(row(file_text,file_input),
                    space5,
                    color_group_text,
                    color_radio_button_group,
                    space6,
                    previous_spline_text,
                    spline_file_input
                    )
        tab0_layout=Panel(child=load,title='Load files')

        plot = column(
                    row(xrange_text,yrange_text),
                    space2,
                    row(color_palette_menu,line_color_pick),
                    row(color_text,color_range_min,color_range_max),
                    range_slider,
                    )
        tab1_layout = Panel(child=plot,title='Adjust plot')

        mark = column(
                    is_boundary_text,
                    is_boundary_button,
                    mirror_text,
                    mirror_button,
                    space3,
                    line_number_text,
                    row(plot_line_button,clear_spline_button,save_spline_button),
                    save_all_button,
                    save_folder_text
                    )
        tab2_layout = Panel(child=mark,title='Mark points')

        tabs = Tabs(tabs=[tab0_layout,tab1_layout,tab2_layout],active=0)

        all_layout = column(title,space1,mark_text,space4,row(tabs,figure1))


        doc.add_root(all_layout)
        doc.title = "Point selection GUI"

