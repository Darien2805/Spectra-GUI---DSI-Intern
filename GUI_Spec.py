# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 11:46:13 2017

@author: NPStudent
"""
import os
import csv
import fnmatch
import numpy as np
import tkinter
import scipy.misc
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from scipy.signal import savgol_filter

def browse():
    global file_list
    global file_name
    
    file_list = []
    file_name = []
    #ask directory
    directory = filedialog.askdirectory()
    #reading all files in the directory
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.txt'):
            file_list.append(os.path.join(root, filename))
            file_name.append(filename)
                      
    #Insert Directory
    LB.delete(0, END)
    LB.insert(0, directory)
    
    return read()

def read():
    global file_list
    global file_n
    global dist
    global max_minf
    global min_maxf
    global array_norm
    global array_norm1
    global holding_frequency
    global holding_field
    global savetxt
    global savefittxt
    
    #number of files
    file_n = len(file_list)
    #Insert number of files
    LBf.delete(1,END)
    LBf.insert(1, file_n)
    #creation on empty array
    holding_minf = np.zeros(file_n)
    holding_maxf = np.zeros(file_n)
    holding_frequency= np.zeros(file_n)
    
    n=0
    i=0;
    for filename in file_list:
        with open(filename, "r") as file:
            data = []
            file.readline()[1:]
            reader = csv.reader(file, delimiter='\t')
            for line in reader:
                data.append(line)
                n = n + 1
        data = np.float64(data)
        #creation of holding cells
        holding_field = np.zeros(n)
        #input into holding cells
        holding_field = data[:,0]   
        holding_frequency[i]=data[1,1]
        #max and mean of field
        holding_maxf[i] = np.max(holding_field)
        holding_minf[i] = np.min(holding_field)
    
        i=i+1;

    holding_minf = np.ceil(holding_minf)
    holding_maxf = np.ceil(holding_maxf)
    
    #create array of len(maxf-minf), len(files)
    max_minf = np.max(holding_minf)
    min_maxf = np.min(holding_maxf)
    dist = np.arange(max_minf,min_maxf+1)
    #array = np.empty([file_n,len(dist)])
    #array_off = np.empty([file_n,len(dist)])
    array_norm = np.empty([file_n,len(dist)])
    array_norm1 = np.empty([file_n,len(dist)])
    savetxt = np.empty([file_n+1,len(dist)])
    savefittxt = np.empty([file_n+1,len(dist)])
    
    return

def interpolation():
    global m
    global dist
    global max_minf
    global min_maxf
    global arraynorm_sort
    global arraynorm1_sort
    global holding_frequency
    global freq_sort_i
    global freq_sort
    global array_norm
    global array_norm1
    global holding_cell
    
    h = 0
    m=0 
    for filename in file_list:
        
        with open(filename, "r") as file:
            new_data = []
            file.readline()[1:]
            reader = csv.reader(file, delimiter='\t')
            for new_line in reader:
                    new_data.append(new_line)
            new_data = np.float64(new_data)
            holding_amp = new_data[:,2]
            new_holdingfield = new_data[:,0]
            #order_field[h] = new_data[:,0]
            #interpolate out
            inter = interp1d(np.ceil(new_holdingfield), holding_amp)
            
            #array inter
            #array[h] = inter(dist)
            #array offset
            #offset = np.min(holding_amp)
            #array_off[h] = inter(dist)-offset
            
            if not (windl.get()%2) == 0: 
            
                array_norm1[h] = (inter(dist)-np.min(holding_amp))/ (np.max(holding_amp)- np.min(holding_amp))
                array_norm[h] = savgol_filter(array_norm1[h], windl.get(), 2, mode='nearest')
                
            else: 
                
                errormess()
            
            h = h + 1;
    freq_sort_i=np.argsort(holding_frequency[:])
    #array_sort=-1*array[np.argsort(holding_frequency[:])]
    freq_sort = holding_frequency[freq_sort_i]
    #arrayoff_sort =-1*array_off[freq_sort_i]
    arraynorm_sort = -1*array_norm[freq_sort_i]
    arraynorm1_sort = -1*array_norm1[freq_sort_i]
    
    holding_cell = np.zeros([1000,3])
    
    #plotting of spectra image
    plt.imshow(np.flipud(arraynorm1_sort), extent=(np.min(dist), np.max(dist), np.min(freq_sort), np.max(freq_sort)),aspect = (np.max(dist)-np.min(dist))/(np.max(freq_sort)-np.min(freq_sort)))
    #saving the image
    plt.savefig('Normimg.jpg', bbox_inches = 'tight')    
    photo = ImageTk.PhotoImage(Image.open("Normimg.jpg"))
    label.config(image = photo)
    label.image =photo
    
    return()

def graph():
    global j
    global m
    global file_n
    global arraynorm_sort
    global arraynorm1_sort
    global holding_field
    global file_name
    global freq_sort_i
    global freq_sort
    global dist
    global holding_cell
    global holding_points
    global print_cell
    
    plt.close()
    if j in range(0, file_n):
            
        LBf1.delete(1, END)
        LBf1.insert(1, file_name[freq_sort_i[j]])
            
        if not np.any(holding_cell[:,0] == j+1):
            #local maxima in indices form
            localmax_position = [argrelextrema(arraynorm_sort[j], np.greater, order = np.int((np.size(holding_field)/4)))]
            #local maxima in coordinate position form
            localmax_coor = arraynorm_sort[j][argrelextrema(arraynorm_sort[j], np.greater, order = np.int((np.size(holding_field)/4)))[0]]

            for k in range(0, np.size(localmax_coor)):
                holding_cell[m] = [j+1,dist[localmax_position[0][0][k]],localmax_coor[k]]

                m = m+1
                
            holding_cell = np.delete(holding_cell,np.where(holding_cell[:,1] > 5000),0)
            
            holding_cell = np.delete(holding_cell,np.where(holding_cell[:,1] < -5000),0)
            
            holding_cell = holding_cell[np.argsort(holding_cell[:,0])]
        #plot
        fig, ax= plt.subplots()          
        ax.plot(dist,arraynorm_sort[j])
        holding_points=holding_cell[holding_cell[:,0] == j+1]
        ax.plot(holding_points[:,1],holding_points[:,2], 'ro', ms = 10)
        #showing in GUI
        canvas = FigureCanvasTkAgg(fig, master=frame1)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=2, column=3)
        plt.show()

        #mouse events
        cid=fig.canvas.mpl_connect('motion_notify_event', motion)
        cid=fig.canvas.mpl_connect('button_press_event', click)
        #highlighting             
        highlight = 0.7*arraynorm1_sort 
        highlight[j] = arraynorm1_sort[j]
        normimg = plt.imshow(np.flipud(highlight), extent=(np.min(dist), np.max(dist), np.min(freq_sort), np.max(freq_sort)),aspect = (np.max(dist)-np.min(dist))/(np.max(freq_sort)-np.min(freq_sort)))
        plt.savefig('Normimg.jpg', bbox_inches = 'tight')    
        photo = ImageTk.PhotoImage(Image.open("Normimg.jpg"))
        label.config(image = photo)
        label.image =photo
        
        #insert of maximum point in listbox
        LBc1.delete(0,END)
        
        if np.any(holding_cell[:,0] == 0):
        
            print_cell = np.delete(holding_cell, np.where(holding_cell[:,0] == 0),0)
    
            for jn in range(0,j+1):
                print_pos = np.where(print_cell[:,0] == jn+1)
            
                for d in range(0, np.size(print_pos)):
                    pslice = print_pos[0][d]
                    print_cell[pslice][0] = freq_sort[jn]
   
        print_cell = print_cell[np.argsort(print_cell[:,0])]
        
        for linepoints in range (0,np.size(print_cell[:,0])):
            LBc1.insert(END, print_cell[linepoints])
        
        return()
    
    else:
        return error()

    
def next_g():
    global j
    
    j = j+1
    return graph()
    
def prev_g():
    global j
    
    j = j - 1
    return graph()


def error():
    global j
    global file_n
    
    messagebox.showerror("Error", "Number not in range")
    
    if j<0:
        j = j + 1
    
    if j>0:
        j = j - 1
        
    return

def errormess():
    
    messagebox.showerror("Error", "Number input is odd or zero! Please try again!")
    Wle.delete(0, END)
    interpolation()
    return 

def motion(event):
    
    if (event.xdata is not None) and (event.ydata is not None):
        LB2.delete(1,END)  
        LB2.insert(1,"( %0.2f, %0.2f )" %(event.xdata, event.ydata))
    return

def click(event):

    global coor_xy
    global leftclick
    global rightclick
    global holding_cell
    
    if event.button == 1:
       
        leftclick = leftclick + 1
        coor_xy = [event.xdata, event.ydata]
        
        LBc.delete(3, END)
        LBc.insert(3, "                                   Left Click [Add]")
        LBc.insert(4, "---------------------------------------------------------------------")
        LBc.insert(5, "Number of left clicks :  %0.f" %leftclick)
        LBc.insert(6,"Mouse Position clicked :( %0.2f, %0.2f )" % (event.xdata, event.ydata))  
        
        add()
        
    if event.button == 3:

        rightclick = rightclick + 1
        coor_xy = [event.xdata, event.ydata]
        LBc.delete(3, END)
        LBc.insert(3, "                               Right Click [Remove]")
        LBc.insert(4, "---------------------------------------------------------------------")
        LBc.insert(5, "Number of right clicks :  %0.f" %rightclick)
        LBc.insert(6, "Mouse Position clicked :  ( %0.2f %0.2f )"% (event.xdata, event.ydata))
        
        remove()    
   
    return graph()

def remove():
    
    global holding_cell
    global coor_xy
  
    #extract local max point on __ files
    lmax = holding_cell[holding_cell[:,0] == j+1]
    #locate which nearest point selected
    diff = abs(lmax[:,1] - coor_xy[0])
    smallest = np.min(diff)
    #locate whole array values
    position = lmax[np.where(diff == smallest)[0][0]]
    #delete(array, indices position)
    newholding_cell = np.delete(holding_cell, np.where(holding_cell[:,1] == position[1])[0][0],0)
    holding_cell = newholding_cell
    
    return

def add():
    
    global holding_cell
    global j
    global pos
    global arraynorm_sort
    global coor_xy
    global nlocalmax_coor
    global nlocalmax_position
       
    #add_indx = np.sum(dist<coor_xy[0]) -1
    #y_v = arraynorm_sort[j][add_indx]
    
    newdist = np.arange((coor_xy[0]-400), (coor_xy[0]+400)+1)
    newarray_sort = arraynorm_sort[j][np.where(np.logical_and(dist>=(coor_xy[0]-400),dist<=(coor_xy[0]+400)))]

    #local maxima in indices form
    nlocalmax_position = [argrelextrema(newarray_sort, np.greater, order = 1000)]
    #local maxima in coordinate position form
    nlocalmax_coor = newarray_sort[argrelextrema(newarray_sort, np.greater, order = 1000)]
    
    pos = np.sum(holding_cell[:,0] > 0)
    holding_cell[pos] = np.array([ j+1, newdist[nlocalmax_position[0][0][0]],nlocalmax_coor])  
    
    return

def saving():
    
    global arraynorm1_sort
    global savetxt
    
    result = messagebox.askyesno("Save", "Save file?")
   
    if result == True:
        
        savetxt[0] = dist
        for a in range (0, file_n):
            savetxt[a+1] = arraynorm1_sort[a]
            
        np.savetxt('arrayimg.dat', savetxt, fmt='%0.6e', delimiter='\t')

    return

def save_graph():
    
    global holding_cell
    global arraynorm_sort
    global savefittxt
    global print_cell
    
    result1 = messagebox.askyesno("Save", "Save file?")
    
    if result1 == True:
        
        savetxt[0] = dist
        for b in range (0, file_n):
            savetxt[b+1] = arraynorm_sort[b]
            
        np.savetxt('arrayfit.dat', savetxt, fmt='%0.6e', delimiter='\t')
        
        save_cell = print_cell
        
        np.savetxt('Localmax.dat', save_cell, fmt = '%0.6e', delimiter = '\t')
    
    return
   
global j
global rightclick
global leftclick
j = 0
rightclick = 0
leftclick = 0

root = Tk()
windl = IntVar()
#top frame
frame1 = LabelFrame(root, width=100, height = 200, text = 'Spectra Image')
frame1.pack(fill= 'both', expand= 'yes')
#frame for buttons (bottom frame)
frame2 = Frame(root, width = 50, height = 50)
frame2.pack(fill = 'both', expand = 'yes')
#frame for picture : spectra
frame3 = LabelFrame(frame1)
frame3.grid(row=3, column =1)
#frame for  graph
frame4 = LabelFrame(frame1,text = 'Spectra Individual Graph')
frame4.grid(row = 3, column = 3)
#frame for mouse events
frame5 = LabelFrame(frame1, text = 'Mouse events')
frame5.grid(row = 2, column = 4, padx = 5)
#frame for left/right click
frame6 = LabelFrame(frame1)
frame6.grid(row = 3, column = 4, padx = 20)

#Image Label
label = Label(frame1)  
label.grid(row=2, column=1, columnspan = 1, rowspan = 1)

#Label : Picture
L = Label(frame1, text = 'Picture', fg= "dark blue", font = "Verdaba 14 bold")
L.grid(row=0, column=1)
#listbox for folder running
LBf = Listbox(frame1, relief = RAISED, bd = 5, height = 2, width = 40)
LBf.grid(row = 1, column = 1)
LBf.insert(0, "Number of files :")
#Label : Graph
L = Label(frame1, text = 'Graph', fg= "dark blue", font = "Verdaba 14 bold")
L.grid(row=0, column=3)#listbox for in which file the graph comes from
LBf1 = Listbox(frame1, relief = RAISED, bd = 5, height = 2, width = 60)
LBf1.grid(row = 1, column = 3)
LBf1.insert(0, "File Name :")
#Label :Spectra
L1 = Label(frame3, text = 'Spectra', fg = 'Purple', font = "verdaba 14 bold")
L1.grid(row=0, column = 1, padx = 30)
#Button : save array
Bss = Button(frame3, text = 'Save', command = saving, width = 12, font = 'Times 12 bold', bg = 'cyan')
Bss.grid(row = 0 , column = 2, padx = 30)
#Listbox
LB1 = Listbox(frame1, relief = RAISED, bd = 5, height = 20, width = 1)
LB1.grid(row = 2, column = 2, padx = 15)

#label for graph plot
Graphframe = Label(frame4)
Graphframe.grid(row=3, column = 3)
#motion for graph
LB2 = Listbox(frame5, relief = RAISED, bd = 5, height = 2, width = 28)
LB2.grid(row = 0, column = 0)
LB2.insert(0,"Mouse Position( x , y ):")
#Mouse events
LBc = Listbox(frame5, relief = RAISED, bd = 5, height = 7, width = 52)
LBc.grid(row = 1, column = 0)
LBc.insert(0, ' =============================================')
LBc.insert(1, '                                  MOUSE EVENTS')
LBc.insert(2, ' =============================================')
#scroll
scrollbar = Scrollbar(frame5)
scrollbar.grid(row = 2,column = 1)#row = 0, column = 1, sticky = "ns")
LBc1 = Listbox(frame5, relief = RAISED, bd = 5, height = 11, width = 52, yscrollcommand = scrollbar.set )
LBc1.grid(row = 2, column = 0)
scrollbar.config( command = LBc1.yview )

#mouse directions/instructions
LBr = Label(frame6, text = "Left click to add region", fg = "brown", font = "Verdaba 10 bold")
LBr.grid(row = 0, column = 0)
LBl = Label(frame6, text = "Right click to remove region", fg = "brown", font = "Verdaba 10 bold")
LBl.grid(row = 1, column = 0)
#next
Nbt = Button(Graphframe, text = 'Previous', command = prev_g, width = 10, font = 'Times 12 bold', bg = 'light green')
Nbt.grid(row = 1, column = 1, padx = 20)
#Previous
Nbt1 = Button(Graphframe, text = 'Next', command = next_g, width = 10, font = 'Times 12 bold', bg = 'light green')
Nbt1.grid(row = 1, column = 2, padx = 20)
#save
Bsg = Button(Graphframe, text = 'Save', command = save_graph, width = 12, font = 'Times 12 bold', bg = 'cyan')
Bsg.grid(row = 1, column = 3, padx = 40)

#Browse Button
Bbt = Button(frame2, text = "Browse", command = browse, width = 20, font = "Times 12 bold", bg = 'orange')
Bbt.grid(row = 0, column = 0)
#listbox for directory
LB = Listbox(frame2, relief = RAISED, bd = 5, height = 1, width = 60)
LB.grid(row = 0, column = 2)
Lblab = Label(frame2 , text = 'Folder Selected : ', font = "Times 12 bold")
Lblab.grid(row = 0, column = 1)
#Button to consolidate
Cbt = Button(frame2, text = "Consolidate", command = interpolation, width = 20, font = "Times 12 bold", bg = 'light blue')
Cbt.grid(row=1, column = 0)
#button to plot
Gbt = Button(frame2, text = "Plot", command = graph, width = 20, font = "Times 12 bold", bg = 'yellow')
Gbt.grid(row=2, column = 0)
#entry box for window length
Wll = Label(frame2, text = 'Window Length (Odd)', font = "Times 12 bold")
Wll.grid(row = 1, column = 1)
Wle = Entry(frame2, textvariable = windl, relief = RAISED, bd = 5)
Wle.grid(row = 1, column = 2, sticky = W)

root.mainloop()