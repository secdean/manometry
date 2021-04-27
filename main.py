import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os 
import glob
import datetime
from utils.processing import get_anal_sensor, smooth_data_average, smooth_data_butter, remove_baseline, correct_anal
from utils.plots import make_contour_plots, make_sensor_plots, make_waterfall_plots, make_individual_sensor_plots, \
    check_butterworth_plots, make_anus_plots, make_segmented_contour_plots

def make_plots(cont, sens, water, individual_sens, check_butter, anus, segmented, csv_dir):
    """
    Generate the desired plots. Plots used for CNN training selected using segmented = 1, all other plots are for
    diagnostic purposes.
    """

    global hms_times
    global hms_times_s
    global df1
    global df4
    global df5
    global df6
    global f_name

    # location of data files
    DataPath = csv_dir + '/*.csv'

    # load data files
    files = sorted(glob.glob(DataPath))
    plt.ion()
    counter = 0
    for file in files:
        counter += 1
        print('\n')
        print(f'Processing file number %s' % counter)
        print(f'Counter %s ' % counter)
        df0 = pd.read_csv(file,  header=5)
        print(file)

        # Checking for missing values. No missing values seen in current data but can be unchecked for testing new files
        # num_nans = df0.isnull().sum().sum()
        # print(f'There are %s missing measurements' % num_nans)

        # Calculate the length of the measurement in HMS. Data collected at 10 Hz.
        t_meas = len(df0)/10
        hms_t_meas = str(datetime.timedelta(seconds=int(t_meas)))

        # Extract measurement number (m_number), 1,2 or 3 from the filename (7th character).
        f_name = os.path.basename(file)
        m_number = f_name[7]
        p_number = f_name[0:6]
        print(f'Patient: %s %s ' % (p_number, m_number))
        print(f'Duration: %s ' % hms_t_meas)

        # Get times in HMS for nice plots
        max_sample_number = df0['Sample number'].max(skipna=True)
        xs = np.linspace(1, max_sample_number + 1, max_sample_number + 1)
        tenths_times = xs/10
        hms_times = [str(datetime.timedelta(seconds=int(item))) for item in tenths_times]

        # read in anal sensor and start of file info
        anal_sensor, begin_file = get_anal_sensor(p_number, m_number)


# ____________________________ processing data files  ________________________________

        # remove the 'Sample number' column
        df1 = df0.drop(['Sample number', ' Marker'], axis=1)

        # 1.  rebinning
        df2, hms_times_s, TenthsTimes_s = smooth_data_average(df1, hms_times, tenths_times)
    
        # 2. butterworth filtering
        df3 = smooth_data_butter(df2)
                
        # 3. remove channel offsets (subtract minimum value)    
        df4, baseline_values = remove_baseline(df3)
        
        # 4. set -ve values to zero
        df5 = df4.copy()
        df5[df5 < 0] = 0
        
        # 5. set anal sensor to always high and set sensors above to zero
        df6 = correct_anal(df5, anal_sensor)
        
# __________________________  making plots  ______________________________

        if cont > 0:
            make_contour_plots(df6, hms_times_s, p_number, m_number, anal_sensor)
        if sens > 0:        
            make_sensor_plots(df6, hms_times_s, p_number, m_number, hms_t_meas)
        if water > 0:           
            make_waterfall_plots(df1, hms_times, p_number, m_number, hms_t_meas)   # want to keep negative values
        if individual_sens > 0:           
            make_individual_sensor_plots(df1, df2, df3, df4, baseline_values, df5, hms_times_s, hms_times, p_number, m_number, hms_t_meas)
        if check_butter > 0:
            check_butterworth_plots(df1, df2, df3, hms_times, hms_times_s, p_number, m_number, hms_t_meas)
        if anus > 0:
            make_anus_plots(baseline_values, hms_times_s, p_number, m_number, hms_t_meas)
        if segmented > 0:
            make_segmented_contour_plots(df6, hms_times_s, p_number, m_number, anal_sensor, begin_file, 600, t_meas)


#make_plots(cont=0, sens=0, water=0, individual_sens = 0,  check_butter = 0, anus = 0, segmented = 1)
