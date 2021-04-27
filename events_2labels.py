
# for 2-label model
# read bounding box details from txt files and extract CMP details  



import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import os 
import glob
import tkinter as tk
from tkinter import filedialog
import datetime
from scipy import signal
import statistics 
from statistics import mode
from matplotlib import ticker, cm
from matplotlib.widgets import Slider, Button, RadioButtons
import peakutils # for background estimation
import math
from sklearn import preprocessing

import csv
import seaborn as sns; sns.set(style="white", color_codes=True)
import statistics


def events_stats(stats_dir):
    
    # set working dir where plots will be saved
    DataPath = stats_dir
    
    length_of_image = 10  # at the moment each image is 10 minutes long 
    files = sorted(glob.glob(DataPath))
    
    dict_results = {}
      
    plt.ion()
    counter = 0
    for file in files:  
            
        counter +=1
        print('\n')
        print(f'Processing file number %s' % counter)
        #print(counter)
        print(f'Counter %s ' % counter)
        
        # read in each txt file
        txt0 = pd.read_csv(file,  header=None, delimiter="\s+")   
        txt1 = txt0.rename(columns={0: 'class', 1: 'confidence', 2: 'x', 3: 'y', 4: 'width', 5: 'height'})      # rename the columns
        class_names = ['HAPC', 'cyclic']                                               # class assignements - colab doc
        txt1['class'] = txt1['class'].replace([0, 1], class_names)                     # update class col with class names
        
        
        class0 = txt1['class']      # the list of classes - 1st column of txt file
        set_class = set(class0)     # list of unique classes    
        
        
        
        # create a dictionary for the results
        results = {}
        
        # get stats on each class separtately    
        for object_class in set_class:
            
            
            # dictionary of results per class
            class_results = {}        
            
            
            print(f'class: %s' % object_class)
            
            txt2 = txt1[txt1['class'].isin([object_class])]         # new df with only current class
            
            # total number of events
            num_events = len(txt2)                                  # total number of events of current class
            print(f'There are %s %s events ' %(num_events, object_class))
              
            # raw freq
            raw_freq = num_events/length_of_image
            print(f'Uncorrected frequency:  %.2f per minute ' %(raw_freq))
            

            
        
            # duration of events  (s) 
            ave_dur = txt2['width'].mean()*length_of_image*60                                   # average duration of an event in seconds
            min_dur = txt2['width'].min()*length_of_image*60                                    # min duration of an event in seconds
            max_dur = txt2['width'].max()*length_of_image*60                                    # max duration of an event in seconds       
            print(f'Average duration is  %.2f s (max =  %.2f s and min =  %.2f s)' %(ave_dur, min_dur, max_dur))   
              
            # extent of events (cm)
            ave_extent = txt2['height'].mean()*100                                  # average duration of an event in seconds
            min_extent = txt2['height'].min()*100                                   # min duration of an event in seconds
            max_extent = txt2['height'].max()*100                                   # max duration of an event in seconds
            print(f'Average length of colon affected  is  %.2f cm (max =  %.2f cm and min =  %.2f cm)' %(ave_extent, min_extent, max_extent)) 
            
            # speed of propagation = extent / duration (cm/s)
            speeds = (txt2['height']*100)/(txt2['width']*length_of_image*60)   
            ave_speed = speeds.mean()
            min_speed = speeds.min()
            max_speed = speeds.max()        
            print(f'Average propagation speed is  %.2f cm per second (max =  %.2f cm and min =  %.2f cm)' %(ave_speed, min_speed, max_speed))        
                
            
            # corrected frequency,  calculate frequency of events taking into account:
            # 1. only periods over which events are seen
            # 2. when there are gaps between events i.e. model doesn't find consecutive events
            # Will calculate deltas (times between events) and then take median
            event_starts  = (txt2['x']-(txt2['width']/2)) * length_of_image         # left-hand side of bounding box is the start of the event
            sorted_event_starts = sorted(event_starts, reverse=False)               # order start times from smallest to largest  
            
            num_deltas = num_events - 1
            delta = [0]*num_deltas
           
    
            # calculate delta values, the times between start times of successive events
            for counter_del in range(num_deltas):
                delta[counter_del] = sorted_event_starts[counter_del+1] - sorted_event_starts[counter_del] 
            
            
            med_delta = 0
            if len(delta) > 2:
                med_delta = statistics.median(delta)
                
            corr_freq = 0
            if med_delta > 0:
                corr_freq = 1/med_delta
            
            
            # plots to show distribution of events
            #fig = plt.figure(figsize=(16,8))  
            #plt.plot(delta)        
            #sns.swarmplot(y=delta)
            #plt.hist(delta, bins = 3)
            #plt.show()
            #plt.close()
            
                
            
            print(f'Corrected frequency:  %.2f  %s per minute ' %(corr_freq, object_class))

                       
            class_results['num_events'] = num_events
            class_results['raw_freq'] = format(raw_freq, '.2f')
            class_results['corr_freq'] = format(corr_freq, '.2f')
            class_results['ave_dur'] = format(ave_dur, '.2f')
            class_results['max_dur'] = format(max_dur, '.2f')
            class_results['min_dur'] = format(min_dur, '.2f')
            class_results['ave_extent'] = format(ave_extent, '.2f')
            class_results['max_extent'] = format(max_extent, '.2f')
            class_results['min_extent'] = format(min_extent, '.2f')
            class_results['ave_speed'] = format(ave_speed, '.2f')
            class_results['max_speed'] = format(max_speed, '.2f')
            class_results['min_speed'] = format(min_speed, '.2f')

            
            
            
            results[object_class] = class_results
    
        print("These are all the results: {}".format(results))
        
        dict_filename = os.path.basename(file)
        
        dict_results[dict_filename] = results
    print("These are ALL the results: {}".format(dict_results))       
     

    return(dict_results)

# how to use
# temp =events_stats(r'PATH\*.txt')

















