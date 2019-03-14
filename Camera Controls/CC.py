#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 15:34:05 2019

@author: MJK
"""

# !/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import datetime as dt
import time
import psutil
import os
from datetime import timedelta
from picamera import PiCamera
from tkinter import *
from tkinter import messagebox
from os import *

top = Tk()
top.title("Camera Controls")
top.geometry("250x430")
timeinterval='NoValue'
timeintervalvalue='NoValue'
global size
size=StringVar()
duration=StringVar()
duration.set('Choose the number of photos')
previewcond = True

camera = PiCamera(resolution=(3280,2464), framerate=14)

# --- functions ---

#Toggles the size of the camera preview.
def preview():
    global previewcond
    previewcond = not previewcond
    if(previewcond==True):
        camera.stop_preview()
        print('Preview Big')
        camera.start_preview(fullscreen=True)
    if(previewcond==False):
        print('Preview Small')
        camera.stop_preview()
        width=top.winfo_screenwidth()
        height=top.winfo_screenheight()
        camera.start_preview(fullscreen=False, window=(5,40, int(width/1.75), int(height/1.75)))

#Takes a single still photo, at the max resolution.
def takephoto():
    #Reset Camera to photo taking settings.
    camera.framerate=(15)
    camera.resolution=(3280,2464)
    currentDT = dt.datetime.now()
    camera.capture(str(currentDT.year)+str(currentDT.month)+str(currentDT.day)+"_"+str(currentDT.hour)+':'+str(currentDT.minute)+':'+str(currentDT.second)+'.jpg')

#Takes multiple high quality stills with a certain amount of time between them
#for a specified duration, as well as a gif to review the timelapse.
def timelapse():
    camera.resolution=(3280,2464)
    camera.framerate=(15)
    for i, x in enumerate(all_comboboxes):
        if i==0:
            timeintervalvalue=int(x.get())
        if i==1:
            if x.get()=="Seconds":
                timeinterval=1
            if x.get()=="Minutes":
                timeinterval=60
            if x.get()=="Hours":
                timeinterval=60*60
        if i==2:
            numofphotos=int(x.get())-1
    delay =timeintervalvalue*timeinterval
    #images= []
    currentDT = dt.datetime.now()
    foldername = "TimeLapse_"+str(currentDT.year)+str(currentDT.month)+str(currentDT.day)+"_"+str(currentDT.hour)+'_'+str(currentDT.minute)
    path="./"+foldername
    try:
        os.makedirs(path)
    except OSError:
        print('Error'+path)
    else:
        print('Error')
    for i, filename in enumerate(camera.capture_continuous(path+'/{counter}-{timestamp:%Y-%m-%d %H %M %S}.jpg')):
        print(filename)
        #images.append(imageio.imread(filename))
        time.sleep(delay)
        if i == numofphotos:
            #imageio.mimsave(path+"/TimeLapse.gif", images)
            break
    tk.messagebox.showinfo('Done','Time Lapse has finished.\nThe time-lapse is stored at: /home/pi/desktop/'+foldername+'/nFile Size Approximately: '+str(0.006*numofphotos)+' Gb')
#Records a video using the selected video settings.
def recvideo():
    currenty=480
    currentx=640
    currentfps=30
    length=3

    for i, x in enumerate(all_comboboxes):
        if i == 3:
            current=x.current()
    if current == 0|current==1|current==2:
        print(current)
        currentx=640
        currenty=480
    if current == 3|current==4:
        print(current)
        currentx=1280
        currenty=720
    if current == 5:
        print(current)
        currentx=1920
        currenty=1080
    if current ==0|current==3|current==5:
        print(current)
        currentfps=30
        length = 4
    if current == 1|current==4:
        print(current)
        currentfps=60
        length = 2
    if current == 2:
        print(current)
        currentfps=90
        length = 1
        
    camera.resolution=(currentx,currenty)
    camera.framerate=(currentfps)
    currentDT = dt.datetime.now()
    camera.start_recording(str(currentDT.year)+str(currentDT.month)+str(currentDT.day)+"_"+str(currentDT.hour)+':'+str(currentDT.minute)+':'+str(currentDT.second)+'.h264')
    camera.wait_recording(length)
    camera.stop_recording()
    tk.messagebox.showinfo('Done','Video finished recording.')

#Calculates the end time for the time lapse and the file size of the timelapse.
def calctime(event=None):
    for i, x in enumerate(all_comboboxes):
        if i==0:
            timeintervalvalue=int(x.get())
        if i==1:
            if x.get()=="Seconds":
                timeinterval=1
            if x.get()=="Minutes":
                timeinterval=60
            if x.get()=="Hours":
                timeinterval=60*60
        if i==2:
            numofphotos=int(x.get())
    global dursec
    dursec=timedelta(seconds=numofphotos*timeintervalvalue*timeinterval)
    obj_disk = psutil.disk_usage('/')
    if (obj_disk.free/(1024.0 ** 3))>0.0055*numofphotos:
        size.set('and take up approximately\n'+str(0.006*numofphotos)+' Gb')
    if (obj_disk.free/(1024.0 ** 3))<=0.0055*numofphotos:
        size.set('but cannot be done as it will take up approximately\n'+str(0.006*numofphotos)+' Gb \n You do not have enough free disk space \nPlease free up at least '+((0.0055*numofphotos)-(obj_disk.free/(1024.0 ** 3)))+' Gb')
    top.update_idletasks()
    drawtime()

#Updates the end time for the timelapse every second.
def drawtime():
    duration.set(dt.datetime.now()+dursec)
    top.update_idletasks()
    top.after(1000,drawtime)

# --- User Interface ---
combostyle = ttk.Style()
combostyle.theme_create('combostyle', parent='alt',
                         settings = {'TCombobox':
                                     {'configure':
                                      {'selectbackground': 'gray',
                                       'fieldbackground': 'gray',
                                       'foreground': '#cccccc',
                                       'background': 'gray'
                                       }}}
                         )
#Applies style to all ttk.Combobox
combostyle.theme_use('combostyle')

all_comboboxes = []

l = Label(top, text="", fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, text="Time Interval:", fg='#cccccc', bg='#0d0d0d')
l.pack()

cb = ttk.Combobox(top, values=list(range(1,60)))
cb.set("1")
cb.pack()
cb.bind('<<ComboboxSelected>>', calctime)
all_comboboxes.append(cb)
cb = ttk.Combobox(top, values=("Seconds", "Minutes", "Hours"))
cb.set("Seconds")
cb['state'] = 'readonly'
cb.pack()
cb.bind('<<ComboboxSelected>>', calctime)
all_comboboxes.append(cb)
l = Label(top, text="", fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, text="How many photos:", fg='#cccccc', bg='#0d0d0d')
l.pack()
cb = ttk.Combobox(top, values=(list(range(1,200))))
cb.set(0)
cb.pack()
cb.bind('<<ComboboxSelected>>', calctime)
all_comboboxes.append(cb)

l = Label(top, text="", fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, text='The photos end at:', fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, textvariable=duration, fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, textvariable=size, fg='#cccccc', bg='#0d0d0d')
l.pack()
l = Label(top, text='', fg='#cccccc', bg='#0d0d0d')
l.pack()

b = Button(top, 
           text="Take Photo", 
           relief=FLAT, 
           activeforeground='#ffffff',activebackground='#333333', 
           fg='#cccccc', bg='#0d0d0d',command=takephoto)
b.pack()
b = Button(top, text="Start Time Lapse", 
           relief=FLAT, 
           command=timelapse, activeforeground='#ffffff',
           activebackground='#333333', fg='#cccccc', bg='#0d0d0d')
b.pack()
l = Label(top, text="", fg='#cccccc', bg='#0d0d0d')
l.pack()

l = Label(top, text="Choose Video Settings:", fg='#cccccc', bg='#0d0d0d')
l.pack()
cb = ttk.Combobox(top, values=('480p 30fps (3 Seconds)',
                               '480p 60fps (2 Seconds)',
                               '480p 90fps (1 Second)',
                               '720p 30fps (4 Seconds)',
                               '720p 60fps (2 Seconds)',
                               '1080p 30fps (1 Second)',))
cb['state'] = 'readonly'
cb.pack()
cb.bind('<<ComboboxSelected>>', calctime)
all_comboboxes.append(cb)
l = Label(top, text='', fg='#cccccc', bg='#0d0d0d')
l.pack()
b = Button(top, text="Start Recording Video", relief=FLAT, 
           command=recvideo, activeforeground='#ffffff',
           activebackground='#333333', fg='#cccccc', bg='#0d0d0d')
b.pack()
b = Button(top, text="Toggle Preview Size", relief=FLAT, 
           command=preview, activeforeground='#ffffff',
           activebackground='#333333', fg='#cccccc', bg='#0d0d0d')
b.pack()
preview()
top.configure(bg='#0d0d0d')
top.mainloop()

