#!/usr/bin/env python
# coding: utf-8

# Comments guidelines:

##### [HEADING 1] #####
### [HEADING 2] ###
# Regular comment
# END [HEADING 2] #
#-- END [HEADING 2] --#

# --------------------

##### IMPORTS #####
import os
import numpy as np
import pandas as pd

from bokeh.themes import Theme
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Range1d, Select, Circle, MultiLine
from bokeh.layouts import column, row
from bokeh.transform import linear_cmap, log_cmap
from bokeh.palettes import Spectral11
from bokeh.models.tickers import FixedTicker

#-- END IMPORTS --#

##### PATHS #####
project_path = os.path.dirname(__file__)

final_data_path = os.path.join(project_path, 'data/final_df.csv')
rvs_path = os.path.join(project_path, 'data/rvs.npy')
xp_path = os.path.join(project_path, 'data/xp.npy')
rvs_embedded_path = os.path.join(project_path, 'data/rvs_embedded.npy')
xp_embedded_path = os.path.join(project_path, 'data/xp_embedded.npy')
rvs_wavelengths_path = os.path.join(project_path, 'data/rvs_wavelengths.npy')
#-- END PATHS --#

##### CONSTANTS #####
DEFAULT_THEME = 'dark_minimal' # 'caliber' | 'dark_minimal' | 'light_minimal' | 'night_sky' | 'contrast' | 'my_theme' (personalized theme defined in the root folder)
AUTOHIDE = False 
TOOLBAR_LOCATION = 'above' # 'above' | 'below' | 'left' | 'right
DEFAULT_COLOR = '#64A6BD'
DEFAULT_SIZE = 4
TEFF_PALETTE = ['#313695',
                '#4575b4',
                '#74add1',
                '#abd9e9',
                '#e0f3f8',
                '#ffffbf',
                '#fee090',
                '#fdae61',
                '#f46d43',
                '#d73027',
                '#a50026']

TEFF_PALETTE.reverse()
#-- END CONSTANTS --#

##### LOAD DATA #####
final_df = pd.read_csv(final_data_path)
xp = np.load(xp_path)
rvs = np.load(rvs_path)
xp_embedded = np.load(xp_embedded_path)
rvs_embedded = np.load(rvs_embedded_path)
rvs_wavelengths = np.load(rvs_wavelengths_path)
#-- END LOAD DATA --#

##### FUNCTION DEFINITION #####
def get_magnitude_sizes(magnitude_range):
    '''
    Returns a representation of the sizes of an object based on their magnitudes
    
    Parameters:
    - magnitude_range: 1d list/array with the object magnitudes
    '''
    _m_r = magnitude_range
    
    # We inverse the magnitude and move the initial range to 0: -g + max(g)
    sizes = -_m_r + max(_m_r)
    
    # We normalize between 0-1
    sizes = (sizes-min(sizes))/(max(sizes)-min(sizes))
    
    # We move the range to 1-10
    sizes = sizes*9 + 1
    
    return sizes


def get_low_resolution_rvs_spectra(rvs_spectra, rvs_wavelengths, reduction_factor=2):
    '''
    Reduce rvs spectra with the correct wavelengths by a defined factor
    
    Parameters:
    - rvs_spectra: 2d numpy array with the rvs spectra
    - rvs_wavelengths: 1d numpy array/list with the rvs wavelengths
    - reduction_factor: the size of the reduction 2=2x, 3=3x...
    '''
    return rvs_spectra[:,::reduction_factor], rvs_wavelengths[::reduction_factor]

#-- END FUNCTION DEFINITION --#

##### PLOT PREPARATION #####
mg_sizes = get_magnitude_sizes(magnitude_range=final_df.mg.values)

low_rvs, low_rvs_wavelengths = get_low_resolution_rvs_spectra(rvs_spectra=rvs, 
                                                              rvs_wavelengths=rvs_wavelengths,
                                                              reduction_factor=64)

source = ColumnDataSource(data={'source_id':final_df.index.values,
                                'g':final_df.mg.values,
                                'sizes': mg_sizes, 
                                'teff':final_df.teff_gspphot.values,
                                'logg':final_df.logg_gspphot.values,
                                'mh':final_df.mh_gspphot.values,
                                'rvs':low_rvs.tolist(),
                                'rvs_wavelengths':[low_rvs_wavelengths]*len(final_df.rvs_flux.values.tolist()),
                                'bp_rp':xp.tolist(),
                                'n_coeffs':[list(range(len(coeffs))) for coeffs in xp],
                                'x_xp_tsne':xp_embedded[:,0],
                                'y_xp_tsne':xp_embedded[:,1],
                                'x_rvs_tsne':rvs_embedded[:,0],
                                'y_rvs_tsne':rvs_embedded[:,1]})

### CREATION CUSTOM PALETTES ###
teff_mapper = log_cmap(field_name='teff', palette=TEFF_PALETTE, low=min(final_df.teff_gspphot), high=max(final_df.teff_gspphot))
mh_mapper = linear_cmap(field_name='mh', palette=Spectral11, low=min(final_df.mh_gspphot), high=max(final_df.mh_gspphot))
logg_mapper = linear_cmap(field_name='logg', palette=Spectral11, low=min(final_df.logg_gspphot), high=max(final_df.logg_gspphot))
# END CREATION CUSTOM PALETTES #
#-- END PLOT PREPARATION --#


##### FIGURE CREATION #####
 
# Define available tools for the user
TOOLS = "pan,box_zoom,wheel_zoom,box_select,lasso_select,help,reset"

figures = list()

hr_figure = figure(title='HR-diagram', tools=TOOLS, output_backend="webgl", toolbar_location=TOOLBAR_LOCATION)
figures.append(hr_figure)

bp_rp_figure = figure(title='BP-RP spectra', tools=TOOLS, output_backend="webgl", toolbar_location=TOOLBAR_LOCATION) 
figures.append(bp_rp_figure)

rvs_figure = figure(title='RVS spectra', tools=TOOLS, output_backend="webgl", toolbar_location=TOOLBAR_LOCATION, y_axis_type='log')
figures.append(rvs_figure)

xp_tsne_figure = figure(title='XP T-SNE', tools=TOOLS, output_backend="webgl", toolbar_location=TOOLBAR_LOCATION)
figures.append(xp_tsne_figure)

rvs_tsne_figure = figure(title='RVS T-SNE', tools=TOOLS, output_backend="webgl", toolbar_location=TOOLBAR_LOCATION)
figures.append(rvs_tsne_figure)
#-- END FIGURE CREATION --#


##### PLOTTING #####
### HR ###
hr_gr = hr_figure.circle(x='teff', y='g', size=DEFAULT_SIZE, source=source, line_color='black', color=DEFAULT_COLOR)
hr_figure.y_range.flipped = True
hr_figure.x_range = Range1d(15000, 2000)
hr_figure.xaxis.axis_label = 'Temperature'
hr_figure.yaxis.axis_label = 'Absolute Magnitude'


# Initialize selected and nonselected sources to be able to color them (https://docs.bokeh.org/en/latest/docs/user_guide/styling.html#selected-and-unselected-glyphs)
selected_circle = Circle(fill_alpha=1)
nonselected_circle = Circle(fill_alpha=0.2)

hr_gr.selection_glyph = selected_circle
hr_gr.nonselection_glyph = nonselected_circle
# --
# END HR #

### XP ###
bp_rp_gr = bp_rp_figure.multi_line(xs='n_coeffs', ys='bp_rp', source=source, color=DEFAULT_COLOR)
bp_rp_figure.xaxis.axis_label = 'Coefficients'
bp_rp_figure.yaxis.axis_label = 'Value'
bp_rp_figure.yaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
#bp_rp_figure.yaxis.major_label_orientation = "vertical"
#bp_rp_figure.y_axis_type="log"
#bp_rp_figure.yaxis.ticker = FixedTicker(ticks=[np.min(source.data['bp_rp']), np.max(source.data['bp_rp'])])


# Initialize selected and nonselected sources to be able to color them
selected_circle = MultiLine(line_alpha=1)
nonselected_circle = MultiLine(line_alpha=0.2)

bp_rp_gr.selection_glyph = selected_circle
bp_rp_gr.nonselection_glyph = nonselected_circle
# --
# END XP #

### RVS ###
rvs_gr = rvs_figure.multi_line(xs='rvs_wavelengths', ys='rvs', source=source, color=DEFAULT_COLOR)
rvs_figure.yaxis.axis_label = 'Flux'
rvs_figure.xaxis.axis_label = 'Wavelengths'
rvs_figure.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
#rvs_figure.yaxis.ticker = FixedTicker(ticks=[np.min(source.data['rvs']), np.max(source.data['rvs'])])

selected_circle = MultiLine(line_alpha=1)
nonselected_circle = MultiLine(line_alpha=0.2)

rvs_gr.selection_glyph = selected_circle
rvs_gr.nonselection_glyph = nonselected_circle
# END RVS #

### XP TSNE ###
xp_tsne_gr = xp_tsne_figure.circle(x='x_xp_tsne', y='y_xp_tsne', size=DEFAULT_SIZE, source=source, line_color='black', color=DEFAULT_COLOR)
xp_tsne_figure.yaxis.axis_label = 'Y'
xp_tsne_figure.xaxis.axis_label = 'X'
xp_tsne_figure.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
xp_tsne_figure.xaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

# Initialize selected and nonselected sources to be able to color them
selected_circle = Circle(fill_alpha=1)
nonselected_circle = Circle(fill_alpha=0.2)

xp_tsne_gr.selection_glyph = selected_circle
xp_tsne_gr.nonselection_glyph = nonselected_circle
# --
### END XP TSNE ###

### RVS TSNE ###
rvs_tsne_gr = rvs_tsne_figure.circle(x='x_rvs_tsne', y='y_rvs_tsne', size=DEFAULT_SIZE, source=source, line_color='black', color=DEFAULT_COLOR)
rvs_tsne_figure.yaxis.axis_label = 'Y'
rvs_tsne_figure.xaxis.axis_label = 'X'
rvs_tsne_figure.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
rvs_tsne_figure.xaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels


# Initialize selected and nonselected sources to be able to color them
selected_circle = Circle(fill_alpha=1)
nonselected_circle = Circle(fill_alpha=0.2)

rvs_tsne_gr.selection_glyph = selected_circle
rvs_tsne_gr.nonselection_glyph = nonselected_circle
# --
### END RVS TSNE ###

# We save all glyph renderer in a list
gr_list = [hr_gr, bp_rp_gr, rvs_gr, xp_tsne_gr, rvs_tsne_gr] # Just in case we wanted to modify common propoerties at once

# Set autohide parameter for each figure to the parameter defined in the constant AUTOHIDE
for fig in figures:
    fig.toolbar.autohide = AUTOHIDE    
#-- END PLOTTING --#

##### WIDGETS #####
### COLORMAP SELECT ###
def colormap_select_handler(attr, old, new):
    if new == 'Teff':
        hr_gr.glyph.fill_color = teff_mapper
        hr_gr.selection_glyph.fill_color = teff_mapper
        hr_gr.nonselection_glyph.fill_color = teff_mapper
        xp_tsne_gr.glyph.fill_color = teff_mapper
        xp_tsne_gr.selection_glyph.fill_color = teff_mapper
        xp_tsne_gr.nonselection_glyph.fill_color = teff_mapper
        rvs_tsne_gr.glyph.fill_color = teff_mapper
        rvs_tsne_gr.selection_glyph.fill_color = teff_mapper
        rvs_tsne_gr.nonselection_glyph.fill_color = teff_mapper
        bp_rp_gr.glyph.line_color = teff_mapper
        bp_rp_gr.selection_glyph.line_color = teff_mapper
        bp_rp_gr.nonselection_glyph.line_color = teff_mapper
        rvs_gr.glyph.line_color = teff_mapper
        rvs_gr.selection_glyph.line_color = teff_mapper
        rvs_gr.nonselection_glyph.line_color = teff_mapper
        return
    elif new == 'Logg':
        hr_gr.glyph.fill_color = logg_mapper
        hr_gr.selection_glyph.fill_color = logg_mapper
        hr_gr.nonselection_glyph.fill_color = logg_mapper
        xp_tsne_gr.glyph.fill_color = logg_mapper
        xp_tsne_gr.selection_glyph.fill_color = logg_mapper
        xp_tsne_gr.nonselection_glyph.fill_color = logg_mapper
        rvs_tsne_gr.glyph.fill_color = logg_mapper
        rvs_tsne_gr.selection_glyph.fill_color = logg_mapper
        rvs_tsne_gr.nonselection_glyph.fill_color = logg_mapper
        bp_rp_gr.glyph.line_color = logg_mapper
        bp_rp_gr.selection_glyph.line_color = logg_mapper
        bp_rp_gr.nonselection_glyph.line_color = logg_mapper
        rvs_gr.glyph.line_color = logg_mapper
        rvs_gr.selection_glyph.line_color = logg_mapper
        rvs_gr.nonselection_glyph.line_color = logg_mapper
        return
    elif new == 'Metallicity':
        hr_gr.glyph.fill_color = mh_mapper
        hr_gr.selection_glyph.fill_color = mh_mapper
        hr_gr.nonselection_glyph.fill_color = mh_mapper
        xp_tsne_gr.glyph.fill_color = mh_mapper
        xp_tsne_gr.selection_glyph.fill_color = mh_mapper
        xp_tsne_gr.nonselection_glyph.fill_color = mh_mapper
        rvs_tsne_gr.glyph.fill_color = mh_mapper
        rvs_tsne_gr.selection_glyph.fill_color = mh_mapper
        rvs_tsne_gr.nonselection_glyph.fill_color = mh_mapper
        bp_rp_gr.glyph.line_color = mh_mapper
        bp_rp_gr.selection_glyph.line_color = mh_mapper
        bp_rp_gr.nonselection_glyph.line_color = mh_mapper
        rvs_gr.glyph.line_color = mh_mapper
        rvs_gr.selection_glyph.line_color = mh_mapper
        rvs_gr.nonselection_glyph.line_color = mh_mapper
        return
    elif new == 'Default':
        hr_gr.glyph.fill_color = DEFAULT_COLOR
        hr_gr.selection_glyph.fill_color = DEFAULT_COLOR
        hr_gr.nonselection_glyph.fill_color = DEFAULT_COLOR
        xp_tsne_gr.glyph.fill_color = DEFAULT_COLOR
        xp_tsne_gr.selection_glyph.fill_color = DEFAULT_COLOR
        xp_tsne_gr.nonselection_glyph.fill_color = DEFAULT_COLOR
        rvs_tsne_gr.glyph.fill_color = DEFAULT_COLOR
        rvs_tsne_gr.selection_glyph.fill_color = DEFAULT_COLOR
        rvs_tsne_gr.nonselection_glyph.fill_color = DEFAULT_COLOR
        bp_rp_gr.glyph.line_color = DEFAULT_COLOR
        bp_rp_gr.selection_glyph.line_color = DEFAULT_COLOR
        bp_rp_gr.nonselection_glyph.line_color = DEFAULT_COLOR
        rvs_gr.glyph.line_color = DEFAULT_COLOR
        rvs_gr.selection_glyph.line_color = DEFAULT_COLOR
        rvs_gr.nonselection_glyph.line_color = DEFAULT_COLOR
        return

colormap_select = Select(title="Colormap:", value="Default", options=["Default", "Teff", "Logg", "Metallicity"], 
                sizing_mode='stretch_height')

colormap_select.on_change("value", colormap_select_handler)
# END COLORMAP SELECT #

### SIZE SELECT ###
def size_select_handler(attr, old, new):
    if new == 'Default':
        hr_gr.glyph.size = DEFAULT_SIZE
        xp_tsne_gr.glyph.size = DEFAULT_SIZE
        rvs_tsne_gr.glyph.size = DEFAULT_SIZE
        return
    elif new == 'Magnitude':
        hr_gr.glyph.size = 'sizes' # name of the ColumnDataSource column
        xp_tsne_gr.glyph.size = 'sizes'
        rvs_tsne_gr.glyph.size = 'sizes'
        return

size_select = Select(title="Size:", value="Default", options=["Default", "Magnitude"], 
                sizing_mode='stretch_height')

size_select.on_change("value", size_select_handler)
# END SIZE SELECT #

### THEME SELECT ###
def theme_select_handler(attr, old, new):
    if (new == 'my_theme'):
        curdoc().theme = Theme(filename='./{}.json'.format(new))
    else:
        curdoc().theme = new

theme_select = Select(title="Theme:", value=DEFAULT_THEME, 
                      options=['my_theme', 'caliber', 'dark_minimal', 'light_minimal', 'night_sky', 'contrast'], 
                      sizing_mode='stretch_height')

theme_select.on_change("value", theme_select_handler)
# END SIZE SELECT #
#-- END WIDGETS --#

##### LAYOUT #####
# Columns for xp and rvs spectra
spectra_figure = column([bp_rp_figure, rvs_figure], sizing_mode='stretch_both')

# Final Layout
p = column(row(colormap_select, size_select, theme_select, sizing_mode='stretch_width', height=60),
           row(hr_figure, spectra_figure, sizing_mode='stretch_both'),
           row(xp_tsne_figure, rvs_tsne_figure, sizing_mode='stretch_both'), sizing_mode='stretch_both')

#-- END LAYOUT --#

# Add final layout to the document
curdoc().add_root(p)

# Define default theme
if (DEFAULT_THEME != 'my_theme'):
    curdoc().theme = DEFAULT_THEME
else:
    curdoc().theme = Theme(filename='./my_theme.json')

# TODO: To change the widget styles https://stackoverflow.com/questions/43057328/change-colour-of-bokeh-buttons

# Define title
curdoc().title = 'GAIA DR3'