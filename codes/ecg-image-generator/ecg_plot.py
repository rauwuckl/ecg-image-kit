import os, sys, argparse
import numpy as np
import random
from scipy.io import savemat, loadmat
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import AutoMinorLocator
from helper_functions import convert_inches_to_seconds,convert_inches_to_volts,convert_mm_to_volts,convert_mm_to_seconds
from math import ceil 
from PIL import Image
from numpy import asarray
from random import randint
import matplotlib.patches as patches
import csv
import matplotlib.patches as patches

standard_values = {'y_grid_size' : 0.5,
                   'x_grid_size' : 0.2,
                   'y_grid_inch' : 0.196,
                   'x_grid_inch' : 0.196,
                   'grid_line_width' : 0.5,
                   'lead_name_offset' : 0.5,
                   'lead_fontsize' : 11,
                   'x_gap' : 1,
                   'y_gap' : 0.5,
                   'display_factor' : 1,
                   'line_width': 0.75,
                   'row_height' : 8,
                   'dc_offset_length' : 0.2,
                   'lead_length' : 3,
                   'V1_length' : 12,
                   'width' : 11,
                   'height' : 8.5
                   }

#standard_major_colors = {'colour1' : (1,0.6823,0.776),
                          #'colour2' : (1,0.796,0.866),
                          #'colour3' : (0.933,0.8235,0.8),
                          #'colour4' : (0.996,0.807,0.8039),
                          #'colour5' : (0.611,0.627,0.647), 
                          #'colour6' : (0.4901,0.498,0.513), 
                          #'colour7' : (0.4274,0.196,0.1843),
                          #'colour8' : (0.992,0.7529,0.7254),
                          #'colour9' : (0.9215,0.9372,0.9725)
    #}

standard_major_colors = {'colour1' : (1,0.6823,0.776),
                          'colour2' : (1,0.796,0.866),
                          'colour3' : (0.933,0.8235,0.8),
                          'colour4' : (0.996,0.807,0.8039),
                          'colour5' : (0.4274,0.196,0.1843),
                          'colour6' : (0.992,0.7529,0.7254)
    }


standard_minor_colors = {'colour1' : (0.9843,0.9019,0.9529),
                         'colour2' : (0.996,0.9294,0.9725),
                         'colour3' : (0.9529,0.8745,0.8549),
                         'colour4' : (0.996,0.9529,0.9529),
                         'colour5' : (0.5882,0.4196,0.3960),
                         'colour6' : (0.996,0.8745,0.8588)
    }

#standard_minor_colors = {'colour1' : (0.9843,0.9019,0.9529),
                         #'colour2' : (0.996,0.9294,0.9725),
                         #'colour3' : (0.9529,0.8745,0.8549),
                         #'colour4' : (0.996,0.9529,0.9529),
                         #'colour5' : (0.7607,0.7725,0.7843),
                         #'colour6' : (0.6039,0.6235,0.6274),
                         #'colour7' : (0.5882,0.4196,0.3960),
                         #'colour8' : (0.996,0.8745,0.8588),
                         #'colour9' : (0.9568,0.9686,0.9843)
    #}

papersize_values = {'A0' : (33.1,46.8),
                    'A1' : (33.1,23.39),
                    'A2' : (16.54,23.39),
                    'A3' : (11.69,16.54),
                    'A4' : (8.27,11.69),
                    'letter' : (8.5,11)
                    }

leadNames_12 = ["III", 'aVF', 'V3', 'V6', 'II', 'aVL', 'V2', 'V5', 'I', 'aVR', 'V1', 'V4']


def inches_to_dots(value,resolution):
    return (value * resolution)

#Function to plot raw ecg signal
def ecg_plot(
        ecg, 
        sample_rate, 
        columns,
        rec_file_name,
        output_dir,
        resolution,
        pad_inches,
        lead_index,
        full_mode,
        store_text_bbox,
        units          = '',
        papersize      = '',
        x_gap          = standard_values['x_gap'],
        y_gap          = standard_values['y_gap'],
        display_factor = standard_values['display_factor'],
        line_width     = standard_values['line_width'],
        title          = '',  
        style          = None,
        row_height     = standard_values['row_height'],
        show_lead_name = True,
        show_grid      = False,
        show_dc_pulse  = False,
        y_grid = 0,
        x_grid = 0,
        is_gt = False,
        standard_colours = False,
        bbox = False
        ):
    #Inputs :
    #ecg - Dictionary of ecg signal with lead names as keys
    #sample_rate - Sampling rate of the ecg signal
    #lead_index - Order of lead indices to be plotted
    #columns - Number of columns to be plotted in each row
    #x_gap - gap between paper x axis border and signal plot
    #y_gap - gap between paper y axis border and signal plot
    #line_width - Width of line tracing the ecg
    #title - Title of figure
    #style - Black and white or colour
    #row_height - gap between corresponding ecg rows
    #show_lead_name - Option to show lead names or skip
    #show_dc_pulse - Option to show dc pulse
    #show_grid - Turn grid on or off


    #Initialize some params
    #secs represents how many seconds of ecg are plotted
    #leads represent number of leads in the ecg
    #rows are calculated based on corresponding number of leads and number of columns

    matplotlib.use("Agg")
    randindex = randint(0,99)
    random_sampler = random.uniform(-0.05,0.004)

    #check if the ecg dict is empty
    if ecg == {}:
        return 

    secs = len(list(ecg.items())[0][1])/sample_rate

    leads = len(lead_index)

    rows  = int(ceil(leads/columns))

    if(full_mode!='None'):
        rows+=1
        leads+=1
    
    #Grid calibration
    #Each big grid corresponds to 0.2 seconds and 0.5 mV
    #To do: Select grid size in a better way
    y_grid_size = standard_values['y_grid_size']
    x_grid_size = standard_values['x_grid_size']
    grid_line_width = standard_values['grid_line_width']
    lead_name_offset = standard_values['lead_name_offset']
    lead_fontsize = standard_values['lead_fontsize']

    #Set max and min coordinates to mark grid. Offset x_max slightly (i.e by 1 column width)

    if papersize=='':
        width = standard_values['width']
        height = standard_values['height']
    else:
        width = papersize_values[papersize][1]
        height = papersize_values[papersize][0]


    if(not is_gt):
        y_grid = standard_values['y_grid_inch'] + random_sampler
        x_grid = standard_values['x_grid_inch'] + random_sampler
        y_grid_dots = y_grid*resolution
        x_grid_dots = x_grid*resolution
 
    #row_height = height * y_grid_size/(y_grid*(rows+2))
    row_height = (height * y_grid_size/y_grid)/(rows+2)
    x_max = width * x_grid_size / x_grid
    x_min = 0
    x_gap = np.floor(((x_max - (columns*secs))/2)/0.2)*0.2
    y_min = 0
    y_max = height * y_grid_size/y_grid
    #Set figure and subplot sizes
    fig, ax = plt.subplots(figsize=(width, height))
   
    fig.subplots_adjust(
        hspace = 0, 
        wspace = 0,
        left   = 0,  
        right  = 1,  
        bottom = 0,  
        top    = 1
        )

    fig.suptitle(title)

    #Mark grid based on whether we want black and white or colour

    if (style == 'bw'):
        color_major = (0.4,0.4,0.4)
        color_minor = (0.75, 0.75, 0.75)
        color_line  = (0,0,0)
    elif(standard_colours):
        random_colour_index = randint(1,6)
        color_major = standard_major_colors['colour'+str(random_colour_index)]
        color_minor = standard_minor_colors['colour'+str(random_colour_index)]
        randcolorindex_grey = randint(0,24)
        grey_random_color = random.uniform(0,0.2)
        if(is_gt):
            color_line = (0,0,0)
        else:
            color_line  = (grey_random_color,grey_random_color,grey_random_color)
    else:
        randcolorindex_red = randint(0,24)
        major_random_color_sampler_red = random.uniform(0,0.8)
        randcolorindex_green = randint(0,24)
        major_random_color_sampler_green = random.uniform(0,0.5)
        randcolorindex_blue = randint(0,24)
        major_random_color_sampler_blue = random.uniform(0,0.5)

        randcolorindex_minor = randint(0,24)
        minor_offset = random.uniform(0,0.2)
        minor_random_color_sampler_red = major_random_color_sampler_red + minor_offset
        minor_random_color_sampler_green = random.uniform(0,0.5) + minor_offset
        minor_random_color_sampler_blue = random.uniform(0,0.5) + minor_offset

        randcolorindex_grey = randint(0,24)
        grey_random_color = random.uniform(0,0.2)
        color_major = (major_random_color_sampler_red,major_random_color_sampler_green,major_random_color_sampler_blue)
        color_minor = (minor_random_color_sampler_red,minor_random_color_sampler_green,minor_random_color_sampler_blue)
        if(is_gt):
            color_line = (0,0,0)
        else:
            color_line  = (grey_random_color,grey_random_color,grey_random_color)

    #Set grid
    #Standard ecg has grid size of 0.5 mV and 0.2 seconds. Set ticks accordingly
    if(show_grid):
        ax.set_xticks(np.arange(x_min,x_max,x_grid_size))    
        ax.set_yticks(np.arange(y_min,y_max,y_grid_size))
        ax.minorticks_on()
        
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))

        #set grid line style
        ax.grid(which='major', linestyle='-', linewidth=grid_line_width, color=color_major)
        
        ax.grid(which='minor', linestyle='-', linewidth=grid_line_width, color=color_minor)
        
    else:
        ax.grid(False)
    ax.set_ylim(y_min,y_max)
    ax.set_xlim(x_min,x_max)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    lead_num = 0
    
    #Step size will be number of seconds per sample i.e 1/sampling_rate
    step = (1.0/sample_rate)

    dc_offset = 0
    if(show_dc_pulse):
        dc_offset = sample_rate*standard_values['dc_offset_length']*step
    #Iterate through each lead in lead_index array.
    y_offset = (row_height/2)
    x_offset = 0

    text_bbox = {}
    
    for i in np.arange(len(lead_index)):
        if len(lead_index) == 12:
            leadName = leadNames_12[i]
        else:
            leadName = lead_index[i]
        #y_offset is computed by shifting by a certain offset based on i, and also by row_height/2 to account for half the waveform below the axis
        if(i%columns==0):

            y_offset += row_height
        
        #x_offset will be distance by which we shift the plot in each iteration
        if(columns>1):
            x_offset = (i%columns)*secs
            
        else:
            x_offset = 0

        #Create dc pulse wave to plot at the beginning of plot. Dc pulse will be 0.2 seconds
        x_range = np.arange(0,sample_rate*standard_values['dc_offset_length']*step + 4*step,step)
        dc_pulse = np.ones(len(x_range))
        dc_pulse = np.concatenate(((0,0),dc_pulse[2:-2],(0,0)))

        #Print lead name at .5 ( or 5 mm distance) from plot
        if(show_lead_name and not is_gt):
                    t1 = ax.text(x_offset + x_gap, 
                            y_offset-lead_name_offset - 0.2, 
                            leadName, 
                            fontsize=lead_fontsize)
                    
                    if (store_text_bbox):
                        renderer1 = fig.canvas.get_renderer()
                        transf = ax.transData.inverted()
                        bb = t1.get_window_extent(renderer = fig.canvas.renderer)
                        bb_datacoords = bb.transformed(transf)
                        h, w = fig.get_size_inches()*fig.dpi 
                        text_bbox[leadName] = [bb.x0, w - bb.y0, bb.x1, w - bb.y1]
                                      
            

        #If we are plotting the first row-1 plots, we plot the dc pulse prior to adding the waveform
        if(columns == 1 and i in np.arange(0,rows)):
            if(show_dc_pulse and not is_gt):
                #Plot dc pulse for 0.2 seconds with 2 trailing and leading zeros to get the pulse
                ax.plot(x_range + x_offset + x_gap,
                        dc_pulse+y_offset,
                        linewidth=line_width * 1.5, 
                        color=color_line
                        )
                
        elif(columns == 4 and i == 0 or i == 4 or i == 8):
            if(show_dc_pulse and not is_gt):
                #Plot dc pulse for 0.2 seconds with 2 trailing and leading zeros to get the pulse
                ax.plot(np.arange(0,sample_rate*standard_values['dc_offset_length']*step + 4*step,step) + x_offset + x_gap,
                        dc_pulse+y_offset,
                        linewidth=line_width * 1.5, 
                        color=color_line
                        )
                       
        ax.plot(np.arange(0,len(ecg[leadName])*step,step) + x_offset + dc_offset + x_gap, 
                ecg[leadName] + y_offset,
                linewidth=line_width, 
                color=color_line
                )
        
        if(not is_gt):
            start_ind = round((x_offset + dc_offset + x_gap)*x_grid_dots/x_grid_size)
            end_ind = round((x_offset + dc_offset + x_gap + len(ecg[leadName])*step)*x_grid_dots/x_grid_size)

            with open(os.path.join(output_dir,"gridsizes.csv"), 'a',newline='') as file:
                writer = csv.writer(file)
                datarow = [rec_file_name,x_grid_dots,y_grid_dots,leadName,start_ind, end_ind]
                writer.writerow(datarow)

    #Plotting longest lead for 12 seconds
    if(full_mode!='None'):
        if(show_lead_name and not is_gt):
            t1 = ax.text(x_gap, 
                    row_height/2-lead_name_offset, 
                    full_mode, 
                    fontsize=lead_fontsize)
            
            if (store_text_bbox):
                        renderer1 = fig.canvas.get_renderer()
                        transf = ax.transData.inverted()
                        bb = t1.get_window_extent(renderer = fig.canvas.renderer)
                        bb_datacoords = bb.transformed(transf)
                        h, w = fig.get_size_inches()*fig.dpi 
                        text_bbox[full_mode] = [bb.x0, w - bb.y0, bb.x1, w - bb.y1]

        if(show_dc_pulse and not is_gt):
            ax.plot(x_range + x_gap,
                    dc_pulse + row_height/2-lead_name_offset + 0.8,
                    linewidth=line_width * 1.5, 
                    color=color_line
                    )
        
        dc_full_lead_offset = 0 
        if(show_dc_pulse):
            dc_full_lead_offset = sample_rate*standard_values['dc_offset_length']*step
        
        ax.plot(np.arange(0,len(ecg['full'+full_mode])*step,step) + x_gap + dc_full_lead_offset, 
                    ecg['full'+full_mode] + row_height/2-lead_name_offset + 0.8,
                    linewidth=line_width, 
                    color=color_line
                    )

        if(not is_gt):
            start_ind = round((dc_full_lead_offset + x_gap)*x_grid_dots/x_grid_size)
            end_ind = round((dc_full_lead_offset + x_gap + len(ecg['full'+full_mode])*step)*x_grid_dots/x_grid_size)

            with open(os.path.join(output_dir,"gridsizes.csv"), 'a',newline='') as file:
                writer = csv.writer(file)
                datarow = [rec_file_name,x_grid_dots,y_grid_dots,'full'+full_mode,start_ind, end_ind]
                writer.writerow(datarow)

    head, tail = os.path.split(rec_file_name)
    rec_file_name = os.path.join(output_dir, tail)
    if(is_gt):
        plt.savefig(os.path.join(output_dir,tail + '-gt'+'.png'),dpi=resolution)
        plt.close(fig)
       

    else:
        if(store_text_bbox):
            if(os.path.exists(os.path.join(output_dir, 'text_bouding_box'))  == False):
                os.mkdir(os.path.join(output_dir, 'text_bouding_box'))
            
            with open(os.path.join(output_dir, 'text_bouding_box', tail + '.txt'), 'w') as f:
                for i, key in enumerate(text_bbox):
                    for val in text_bbox[key]:
                        f.write(str(val))
                        f.write(',')
                    f.write(key)
                    f.write('\n')
                    
        plt.savefig(os.path.join(output_dir,tail +'.png'),dpi=resolution)
        plt.close(fig)
        plt.clf()
        plt.cla()

        #plt.show()

    if(not is_gt):
        if(bbox):
            with open(os.path.join(output_dir,"Coordinates.csv"), 'a',newline='') as file:
                writer = csv.writer(file)
                y_offset = (row_height/2)
                for i in np.arange(len(lead_index)):
                    if(i%columns==0):
                        y_offset += row_height
                    
                    #x_offset will be distance by which we shift the plot in each iteration
                    if(columns>1):
                        x_offset = (i%columns) * secs
                    else:
                        x_offset = 0

                    #Plot raw waveform for 3 seconds, offset is adjusted based on lead index
                    bb_width = len(ecg[lead_index[i]])*step
                    bb_height = max(ecg[lead_index[i]]) - min(ecg[lead_index[i]])

                    # Create a Rectangle patch
                    rect = patches.Rectangle((x_offset + dc_offset + x_gap, y_offset+min(ecg[lead_index[i]])), bb_width, bb_height, linewidth=1, edgecolor='r', facecolor='none')

                    #Get X and Y coordinates of centre of bounding box
                    label = 0

                    box_edges = rect.get_bbox().get_points()
                    x_center_normalized = ((box_edges[0][0] + box_edges[1][0])/2 - x_min)/(x_max-x_min)
                    y_center_normalized = 1 - ((box_edges[0][1] + box_edges[1][1])/2 - y_min)/(y_max - y_min)
                    bb_width_normalized = bb_width/(x_max-x_min)
                    bb_height_normalized = bb_height/(y_max - y_min)

                    data_row = [os.path.join(output_dir,tail + '-gt'+'.png'),label,x_center_normalized,y_center_normalized,bb_width_normalized,bb_height_normalized]
                    writer.writerow(data_row)

                    # Add the patch to the Axes
                    ax.add_patch(rect)

                if(full_mode!='None'):
                    dc_full_lead_offset = 0 

                    if(show_dc_pulse):
                        dc_full_lead_offset = sample_rate*standard_values['dc_offset_length']*step

                    bb_width = len(ecg['full'+full_mode])*step
                    bb_height = max(ecg['full'+full_mode]) - min(ecg['full'+full_mode])
                    rect = patches.Rectangle((x_gap + dc_full_lead_offset, row_height/2+(rows-1)*row_height + min(ecg['full'+full_mode])), bb_width, bb_height, linewidth=1, edgecolor='r', facecolor='none')

                    label = 1
                    box_edges = rect.get_bbox().get_points()
                    x_center_normalized = ((box_edges[0][0] + box_edges[1][0])/2 - x_min)/(x_max-x_min)
                    y_center_normalized = 1 - ((box_edges[0][1] + box_edges[1][1])/2 - y_min)/(y_max - y_min)
                    bb_width_normalized = bb_width/(x_max-x_min)
                    bb_height_normalized = bb_height/(y_max - y_min)
                    data_row = [os.path.join(output_dir,tail + '-gt'+'.png'),label,x_center_normalized,y_center_normalized,bb_width_normalized,bb_height_normalized]
                    writer.writerow(data_row)

                    # Add the patch to the Axes
                    ax.add_patch(rect)
        
                plt.savefig(os.path.join(output_dir,tail + '-boxed'+'.png'),dpi=resolution)
                plt.close(fig)
                plt.clf()
                plt.cla()

    if pad_inches!=0:
        if(is_gt):
            ecg_image = Image.open(os.path.join(output_dir,tail+'-gt.png'))
        else:
            ecg_image = Image.open(os.path.join(output_dir,tail +'.png'))
            if(bbox):
                ecg_image_boxed = Image.open(os.path.join(output_dir,tail + '-boxed'+'.png'))
        right = pad_inches * resolution
        left = pad_inches * resolution
        top = pad_inches * resolution
        bottom = pad_inches * resolution
        width, height = ecg_image.size
        new_width = width + right + left
        new_height = height + top + bottom
        result_image = Image.new(ecg_image.mode, (new_width, new_height), (255, 255, 255))
        result_image.paste(ecg_image, (left, top))
        if(not is_gt):
            if(bbox):
                result_image_boxed = Image.new(ecg_image_boxed.mode, (new_width, new_height), (255, 255, 255))
                result_image_boxed.paste(ecg_image_boxed, (left, top))
        if(is_gt):
            result_image.save(os.path.join(output_dir,tail + '-gt'+'.png'))
        else:
            result_image.save(os.path.join(output_dir,tail +'.png'))
            if(bbox):
                result_image_boxed.save(os.path.join(output_dir,tail + '-boxed'+'.png'))

        plt.close('all')
        plt.close(fig)
        plt.clf()
        plt.cla()

    return x_grid,y_grid
       