# manometry making plots

import numpy as np
import pandas as pd
import statistics
from matplotlib import ticker, cm
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import math
from sklearn import preprocessing


def format_x(x, pos=None):
    """
    Formatting the time for plots into hours:min:sec for plots for 10Hz data
    """

    mseconds = (x % 10) * 100
    seconds = int(x / 1) % 60
    minutes = int(x / 60) % 60
    hours = int(x / 3600) % 3600
    new_x = "%d:%02d:%02d" % (hours, minutes, seconds)
    return new_x


def get_sec(time_str):
    """Get Seconds from time."""
    # reverse formatting hours:min:sec to x-value for plotting
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def update(val, s=None):
    """
    Update the plots with the new max value when plot slider is moved
    """

    # _cmin = s_cmin.val
    _cmax = s_cmax.val
    img.set_clim(0, _cmax)
    plt.draw()


def make_contour_plots(df0, HMStimes_s, PName, MNumber, anal_sensor):
    """
    Contour plot of entire file with colour bar
    """

    maxSampleNumber = len(df0)
    minSampleNumber = 0

    df = df0.transpose()
    # Find the maximum values
    maxSensorValues = df.max(skipna=True)       # maximum value per sensor
    maxAllValues = df.max().max()               # max in dataframe

    # Find the minumum values
    minSensorValues = df.min(skipna=True)       # minimum value per sensor
    minAllValues = df.min().min()               # minimum in dataframe

    # generate the meshgrid for the countour plot
    # xs = np.floor(np.linspace(1,maxSampleNumber+1,maxSampleNumber+1))
    xs = np.linspace(1 ,maxSampleNumber ,maxSampleNumber)
    ys = np.linspace(1 ,40 ,40)           # Returns 40 (last number) numbers in the range 40 to 1
    XX ,YY = np.meshgrid(xs ,ys)
    zs = df   # original
    # zs = np.log(df)   # comment out afterwards, plotting log values
    # zs[zs < 0] = 0    # comment out afterwards,
    zs.shape

    fig = plt.figure(figsize=(16 ,8))
    # fig = plt.figure(figsize=(12,12))
    left, bottom, width, height = 0.1, 0.18, 0.95, 0.75
    ax = fig.add_axes([left, bottom, width, height])
    ax.invert_yaxis()                                           # to show same orientation as Jasper's software

    global img
    plt.contourf(XX ,YY, zs, cmap=cm.PuBu_r)
    # ContourLevels = np.linspace(0,10,20)  # to use in logplots
    ContourLevels = np.linspace(0 ,1000, 41)  # Final plots
    # everthing above vmax is is set to max colour, vice versa for vmin.
    img = plt.contourf(XX ,YY, zs, levels=ContourLevels, cmap='jet', vmin=0, vmax=200)
    # plt.colorbar()
    ax.set_title('file: ' + str(PName) + ' (' + str(MNumber) + '), ' +  'anal sensor: ' + str(anal_sensor))
    ax.set_xlabel('Time')
    ax.set_ylabel('Sensor')
    #x = hms_times
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x))

    # add interactive slider for colour bar
    # img = ax.imshow(img_data, interpolation='nearest')
    cb = plt.colorbar(img)
    axcolor = 'lightgoldenrodyellow'
    ax_cmax  = plt.axes([0.15, 0.05, 0.65, 0.03])
    c_max = "%1.0f"
    global s_cmax
    s_cmax = Slider(ax_cmax, 'colour bar', -10, 700, valinit= 0, valfmt=c_max)  # HAPC think need to make this global

    # update plot on slider position
    s_cmax.on_changed(update)
    # s_cmax.on_changed(lambda val: ax.set_xlim([val, val + 1]))   # suggested change to fix slider problem but doesn't work

    # showing and saving plots
    plt.show()
    plt.draw()

    # pausing
    # plt.waitforbuttonpress()
    # while not plt.waitforbuttonpress(): pass    # allows to interact with plot and not carry on with loop

    plt.savefig("%s_%s_cont.png" %(PName, MNumber))
    #  plt.close()
    return s_cmax


def make_sensor_plots(df, HMStimes, PName, MNumber, HMS_Tmeas):
    """
    Plots all sensors in a file in a single plot
    """

    x = HMStimes
    fig = plt.figure(figsize=(16, 8))  # size of plot
    # fig.suptitle(PName, fontsize=14, fontweight='bold')
    ax = plt.axes()
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # set max number of labels on x-axis
    plt.plot(HMStimes, df)  # plot data with time in HMS
    # plt.legend()
    ax.set_title(str(PName) + ' (' + str(MNumber) + '), ' + str(HMS_Tmeas))
    # ax.set_title(HMS_Tmeas)
    ax.set_xlabel('Time')
    ax.set_ylabel('sensor')
    # plt.show()
    # showing and saving plots
    plt.savefig("%s_%s_sens.png" % (PName, MNumber))
    plt.close()


def make_anus_plots(df, HMStimes_s, PName, MNumber, HMS_Tmeas):
    """
    Makes several plots to help identify the sensor closes to the anal sphincter.
    Plots of percentage of points above a threshold for increasing threshold. All 40 sensors on same plot
    """

    lcols = df.columns
    infos = pd.DataFrame(columns=lcols)
    mean_P = [0] * 40
    median_P = [0] * 40
    std_P = [0] * 40
    max_P = [0] * 40
    sum_P = [0] * 40
    threshold_P = [0] * 40
    pc_10 = [0] * 40
    loop_num = -1
    channel_num = list(range(1, 41))

    for column in df:
        loop_num += 1
        # print(loop_num)
        y = df[column]

        # calculate basics stats per channel
        mean_P[loop_num] = np.mean(y)
        median_P[loop_num] = statistics.median(y)
        std_P[loop_num] = np.std(y)
        max_P[loop_num] = max(y)
        sum_P[loop_num] = y.sum()

        # calculate percentage cutoff values
        range_y = math.ceil(max(y))  # max value of sensor measurement used for threshold range
        # print(range_y)
        sum_points = 0
        perc_points = [0] * range_y  # percentage of data points above the threshold
        x = [0] * range_y  # x-coords

        for threshold in range(range_y):
            # print(threshold)
            sum_points = sum(i >= threshold for i in y)  # number of data point above the threshold
            perc_points[threshold] = (sum_points * 100) / (len(y))  # percentage above threshold

            x[threshold] = threshold  # x-values for plot

            if perc_points[threshold] > 10:
                # print('its above')
                pc_10[loop_num] = x[threshold]  # x value for which percdentage is still greater than 10

    # ____________________  anal prob factor  _______________________________

    norm_mean_P = preprocessing.minmax_scale(mean_P, feature_range=(0, 1))
    norm_median_P = preprocessing.minmax_scale(median_P, feature_range=(0, 1))
    norm_std_P = preprocessing.minmax_scale(std_P, feature_range=(0, 1))
    norm_max_P = preprocessing.minmax_scale(max_P, feature_range=(0, 1))
    norm_pc_10_P = preprocessing.minmax_scale(pc_10, feature_range=(0, 1))

    anal_factor = norm_mean_P + norm_median_P - norm_std_P + norm_max_P + norm_pc_10_P
    fig = plt.figure(figsize=(10, 8))
    plt.plot(channel_num, anal_factor, label='anal factor')
    most_prob_anal = channel_num[anal_factor.argmax()]
    top_three = sorted(zip(anal_factor, channel_num), reverse=True)[
                :3]  # sort by anal_factor and output the three highest
    print('top 3= ' + str(top_three))
    print('most likely anal sensor is ' + str(most_prob_anal))
    print('\n')

    # _________________  plots  ___________________________

    # plot: mean, median, mode, std
    fig = plt.figure(figsize=(10, 8))  # size of plot
    fig.suptitle(PName, fontsize=14, fontweight='bold')
    ax = plt.axes()
    plt.plot(channel_num, mean_P, label='mean')
    plt.plot(channel_num, median_P, label='median')
    plt.plot(channel_num, std_P, label='std')
    # plt.legend()
    ax.set_title('Baseline values')
    ax.set_xlabel('Channel')
    ax.set_ylabel('Value')
    plt.grid(which='major')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.xlim(0, 41)
    plt.legend(loc='upper left', shadow=True)
    # showing and saving plots
    plt.savefig("%s_%s_mean_med_std.png" % (PName, MNumber))
    plt.close()

    # plot: max
    fig = plt.figure(figsize=(10, 8))  # size of plot
    fig.suptitle(PName, fontsize=14, fontweight='bold')
    ax = plt.axes()
    plt.plot(channel_num, max_P, label='max')
    # plt.legend()
    ax.set_title('Baseline values')
    ax.set_xlabel('Channel')
    ax.set_ylabel('Value')
    plt.grid(which='major')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.xlim(0, 41)
    plt.legend(loc='upper left', shadow=True)
    # showing and saving plots
    plt.savefig("%s_%s_max.png" % (PName, MNumber))
    plt.close()

    # plot percentage cutoffs
    fig = plt.figure(figsize=(10, 8))  # size of plot
    fig.suptitle(PName, fontsize=14, fontweight='bold')
    ax = plt.axes()
    plt.plot(channel_num, pc_10, label=' 90% cutoffs per channel')
    # plt.legend()
    ax.set_title('Baseline values')
    ax.set_xlabel('Channel')
    ax.set_ylabel('90% cutoff value')
    plt.grid(which='major')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.xlim(0, 41)
    plt.legend(loc='upper left', shadow=True)
    plt.savefig("%s_%s_cutoffs.png" % (PName, MNumber))
    plt.close()


def make_individual_sensor_plots(df1, df2, df3, df4, baseline_values, df5, HMStimes_s, HMStimes, PName, MNumber,
                                 HMS_Tmeas):
    """
    Make separate plots of each sensor for each processing stage
    """

    for column in df1:
        print(column)
        y1 = df1[column]
        y2 = df2[column]
        y3 = df3[column]
        y4 = df4[column]
        y4_baseline = baseline_values[column]
        y5 = df5[column]
        x = HMStimes

        # fig = plt.figure(figsize=(500,20))                        # to show how
        fig = plt.figure(figsize=(20, 10))  # size of plot
        fig.suptitle(column, fontsize=14, fontweight='bold')
        ax = plt.axes()
        ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # set max number of labels on x-axis

        # plt.plot(hms_times, y1)  # only  used this in check smoothing plot
        plt.plot(HMStimes_s, y2)
        plt.plot(HMStimes_s, y3)
        plt.plot(HMStimes_s, y4)
        # plt.plot(hms_times_s,y5)
        plt.plot(HMStimes_s, y4_baseline)

        # plt.legend()
        ax.set_title(HMS_Tmeas)
        ax.set_xlabel('Time')
        ax.set_ylabel('sensor')
        plt.grid(True)
        plt.legend(('df2: rebin', 'df3: BF', 'df4: remove offset', 'baseline'), loc='upper right', shadow=True)
        # plt.show()

        # showing and saving plots
        plt.savefig("%s_%s_%s_ind_sens.png" % (PName, MNumber, column))
        plt.close()


def check_butterworth_plots(df1, df2, df3, hms_times, HMStimes_s, PName, MNumber, HMS_Tmeas):
    """
    Check the effect of the Butterworth filter for a particular sensor within the specified time interval
    """

    # select which single sensor to plot
    #column = ' P14'
    column = f" P{input('Type in a sensor number: ')}"
    print(column)
    y1 = df1[column]
    y2 = df2[column]
    y3 = df3[column]

    fig = plt.figure(figsize=(20, 10))  # to show how
    fig.suptitle(column, fontsize=14, fontweight='bold')
    ax = plt.axes()
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # set max number of labels on x-axis

    plt.plot(hms_times, y1)
    plt.plot(HMStimes_s, y2)
    plt.plot(HMStimes_s, y3)

    # plt.legend()
    ax.set_title(HMS_Tmeas)
    ax.set_xlabel('Time')
    ax.set_ylabel('Pressure (mmHg)')
    plt.grid(True)
    #  plt.legend(('df2: rebinned','df3: butterworth filter'), loc='upper right', shadow=True)
    plt.legend(('df1: raw (10Hz)', 'df2: rebinned (1Hz)', 'df3: butterworth filter'), loc='upper right', shadow=True)

    beg_plot = get_sec('3:00:00')
    end_plot = get_sec('3:05:00')
    plt.xlim(beg_plot, end_plot)  # this works
    plt.ylim(0, 300)
    # plt.show()

    # showing and saving plots
    plt.savefig("%s_%s_%s_check_butter.png" % (PName, MNumber, column))
    plt.close()


def make_waterfall_plots(df4, HMStimes, PName, MNumber, HMS_Tmeas):
    """
    Date for all sensors on same plot vertically displaced from each other.
    Uses data with zeros still present.
    """

    df = df4.transpose()
    # fig = plt.figure(figsize=(60,30))                        # size of plot
    fig = plt.figure(figsize=(20, 10))  # size of plot
    fig.suptitle(PName, fontsize=32, fontweight='bold')
    ax = plt.axes()
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # set max number of labels on x-axis
    x_max = df.shape[1]  # using this to plot as hms_times takes so long but confusing since don't know time
    # x = np.linspace(0,1,x_max)
    x = HMStimes

    for iy in range(40):
        offset = (40 - iy) * 60
        # Plot the line and fill under it: increase the z-order each time
        # so that lower lines and their fills are plotted over higher ones
        ax.plot(x, df.iloc[iy] + offset, 'k', lw=1, zorder=(iy + 1) * 2)
        # ax.fill_between(x, df.iloc[iy]+offset, offset, facecolor='k', lw=0, zorder=(iy+1)*2-1)   # this adds the black fill colour
    # plt.show()

    ax.set_title(HMS_Tmeas, fontsize=32)
    ax.set_xlabel('Time')
    ax.set_ylabel('sensor')

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x))

    # To interact with plot, allows uncomment 3-lines below to use
    #   print("Press any key to go to next file")
    #   while not plt.waitforbuttonpress(): pass
    #   print("continuing ... ")

    plt.savefig("%s_%s_water.png" % (PName, MNumber))
    # plt.close()


def make_segmented_contour_plots(df6, HMStimes, PName, MNumber, anal_sensor, begin_file, length_plot, TMeas):
    """
    Generates contour plots of duration length_plot minutes. No axes, border or colour bar.
    These images are used as input for CNN
    """

    maxSampleNumber = len(df6)
    minSampleNumber = 0

    df = df6.transpose()
    # Find the maximum values
    maxSensorValues = df.max(skipna=True)  # maximum value per sensor
    maxAllValues = df.max().max()  # max in dataframe

    # Find the minimum values
    minSensorValues = df.min(skipna=True)  # minimum value per sensor
    minAllValues = df.min().min()  # minimum in dataframe

    # generate the meshgrid for the contour plot
    # xs = np.floor(np.linspace(1,maxSampleNumber+1,maxSampleNumber+1))
    xs = np.linspace(1, maxSampleNumber, maxSampleNumber)
    ys = np.linspace(1, 40, 40)  # default, Returns 40 (last number) numbers in the range 40 to 1
    XX, YY = np.meshgrid(xs, ys)  # default
    zs = df
    zs.shape


    global img
    # plt.contourf(XX,YY, zs, cmap=cm.PuBu_r)
    # ContourLevels = np.linspace(0,1000, 41)  # Final plots, 25mmHg levels
    ContourLevels = np.linspace(0, 1000, 101)  # Final plots, 10mmHg levels,  101 ok
    # ContourLevels=[0, 10, 50, 70, 100, 150, 200, 300, 500, 900]   # manual setting of contour levels


    begin_file_sec = get_sec(begin_file)  # convert begin_file(HMS) to seconds
    print('begin in sec ' + str(begin_file_sec))
    # calculate the number of images that can be made of the file, round down
    num_images = math.floor((TMeas - begin_file_sec) / length_plot)
    print('number of images is ' + str(num_images))

    time_increment = 0
    begin_plot = 0

    for i in range(num_images):
        print(i)
        time_increment = i * length_plot
        print('time incr =' + str(time_increment))
        begin_plot = begin_file_sec + (i * length_plot)
        end_plot = begin_plot + length_plot
        print(begin_plot)
        print(end_plot)
        # plt.xlim(begin_plot, end_plot)

        # fig = plt.figure(figsize=(12,12))
        fig = plt.figure(figsize=(24, 24))
        #   left, bottom, width, height = 0.1, 0.18, 0.95, 0.75
        left, bottom, width, height = 0, 0, 1, 1
        #   ax = fig.add_axes([left, bottom, width, height])
        ax = fig.add_axes([left, bottom, width, height], frameon=False)
        ax.invert_yaxis()

        # img = plt.contourf(XX,YY, zs, levels=ContourLevels, cmap='jet')
        # plt.colorbar()
        # ax.set_title('file: ' + str(PName) + ' (' + str(MNumber) + '), ' +  'segmentation number: ' + str(i))
        ax.set_xlabel('Time')
        ax.set_ylabel('Sensor')

        x = HMStimes

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_x))
        ax.axis('off')
        plt.xlim(begin_plot, end_plot)

        # everything above vmax is is set to max colour, vice versa for vmin.
        # img = plt.contourf(XX,YY, zs, levels=ContourLevels, cmap='jet', vmin=0, vmax=200)    # 25mmHg levels,
        img = plt.contourf(XX, YY, zs, levels=ContourLevels, cmap='jet', vmin=0, vmax=100)  # 10mmHg levels

        # using contourmesh to plot pixel values
        # img = plt.pcolormesh(XX,YY, zs,  cmap='jet', vmin=0, vmax=100)    # 10mmHg levels
        # im = ax.imshow(zs)

        # # add interactive slider for colour bar
        # #img = ax.imshow(img_data, interpolation='nearest')

        # cb = plt.colorbar(img)

        # axcolor = 'lightgoldenrodyellow'
        # ax_cmax  = plt.axes([0.15, 0.05, 0.65, 0.03])
        # c_max = "%1.0f"
        # global s_cmax
        # s_cmax = Slider(ax_cmax, 'colour bar', -10, 700, valinit= 0, valfmt=c_max)  # HAPC think need to make this global

        # # pausing
        # #plt.waitforbuttonpress()
        # #while not plt.waitforbuttonpress(): pass    # allows to interact with plot and not carry on with loop

        # fig.tight_layout()

        plt.savefig("%s_%s_%s_cont.png" % (PName, MNumber, i), bbox_inches='tight')
        plt.close()



