import pandas as pd
import numpy as np
import tkinter as tk
import sys

from bokeh.io import output_file, show      # if displaying in-app will need save instead of show
from bokeh.models import (BasicTicker, ColorBar, ColumnDataSource, CustomJS, TapTool,
                          LogColorMapper, PrintfTickFormatter, HoverTool)
from bokeh.events import Tap
from bokeh.plotting import figure, curdoc
#from bokeh.sampledata.unemployment1948 import data
from bokeh.transform import transform
from bokeh.layouts import gridplot
from bokeh.resources import INLINE
from tkinter import filedialog
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

# Function Name: Envelope Histogram
# Input: 1 list (or pandas dataframe?)
# Output: updates input, no output?
# Description: This function takes a list (of the data read from the input ms1ft file) and 
def EnvelopeHistogram(df_ms1ft):
    envelope = list(df_ms1ft['Envelope'])
    carb_isotope = []
    carb_abundance = []
    convert = []
    pool_c13 = []
    pool_isoabd = []
     
    for distribution in envelope:
        for idx, val in enumerate(distribution):
            if val == ',': 
                link = "".join(convert)
                carb_isotope.append(int(link))
                convert = []
            elif val == ';' or idx == (len(distribution)-1): # older versions of ms1ft have Envelopes that end with ';' vs. an empty space
                link = "".join(convert)
                carb_abundance.append(float(link))
                convert = []
            else:
                convert.append(val)
        
        pool_c13.append(carb_isotope)
        pool_isoabd.append(carb_abundance)
        carb_isotope,carb_abundance = [],[]
    df_ms1ft['C13'],df_ms1ft['IsoAbd'] = pool_c13, pool_isoabd 

# When run, the program prompts for the user to upload an MS1FT file
ms1ft_file = filedialog.askopenfilename(title="Select an MS1FT File", filetypes=[("Select an MS1FT File","*.ms1ft")])

# The abbreviated file name 'filename.ms1ft' of the uploaded file is extracted from its path '.../.../.../.../filename.ms1ft'
filename = str(ms1ft_file)[::-1]        # takes the uploaded file path as a string, reverses it, and saves this to the variable filename
for i in range(len(filename)):
    if filename[i] == '/':
        ext_filename = filename[0:i][::-1]    # takes reversed file path up to the first '/', reversed, and saves this to the variable ext_filename
        break

# The MS1FT column values MUST be the following:
    # FeatureID, MinScan, MaxScan, MinCharge, MaxCharge, MonoMass,
    # RepScan, RepCharge, RepMz, Abundance, ApexScanNum, ApexIntensity,
    # MinElutionTime, MaxElutionTime, ElutionLength, Envelope, LikelihoodRatio                
if len(ms1ft_file) > 0:
    df_ms1ft = pd.read_csv(ms1ft_file,sep='\t')     # reads input file (tab delimited) into a pandas dataframe
    if df_ms1ft.columns[0] != "FeatureID":          # to make sure the file was formatted correctly, check that the first column heading is "FeatureID"
        messagebox.showerror("File Error", "Check the MS1FT file: Expected 'FeatureID' as first column!") # question: is this the only column we should check?
        sys.exit()
    else:
        df_ms1ft = df_ms1ft.sort_values(by='MonoMass').set_index(keys='MonoMass')   # sets the 'MonoMass' datapoint as the key for its corresponding data, and sorts the dataframe by it
else:
    messagebox.showerror("File Error", "Selected file has no data.")
    sys.exit()

output_file("featuremap_"+ext_filename+".html", mode='inline')  # opens an HTML file (containing the feature map) in the browser

EnvelopeHistogram(df_ms1ft)                                     # forms envelope histogram out of sorted dataframe containing ms1ft file data

source = ColumnDataSource(df_ms1ft)
source2 = ColumnDataSource(data=dict(x=[], y=[]))

colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LogColorMapper(palette=colors, low=df_ms1ft['Abundance'].min(), high=df_ms1ft['Abundance'].max())

p = figure(width=1000, height=800, title="Feature Map of "+ext_filename,
           x_range=(0,df_ms1ft['MaxElutionTime'].max()+1), y_range=(0,df_ms1ft.index.max()+1),
           toolbar_location="right",  x_axis_location="below",active_drag="box_zoom",active_scroll="wheel_zoom",)

iso_distrib = figure(width = 500, height = 400, title="Isotopic Distribution",x_axis_label="C13", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                    active_scroll="wheel_zoom",y_axis_label="Rel. Abundance", active_drag="box_zoom")
 
z = iso_distrib.vbar(x='x', width=0.5, bottom=0, top='y', color="red", source=source2)


mass = p.rect(x="MinElutionTime", y="MonoMass", width='ElutionLength', height=10, source=source,
       line_color=None, fill_color=transform('Abundance', mapper))

p.add_tools(TapTool())

p.js_on_event(Tap, CustomJS(args=dict(source=source, source2=source2,title=iso_distrib.title), code="""
    // get data source from Callback args
    let data = Object.assign({}, source.data);
    source2.data.x = data.C13[source.selected.indices];
    source2.data.y = data.IsoAbd[source.selected.indices];
    title.text = 'Isotopic Distribution for: '+(new String(data.MonoMass[source.selected.indices]));
    source2.change.emit();
""")
)

color_bar = ColorBar(color_mapper=mapper, title="Log Abundance")

p.add_layout(color_bar, 'right')

p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.xaxis.axis_label = 'Retention Time (min)'
p.yaxis.axis_label = 'Monoisotopic Mass'
p.axis.major_label_text_font_size = "20px"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = 1.0
p.axis.axis_label_text_font_size = "20px"

grid = gridplot([[p,iso_distrib]], merge_tools=False)
show(grid)
