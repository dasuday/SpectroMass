"""
TITLE: Mass_Finder_and_Quantifier.py or Spectromass.py?

INPUT: msalign file(s) (.csv)
*must be in same folder as application

OUTPUT: interactive quant graphs (.html), quant data (.csv)

DESCRIPTION: This application takes the msalign file(s) resulting from running FlashDECONV on the mass spectrum of some sample(s), and uses this data along with user input retrieved in app to plot the mass vs. abundance of all samples on the same interactive mass vs. abundance graph. User input is straightforward & minimal:
   - Users will be prompted to upload msalign files (at least one is required).
   - Each file can be re-labeled (e.g. "control group", "stage 1") in app immediately after uploading. These labels help distinguish between samples on the graph legend. A default label ("exp. group") is provided.
   - Users are prompted to specify the mass ranges, retention times, etc that they are interested in seeing plotted. Default values are provided.
The interactive output graph (with a quality control graph for each file uploaded) is generated in browser, where users can further inspect & compare the samples' data. A csv file containing the same information as the main graph is saved to the same folder as the application and input files.

NOTE: While the program runs, many additional features (such as the "New Analysis" and "Test" buttons) are broken and the code (& console) are messy. Currently we've been working on switching to pandas, so several functions have "two versions" of code with one commented out. This switch has been difficult because of these functions kind of depend on each other. So all of the commented code (attempts to use pandas) result in errors, but I'm not sure if that's because I'm doing things wrong or just because without everything in the same format throughout, I get a bunch of inconsistencies. I'm running into a similar problem with what I was hoping would be a solution, the "Test" function - I don't know how to get all these functions from different classes to talk to each other.
"""

import timeit
    # used to determine function runtime while editing & testing
import pandas as pd
    # data anlysis toolkit
        # used to convert data table (from reading .csv file) into NumPy matrix array in
        # df_ms1ft = pd.read_csv(file_path)
import numpy as np
    # numpy: for working with arrays
    # append, reshape, array
import tkinter as tk
    # tkinter: for Tcl/Tk GUI toolkit (standard, n  ot necessarily best?)
    # Frame, Button, Label, Entry, Checkbutton
import time, sys    # -----------------------------------------------------------------> import time?
    # time: for time-related functions, such as strptime() used in output_quant_file and qc_graph
    # sys: to access system-specific parameters and functions, i/o
        # seemse like it's only being used for one output line, which is commented out
import matplotlib                               # remove and test
import matplotlib.pyplot as plt
    # pyplot: makes matplotlib work like matlab, used for plotting qc graphs
import matplotlib.backends._tkagg
matplotlib.use("TkAgg")
    # backends._tkagg: to use matplotlib with tkinter, more imports from here below
from matplotlib import style
style.use('ggplot')
    # style: used to customized appearance of plots,
    # ggplot: a style that emulates the ggplot package for R
import os, time, os.path     # -----------------------------------------------------------------> import time?
    # os: "provides a portable way of using operation system dependent functionality"
    # i'm guessing these are just used to access the date&time on the computer, for plotting?
import statistics
    # statistics: don't think we need everything in here, just pstdev and mean
    # used in calculate_avg_stdev() in QuantOutput
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    # FigureCanvasTkAgg: interface between the Figure and Tkinter Canvas
    # NavigationToolbar2Tk: built-in toolbar for the figure on the graph
    # these make the graph interactive as desired
    # in makegraph(), specifications for toolbar are passed in as parameters
from matplotlib.figure import Figure
    # Figure: contains all plot elements, used to control spacing of subplots & container
    # needed for multiple qc graphs in case of multiple msalign file uploads
from operator import itemgetter, attrgetter         # not sure how/where these are used
    # itemgetter: constructs a callable that assumes an iterable object and returns the nth element
    # attrgetter: returns a callable object that fetches one/more attributes from its operand
from datetime import datetime
    # datetime: such as datetime, used in output_quant_file and qc_graphs
from tkinter import filedialog as fd                                    # REMOVE
    # filedialog: provides a set of dialogs to use when working with file, such as open, save, etc.
    # used askopenfilename once in msalignfile() in FileSelection
from tkinter import messagebox as mb
    # messagebox: provides a template base class for messageboxes
    # used to display error messages during file uploads
from tkinter import ttk
    # ttk: provides acces to Tk themed widge set - buttons, etc.
from tkinter import *                           # remove and test
from collections.abc import Iterable
    # Iterable: provides abstract base classes that can be used to test whether a class
    # provides a particular interface, so like issubclass() or isinstance()
from bokeh.models import ColumnDataSource, Whisker, HoverTool, Legend, LegendItem, Tabs, Div, BasicTicker, ColorBar, CustomJS, TapTool, LogColorMapper, PrintfTickFormatter, TabPanel, Dropdown
    # ColumnDataSource: provides data to the glyphs of plot so you can pass in lists, etc.
    # Whisker: adds a whisker for error margins
    # HoverTool: passive inspector tool, for actions to occur when cursor hovering
    # Legend: allows us more advanced control of the legend object provided by bokeh for the graphs
    # LegendItem: set True to have legend visible, False to hide legend
    # Tabs and Panel: Lets you use panels and tabs for graphs
    # Div: corresponds to an HTML <div> element
from bokeh.plotting import figure, show, curdoc
    # figure: a function that creates a Figure model, which composes axes, grids, default tools, etc.
    # and includes methods for adding different kinds of glyphs (shapes & things) to a plot
    # show: displays the figure
    # curdoc:
from bokeh.layouts import gridplot, column, row, layout
    # gridplot: a function which arranges bokeh plots in a grid and merges all plot tools into a single
    # toolbar so that each plot int he grid has the same active tool
from bokeh.io import output_file
    # output_file: configures the default output state to generate output saved to a file when show()
    # is called
from bokeh.palettes import Category20b, Category20c
    # Category20b: 4 purple, 4 green, 4 brown, 4 red, 4 pink
    # Category20c: 4 blue, 4 orange, 4 green, 4 purple, 4 grey
from bokeh.transform import dodge, transform
    # dodge: creates a DataSpec dict that applies a client-side Dodge transformation to a
    # ColumnDataSoure column. has parameters:
        # field_name (str) - a field name to configure DataSpec with
        # value (float) - the fixed offset to add to column data
        # range (Range, optional) - a range to use for computing synthetic coordinates when necessary,
        # e.g. a FactorRange when the column data is categorical (not the fun kind)
    # transform:
from bokeh.resources import INLINE
    # INLINE:
from bokeh.events import Tap
    # Tap:
from tkinter import filedialog
    # filedialog: provides a set of dialogs to use when working with file, such as open, save, etc.
        # used to upload & open ms1ft .csv files
# from tktooltip import ToolTip
from idlelib.tooltip import Hovertip
import math
from functools import reduce

LARGE_FONT= ("Verdana", 12)



"""
APP

This builds the backbone of the app using tkinter. Each page of the app is a frame in App.frames. Throughout the code, pages are displayed using App.show_frame('pagename'). The first page is set here as well, and is temporarily set to the 'File Selection' page (an explanation for this is provided in the comments for the 'Start Page').

The functions new_analysis() and test_app() are also defined here, but both are broken, so their buttons have been disabled. 

"""
class App(tk.Tk):   
    msalign_filearray = []
    processed_filearray = []
    shortened_filenames = []
    expgroup = []
    ms1ft_filenames = []
    total_files = 0
    Test = True                 # shows test button, which performs a test run of n identical files (WIP)

    def __init__(self, *args, **kwargs):
        # initializing App
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,"Mass Finder and Quantifier")       # "Mass Finder and Quantifier" or "Spectromass"?

        # create the Frame the App is contained in (container for App)
        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("1280x740")                               # size of window (width x height) in pixels

        # creates the frames (pages in the App)
        self.frames = {}
        for F in (StartPage, FileSelection, SearchParams, QuantOutput, QCGraphs, TestApp):
            frame = F(container, self)                          # creates a frame for each page
            self.frames[F] = frame                              # adds to App's array self.frames
            frame.grid(row=0, column=0, sticky="news")

        # app opens with File Selection while we work on New Analysis, Test, and linking pages
        self.show_frame(FileSelection)                              # self.show_frame(StartPage)

    # show_frame(): shows a page of the app (usually called when a button is pressed, except above)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # new_analysis(): BROKEN probably because code execution stops with app.mainloop(), so python isn't reading anything after the "New Analysis" button is pressed
    def new_analysis(self):
        app = App()
        app.mainloop()


    # test_app(): WIP, takes a positive integer n as input and uploads the default sample file n times
    def test_app():
        file_path = filedialog.askopenfilename(title="Please select an MS1 MSALIGN file", filetypes=[('All files','*.*')])
        returnF



"""
START PAGE (CURRENTLY DISABLED)

The 'Start Page' is the first page of the app. 

However, since the pages don't link back to one another the only real option here is for the user to click 'MS1 File Selection'. File selection is the first step of the program, so we would want that to be the first page users go to. I assume the Start Page is intended for if we were able to link up all the pages, so the user wouldn't have to go through this process in a linear fashion (or even if in the future we allow people to save data from previous runs in-app). 

For now, since every other button leads to an error or failure to complete, I think it makes the most sense to have 'MS1 File Selection' be either the only button on this page or for the File Selection page to be the first page of the app. I've set the 'File Selection' page as the first page of the app for now.

"""
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        # Start Page creation & initialization
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Each button has a lambda calling show_frame to display a certain page

        # File Selection Button
        button1 = ttk.Button(self, text="MS1 File Selection",
                            command=lambda: controller.show_frame(FileSelection))
        button1.grid(column=0, row=1, sticky='w')

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')

        # Results Output Button
        button3 = ttk.Button(self, text="Results Output",
                            command=lambda: controller.show_frame(QuantOutput))
        button3.grid(column=2, row=1, sticky='w')

        # QC Graphs Button
        button4 = ttk.Button(self, text="Quality Control Graphs",
                            command=lambda: controller.show_frame(QCGraphs))
        button4.grid(column=3, row=1, sticky='w')

        # Test Button (WIP)
        # This function should run the program normally (rumming and timing all applicable functions) while bypassing all user input (including parameter entries and button clicks). It is intended to make testing easier.
        if App.Test==True:
            button5 = ttk.Button(self, text="Test n Files",
                                command=lambda: controller.show_frame(TestApp), state=DISABLED)
            button5.grid(column=4, row=1, sticky='w')



"""
TESTING (CURRENTLY DISABLED, WIP)

Clicking "Test n Files" on the 'Start Page' leads to the 'Testing' page, which has one entry which takes an integer value, the number of files wish to be run. To add later?: number of repeats, complexity of files (small, medium, large), anything else that might help. After this user entry, the program should run through the end, bypassing button clicks and timing all functions. Once this is complete, we can clean up the mess I made everywhere else...

"""
class TestApp(tk.Frame):
    def __init__(self, parent, controller):
        # Testing page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Testing", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')
        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row=3, column = 0)

        # file size: user can select a file size (small, med, large) from menu
        # option list
        option_list = ['Small','Medium', 'Large']        # better to list actual sizes once we have the files
        self.file_size = StringVar(self)
        self.file_size.set('Medium')                     # default file size is medium
        self.popupMenu = OptionMenu(self, self.file_size, *option_list)
        # menu label
        label2 = tk.Label(self, text="Size of files")
        label2.grid(row=5, column=0, sticky='w')
        self.popupMenu.grid(row=5, column=1)            # does not look like it's in column 1, very annoying
        self.file_size.trace('w',self.get_parameters)

        # gets parameters from entries
        self.controller = controller
        self.get_parameters(self)

        # calls process_msalign_files() with given parameters
        processbutton = tk.Button(self, text='Process File(s)', name='pbutton',  fg="green", command=(lambda : self.run_test()))
        processbutton.grid(column=0, row=1, sticky='w')
        self.controller = controller # necessary?


    # GET_PARAMETERS(): Creates entries for user input and gets parameters from them.
    # The parameters to be gotten here are: number of files to be tested and size of file.
    # Maybe three sizes to choose from: small (), medium (), and large ()?
    def get_parameters(self,*args):
        TestApp.entries = []
        
        for child in self.entry_frame.winfo_children():
            child.destroy()

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row=3, column = 0, sticky='w')

        # Testing parameters with integer values:
            # number of files
            # anything else?
        test_fields = ['Number of files']
        i=2
        for field in test_fields:
            lab = tk.Label(self.entry_frame, width=len(field), text=field, anchor='w')
            ent = tk.Entry(self.entry_frame, width=8)
            lab.grid(row=i, column=0)
            ent.grid(row=i, column=1, sticky='w')
            TestApp.entries.append((field, ent))
            i+=1
        TestApp.entries[0][1].insert(0,1)       # Number of files to test (default 1)

        # Testing parameters with non-integer values:
            # size of file (idk how to include "default" files for testing but we may have 
                # to figure that out anyway, so we might as well have different sizes)
            # anything else?   


    # TO DO: figure this out
    def run_test():
        # i wanted to just call each of the process functions here, but they take you to new pages.
        # so i'm confused about how to do testing... lots of things to google here.
        # may just need to rewrite some functions to have default args and call those
        return 


"""
FILE SELECTION

Clicking "MS1 File Selection" on the 'Start Page' leads to the 'MS1 File Selection' page, which has two buttons, one for "New Analysis" and one for "Add File". Once one file has been uploaded, a button to "Process Files" appears, created within msalignfile().
    - temporary to prevent upload loops: can add max of 20 files (TO DO: replace with error message?)

"""
class FileSelection(tk.Frame):
    gridrow = 4
    gridcolumn = 0
    button_identities = []
    filelabel_identities = []
    group_identities = []

    def __init__(self, parent, controller):
        # File Selection Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="MS1 File Selection", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # New Analysis Button (issues w/file selection in new analysis so currently disabled)
        button2 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis(), state=DISABLED)
        button2.grid(column=1, row=1, sticky='w')

        # Add File Button
        addbutton = tk.Button(self, text='Add File',  fg="green", command=(lambda : self.msalignfile()))
        addbutton.grid(column=0, row=2,sticky='w')
        addbutton_tip = Hovertip(addbutton, 'Upload a file\n(.msalign or .tsv)', hover_delay=100)

        self.controller = controller


    # MSALIGNFILE(): uploads a new msalign file and builds/updates File Selection Page throughout upload process.
    # This function is called each time the "Add File" button is pressed.
    def msalignfile(self):
        if App.total_files > 20:                                                          # 20 file max (temporary)
            mb.showerror("Warning","Cannot load more files. Maximum files (20) reached.") # i assume to avoid infinite loop
            
        else:
            # Retrieve file path from upload
            file_path = filedialog.askopenfilenames(title="Please select MS1 msAlign or tsv file(s)", filetypes=[('All files','*.*')])  # Question: Does this still not work on mac?

            for file in file_path:
                # The abbreviated file name 'filename.msalign' of the uploaded file is extracted from its path '.../.../.../.../filename.msalign'
                filename = str(file)[::-1]        # takes the uploaded file path as a string, reverses it, and saves this to the variable filename
                for i in range(len(filename)):
                    if filename[i] == '/':
                        ext_filename = filename[0:i][::-1]    # takes the reversed file path up to the first '/', reversed, and saves this to the variable ext_filename
                        break
                App.shortened_filenames.append(ext_filename)

                #make ms1ft filname
                root_ext = os.path.splitext(file)
                ms1ft_filename = root_ext[0][:-4]+'.ms1ft'
                App.ms1ft_filenames.append(ms1ft_filename)
                
                # Once a file has been successfully uploaded, display in app while:
                    # allowing user to relabel each file, usually by group (e.g. 'exp group', 'ctrl group')
                    # allowing user remove individual uploaded files with a button
                if ext_filename != "":
                    # displays uploaded file on grid as an (editable - why?) Label object
                    filelabel = Label(self, text = 'File: '+ ext_filename, anchor="w", width=len(ext_filename)+5)  # textvariable? to pass to Entry?
                    filelabel.grid(row=FileSelection.gridrow, column=FileSelection.gridcolumn, sticky='w')

                    # creates editable group_label_entry, so that the user can specify what each msalign file represents (control, experiment 1, etc) in app
                    # these will be the labels shown on the output graphs
                    group_label_entry = tk.Entry(self, width=13)
                    group_label_entry.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+1, sticky='w')
                    group_label_entry.insert(0,'<exp. group>')

                    # creates a removebutton alongside & specific to each uploaded file using a lambda that calls the function "Xclick", defined below this fn
                    removebutton = tk.Button(self, text='X', fg="red", command=(lambda : Xclick(filelabel,group_label_entry,removebutton)))
                    removebutton.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+2)
                    removebutton_tip = Hovertip(removebutton, 'Remove ' + ext_filename, hover_delay=100)

                    # changes to FileSelection page
                    FileSelection.filelabel_identities.append(filelabel)
                    FileSelection.group_identities.append(group_label_entry)
                    FileSelection.button_identities.append(removebutton)
                    FileSelection.gridrow += 1
                    App.total_files+=1

                    # update main array by appending file Label and string (why both?)
                    # msalign_filearray = [Label1, string1, Label2, string2, ...]
                    App.msalign_filearray.append(filelabel)
                    # App.msalign_filearray.append(ext_filename)
                    App.msalign_filearray.append(str(file))

                # timing start
                start_time = timeit.default_timer()
                    
                # only show "Process Files" button once there are files to process
                # pressing the "Process Files" button calls the lambda populate_entries()
                if len(App.msalign_filearray) == 2:         # if something uploaded, msalign_file array should have 2 vals (file label & name)
                    # spacing around process files button
                    space = tk.Label(self, text="\n")
                    space.grid(column=0, row=20, sticky='w')
                    
                    # process files button
                    processbutton = tk.Button(self, text='Process File(s)', name='processbutton', bg="green", fg="white", command=(lambda : populate_entries()))
                    processbutton.grid(column=0, row=21, sticky='w')
                    process_tip = Hovertip(processbutton, 'Warning! Once processed, files cannot be changed.', hover_delay=100)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('Fileselection \t msalignfile \t\t\t', total_time)
        # with open("timing_0_msalignfile.csv", "a") as out_file:         # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")


        # XCLICK(): destroys all info for a selected file in FileSelection page (filelabel, entry box, removebutton) and the corresponding values in the identity arrays for those 3 values. Then destroys its 2 values in msalign_filearray and updates the app's total number of files, removing the "Process Files" button if this is 0. The result is as though the selected file was never uploaded.
        # THIS DOES NOT WORK WHEN MULTIPLE FILES ARE SELECTED AT ONCE. I THINK THE filelabel VARIABLE DOES NOT BECOME A UNIQUE IDENTIFIER!!!
        def Xclick(filelabel, group_label_entry, removebutton):
            print('Xclick array: ',filelabel)
            # timing start
            start_time = timeit.default_timer()

            # destroy file's boxes on File Selection page
            filelabel.destroy()
            group_label_entry.destroy()
            removebutton.destroy()
            
            # destroy file's vals in identity arrays
            FileSelection.filelabel_identities.remove(filelabel)
            FileSelection.group_identities.remove(group_label_entry)
            FileSelection.button_identities.remove(removebutton)
            
            # remove file label and name from msalign_filearray
            for i in App.msalign_filearray:
                if i == filelabel:
                    del App.msalign_filearray[App.msalign_filearray.index(i)+1]
                    del App.msalign_filearray[App.msalign_filearray.index(i)]

            # update total # of files, if 0 remove "Process Files" button
            App.total_files-=1
            if len(App.msalign_filearray) == 0:
                self.nametowidget('processbutton').destroy()

            # timing end
            total_time = timeit.default_timer() - start_time
            print('FileSelection \t Xclick \t\t\t', total_time)
            # with open("timing_0_Xclick.csv", "a") as out_file:          # timing output file for testing
                # out_file.write(str(total_time))
                # out_file.write("\n")


        # POPULATE_ENTRIES(): fills msalign_filearray with data from group_identities array.
        # Called after all input files are uploaded and 'Process Files' button is pressed.
        #
        # It would be nice to make an option to undo this process (similar to how xClick undoes the upload process) so that users can return to the File Selection page at any point to make changes (like they can with Search Parameters).
        def populate_entries():
            # timing start
            start_time = timeit.default_timer()

            # Fill expgroup (array) with group names (e.g. 'exp. group')
            # parse through group_identities, one per file but many can hold same string val
            for group in self.group_identities:     # might make this one line
                group_name = group.get()            # group_label_entry in msalignfile()
                App.expgroup.append(group_name)     # ^ these fill prev empty array expgroup
                # App.expgroup.append(group.get())

            # extracts filenames to abrv_filenames for graphing display
            # msalign_filearray consists of, for each file, the Label and name, so skip by 2
            # TO DO: remove this and just use msalign_filearray?
            for i in range(1,len(App.msalign_filearray),2):     # len(...) = # of input files
                SearchParams.abrv_filenames.append(App.msalign_filearray[i])
                
            # timing end
            total_time = timeit.default_timer() - start_time
            print('FileSelection \t populate_entries \t\t', total_time)
            # with open("timing_populate_entries.csv", "a") as out_file:      # timing output file for testing
            #     out_file.write(str(total_time))
            #     out_file.write("\n")

            # When done processing input files, show 'Search Parameters' page
            self.controller.show_frame(SearchParams)


"""
SEARCH PARAMS

Clicking "Search Parameters" on the 'Start Page' leads to the 'Search Parameters' page, which defaults to Static mode, where the user can specify the values of 6 parameters. Switching to Dynamic mode allows the user to specify different start and end retention times for each file. Also, in Dynamic mode, the user has the option to 'search by mass range' rather than specifying masses of interest by listing them.

"""
class SearchParams(tk.Frame):
    abrv_filenames = []             # abbreviated filenames for display purposes
    entries = []
    dynamic_entries = []
    dynamic_counter = 1             # this will be used for file-specific search conditions (e.g., retention times)

    def __init__(self, parent, controller):
        # Search Parameters Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Search Parameters", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Mass Range Entry
        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row=3, column = 0)
        self.mass_range = IntVar()

        # Search Modes: Static, Dynamic
        option_list = ['Static','Dynamic']
        self.search_optn = StringVar(self)          # search_optn changes mode
        self.search_optn.set('Static')              # default is Static
        self.popupMenu = OptionMenu(self, self.search_optn, *option_list)

        # Menu label for Search Mode
        search_mode = tk.Label(self, text="Search Mode:")
        search_mode.grid(row = 0, column = 1)
        search_mode_tip = Hovertip(search_mode, 'Static Mode is usually recommended for the first run. \nUse Dynamic Mode to specify retention time per file \nand masses of interest by range.', hover_delay=100)
        self.popupMenu.grid(row = 0, column = 2)
        self.search_optn.trace('w',self.get_parameters)

        # Pre-populate search options w/(default static) parameters
        self.controller = controller
        self.get_parameters(self)

        # empty space before process files button
        space = tk.Label(self, text="\n")
        space.grid(column=0, row=7, sticky='w')

        # 'Process Files' Button calls process_msalign_files()
        processbutton = tk.Button(self, text='Process File(s)', name='pbutton', bg="green", fg="white", command=(lambda : self.process_msalign_files()))
        processbutton.grid(column=0, row=8, sticky='w')
        process_tip = Hovertip(processbutton, 'Process file(s) according to specified search parameters', hover_delay=500)

        # Set up for progress()
        self.e=StringVar()
        self.e.set("Loading")


    # GET_PARAMETERS(): Displays user entry fields for user specified parameters such as scan start and end time, mass tolerance, etc. Contains two modes - Static (the default mode) and Dynamic. 
    # In Static mode, the user specifies masses of interest by entering a list (separated by spaces or commas and spaces) and a mass tolerance (which specifies what 'distance' away a mass can be to be counted as a mass of interest). The user specifies a single start & end retention time for all files.
    # In Dynamic mode, the user can set masses of interest by range instead of inputting a list, by specifying the minimum and maximum mass values and the interval between them. The program uses these three parameters to create a list of masses of interest. The user specifies mass tolerance as in Static mode. In this mode, the user can specify different start & end retention times for different files.
    def get_parameters(self,*args):
        # Reset entries (for starting or switching back to Search Params page)
        # In Static mode, entries = [('Start Scan', Entry), ('End Scan', Entry), ('Start ret. time', Entry), ('End ret. time', Entry), ('Masses', Entry), ('Mass Tolerance (Da)', Entry)]
        # In Dynamic mode, entries = [('Masses', Entry, Entry, Entry), ('Mass Tolerance (Da)', Entry)]
        # In Dynamic mode, dynamic_entries = ['filename.msalign', ('Start ret. time', Entry), ('End ret. time', Entry), ...], where this info is provided per input file
        SearchParams.entries = []
        SearchParams.dynamic_entries = []

        """ ------------------- CHANGEABLE PARAMETERS START HERE ------------------- """
        """                        (Pesavento Lab use H3, H2A)                       """
        # The code below determines the default parameters with regards to the masses of interest in both Static and Dynamic mode.
        # To replace these with your own values, follow the steps below. Add a list containing your masses of interest, then edit the default_masses variable to refer to your new list. 

        # STEP 1/2: List your masses of interest below (give your list a name like H3 then list the masses between brackets and separated by commas, as shown).
        H3 = [15168,15182,15196,15210,15224,15238,15252,15266,15280,15294,15308,15322,15336,15350,15364,15378,15392,15406,15430,15444,15458,15472,15486,15500]
        H2A = [13488,13514,13530,13572,13545,13587,13629,13700,13742,13784,13713,13755,13797]
        # H4 = [11318,11332,11346,11360,11374,11388,11402,11416,11430,11444,11458,11472,11486,11500,11514,11528,11542,11556]
        # H4ox = [11334, 11348, 11362,11376,11390,11404,11418,11432,11446,11460,11474,11488,11502,11516,11530,11544,11558]

        # Static mode default values (changeable)
        default_masses = H2A                      # STEP 2/2: Replace H3 in this line with the name of your list.
        default_tolerance = 2
        default_scan_start = 100
        default_scan_end = 11111
        default_ret_start = 100
        default_ret_end = 11111
        """ -------------------- CHANGEABLE PARAMETERS END HERE -------------------- """

        # Dynamic mode default values are calculated based on Static mode default values (NOT recommended to change)
        default_min = min(default_masses)
        default_max = max(default_masses)
        default_interval = (2*default_tolerance)+1

        # CHANGE_RANGE(): manages updates to the app when user switches mass search mode between list and range by updating, creating, and destroying fields, entries, and tips.
        def change_range(self,*args,):
            if self.mass_range.get() == 1:              # if "Search by mass range" selected:
                self.mass_field.config(text = 'Mass Range (min, max, interval) ')   # update field to 'Mass Range (...)'
                self.mass_max.grid(row=3, column=2,sticky='news')                   # make entry for max
                self.mass_interval.grid(row=3, column=3,sticky='news')              # make entry for interval
                self.entries[0][1].delete(0, END)                                   # change default parameter in first fieild
                self.entries[0][1].insert(0,default_min)                            # to default min
                tip = Hovertip(self.mass_field_ent, 'Specify minimum mass of interest.\nEx: Entering 1 in (1,9,2) yields\nthe mass range [1,3,5,7,9].', hover_delay=100)
            if self.mass_range.get() == 0:              # if "Search by mass range" not selected:
                self.mass_field.config(text = 'Masses ')    # update field to 'Masses'
                self.mass_max.grid_forget()                 # remove entry for max
                self.mass_interval.grid_forget()            # remove entry for interval
                self.entries[0][1].delete(0, END)           # change default parameter in first field
                self.entries[0][1].insert(0,default_masses) # to default masses
                tip = Hovertip(self.mass_field_ent, 'List masses of interest. \nSeparate each mass with either \na space or a comma and a space.', hover_delay=100)

        # In Static Mode, create buttons and entry boxes
        if self.search_optn.get() == "Static":
            for child in self.entry_frame.winfo_children():
                child.destroy()
            self.mass_range.set(0)

            self.entry_frame = tk.Frame(self)
            self.entry_frame.grid(row=3, column = 0, sticky='w')

            # input fields in Static Mode
            s_fields = ('Start scan', 'End scan', 'Start ret. time', 'End ret. time', 'Masses', 'Mass Tolerance (Da)')
            i=3

            # for each entry in Static Mode, enter the field name and entry as a pair into SearchParams.entries
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=len(field), text=field, anchor='w')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                SearchParams.entries.append((field, ent))
                i+=1

            # a tip pops up when the user hovers over each entry field
            scan_start_tip = Hovertip(SearchParams.entries[0][1], 'Specify starting time of scan range to be considered', hover_delay=100)
            scan_end_tip = Hovertip(SearchParams.entries[1][1], 'Specify ending time of scan range to be considered', hover_delay=100)
            ret_start_tip = Hovertip(SearchParams.entries[2][1], 'Specify smallest retention time to be considered', hover_delay=100)     # TO DO: this probably doesn't make sense, please help!
            ret_end_tip = Hovertip(SearchParams.entries[3][1], 'Specify longest retention time to be considered', hover_delay=100)        # i feel like you would want retention time to be longer?
            masses_tip = Hovertip(SearchParams.entries[4][1], 'List masses of interest. \nSeparate each mass with either \na space or a comma and a space.', hover_delay=100)
            mass_tolerance_tip= Hovertip(SearchParams.entries[5][1], 'Specify mass tolerance. \nEx: A tolerance of 2 will count \nmasses 15180 through 15184 \ntowards the mass 15182.', hover_delay=100)

            # Inserts default parameters into entries (Static mode)
            self.entries[0][1].insert(0,default_scan_start)     # Start scan
            self.entries[1][1].insert(0,default_scan_end)       # End scan
            self.entries[2][1].insert(0,default_ret_start)      # Start ret. time
            self.entries[3][1].insert(0,default_ret_end)        # End ret. time
            self.entries[4][1].insert(0,default_masses)         # Masses
            self.entries[5][1].insert(0,default_tolerance)      # Mass Tolerance (Da)

        # In Dynamic Mode, recreate buttons and entry boxes
        if self.search_optn.get() == "Dynamic":
            for child in self.entry_frame.winfo_children():
                child.destroy()
            self.mass_range.set(0)                      # sets "search by mass range" off by default
            self.entry_frame = tk.Frame(self)           # populates frame with dynamic mode input
            self.entry_frame.grid(row=3, column = 0, sticky='w')

            # These lists contain only fields that are NOT affected by 'Search by mass range'
            s_fields = ('Mass Tolerance (Da)',)                 # fields that appear in static mode that are not affected by Sbmr
            d_fields = ('Start ret. time', 'End ret. time')     # fields that appear in dynamic mode that are not affected by Sbmr

            # Search by mass range button
            self.mass_range_btn = tk.Checkbutton(self.entry_frame, text="Search by mass range: ", variable=self.mass_range, command=(lambda : change_range(self, self.mass_field_ent)))
            self.mass_range_btn.grid(row=0,column=1, columnspan=2, sticky='w')
            button_tip = Hovertip(self.mass_range_btn, 'Specify masses of interest by\nmin, max, and interval size\n(rather than providing a list)', hover_delay=100)

            # 'Masses' field either serves as a mass list OR the min mass for search by mass range
            self.mass_field = tk.Label(self.entry_frame, width=25, text='Masses', anchor='w')
            self.mass_field_ent = tk.Entry(self.entry_frame, width=len("".join(map(str,default_masses)))+len(default_masses))
            self.mass_field.grid(row=3, column=0,sticky='news')
            self.mass_field_ent.grid(row=3, column=1,sticky='w')
            tip = Hovertip(self.mass_field_ent, 'List masses of interest. \nSeparate each mass with either \na space or a comma and a space.', hover_delay=100)

            # 'Max Mass' and 'Mass Interval' fields for search by mass range
            self.mass_max = tk.Entry(self.entry_frame, width=8)
            max_tip = Hovertip(self.mass_max, 'Specify maximum mass of interest.\nEx: Entering 9 in (1,9,2) yields\nthe mass range [1,3,5,7,9].', hover_delay=100)
            self.mass_interval = tk.Entry(self.entry_frame, width=8) #make entry, but don't show until needed
            interval_tip = Hovertip(self.mass_interval, 'Specify interval for masses of interest.\nEx: Entering 2 in (1,9,2) yields\nthe mass range [1,3,5,7,9].', hover_delay=100)

            # Append info from 3 entries to SearchParams.entries
                # entries = [(masses list or min mass, mass max or None, mass_interval or None)]
                # where 2nd and 3rd elements contain None if in search by mass range
                # If we want separate entries for masses and min_mass (which might be necessary for separate tips), we will have to redesign and deal with this entries list differently.  
            SearchParams.entries.append(('Masses',self.mass_field_ent,self.mass_max,self.mass_interval))

            i=4 
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=len(field)+5, text=field, anchor='e')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                mass_tolerance_tip= Hovertip(ent, 'Specify mass tolerance.\nEx: A tolerance of 2 will count\nmasses 15180 through 15184\ntowards the mass 15182.', hover_delay=100)
                SearchParams.entries.append((field, ent))
                i+=1

            space = tk.Label(self.entry_frame, width=20, text='\n', anchor='w').grid(row=i, column=0, sticky='w')
            i+=1
            count = 0
            # Build entries & fields for Start & End Ret. Time (per file)
            for file in SearchParams.abrv_filenames:
                print('FILENAMES')
                print(App.shortened_filenames)
                print('FILENAMES')
                # build and place labels for each file
                # lab = tk.Label(self.entry_frame, width=20, text=str(file), anchor='w')
                lab = tk.Label(self.entry_frame, width=len(App.shortened_filenames[count]), text=str(App.shortened_filenames[count]), anchor='w')
                lab.grid(row=i, column=0,columnspan=3,sticky='news')
                SearchParams.dynamic_entries.append(file)       # append filename (String?) to dynamic_entries
                j=2
                for field in d_fields:
                    lab = tk.Label(self.entry_frame, width=len(field), text=field, anchor='w')
                    ent = tk.Entry(self.entry_frame, width=8)
                    lab.grid(row=i, column=j, columnspan=1, sticky='news')
                    ent.grid(row=i, column=j+1, sticky='w')
                    # create tips for retention time entries in dynamic mode (stupid way)
                    if field == 'Start ret. time':
                        ret_start_tip = Hovertip(ent, 'Specify shortest retention time to be considered for\n' + file, hover_delay=100)
                    else:
                        ret_end_tip = Hovertip(ent, 'Specify longest retention time to be considered for\n' + file, hover_delay=100)
                    SearchParams.dynamic_entries.append((field, ent))
                    j+=2
                i+=1
                count+=1

            # Inserts default parameters into entries (Dynamic mode)
            # Masses / Mass Range and Mass Tolerance
            SearchParams.entries[0][1].insert(0,default_masses)         # since search by mass range is off by default, show mass list by default (changes to min mass in change_range())
            SearchParams.entries[0][2].insert(0,default_max)
            SearchParams.entries[0][3].insert(0,default_interval)
            SearchParams.entries[1][1].insert(0,default_tolerance)
            # Start and End Ret. Times (per file)
            n = 0
            while (n < len(SearchParams.dynamic_entries)):              # going through every element of dynamic_entries, which has 3 elements per uploaded file
                start = SearchParams.dynamic_entries[n+1]               # every second element contains ('Start ret. time', Entry)
                end = SearchParams.dynamic_entries[n+2]                 # every third element contains ('End ret. time', Entry)
                start[1].insert(0, default_ret_start)                   # insert default value into entry
                end[1].insert(0, default_ret_end)                       # insert default value into entry
                n += 3                                                  # move on to next file


    # PROCESS_MSALIGN_FILES(): Checks for search parameter errors (no files, empty search params, conflicts with mass interval and mass tolerance) before processing (and tracking progress on) input files according to user-given search parameters.
    def process_msalign_files(self):
        # timing start
        start_time = timeit.default_timer()
                
        # Start assuming no error
        # Errors occur if there are no files to process or any empty search parameters in Static or Dynamic mode
        error = False

        # No files uploaded (nothing to process)
        if len(App.msalign_filearray) == 0:
            mb.showerror("Warning", "There are no files to process.")

        # Static Mode
        # Warning: Empty search parameter field
        if self.search_optn.get() == "Static":
            for entry in SearchParams.entries:
                if len(entry[1].get()) == 0:
                    mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break

        # Dynamic Mode
        if self.search_optn.get() == "Dynamic":
            # Warning: Empty 'Masses'/'Min Mass' or 'Mass Tolerance' entries 
            # TO DO: FIX ERROR where this only checks first entry, and not the max or interval entries
                # entries = [('Masses', Entry obj, Entry obj, Entry obj), ('Mass Tolerance (Da)', Entry object)]
                # where the Entry objects contain mass list / min mass, max mass, mass interval, and mass tolerance, respectively
            for entry in SearchParams.entries:
                if len(entry[1].get()) == 0:
                    mb.showerror("Warning", "Please fill out all mass information.")
                    # mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break
            
            # Warning: Overlap between 'Mass Interval' and 'Mass Tolerance'
            # The mass interval must be more than twice as large as the mass tolerance, otherwise one datapoint may be counted towards two neighboring masses of interest. Once we have the above issue fixed we can put this in the same for loop as checking the entries above and won't need  so many if statements.
            if self.mass_range.get() == 1:
                if (float(SearchParams.entries[1][1].get()) >= math.ceil(float(SearchParams.entries[0][3].get())/2)):
                    mb.showerror("Warning", "Overlap between mass interval and mass tolerance.\nInterval must be more than twice as large as tolerance.")
                    error = True

            # Warning: Empty 'Start Ret. Time' or 'End Ret. Time' entries
                # dynamic_entries = ['filename1.msalign', ('Start ret. time', Entry object), ('End ret. time', Entry object), ...]
                # where the entries contain the start and end retention times, respectively.
            # I think this search for errors will get slightly simpler if we restructure this list to remove the file names and fields (just contain the entries, which are what we work with here). I just have to check and make sure we don't use the file names in graphing, or if we do, that we can't do it another way.
            for entry in range(len(SearchParams.dynamic_entries)):              # if restructure, directly access entry objs like above
                if len(SearchParams.dynamic_entries[entry]) == 2:               # if restructure, switch 2 to 1 here
                    if len(SearchParams.dynamic_entries[entry][1].get()) == 0:
                        mb.showerror("Warning", "Please fill out min and max retention times for all files.")
                        # mb.showerror("Warning", "All search parameter fields must be filled out.")
                        error = True
                        break

        # If there are files to process & no errors, process msalign files according to search parameters
        if len(App.msalign_filearray) > 0 and error == False:
            # Create loading box
            self.loading = tk.Label(self, textvariable=self.e)
            self.loading.grid(column=0, row=2, columnspan=1, sticky="w")
            # Process each file, updating progress in between
            for i in range(1,len(App.msalign_filearray),2):
                self.update_progress((i/len(App.msalign_filearray)))
                SearchParams.process(self,App.msalign_filearray[i])
            # When all the calculations are complete, destroy loading page & move to Output page
            self.loading.destroy()
            self.controller.show_frame(QuantOutput)

        # timing end
        total_time = timeit.default_timer() - start_time
        # Output timing data to diff files to see static vs. dynamic performance (should just depend on size of 'Masses' list vs. list created by mass range)
        if self.search_optn.get() == "Static":
            print('SearchParams \t process_static_msalign_files \t', total_time)
            # with open("timing_0_process_static_msalign_files.csv", "a") as out_file:    # timing output file for testing
                # out_file.write(str(total_time))
                # out_file.write("\n")
        if self.search_optn.get() == "Dynamic":
            print('SearchParams \t process_dynamic_msalign_files \t', total_time)
            # with open("timing_0_process_static_dynamic_files.csv", "a") as out_file:    # timing output file for testing
                # out_file.write(str(total_time))
                # out_file.write("\n")

        
    # UPDATE_PROGRESS(): updates progress as msalign files are being processed. This function updates the progress bar. In case of any progress-specific errors (the progress calculation yields an unexpected and undecipherable result) the progress bar displays an error message, progress resets to 0, and the upload continues.
    # This function is called for each input file alongside process() in process_msalign_files().
    #
    # TO DO: I don't think this was timed properly. This function is called continuously, so there should be a variable outside of this that's summing the total_time we get each time we run it.
    def update_progress(self,progress):
        # timing start
        start_time = timeit.default_timer()
        
        barLength = 15          # modify to change the length of the progress bar
        status = ""

        # if progress is int, convert to float
        if isinstance(progress, int):
            progress = float(progress)

        # if progress is not float, display 'error' for status, reset progress to 0, and continue
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"

        # if progress is negative, display 'Halt' for status, reset progress to 0, and continue
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"

        # if progress is 1, upload is done
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"

        # update progress bar
        block = int(round(barLength*progress))
        progresstext = "\rLoading (%): [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
        self.e.set(progresstext)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t update_progress \t\t', total_time)
        # with open("timing_0_update_progress.csv", "a") as out_file:         # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")


    # PROCESS(): takes a file as input, reads the entire file as a string, separates the information in the string and sorts appropriate info into two arrays (ms1_ions and scan_ions), then calls mass_selection on the scan_ions array.
    def process(self,filename):
        # timing start
        start_time = timeit.default_timer()
        
        global scan_ions        # for now, leave global, but this will be a passed array eventually
        scan_ions = []          # ions to perform mass selection on
        temp_array = [0,0,0,0]  # temp array for each scan
        ms1_ions = []           # last in scan array
        ms1events = 0           # Question: Do we use this counter at all?
        convert = []            # file data fills here as it is being converted
        lines = []              # lines/rows of data fill here 

        # RMV_CHARS(): takes a string and returns a string of only the numbers and periods. 
        # This function will be called on lines gathered from input msalign files, and is intended to filter out headings/labels to gather data for calculations. 
        # Ex: rmv_chars('RETENTION_TIME=13.20') = '13.20'
        def rmv_chars(string):
            getVals = list([val for val in string
                if (val.isnumeric() or val==".")])
            return "".join(getVals)

        # Read input file as one massive string
        root_ext = os.path.splitext(filename)
        if root_ext[1] == '.msalign':
            with open(filename) as fp:
                data = fp.read()

            # Read through the string obtained from the file and sort it into "lines". 
            # Lines consist of the data between each comma or newline character. 
            for i in data:
                if i == ',' or i == '\n':
                    link = "".join(convert)
                    link.strip()
                    if len(link) > 1:
                        lines.append(link)
                        convert = []
                else:
                    convert.append(i)

            # Extract numerical data from lines using rmv_chars(), defined above. 
            # By inspection, the data in the input (.msalign) files is in the form:
                # BEGIN IONS
                # ID=int
                # SCANS=int
                # RETENTION_TIME=float
                # ACTIVATION= 
                # float float int (ion 1 data?)
                # float float int (ion 2 data?)
                # ...
                # END IONS
                #
                # (repeat above)
            # So we use these headers (and a temp array) to sort the appropriate data into ms1_ions and scan_ions.
            # Question: Is this the exact format every time? If so we can probably rewrite the following loop to be a bit more efficient.
            while (len(lines)-1)>0:
                text = str(lines[0])
                if text.startswith('ID='):
                    temp_array[0] = int(rmv_chars(text))        # append id no. to temp array
                    self.update()
                elif text.startswith('SCANS='):                 # append scan no. to temp array
                    temp_array[1] = int(rmv_chars(text))
                elif text.startswith('RETENTION_TIME='):        # append ret. time to temp array
                    temp_array[2] = float(rmv_chars(text))
                elif text[0].isdigit():
                    while lines[0]!='END IONS':
                        ms1_ions = np.append(ms1_ions,[float(s) for s in lines[0].split("\t")])     # append ions to ms1_ions
                        del lines[0]
                    ms1_ions = np.reshape(ms1_ions,(int(len(ms1_ions)/3),3))    # each element now contains 3 pieces of data for an ion, the start and end times and the intensity?
                    temp_array[3] = ms1_ions
                    scan_ions.append(temp_array)
                    temp_array = [0,0,0,0]
                    ms1_ions = []
                    ms1events+=1
                del lines[0]
            
            # timing end (end timing before calling next function)
            total_time = timeit.default_timer() - start_time
            print('SearchParams \t process \t\t\t', total_time)
            # with open("timing_0_progress.csv", "a") as out_file:        # timing output file for testing
                # out_file.write(str(total_time))
                # out_file.write("\n")

            # Perform mass selection (defined below) on scan ions
            SearchParams.mass_selection(self,scan_ions,root_ext[1])

        elif root_ext[1] == '.tsv':
            req_columns = ['Index','ScanNum','RetentionTime','MonoisotopicMass','SumIntensity']
            df_tsv = pd.read_csv(filename,usecols=req_columns,sep='\t')
            SearchParams.mass_selection(self,df_tsv,root_ext[1])

        else:
             mb.showerror("Warning","File extension not .msalign or .tsv. Closing program.")
             sys().exit
        
    # MASS_SELECTION(): given scan_ions array from process(), where
    # scan_ions = [[[ID, SCANS, RETENTION_TIME, [Mass, Intensity, Charge]],...],
        # gathers parameter data from user input
        # converts all mass data (idx, val) from string to float
        # forms found_masses, masses, tolerance arrays from mass data & parameters, where 
            # found_masses = 
            # masses = 
            # tolerance = 
    def mass_selection(self,scan_ions,root_ext):
        # timing start
        start_time = timeit.default_timer()

        masses = []
        input_masses = [0]      # question: why?

        # Gather entries from parameters in Static Mode
        if self.search_optn.get() == "Static":
            scan_min = float(SearchParams.entries[0][1].get())          # Start Scan
            scan_max = float(SearchParams.entries[1][1].get())          # End Scan
            retention_min = float(SearchParams.entries[2][1].get())     # Start Ret. Time
            retention_max = float(SearchParams.entries[3][1].get())     # End Ret. Time
            input_masses = str(SearchParams.entries[4][1].get())        # Masses
            mass_tolerance = float(SearchParams.entries[5][1].get())    # Mass Tolerance (Da)

        # OR Gather entries from parameters in Dynamic Mode
        if self.search_optn.get() == "Dynamic":
            scan_min = 0                                                # Question: Do we want an entry for this per file?
            scan_max = 30000                                            # same here
            retention_min = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter][1]).get())
            retention_max = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter+1][1]).get())
            SearchParams.dynamic_counter+=3
            if self.mass_range.get() == 1:                              # gather 'Search by mass range' data
                min_mass = float(SearchParams.entries[0][1].get())
                max_mass = float(SearchParams.entries[0][2].get())
                mass_interval = float(SearchParams.entries[0][3].get())
                mass_tolerance = float(SearchParams.entries[1][1].get())
                input_masses = [min_mass]
                temp_mass = min_mass
                while temp_mass <= max_mass:
                    temp_mass+=mass_interval
                    input_masses.append(temp_mass)
                input_masses = str(input_masses)                        # not sure
            else:                                                       # if 'Search by masses' not selected
                input_masses = str(SearchParams.entries[0][1].get())    # only additional data to gather is
                mass_tolerance = float(SearchParams.entries[1][1].get())    # Masses and Mass tolerance (Da)

        found_masses = []
        graph_found_masses = []         # this array will pass on 0 intensity values for QC graphs
        convert = []
        pool = []

        print('input masses')
        print(input_masses)
        print('input masses')
        # convert string masses to float so their data can be used in calculations
        if type(input_masses[0]) == str:                # input_masses = list of masses as strings, why if?
            masses = []
            for idx, val in enumerate(input_masses):
                if val == ',' or val == ' ' and len(convert) !=0:
                    link = "".join(convert)
                    pool.append(float(link))
                    convert = []
                elif idx == (len(input_masses)-1) and input_masses[idx].isnumeric():
                    convert.append(input_masses[idx])
                    link = "".join(convert)
                    pool.append(link)
                elif val.isnumeric() or val == '.':
                    convert.append(val)

            for i in pool:
                masses.append(float(i))

        # Search through scan_ion array using parameters above and output array
        # [retention time, mass, intensity] for each mass in the array.
        if root_ext == ".msalign":
            for i in scan_ions:
                if scan_min <= (i[1]) <= scan_max and retention_min <= (i[2]) <= retention_max:
                    for l in i[3]:
                        temp_array = []
                        graph_temp_array = []
                        for mass in masses:
                            if (mass - mass_tolerance) <= l[0] <= (mass + mass_tolerance):
                                temp_array.extend((i[2],l[0],l[1]))
                                found_masses.append(temp_array)
                                graph_temp_array.extend((i[2],l[0],l[1]))
                                graph_found_masses.append(graph_temp_array)
                    if len(graph_temp_array) == 0:
                        for mass in masses:
                            graph_found_masses.append(([i[2],mass,0]))
        elif root_ext == ".tsv":
            for i, row in scan_ions.iterrows():
                for mass in masses:
                    if (mass - mass_tolerance) <= row['MonoisotopicMass'] <= (mass + mass_tolerance):
                        if scan_min <= row['ScanNum'] <= scan_max and retention_min <= row['RetentionTime'] <= retention_max:
                            temp_array = []
                            graph_temp_array = []
                            temp_array.extend((row['RetentionTime'],row['MonoisotopicMass'],row['SumIntensity']))
                            found_masses.append(temp_array)
                            graph_temp_array.extend((row['RetentionTime'],row['MonoisotopicMass'],row['SumIntensity']))
                            graph_found_masses.append(graph_temp_array)

            #huge savings in time and file size here! instead of adding a blank intensity for each mass at each retention time, i added a blank value for
            #each mass at the min and max retention time for each mass. Bokeh still plots the entire elution window, which was the purpose in the first place!
            for mass in masses:
                graph_found_masses.append([scan_ions['RetentionTime'].min(),mass,0])
                graph_found_masses.append([scan_ions['RetentionTime'].max(),mass,0])
   
        # Perform mass quantification on found masses
        SearchParams.mass_quantification(self,found_masses, masses, mass_tolerance)

        # Build qc graph result from found masses, masses, and mass tolerance arrays
        # and append this to total_qc_graph_array.
        QCGraphs.graph_found_masses, QCGraphs.masses, QCGraphs.mass_tolerance = graph_found_masses, masses, mass_tolerance
        qc_graph_result = [graph_found_masses, masses, mass_tolerance]              # qc_graph_result = [graph_found_masses, masses, mass tolerance]
        QCGraphs.total_qc_graph_array.append(qc_graph_result)                       # QCGraphs.total_qc_graph_array[0][2] = qc_graph_result

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t mass_selection \t\t', total_time)
        # with open("timing_0_mass_selection.csv", "a") as out_file:      # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")


    # MASS_QUANTIFICATION(): Uses found_masses, masses, and mass_tolerance arrays to calculate the intensity of each mass of interest (using values from within the specified tolerance), then sums all the intensities and pairs each mass with its percent of the total intensity, to yield the abundance of each mass. This data is saved to App.processedfilearray.
    # Also contains warning for no masses found (per file).
    def mass_quantification(self,found_masses,masses,mass_tolerance):
        # timing start
        start_time = timeit.default_timer()

        # Initialize intensity information to 0 and empty before performing calculations
        summed_intensities = []
        total_intensity = 0
        percent_intensities = []

        # For each mass found, determine its intensity based on avgs
        for i in masses:
            intensity = 0
            for j in found_masses:
                if (j[1] - mass_tolerance) <= i <= (j[1] + mass_tolerance):     # count masses within range specified by tolerance toward mass of interest
                    intensity = intensity + j[2]
            summed_intensities.append([i,intensity])                            # summed intensities contains elements (mass, intensity)

        # Calculate total intensity (sum of intensities of all masses) in order to determine abundance
        for i in summed_intensities:
            total_intensity = total_intensity + i[1]

        # If total_intensity > 0 we can calculate the abundance of each mass. Append these values to percent_intensities, containing elements (mass, percent of total intensity in sample).
        if total_intensity > 0:
            for i in summed_intensities:
                percent_intensities.append([i[0],(i[1]/total_intensity*100)])

            App.processed_filearray.append(percent_intensities)                 #((mass1,percent1),(mass2,percent2),...)
        # If total_intensity nonpositive, cannot calculate percentages
        else:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t mass_quantification \t\t', total_time)
        # with open("timing_0_mass_quantification.csv", "a") as out_file:             # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")



"""
QUANT OUTPUT
Takes calculated data from SearchParams to form output graphs & csv files.

"""
class QuantOutput(tk.Frame):
    averaged_data = [] #[[averages],[stdev]]

    def __init__(self, parent, controller):                                 # creating buttons for quant output: output, calc data, search params
        # Quant Output Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Results Output", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Calculate Avg & Std Dev Button
        button1 = tk.Button(self, text="Calculate Avg and Stdev", bg="green", fg="white",
                            command=lambda: self.analyze_data())
        button1.grid(column=0, row=1, sticky='w')
        calculations_tip = Hovertip(button1, 'Perform calculations based on entered search parameters', hover_delay=500)

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')
        searchparams_tip = Hovertip(button2, 'Return to Search Parameters page', hover_delay=500)

        self.controller = controller




    ''' NOTE TO SELF: CORRECTING ERRORS IN HERE IS A !!!PRIORITY!!! '''

    # ANALYZE_DATA(): given data in processed_filearray and expgroup, groups data
    # then calculates avg and std deviation. this data is appended to the arrays
    # grouped_data and calc_avg_stdev, the latter of which is passed to QC Graphs
    # (to form error bars).
    def analyze_data(self):
        # timing start
        start_time = timeit.default_timer()

        # arrays we are filling in this function
        restructured_data = []
        grouped_data = []
        calc_avg_stdev = []
        temp_array = []

        # arrays that contain the data to be used in calculations
        processed_filearray_temp = App.processed_filearray
        expgroup_temp = App.expgroup

        # restructure data into a new array [[group1, [data1]], [group2, [data2]],...]
        # where [data] is [mass, intensity]
        if len(expgroup_temp) == 0 or len(processed_filearray_temp) == 0:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)
        else:
            for i in range(len(expgroup_temp)):
                temp_array = [expgroup_temp[i],processed_filearray_temp[i]]
                restructured_data.append(temp_array)

        # sort data based on group name
        # [[group1, [data1]], [group1, [data2]], [[group2],[data1]],...]
        restructured_data = sorted(restructured_data, key=lambda x: x[0])
        while len(restructured_data) != 0:
            if len(restructured_data) == 1:
                grouped_data.append(restructured_data[0][1])
                calc_avg_stdev.append(([restructured_data[0][0],(self.calculate_avg_stdev(grouped_data))]))
                del restructured_data[0]
            elif restructured_data[0][0] == restructured_data[1][0]:
                grouped_data.append(restructured_data[1][1])
                del restructured_data[1]
            else:
                grouped_data.append(restructured_data[0][1])
                calc_avg_stdev.append(([restructured_data[0][0],(self.calculate_avg_stdev(grouped_data))]))
                del restructured_data[0]
                grouped_data =[]

        # the final product [[group1, [avg,stdev]],[group2, [avg,stdev],...]
        # will be sent to the same variable in the QCGraphs for graph creation
        QCGraphs.calc_avg_stdev = calc_avg_stdev
        self.output_quantification_file()
        self.controller.show_frame(QCGraphs)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('QuantOutput \t analyze_data \t\t\t', total_time)
        # with open("timing_0_analyze_data.csv", "a") as out_file:                # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")


    # CALCULATE_AVG_STDEV(): calculates average and standard deviation of grouped data
    # in analyze_data() above. this is called for each subarray in grouped_data.
    def calculate_avg_stdev(self,grouped_data):
        # timing start
        start_time = timeit.default_timer()

        # fill these arrays with calculated values
        averaged_values = []
        stdev_values = []
        mass_array = []

        # for each user-defined search mass, create an array of
        # all data for that single mass, append to mass_array
        for mass in QCGraphs.total_qc_graph_array[0][1]:
            temp_array = []
            temp_array.append(mass)
            for i in grouped_data:
                for j in i:
                    if j[0] == mass:
                        temp_array.append(j[1])
            mass_array.append(temp_array)
        #print('mass array',mass_array)

        # use statistics to calculate std dev and mean of full subarrays
        for i in mass_array:
            stdev_values.append(statistics.pstdev(i[1:]))
            averaged_values.append(statistics.mean(i[1:]))
            
        # timing end
        total_time = timeit.default_timer() - start_time
        print('QuantOutput \t analyze_data \t\t\t', total_time)
        # with open("timing_0_analyze_data", "a") as out_file:            # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")

        # return array with avg & std dev vals for all masses
        calculated_group_data = [averaged_values,stdev_values]
        return calculated_group_data


    # OUTPUT_QUANTIFICATION_FILE(): 
    def output_quantification_file(self):
        # timing start
        start_time = timeit.default_timer()

        # qc graphs will be named by date (up to second)
        date = datetime.today().strftime('%Y%m%d_%H%M%S')   # calculate exact time/date
        filenames = []
        a = []

        # check if any files were uploaded (if not, Error generating output)
        if (len(App.processed_filearray)) == 0:
            mb.showerror("Warning", "Based on your search criteria, no results were generated.")
        else:
            # name output files by date, calculated above
            # output data (SearchParams.abrv_filenames, App.processed_filearray) to file
            filename = "MS1_quantification"+"_"+date+".csv"
            with open(filename,"a") as out_file:
                for i in range(len(SearchParams.abrv_filenames)):
                    out_file.write(str(SearchParams.abrv_filenames[i])+"\n")
                    for j in App.processed_filearray[i]:
                        x,y = str(j[0]),str(j[1])
                        temp = (x+','+y+',')
                        out_file.write(temp)
                    out_file.write(" \n")

        # timing end
            total_time = timeit.default_timer() - start_time
            print('QuantOutput \t output_quantification_file \t', total_time)
            # with open("timing_0_output_quantification_file.csv", "a") as out_file:      # timing output file for testing
                # out_file.write(str(total_time))
                # out_file.write("\n")


"""
QUALITY CONTROL GRAPHS
This class contains the actual QC graphs so its only function is makegraph().
"""
class QCGraphs(tk.Frame):
    total_qc_graph_array = []   #([[graph_found_masses, masses, mass_tolerance],...])
    calc_avg_stdev = []         # array of calculated averages & std deviations

    def __init__(self, parent, controller):
        # QC Graphs Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Results with quality control graphs", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Show QC Graphs Button
        button1 = tk.Button(self, text="Show QC Graphs", bg="green", fg="white",
                            command=lambda: self.makegraph())
        button1.grid(column=0, row=1, sticky='w')
        graphs_tip = Hovertip(button1, 'Show output graphs', hover_delay=500)         # this needs a better message

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')
        searchparams_tip = Hovertip(button2, 'Return to Search Parameters page', hover_delay=500)

        # New Analysis Button
        button3 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis(), state=DISABLED)      # temporarily disabled
        button3.grid(column=2, row=1, sticky='w')
        newanalysis_tip = Hovertip(button3, 'Currently unavailabled', hover_delay=500)      # temporarily unavailable


    # MAKEGRAPH(): uses data from calculations above to form QC Graphs,
    # displayed in browser (will change to display in App later).
    def makegraph(self):
        # timing start
        start_time = timeit.default_timer()

        # max number of graphs is total number of input files
        # plus one for main graph w data averaged across conditions
        max_graphs = len(QCGraphs.total_qc_graph_array[0][1])
        qc_plots = []
        group_plots = []
        str_mass_names = []

        # change font size for QC graphs depending on number of masses
        if max_graphs < 7:
            graph_font_size = '16px'
            glyph_size = 20
        elif 8 <= max_graphs <= 12:
            graph_font_size = '12px'
            glyph_size = 10
        elif max_graphs > 13:
            graph_font_size = '10px'
            glyph_size = 6
        else:
            graph_font_size = '12px'
            glyph_size = 20

        # data is organized in chart by mass, abundance, and condition
        TOOLTIPS = [("Mass: ", "@x"),("Abundance (%): ", "@top"),("Condition: ", "@desc"),]
        TOOLTIPSQC = [("index", "$index"),("(x,y)", "($x, $y)"),("desc", "@desc"),]

        # averaged plot displayed first
        averaged_plot = figure(title="Averaged MS1 Data per Condition", x_axis_label="Mass", y_axis_label="Abundance (%)", tools="pan,box_zoom,wheel_zoom,reset,undo,save", active_drag="box_zoom",
                               active_scroll="wheel_zoom", x_range=((min(QCGraphs.masses)-100), (max(QCGraphs.masses)+100)),tooltips=TOOLTIPS, height=500)

        # convert searched masses to string values for legend
        for i in QCGraphs.masses:
            str_mass_names.append(str(i))

        # color selection variable used to change color AND
        # serves as the off-set for grouped data bar graphs
        color_selection = 0
        offset = 0.25
        for group_data in QCGraphs.calc_avg_stdev:
            group_name = []
            #adding stdev to avgs to get bar placement on graph
            lower, upper = [], []
            for i in range(len(group_data[1][0])): #average values
                lower.append(group_data[1][0][i]-group_data[1][1][i]) #average value for a mass i - stdev
                upper.append(group_data[1][0][i]+group_data[1][1][i]) #average value for a mass i + stdev
                group_name.append(group_data[0])

            color_palette = Category20c[20]                             # color palette 
            if color_selection == 19:                                   # once all colors used, reset & cycle back
                color_palette = Category20b[20]
                color_selection = 0

            data = {"x": QCGraphs.masses,
                    "lower": lower,                                     # can we just do this in a for loop
                    "upper": upper,                                     # with the calculations in the for loop above
                    "top": group_data[1][0],                            # and just get rid of the lower & upper vars
                    "desc": group_name}                                 # and the for loop up there

            source = ColumnDataSource(data=data)

            averaged_plot.vbar(x=dodge("x",offset), width=2, bottom=0, top="top",source=source,
                                legend_label="Condition: "+str(group_data[0]), color=color_palette[color_selection])
            averaged_plot.add_layout(Whisker(source=source, base=dodge("x",offset), upper="upper", lower="lower"))

            color_selection+=1
            offset+=2

        tab = []    

        for j in QCGraphs.total_qc_graph_array:                 # where j is each processed msalign file as an array
            idx = QCGraphs.total_qc_graph_array.index(j)        # used to title the graph after the cooresponding filename

            color_selection = 0
            color_palette = Category20c[20]

            filename = str(SearchParams.abrv_filenames[idx])[::-1]        # takes the uploaded file path as a string, reverses it, and saves this to the variable filename
            for i in range(len(filename)):
                if filename[i] == '/':
                    ext_filename = filename[0:i][::-1]    # takes the reversed file path up to the first '/', reversed, and saves this to the variable ext_filename
                    break

            p = figure(title="QC Graph for "+ext_filename,x_axis_label="Ret. time(s)", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                       active_scroll="wheel_zoom",y_axis_label="Intensity", tooltips=TOOLTIPSQC, active_drag="box_zoom", height=500)
            offset = .25
            v=[]
            for i in QCGraphs.masses:                           # for each mass... is this ret time?
                ret_time = []                                   # create empty arrays for ret_time, intensity, and mass
                intensity = []
                mass = []

                if color_selection == 19:                       # if reached end of color options
                    color_palette = Category20b[20]             # reset & cycle back
                    color_selection = 0

                for k in j[0]:              # j[0] is [graph_found_masses] of msalign file j and k is [ret. time, mass, intensity]
                    if (k[1] - QCGraphs.total_qc_graph_array[0][2]) <= i <= (k[1] + QCGraphs.total_qc_graph_array[0][2]):
                        ret_time.append(k[0])                   # if ret_time - ? <= mass??
                        mass.append(k[1])
                        intensity.append(k[2])
                mass_coord = [ret_time,mass,intensity]
                mass_coord = np.array(mass_coord)

                if len(mass_coord[0]) >=1:                      # if mass_coord nonempty
                    color_selection+=1

                    data = {"x": mass_coord[0],
                            "y": mass_coord[2],
                            "desc": mass_coord[1]}

                    source = ColumnDataSource(data=data)

                    z = p.vbar(x=dodge('x',offset), width=0.25, bottom=0, top='y', color=color_palette[color_selection], source=source) #legend_label=str(i))
                    v.append(z)
                    offset+=0.25
            legend_items = [LegendItem(label=str_mass_names[i]+"Da", renderers=[r]) for i, r in enumerate(v)]
            legend = Legend(items=legend_items,label_text_font_size=graph_font_size,glyph_width=5,label_standoff=1,
                            glyph_height=glyph_size,padding=1,spacing=1,margin=5,label_text_line_height=0.1,label_height=0)
            p.add_layout(legend,'right')
            p.legend.click_policy="hide"
            qc_plots.append(p)
            tab_temp = TabPanel(child=p, title=ext_filename)
            tab.append(tab_temp)
            del p
        
        date = datetime.today().strftime('%Y%m%d_%H%M%S')
        filename = "MS1_quant_graphs"+"_"+date+".html"      # names qcgraph file by date
        output_file(filename)                               # from bokeh, outputs file containing quant graphs \

        # make a graphical layout of all plots
        stylesheet = """
        :host(.bk-Tabs) .bk-header {
          font-size: 15px;
          max-width: 500px;
          overflow: hidden;
          border-color: orange;
        }

        .bk-tab {
            padding: 2px 3px;
            border: solid transparent;
            outline: 0;
            outline-offset: -5px;
            white-space: nowrap;
            cursor: pointer;
            text-align: center;
            max-width: 30px;
            border-color: orange;
            overflow: hidden;
            text-wrap: wrap;
        }

        .bk-tab.bk-active {
          font-size: 15px;
          max-width: 500px;
          overflow: hidden;
          background-color: orange;
        }
        """
        
        layout = row(averaged_plot,Tabs(tabs=tab, tabs_location='above', stylesheets=[stylesheet]),Tabs(tabs=VisualizeMS1FT.make_ms1ft_graphs(ext_filename),tabs_location='above',stylesheets=[stylesheet]))
        show(layout)

        ''' TO DO once "New Analysis" button fixed, move this there '''
        # clear out graphing data
        QCGraphs.total_qc_graph_array,QCGraphs.calc_avg_stdev,QuantOutput.averaged_data, App.processed_filearray = [],[],[],[]
        SearchParams.dynamic_counter = 1                                # need to reset counter if another search is done

        # timing end
        total_time = timeit.default_timer() - start_time
        print('QCGraphs \t makegraph \t\t\t', total_time)
        # with open("timing_0_makegraph.csv", "a") as out_file:       # timing output file for testing
            # out_file.write(str(total_time))
            # out_file.write("\n")

        # QC Graph output is last step of app but don't close app, just return
        return

class VisualizeMS1FT():
    
    def make_ms1ft_graphs(ext_filename):
        ms1ft_graphs = []
        for file in App.ms1ft_filenames:
            print(file)
            if os.path.isfile(file):
                print('found file')
                df_ms1ft = pd.read_csv(file,sep='\t')     # reads input file (tab delimited) into a pandas dataframe
                if df_ms1ft.columns[0] != "FeatureID":          # to make sure the file was formatted correctly, check that the first column heading is "FeatureID"
                    mb.showerror("File Error", "Check the MS1FT file: Expected 'FeatureID' as first column!") # question: is this the only column we should check?
                else:
                    df_ms1ft = df_ms1ft.sort_values(by='MonoMass').set_index(keys='MonoMass')   # sets the 'MonoMass' datapoint as the key for its corresponding data, and sorts the dataframe by it
                    #need to convert times from min to sec
                    #df_ms1ft["ElutionLength"]=np.where(df_ms1ft["ElutionLength"]*60)
                    #df_ms1ft["MaxElutionTime"]=np.where(df_ms1ft["MaxElutionTime"]*60)
                    #df_ms1ft["MinElutionTime"]=np.where(df_ms1ft["MinElutionTime"]*60)
                    cols = ['ElutionLength','MaxElutionTime','MinElutionTime']
                    df_ms1ft[cols] = df_ms1ft[cols].multiply(60)

                                          
                    date = datetime.today().strftime('%Y%m%d_%H%M%S')   # calculate exact time/date
                    
                    output_file("featuremap_"+date+".html", mode='inline')
                    VisualizeMS1FT.envelope_histogram(df_ms1ft)                                     # forms envelope histogram out of sorted dataframe containing ms1ft file data

                    #Autopopulate istopic distribution histogram with that of the most abundant ion
                    max_abd_idx = df_ms1ft['Abundance'].idxmax()
                    max_abd_C13 = df_ms1ft['C13'].loc[max_abd_idx]
                    max_abd_IsoAbd = df_ms1ft['IsoAbd'].loc[max_abd_idx]                    
                    initial_data = {'x': max_abd_C13, 'y':max_abd_IsoAbd}
                                    
                    source = ColumnDataSource(df_ms1ft)
                    source2 = ColumnDataSource(initial_data)



                    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
                    mapper = LogColorMapper(palette=colors, low=df_ms1ft['Abundance'].min(), high=df_ms1ft['Abundance'].max())

                    p = figure(title="Feature Map of "+ext_filename,
                               x_range=(0,df_ms1ft['MaxElutionTime'].max()+1), y_range=(0,30000), #y_range=(0,df_ms1ft.index.max()+1) = this will scale to largest mass identified, really impratical so i set to 30,000
                               toolbar_location="right",  x_axis_location="below",active_drag="box_zoom",active_scroll="wheel_zoom", height=300)

                    
                    iso_distrib = figure(title="Isotopic Distribution for: "+str(max_abd_idx),x_axis_label="C13", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                                        active_scroll="wheel_zoom",y_axis_label="Rel. Abundance", active_drag="box_zoom", height=200)
                     
                    z = iso_distrib.vbar(x='x', width=0.5, bottom=0, top='y', color="red", source=source2)


                    mass = p.rect(x="MinElutionTime", y="MonoMass", width='ElutionLength', height=2, source=source,
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

                    temp = layout([p, iso_distrib])
                    tab = TabPanel(child=temp, title=ext_filename)
                    ms1ft_graphs.append(tab)
                
        return ms1ft_graphs

    # Function Name: Envelope Histogram
    # Input: 1 list (or pandas dataframe?)
    # Output: updates input, no output?
    # Description: This function takes a list (of the data read from the input ms1ft file) and 
    def envelope_histogram(df_ms1ft):
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


print('Class\t\t Function \t\t\t Runtime (s)')
print('-------\t\t ----------\t\t\t -----------')







app = App()
app.mainloop()
