# manometry processing file

import pandas as pd
import numpy as np
from scipy import signal
from BaselineRemoval import BaselineRemoval


def get_anal_sensor(p_number, m_number):
    """ 
    Reads in the anal_sensors file which contains the number of the sensor closest to the anal sphincter and
    the start time of the file (1hr20 for all files).
    """
    
    df_as = pd.read_csv(r"C:\Users\Sarah\Sarah\Master of AI\thesis\analysis\python\manometry\anal_sensors_3.csv", header=0)
    df_as['PName_as'] = df_as['PName_as'].astype(str)
    # find the row in csv file for current measurement using p_number
    row = df_as.loc[(df_as['PName_as'] == p_number[2:]) & (df_as['MNumber_as'] == int(m_number))]
    anal_sensor = row.iat[0, 2]  # this also works to reference the df
    print('The anal sensor is channel ' + str(anal_sensor))
    # start of file
    row = df_as.loc[(df_as['PName_as'] == p_number[2:]) & (df_as['MNumber_as'] == int(m_number))]
    begin_file = row.iat[0, 3]
    print('The file begins at ' + str(begin_file))
    return anal_sensor, begin_file


def smooth_data_average(df, HMStimes, TenthsTimes):
    """
    Down samples data by factor = reduce_fac, new samples are mean of reduce_fac number of samples
    """

    reduce_fac = 10
    # reduce the non-HMS times
    TenthsTimes_s = TenthsTimes[1::reduce_fac]
    # reduce the HMS times
    HMStimes_s = HMStimes[1::reduce_fac]
    # reduce the signal data
    df_short = df.groupby(np.arange(len(df)) // reduce_fac).mean()
    df_short = df_short[:len(HMStimes_s)]  # need to include this as sometimes hms_times data is shorter
    return df_short, HMStimes_s, TenthsTimes_s


def smooth_data_butter(df):
    """
    Add a high-pass Butterworth filter to smooth the data.
    """

    N = 2  # Filter order
    Wc = 0.4  # Cutoff frequency (lower the filter the more high-freq cutoff)
    B, A = signal.butter(N, Wc, output='ba')
    # apply the filter on each sensor in the file
    lcols = df.columns
    df_high = pd.DataFrame(columns=lcols)
    for i in df:
        df_high[i] = signal.filtfilt(B, A, df[i])
    return df_high


def remove_baseline(df):
    """
    Baselines are corrected using the python baseline remover: https://pypi.org/project/BaselineRemoval/
    """

    lcols = df.columns
    df_off = pd.DataFrame(columns=lcols)
    baseline_values = pd.DataFrame(columns=lcols)
    Zhangfit_output = pd.DataFrame(columns=lcols)
    for i in df:
        temp = df[i]
        if (temp.sum() == 0):  # When all reading are zero for a particular channel,
            print("baseline values = 0")  # the zhang routine will fail. This IF statement
            df_off[i] = df[i]  # avoids that eventuality.
            baseline_values[i] = df[i]
        else:
            baseObj = BaselineRemoval(df[i])
            Zhangfit_output[i] = baseObj.ZhangFit()
            df_off[i] = Zhangfit_output[i]  # The BaselineRemoval routine automatically subtracts
            baseline_values[i] = df[i] - df_off[i]  # the calculated baseline.
    return df_off, baseline_values


def correct_anal(df, anal_sensor):
    """
    Set all anal sensor values to high (599mmHg) adn set all sensors above that (out-of-body sensors) to zero.
    """

    # below 3 lines original, uncomment after
    df6 = df.copy()
    anal_col = df6.columns[
        anal_sensor - 1]  # find which column in the df corresponds to the anal sensor. -1 since anal_sensor is a number not a column name
    df6[anal_col] = 500  # set all values of anal sensor = 500
    out_body_sensors = list(range(anal_sensor, len(df6.columns)))  # get a list of all sensors above the anal sensor
    out_cols = df6.columns[out_body_sensors]  # get the corresponding column headers
    df6[out_cols] = 0  # set all values in column to zero
    return df6

