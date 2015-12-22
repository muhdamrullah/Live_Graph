from __future__ import division
from astropy.io import ascii
import numpy as np
import scipy
#from scipy import stats
import datetime
import time
from time import strftime
import sys
import os
import glob
import matplotlib.pyplot as plt
#%matplotlib inline
import calendar
from matplotlib import dates
import datetime
 
 
def cat_string(list_of_files):
    iterator = list_of_files[-97:]
    output=""
    for x in range(0, len(iterator)):
        output = output+iterator[x]+" "
    return output[:-1]
 
def convert_epoch(x):
    t = (datetime.datetime( int((x.split(" ")[0]).split("-")[0]),  int(x.split(" ")[0].split("-")[1]),  int(x.split(" ")[0].split("-")[2]), int(x.split(" ")[1].split(":")[0]) ,   int(x.split(" ")[1].split(":")[1])  , int(x.split(" ")[1].split(":")[2])))
    return calendar.timegm(t.timetuple())
 
def convert_time(arr):
    return np.array([convert_epoch(x) for x in np.array(arr)])
 
def find_people(curr_time, arr_last_seen, arr_first_seen):
    return np.count_nonzero((np.array(arr_last_seen) >= (curr_time-60)) & ((np.array(arr_last_seen)<=(curr_time))))
 
while True:
    with open('../Versioning/master.csv','r') as in_file, open('./Intermediate/real_time_full_day_master.csv','w') as out_file:
        switch = 0
        out_file.write("Station MAC, First time seen, Last time seen, Power, # packets, BSSID \r")
        for line in in_file:
            if (line[0:5]=="Stati"):
                switch = 1
            if (line[0]=="\r"):
                switch = 0
            if switch==1:
                if line[0]!="\r":
                    if (line.split(",")[0]!="Station MAC"):
                        processed_line = line.split(",")[0]+","+ line.split(",")[1]+","+line.split(",")[2]+","+line.split(",")[3]+","+line.split(",")[4]+","+line.split(",")[5]+"\r"
                        out_file.write(processed_line)
                         
    device = ascii.read("./Intermediate/real_time_full_day_master.csv")
 
    device_data = np.array(zip(device['Station MAC'], convert_time(device['First time seen']), convert_time(device['Last time seen'])))
 
    sorted_device= sorted(device_data,key=lambda x: x[0])
 
    sorted_mac_b = np.array([x[0] for x in sorted_device])
    sorted_first_b = (np.array([x[1] for x in sorted_device], dtype=int))
    sorted_last_b = (np.array([x[2] for x in sorted_device], dtype=int))
 
    final_mac_b = np.array([sorted_mac_b[0]])
    final_first_b = np.array([sorted_first_b[0]])
    final_last_b = np.array([sorted_last_b[0]])
 
    for x in range(1, len(sorted_device)):
        if sorted_mac_b[x-1]!=sorted_mac_b[x]:
            final_first_b = np.append(final_first_b, sorted_first_b[x])
            final_mac_b = np.append(final_mac_b, sorted_mac_b[x])
            final_last_b = np.append(final_last_b, sorted_last_b[x])
             
        elif np.absolute(int(sorted_last_b[x-1])-int(sorted_last_b[x]))>300:
            final_first_b = np.append(final_first_b, sorted_first_b[x])
            final_mac_b = np.append(final_mac_b, sorted_mac_b[x])
            final_last_b = np.append(final_last_b, sorted_last_b[x])      
             
        elif (sorted_mac_b[x-1]==sorted_mac_b[x]) & (np.absolute(int(sorted_last_b[x-1])-int(sorted_last_b[x]))<=300):
            final_first_b[-1]= min(int(sorted_first_b[x-1]),int(sorted_first_b[x]))
            final_last_b[-1] = max(int(sorted_last_b[x-1]),int(sorted_last_b[x]))
             
 
    no_people_b = np.array([np.count_nonzero((final_last_b+60 >= x) & (final_last_b<=x)) for x in range(np.min(final_last_b),  np.max(final_last_b))])
    np.savetxt('device.csv', np.array([no_people_b[-1]]))  #path to the Scripts-shop folder in our Dropbox
 
    plt.figure(figsize=(40,10))
    x_ax= range(np.min(final_last_b),  np.max(final_last_b))
    y_ax = no_people_b
    plt.scatter(x_ax, y_ax,s=15, alpha=0.05, c='Crimson')
    plt.xlim(np.max(final_last_b)-86400,  np.max(final_last_b))
    plt.ylim(-1,np.max(y_ax))
    plt.tick_params(axis='y', which='both',bottom='on', top='on',labelsize=30) 
    plt.tick_params(axis='x', which='both',bottom='on', top='on',labelsize=20) 
    plt.ylabel("$Number\  of\  People$", fontsize=60, fontweight='bold')
    plt.xlabel("$Time$", fontsize=60, fontweight='bold')
    plt.savefig("device.jpg")
    plt.close('all') 
    print "Done"
 
    time.sleep(1)
