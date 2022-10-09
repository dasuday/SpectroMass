import numpy as np
import tkinter as tk
import time, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends._tkagg
matplotlib.use("TkAgg")
from matplotlib import style
style.use('ggplot')
import os, time
import statistics

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from operator import itemgetter, attrgetter
from datetime import datetime
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import *
from collections.abc import Iterable
from bokeh.models import ColumnDataSource, Whisker, HoverTool, Legend, LegendItem
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot
from bokeh.io import output_file
from bokeh.palettes import Category20b, Category20c
from bokeh.transform import dodge

LARGE_FONT= ("Verdana", 12)

class App(tk.Tk):
    
    msalign_filearray, processed_filearray, expgroup = [], [], [] #msalign_filearray is a 1D array [uniqueID#1, filename#1, uniqueID#2, filename#2,...]
    total_files = 0
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,"Mass Finder and Quantifier")
        
        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("1280x740")

        self.frames = {}

        for F in (StartPage, FileSelection, SearchParams, QuantOutput, QCGraphs):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
    
    def new_analysis(self):
        app = App()
        app.mainloop()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        button1 = ttk.Button(self, text="MS1 File Selection",
                            command=lambda: controller.show_frame(FileSelection))
        button1.grid(column=0, row=1, sticky='w')

        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')

        button3 = ttk.Button(self, text="Results Output",
                            command=lambda: controller.show_frame(QuantOutput))
        button3.grid(column=2, row=1, sticky='w')
        
        button4 = ttk.Button(self, text="Quality Control Graphs",
                            command=lambda: controller.show_frame(QCGraphs))
        button4.grid(column=3, row=1, sticky='w')        
        
        
        
class FileSelection(tk.Frame):
    
    gridrow = 4
    gridcolumn = 0
    button_identities,filelabel_identities,group_identities = [],[],[]

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text="MS1 File Selection", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        button2 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis())
        button2.grid(column=1, row=1, sticky='w')
    
        addbutton = tk.Button(self, text='Add File',  fg="green", command=(lambda : self.msalignfile()))
        addbutton.grid(column=0, row=2,sticky='w')
        
        self.controller = controller

    def msalignfile(self):    
        
        if App.total_files > 20:
            mb.showerror("Warning","Cannot load more files. Maximum files (20) reached.")
        else:
            filename = fd.askopenfilename(filetypes=[('All files','*.*')],
                                         title='Please select an MS1 MSALIGN file')
            if filename != "":
                filelabel = Label(self, text = 'File: '+filename)
                filelabel.grid(row=FileSelection.gridrow, column=FileSelection.gridcolumn, sticky='w')
                FileSelection.filelabel_identities.append(filelabel)
                
                group_label_entry = tk.Entry(self, width=13)
                group_label_entry.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+1, sticky='w')
                group_label_entry.insert(0,'<exp. group>')
                FileSelection.group_identities.append(group_label_entry) 

                removebutton = tk.Button(self, text='X', fg="red", command=(lambda : Xclick(filelabel,removebutton,group_label_entry)))
                removebutton.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+2)
                FileSelection.button_identities.append(removebutton)

                FileSelection.gridrow += 1
                App.msalign_filearray.append(filelabel)
                App.msalign_filearray.append(filename)

                App.total_files+=1
        
            #only process files when there are files to process
            if len(App.msalign_filearray) == 2:
                processbutton = tk.Button(self, text='Process File(s)', name='processbutton',  fg="green", command=(lambda : populate_entries()))
                processbutton.grid(column=0, row=20, sticky='w')
          
            
        #This function removes the file name from the array and destroys the label and corresponding
        #removal button. It uses the tkinter name for the button (e.g., !button) to identify which
        #button was clicked and the corresponding label and file name to remove. 
        def Xclick(filelabel,removebutton,group_label_entry):
            #n = FileSelection.filelabel_identities.index(filelabel)
            filelabel.destroy()
            removebutton.destroy()
            group_label_entry.destroy()
            FileSelection.button_identities.remove(removebutton)
            FileSelection.filelabel_identities.remove(filelabel)
            FileSelection.group_identities.remove(group_label_entry)  
            
            for i in App.msalign_filearray:
                if i == filelabel: 
                    del App.msalign_filearray[App.msalign_filearray.index(i)+1]
                    del App.msalign_filearray[App.msalign_filearray.index(i)]
            
            App.total_files-=1
            
            #remove the processing function if there are no files
            if len(App.msalign_filearray) == 0:
                self.nametowidget('processbutton').destroy()
        
        def populate_entries():
            for group in self.group_identities:
                group_name = group.get()
                App.expgroup.append(group_name)
            
            #abbreviate msalign MS1 filenames for graphing display
            for i in range(1,len(App.msalign_filearray),2):
                temp_name=App.msalign_filearray[i].split("/")[-1]
                SearchParams.abrv_filenames.append(temp_name)            
            
            self.controller.show_frame(SearchParams)
                   
    
class SearchParams(tk.Frame):
    abrv_filenames = [] #abbreviate filenames for display purposes
    entries = []
    dynamic_entries = [] #('file name1', ('start ret time1', entry1),('end ret time1, entry1'),'file name2',...)
    dynamic_counter = 1 #this will be used for file-specific search conditions (e.g., retention times)
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Search Parameters", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')
        
        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row=3, column = 0)
        self.mass_range = IntVar()
        
        
        option_list = ['Static','Dynamic']
        self.search_optn = StringVar(self)
        self.search_optn.set('Static') 
        self.popupMenu = OptionMenu(self, self.search_optn, *option_list)
        label2 = tk.Label(self, text="Search Mode:")
        label2.grid(row = 0, column = 1)
        self.popupMenu.grid(row = 0, column =2)
        self.search_optn.trace('w',self.get_parameters)
        
        self.controller = controller
        
        self.get_parameters(self) #pre-populate search options w/static parameters
        
        processbutton = tk.Button(self, text='Process File(s)', name='pbutton',  fg="green", command=(lambda : self.process_msalign_files()))
        processbutton.grid(column=0, row=2, sticky='w')
        
        self.e=StringVar()
        self.e.set("Loading")    

    def get_parameters(self,*args):
        SearchParams.entries = []
        SearchParams.dynamic_entries = []
        
        def change_range(self,*args):
            
            print('mass_range get',self.mass_range.get())
            if self.mass_range.get() == 1:
                self.mass_field.config(text = 'Mass range (min, max, interval): ')
                self.mass_max.grid(row=3, column=2,sticky='news')
                self.mass_interval.grid(row=3, column=3,sticky='news')
            
            if self.mass_range.get() == 0:
                self.mass_max.grid_forget()
                self.mass_interval.grid_forget()
                self.mass_field.config(text = 'Masses: ')
     
            
        if self.search_optn.get() == "Static":
            for child in self.entry_frame.winfo_children():
                child.destroy()
            self.mass_range.set(0)
                
            self.entry_frame = tk.Frame(self)
            self.entry_frame.grid(row=3, column = 0, sticky='w')
                
            s_fields = ('Start scan', 'End scan', 'Start ret. time', 'End ret. time', 'Masses','Mass Tolerance (Da)')
            i=3  #start grid at row 3 
            
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                SearchParams.entries.append((field, ent))
                i+=1
        
            #pre-set parameters / can be changed by user
            #H4 [11318,11332,11346,11360,11374,11388,11402,11416,11430,11444,11458,11472,11486,11500,11514,11528,11542,11556]
            #H4ox [11334, 11348, 11362,11376,11390,11404,11418,11432,11446,11460,11474,11488,11502,11516,11530,11544,11558]
            H3 = [15168,15182,15196,15210,15224,15238,15252,15266,15280,15294,15308,15322,15336,15350,15364,15378,15392,15406,15430,15444,15458,15472,15486,15500]
            H2A = [13488,13530,13572,13545,13587,13629,13700,13742,13784,13713,13755,13797]
            
            SearchParams.entries[0][1].insert(0,1)     #Start scan
            SearchParams.entries[1][1].insert(0,11111) #End scan
            SearchParams.entries[2][1].insert(0,1)     #Start ret. time
            SearchParams.entries[3][1].insert(0,11111) #End ret. time
            SearchParams.entries[4][1].insert(0,H3)    #Masses
            SearchParams.entries[5][1].insert(0,2)     #Mass Tolerance (Da)
        
        if self.search_optn.get() == "Dynamic":
            for child in self.entry_frame.winfo_children():
                child.destroy()
            self.mass_range.set(0)
                
            self.entry_frame = tk.Frame(self)
            self.entry_frame.grid(row=3, column = 0, sticky='w')
        
            s_fields = ('Mass Tolerance (Da)',)
            d_fields = ('Start ret. time', 'End ret. time')
            
            self.mass_range_btn = tk.Checkbutton(self.entry_frame, text="Search by mass range: ", variable=self.mass_range, command=(lambda : change_range(self)))
            self.mass_range_btn.grid(row=0,column=3, columnspan=2, sticky='news')
            
            #fixed 'Masses' to index 0 of entries. the entry will either serve as a mass list OR the min mass
            #for dynamic searching
            self.mass_field = tk.Label(self.entry_frame, width=20, text='Masses', anchor='w')
            self.mass_field_ent = tk.Entry(self.entry_frame, width=8)
            self.mass_field.grid(row=3, column=0,sticky='news')
            self.mass_field_ent.grid(row=3, column=1,sticky='w')
            self.mass_max = tk.Entry(self.entry_frame, width=8) #make entry, but don't show until needed
            self.mass_interval = tk.Entry(self.entry_frame, width=8) #make entry, but don't show until needed
            SearchParams.entries.append(('Masses',self.mass_field_ent,self.mass_max,self.mass_interval))
            
            i=4 #start grid at row 3 
            
            #masses will be at row 3 (label at column 0, entry at column 1)
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                SearchParams.entries.append((field, ent))
                i+=1
            
            for files in SearchParams.abrv_filenames:
                lab = tk.Label(self.entry_frame, width=20, text=str(files), anchor='w')
                lab.grid(row=i, column=0,columnspan=3,sticky='news')
                SearchParams.dynamic_entries.append(files)
                j=2
                for field in d_fields:
                    lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                    ent = tk.Entry(self.entry_frame, width=8)
                    lab.grid(row=i, column=j, columnspan=1, sticky='news')
                    ent.grid(row=i, column=j+1, sticky='w')
                    SearchParams.dynamic_entries.append((field, ent))
                    j+=2
                i+=1
        
    
    def process_msalign_files(self):
        error = False
        
        if len(App.msalign_filearray) == 0:
            mb.showerror("Warning","There are no files to process.")
          
        if self.search_optn.get() == "Static":
            for field in SearchParams.entries:
                if len(field[1].get()) == 0:
                    mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break            
        
        if self.search_optn.get() == "Dynamic":
            for field in SearchParams.entries:
                if len(field[1].get()) == 0:
                    mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break
            for field in range(len(SearchParams.dynamic_entries)):
                if len(SearchParams.dynamic_entries[field]) == 2:
                    if len(SearchParams.dynamic_entries[field][1].get()) == 0:
                        mb.showerror("Warning", "All search parameter fields must be filled out.")
                        error = True
                        break 
                
        if len(App.msalign_filearray) > 0 and error == False:
            self.loading = tk.Label(self, textvariable=self.e) 
            self.loading.grid(column=0, row=2, columnspan=1, sticky="w")
            
            for i in range(1,len(App.msalign_filearray),2):
                self.update_progress((i/len(App.msalign_filearray)))
                SearchParams.process(self,App.msalign_filearray[i])
                
            self.loading.destroy()
            self.controller.show_frame(QuantOutput) #When all the calculations are complete, move to the next analysis page.
    
 
    def update_progress(self,progress):
        
        barLength = 15 # Modify this to change the length of the progress bar
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        progresstext = "\rLoading (%): [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
        self.e.set(progresstext)
        #sys.stdout.write(progresstext)            
              
    def process(self,filename):
        
        global scan_ions #for now, leave global, but this will be a passed array eventually
        scan_ions = []
        temp_array = [0,0,0,0]
        ms1_ions = []
        ms1events = 0
        convert = []
        lines = []
        
        def rmv_chars(string):
            
            getVals = list([val for val in string 
                if (val.isnumeric() or val==".")]) 
            return "".join(getVals)
       
        with open(filename) as fp:
            data = fp.read()

        for i in data:
            if i == ',' or i == '\n':
                link = "".join(convert)
                link.strip()
                if len(link) > 1:
                    lines.append(link)
                    convert = []
            else:
                convert.append(i)
        
        while (len(lines)-1)>0:
            text = str(lines[0])
            if text.startswith('ID='):
                temp_array[0] = int(rmv_chars(text))
                self.update()
            elif text.startswith('SCANS='):
                temp_array[1] = int(rmv_chars(text))
            elif text.startswith('RETENTION_TIME='):
                temp_array[2] = float(rmv_chars(text))
            elif text[0].isdigit():
                while lines[0]!='END IONS':
                    ms1_ions = np.append(ms1_ions,[float(s) for s in lines[0].split("\t")])
                    del lines[0]
                ms1_ions = np.reshape(ms1_ions,(int(len(ms1_ions)/3),3))
                temp_array[3] = ms1_ions
                scan_ions.append(temp_array)
                temp_array = [0,0,0,0]
                ms1_ions = []
                ms1events+=1
            del lines[0]
        
        #This is very important: Here is the final format of the np array:
        #For each scan, the format is [ID,SCANS,RETENTION_TIME,[ARRAY OF MS1 IONS]]
        #The array of MS1 ions is [Mass,Intensity,Charge]
        SearchParams.mass_selection(self,scan_ions) #forced pass, will change later to be user-controlled
        
    def mass_selection(self,scan_ions):
        masses = []
        input_masses = [0]
        
        if self.search_optn.get() == "Static":
            scan_min = float(SearchParams.entries[0][1].get())
            scan_max = float(SearchParams.entries[1][1].get())
            retention_min = float(SearchParams.entries[2][1].get())
            retention_max = float(SearchParams.entries[3][1].get())
            input_masses = str(SearchParams.entries[4][1].get())
            mass_tolerance = float(SearchParams.entries[5][1].get())
        
        if self.search_optn.get() == "Dynamic":
            scan_min = 0 #default to ret time min
            scan_max = 30000 #default to ret time max
            retention_min = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter][1]).get())
            retention_max = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter+1][1]).get())
            SearchParams.dynamic_counter+=3
            if self.mass_range.get() == 1:
                min_mass = float(SearchParams.entries[0][1].get())
                max_mass = float(SearchParams.entries[0][2].get())
                mass_interval = float(SearchParams.entries[0][3].get())
                mass_tolerance = float(SearchParams.entries[1][1].get())
                masses = [min_mass]
                
                temp_mass = min_mass
                while temp_mass <= max_mass:
                    temp_mass+=mass_interval
                    masses.append(temp_mass)
                print('mass range=',masses)
            else:
                input_masses = str(SearchParams.entries[0][1].get())
                mass_tolerance = float(SearchParams.entries[1][1].get())
                
    
        found_masses = []
        graph_found_masses = [] #this array will pass on 0 intensity values for QC graphs
        convert = []
        pool = []
        
        if type(input_masses[0]) == str:
            masses = []
            for idx, val in enumerate(input_masses):
                if val == ',' or val == ' ': 
                    link = "".join(convert)
                    pool.append(link)
                    convert = []
                elif idx == (len(input_masses)-1) and input_masses[idx].isnumeric():
                    convert.append(input_masses[idx])
                    link = "".join(convert)
                    pool.append(link)
                else:
                    convert.append(val)

            for i in pool:
                masses.append(float(i))
        
        #Search through scan_ion array using parameters above and output array [retention time, mass, intensity]
        #for each of the masses in the array.
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
        
        SearchParams.mass_quantification(self,found_masses, masses, mass_tolerance)
        
        
        QCGraphs.graph_found_masses, QCGraphs.masses, QCGraphs.mass_tolerance = graph_found_masses, masses, mass_tolerance
        qc_graph_result = [graph_found_masses, masses ,mass_tolerance]
        QCGraphs.total_qc_graph_array.append(qc_graph_result)
                
    def mass_quantification(self,found_masses,masses, mass_tolerance):
        summed_intensities = []
        total_intensity = 0
        percent_intensities = []
        
        for i in masses:
            intensity = 0
            for j in found_masses:
                if (j[1] - mass_tolerance) <= i <= (j[1] + mass_tolerance):
                    intensity = intensity + j[2]
            summed_intensities.append([i,intensity])
        
        for i in summed_intensities:
            total_intensity = total_intensity + i[1]
        
        if total_intensity > 0:
            for i in summed_intensities:
                percent_intensities.append([i[0],(i[1]/total_intensity*100)]) 

            App.processed_filearray.append(percent_intensities) #((mass1,percent1),(mass2,percent2),...)
        else:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)
                  

class QuantOutput(tk.Frame):
    averaged_data = [] #[[averages],[stdev]]

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Results Output", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')
        
        button1 = tk.Button(self, text="Calculate Avg and Stdev", fg='green',
                            command=lambda: self.analyze_data())
        button1.grid(column=0, row=1, sticky='w')
        
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')
        
        self.controller = controller

    def analyze_data(self):
        restructured_data, grouped_data,calc_avg_stdev, temp_array = [],[],[],[]
        print('len of processed_filearray, exgroup = ',len(App.processed_filearray),len(App.expgroup))
        processed_filearray_temp = App.processed_filearray
        expgroup_temp = App.expgroup
        
        #restructure data into a new array [[group1, [data1]], [group2, [data2]],...] where [data] is [mass, intensity]
        
        if len(expgroup_temp) == 0 or len(processed_filearray_temp) == 0:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)
        else:
            for i in range(len(expgroup_temp)):
                temp_array = [expgroup_temp[i],processed_filearray_temp[i]]
                restructured_data.append(temp_array)
        
        #sort data based on group name [[group1, [data1]], [group1, [data2]], [[group2],[data1]],...]
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

        #the final product [[group1, [avg,stdev]],[group2, [avg,stdev],...] will be sent to the same
        #variable in the QCGraphs for graph creation
        QCGraphs.calc_avg_stdev = calc_avg_stdev
        self.output_quantification_file()
        self.controller.show_frame(QCGraphs)
        
        
    def calculate_avg_stdev(self,grouped_data):
        averaged_values = []
        stdev_values = []
        mass_array = []
        
        for mass in QCGraphs.total_qc_graph_array[0][1]: #these are user-defined searched masses
            temp_array = []
            temp_array.append(mass)
            for i in grouped_data:
                for j in i:
                    if j[0] == mass:
                        temp_array.append(j[1])
            mass_array.append(temp_array)
        
        print('mass array',mass_array)
        for i in mass_array:
            stdev_values.append(statistics.pstdev(i[1:]))
            averaged_values.append(statistics.mean(i[1:]))
          
        calculated_group_data = [averaged_values,stdev_values]
        return calculated_group_data       

    def output_quantification_file(self):
        
            date = datetime.today().strftime('%Y%m%d_%H%M%S')
            filenames = []
            a = []

            if (len(App.processed_filearray)) == 0:
                mb.showerror("Warning", "Based on your search criteria, no results were generated.")
            else:
                filename = "MS1_quantification"+"_"+date+".csv"
                with open(filename,"a") as out_file:   
                    for i in range(len(SearchParams.abrv_filenames)):
                        out_file.write(str(SearchParams.abrv_filenames[i])+"\n")
                        for j in App.processed_filearray[i]:
                            x,y = str(j[0]),str(j[1])
                            temp = (x+','+y+',')
                            out_file.write(temp)
                        out_file.write(" \n")
                            
class QCGraphs(tk.Frame):
    total_qc_graph_array = [] #([[graph_found_masses, masses ,mass_tolerance],...])
    calc_avg_stdev = []

    def __init__(self, parent, controller):
        
        
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text="Results with quality control graphs", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')        
        
        button1 = tk.Button(self, text="Show QC Graphs", fg ='green',
                            command=lambda: self.makegraph())
        button1.grid(column=0, row=1, sticky='w')
        
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')
        
        button3 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis())
        button3.grid(column=2, row=1, sticky='w')        
            
    def makegraph(self):
        
        max_graphs = len(QCGraphs.total_qc_graph_array[0][1])
        qc_plots, group_plots, str_mass_names = [],[],[]
               
        #change font size for QC graphs depending on number of masses
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
        
        TOOLTIPS = [("Mass: ", "@x"),("Abundance (%): ", "@top"),("Condition: ", "@desc"),]
        TOOLTIPSQC = [("index", "$index"),("(x,y)", "($x, $y)"),("desc", "@desc"),]
   
        averaged_plot = figure(title="Averaged MS1 Data per Condition", x_axis_label="Mass", y_axis_label="Abundance (%)", tools="pan,box_zoom,wheel_zoom,reset,undo,save", active_drag="box_zoom",
                               active_scroll="wheel_zoom", x_range=((min(QCGraphs.masses)-100), (max(QCGraphs.masses)+100)),tooltips=TOOLTIPS, plot_width=1080, plot_height=740)

        #need to convert searched masses to string values for legend
        for i in QCGraphs.masses:
            str_mass_names.append(str(i))
            
        #using the color selection variable to both change color AND serve as the off-set for grouped data bar graphs
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
            
            color_palette = Category20c[20]
            if color_selection == 19:
                color_palette = Category20b[20]
                color_selection = 0
                
            
            
            data = {"x": QCGraphs.masses,
                    "lower": lower,
                    "upper": upper, 
                    "top": group_data[1][0],
                    "desc": group_name}
            
            source = ColumnDataSource(data=data)

            averaged_plot.vbar(x=dodge("x",offset), width=2, bottom=0, top="top",source=source,
                                legend_label="Condition: "+str(group_data[0]), color=color_palette[color_selection])
            averaged_plot.add_layout(Whisker(source=source, base=dodge("x",offset), upper="upper", lower="lower"))

            color_selection+=1
            offset+=2

        
        for j in QCGraphs.total_qc_graph_array: # where j is each processed msalign file as an array
            idx = QCGraphs.total_qc_graph_array.index(j) #used to title the graph after the cooresponding filename
            
            color_selection = 0
            color_palette = Category20c[20]        
            
            p = figure(title="QC Graph for "+str(SearchParams.abrv_filenames[idx]),x_axis_label="Ret. time(s)", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                       active_scroll="wheel_zoom",y_axis_label="Intensity", tooltips=TOOLTIPSQC, active_drag="box_zoom", plot_width=1080, plot_height=740)
            offset = .25
            v=[]
            for i in QCGraphs.masses:
                ret_time = []
                intensity = []
                mass = []
                
                if color_selection == 19:
                    color_palette = Category20b[20]
                    color_selection = 0
                    
                for k in j[0]: #j[0] is [graph_found_masses] of msalign file j and k is [ret. time, mass, intensity]
                    if (k[1] - QCGraphs.total_qc_graph_array[0][2]) <= i <= (k[1] + QCGraphs.total_qc_graph_array[0][2]):
                        ret_time.append(k[0])
                        mass.append(k[1])
                        intensity.append(k[2])
                mass_coord = [ret_time,mass,intensity]
                mass_coord = np.array(mass_coord)

                if len(mass_coord[0]) >=1:
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
            del p
        
        date = datetime.today().strftime('%Y%m%d_%H%M%S')
        filename = "MS1_quant_graphs"+"_"+date+".html"
        output_file(filename)

        # make a grid
        grid = gridplot([[averaged_plot,None],qc_plots], merge_tools = False, toolbar_location="left", plot_width=800, plot_height=500)
        show(grid)

        #clear out graphing data
        QCGraphs.total_qc_graph_array ,QCGraphs.calc_avg_stdev,QuantOutput.averaged_data, App.processed_filearray = [],[],[],[]
        SearchParams.dynamic_counter = 1 #need to reset counter if another search is done
        
        return




app = App()
app.mainloop()
