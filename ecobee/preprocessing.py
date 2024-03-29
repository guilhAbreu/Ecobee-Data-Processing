#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 18:45:31 2019

@author: Guilherme de Brito Abreu, undergraduate student at @unicamp.

This library contains classes that will be helpful in case you want to preprocess data from Ecobee Donate Your Data 2019 dataset.

"""

# macro names
dayCol   = 'Day'
yearCol  = 'Year'
monthCol = 'Month'
dateCol  = 'DateTime'
timeCol  = 'Time'

julianDayCol    = 'Days in Order'
timeDeviceOnCol = 'Time on (min)'
systemModeCol   = 'HvacMode'


outHumCol = 'RH_out'
inTemCol  = 'Thermostat_Temperature'
inHumCol  = 'Humidity'
outTemCol = 'T_out'

maxInHumCol  = 'Max Indoor Humidity (%RH)'
maxInTemCol  = 'Max Indoor Temp (C)'
maxOutTemCol = 'Max Outdoor Temp (C)'
outHumColMax = 'Max Outdoor Humidity (%RH)'

minInHumCol  = 'Min Indoor Humidity (%RH)'
minInTemCol  = 'Min Indoor Temp (C)'
minOutTemCol = 'Min Outdoor Temp (C)'
minOutHumCol = 'Min Outdoor Humidity (%RH)'

meanInHumCol  = 'Mean Indoor Hum (%RH)'
meanInTemCol  = 'Mean Indoor Temp (C)'
meanOutTemCol = 'Mean Outdoor Temp (C)'
meanOutHumCol = 'Mean Outdoor Hum (%RH)'

stdOutTemCol = 'Outdoor Temp Standard Deviation (C)'
stdInHumCol  = 'Indoor Humidity Standard Deviation (%RH)'
stdInTemCol  = 'Indoor Temp Standard Deviation (C)'
stdoutHumCol = 'Outdoor Humidity Standard Deviation (%RH)'

eventCol = 'Event'

class ecobeeData:
  
    def __init__(self):
        '''
        Description: Initialize object with an empty dataframe.
        '''
        
        import pandas as pd
        self.data = pd.DataFrame([])
        self.maxJulianDay = 0
        self.size = 0

    def append(self, path):
        '''
        Description:
            It receives a file path of an ecobee data as input, gets its dataframe and
            append it to self.data.
        Input:
            datframe: An ecobee data file path.
        '''
        try:
            newData = self.getDataFrame(path)
        except FileNotFoundError:
            return
        
        nextMaxJulianDay = newData[julianDayCol].max()
        new_min = newData[julianDayCol].min()
        
        # shift all days in order to make the first day be 1
        newData[julianDayCol] -= new_min - 1 
        if self.size > 0:
            newData[julianDayCol] += self.data[julianDayCol].max() + (new_min - self.maxJulianDay) - 1
        
        self.maxJulianDay = nextMaxJulianDay
        self.data = self.data.append(newData, ignore_index=True, sort=True)
        self.size += 1
 
    def getDataFrame(self, path):
        '''
        Description: It creates a data frame from a ecobee report csv table and includes new columns as the following:
          dayCol       = 'Day'
          yearCol      = 'Year'
          monthCol     = 'Month'
          JulianDayCol = 'Days in Order'
          timeCol      = 'Time'
          
        It also converts temperature from fahrenheit to celsius, cast temperatures and humidities from string to numeric, 
        and calculates 'julian day' for each day.
          
        Obs: This function doesn't solve problems like incorrect number of columns or rows. If there is any problem like these, it is needed
        to treat them before this function call.
        
        Input:
          path: The report file path.
          
        Output:
          A pandas data frame.
        '''
        
        import pandas as pd
        import numpy as np
        import datetime as dt
        
        try:
            data = pd.read_csv(path)
        except pd.errors.ParserError:
            # just open file and read the data
            file = open(path, 'r')
            rawData = file.readlines()
            file.close()
          
            # clean up the data removing empty rows and commentaries
            i = 0;
            while i < len(rawData):
                if '#' in rawData[i] or '\n' == rawData[i] or '' == rawData[i]:
                    data.pop(i)
                else:
                    i+=1

            columns = rawData[0].split(',')
            try:
                data = pd.DataFrame([line.split(',') for line in rawData[1:]], columns=columns)
            except ValueError as e:
                import sys
                print(e)
                sys.exit()
              
        data.rename(columns={'RH_out\n':'RH_out'}, inplace=True)
          
        #split datetime into date and time columns
        datetime = np.asarray([d.split(' ') for d in data[dateCol]], dtype='str')
        data[dateCol] = datetime[:,0]
        data[timeCol] = datetime[:,1]
          
        # get year month and day from Date
        date = np.asarray([d.split('-') for d in data[dateCol]], dtype='uint16')
          
        # create new coluns
        data[yearCol]  = date[:,0]
        data[monthCol] = date[:,1]
        data[dayCol]   = date[:,2]
        data[julianDayCol] = 0
          
        # cast these columns from str to numeric
        data[outTemCol]  = pd.to_numeric(data[outTemCol], errors='coerce')
        data[inHumCol]  = pd.to_numeric(data[inHumCol], errors='coerce')
        data[inTemCol] = pd.to_numeric(data[inTemCol], errors='coerce')
        data[outHumCol]   = pd.to_numeric(data[outHumCol], errors='coerce')
          
        # convert temperature from fahrenheit to celsius
        data[outTemCol]  = (data[outTemCol]  - 32) * (5/9)
        data[inTemCol] = (data[inTemCol] - 32) * (5/9)
        
        # get Julian Day
        for date in data[dateCol].unique():
            d = dt.datetime.strptime(date, "%Y-%m-%d") # get datetime object
            data.loc[ (data[yearCol] == d.year) & (data[monthCol] == d.month) & (data[dayCol] == d.day), julianDayCol] = dt.date(d.year,d.month,d.day).toordinal()
        return data
    
    def getMaxMin(self, column):
        '''
        Description:
            It computes max and min value of the specified column passed for each day. 
            It returns a list with the values for each day.
        Input:
            column: The name of the column of interest.
        Output:
            A list with lists containing max and min value for each day. 
            As the following example:
                
            returning list := [[max1,min1], [max2,min2], ...,[maxN,minN]]
        '''
        import numpy as np
        
        data = self.data.copy()
        
        mxmn_list = list()
        for day in data[julianDayCol].unique():
            d = data[data[julianDayCol] == day] 
            mxmn_list.append([round(np.max(d[column]),2), round(np.min(d[column]),2)])
        return mxmn_list
    
    def getMean(self, column):
        '''
        Description:
            It computes mean and standard deviation of the values from the specified column passed for each day. 
            It returns a list with the values calculated.
        Input:
            column: The name of the column of interest.
        Output:
            A list with lists containing mean and stddev for each day. 
            As the following example:

            returning list := [[mean1,stddev1], [mean2,stddev2], ...,[meanN,stddevN]]
        '''
        import numpy as np
        
        data = self.data.copy()
        
        mean_list = list()
        for day in data[julianDayCol].unique():
            d = data[data[julianDayCol] == day]
            mean_list.append([round(np.mean(d[column]), 2), round(np.std(d[column]), 2)])
        return mean_list
    
    def getTimeOn(self):
        '''
        Description:
            It computes how much time the device that controls temperature was left on mode on. 
            It returns a list with the values for each day in order.

        Output:
            A list with each time that the device was left on mode on for each day.
        '''
        
        data = self.data.copy()
        
        count_list = list()
        for day in data[julianDayCol].unique():
            d = data[data[julianDayCol] == day]
            modes = d[systemModeCol].values
            clock = d[timeCol].values
            clock = [x.split(':') for x in clock]
            
            count = 0
            i = 0
            while i < len(modes):
                if modes[i]!= "off":
                    b = int(clock[i][0])*60 + int(clock[i][1])
                    i+=1
                    while i < len(modes) and modes[i]!= "off":
                        i+=1
                    if i < len(modes):
                        a = int(clock[i][0])*60 + int(clock[i][1])
                    else:
                        a = 1440
                        
                    count += a - b
                i+=1
            
            count_list.append(count)
        return count_list
    
    def summarizeData(self):
        '''
        Description:
            It computes mean, standard deviation, max and min values from Outdoor and Indoor measures. 
            It returns a new dataframe with these values.

        Output:
            A simplified data frame containing mean, standard deviation, max, and
            min values from Indoor and Outdoor Humidity and Temperature.
        '''
        import pandas as pd
        import numpy as np
        
        data = self.data.copy()
        
        columns= [outTemCol, inTemCol, inHumCol, outHumCol]
        
        meanv = list()
        mxmnv = list()
        for c in columns:
            meanv.append(np.asarray(self.getMean(c)))
            mxmnv.append(np.asarray(self.getMaxMin(c)))
        
        tmOn = np.asarray([self.getTimeOn()])
        days = np.asarray([data[julianDayCol].unique()])
        
        meanv = np.concatenate((meanv[:]), axis=1)
        mxmnv = np.concatenate((mxmnv[:]), axis=1)
        
        values = np.concatenate((days.T,meanv,mxmnv,tmOn.T), axis=1)
        
        
        cln_columns = [julianDayCol, 
                      meanOutTemCol, stdOutTemCol,
                      meanInTemCol, stdInTemCol,
                      meanInHumCol, stdInHumCol,
                      meanOutHumCol, stdoutHumCol,
                      maxOutTemCol, minOutTemCol,
                      maxInTemCol, minInTemCol,
                      maxInHumCol, minInHumCol,
                      outHumColMax, minOutHumCol,
                      timeDeviceOnCol]
        
        self.summ = pd.DataFrame(values, columns = cln_columns)
    
    def plotTxD(self):
        '''
        Description:
            It plot the relation between the temperature bands and the mean time 
            that the user let the device on mode on. Each band has a width of 5 Celsius degrees.
            If there is a point for temperature T, it means that the mean time left on mode on 
            from T-5 to T celsius degrees is represented by this point.
        '''
        import matplotlib.pyplot as plt
        import numpy as np
        
        data = self.summ.copy()
        
        # get boundaries and bands
        min_t = data[meanOutTemCol].min()
        max_t = data[meanOutTemCol].max()
        temp = np.arange(min_t+5,max_t+5,5)
        mean = []
        std = []
        
        # get mean time on and the respectives standard deviations
        for t in temp:
            f = data.loc[(data[meanOutTemCol] < t) & (data[meanOutTemCol] > t - 5), timeDeviceOnCol]
            mean.append(f.sum()/(f.size*60.0))
            std.append(np.std(np.asarray(f)/60.0))
                
        x = temp
        y = mean
        e = std
        
        fig = plt.figure(figsize = (16,12))
        ax = fig.add_subplot(1, 1, 1)
        
        ax.set_xlabel('Mean Temperature Band (C)')
        ax.set_ylabel('Device On Mean Time (hours/day)')
        
        # Major ticks every 20, minor ticks every 1
        major_ticks = np.arange(0, int(np.max(y))+int(np.max(e) + 50 ), 20)
        minor_ticks = np.arange(int(min_t)-5, int(max_t)+5, 1)
        
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(major_ticks, minor=True)
        
        ax.grid(which='minor', alpha=1)
        ax.grid(which='major', alpha=0.5)
        
        plt.errorbar(x, y, yerr = e, ecolor = 'r', linestyle='None', marker='d')
        plt.show()
        
    def plotComparison(self, 
                    summ = False,
                    xlabel  = 'Day',
                    ylabel  = 'Temperature (C)',
                    y1label = 'Outdoor', 
                    y2label = 'Indoor', 
                    title   = "Outdoor x Indoor", 
                    columns = [meanOutTemCol, meanInTemCol, julianDayCol]):
        '''
        Description:
            It plot two different measurements to make a comparison.
        Input:
            columns: A list with the columns to be ploted.
            summ: If True, It will be used dataframe self.summ. If False, it will be used self.data.
            xlabel: x-axis label
            ylabel: y-axis label
            y1label: legend for the 1st measurement
            y2label: legend for the 2nd measurement
            title: title for the plot
        '''
        import matplotlib.pyplot as plt
        import pylab as pl
        import numpy as np
        
        if summ:
            dataframe = self.summ
        else: 
            dataframe = self.data
        
        # get values
        y1, y2, t = dataframe[columns[0]].values, dataframe[columns[1]].values, dataframe[columns[2]].values
        
        # remove nan from x and y
        fltr = ~np.isnan(y1)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        fltr = ~np.isnan(y2)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        
        fig = plt.figure(figsize = (16,12))
        ax = fig.add_subplot(1, 1, 1)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        min_y = min([y1.min(), y2.min()])
        max_y = max([y1.max(), y2.max()])
        
        # Major ticks every 20, minor ticks every 1
        major_ticks = np.arange(min_y-5, max_y+5, 1)
        minor_ticks = np.arange(t[0]-1, t[-1]+5, 5)
        
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_yticks(major_ticks, minor=True)
        
        ax.grid(which='both')
        
        ax.plot(t, y1, 'darkblue', linestyle='--', label = y1label, marker='o')
        ax.plot(t, y2, 'lime', linestyle='--', label = y2label , marker='o')
        pl.legend(loc='lower right')
        pl.title(title)
        plt.show()  
        
    def animatedPlot(self,
                    fileName,
                    dataframe = None,
                    summ = False,
                    columns=[outTemCol,inTemCol,timeCol], 
                    nFrames = 300, 
                    nfps = 30, 
                    nInterval = 500, 
                    step = 10, 
                    legend = "", 
                    y2label = "", 
                    y1label= "", 
                    xlabel = "", 
                    ylabel = "", 
                    title = ""):
        '''
        Description:
            It plot an animated plot of two different measurements to make a comparison.
        Input:
            filename: File name path to be saved on the machine.
            dataframe: If a dataframe isn't passed, then it will be used self.data or self.summ.
            nFrame: number of frames to be created.
            nfps: frames per second to be recorded.
            nInterval: Delay between frames in milliseconds.
            step: how much points will be ploted on each frame.
            columns: A list with the columcolumns=[outTemCol,inTemCol,timeCol]ns to be ploted.
            summ: If True, It will be used dataframe self.summ. If False, it will be used self.data.
            xlabel: x-axis label
            ylabel: y-axis label
            y1label: legend for the 1st measurement
            y2label: legend for the 2nd measurement
            title: title for the plot
        '''
        
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import pylab as pl
        import numpy as np
        import pandas as pd
        
        if type(dataframe) != pd.core.frame.DataFrame:
            if summ:
                dataframe = self.summ
            else:
                dataframe = self.data
        
        # get values
        y1, y2, t = dataframe[columns[0]].values, dataframe[columns[1]].values, dataframe[columns[2]].values
        
        # remove nan from y1 and y2
        fltr = ~np.isnan(y1)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        fltr = ~np.isnan(y2)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        
        if 'Time' in columns[2]:
            t = t - t.min()
        
        fig = plt.figure(figsize = (24,16))
        ax = fig.add_subplot(1, 1, 1)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        k = y1[:step]
        k[0], k[-1] = y1.max(), y1.min()
        
        l = y2[:step]
        l[0], l[-1] = y2.max(), y2.min()
        
        line = list()
        ax1, = ax.plot(t[:step], k, 'darkblue', label = y1label)
        ax2, = ax.plot(t[:step], l, 'lime', label = y2label)
        line.append(ax1)
        line.append(ax2)
        pl.legend(loc='lower right')
        pl.title(title)
        
        def init():  # only required for blitting to give a clean slate.
            line[0].set_ydata([np.nan]*step)
            line[1].set_ydata([np.nan]*step)
            return line
        
        def animate(i):
            if len(y1[i: i+step]) == step:
                line[0].set_ydata(y1[i:i + step])
                line[1].set_ydata(y2[i:i + step])
            return line
            
        ani = animation.FuncAnimation(
            fig, animate, init_func=init, interval=nInterval, blit=True, save_count=50, frames=nFrames)
        
        ani.save(fileName, fps=nfps, extra_args=['-vcodec', 'libx264'])
        
        plt.show()
        
    def animatedPlotStatic(self,
                        fileName,
                        dataframe = None,
                        summ = False,
                        columns=[outTemCol,inTemCol,timeCol], 
                        nFrames = 300, 
                        nfps = 30, 
                        nInterval = 500, 
                        step = 10, 
                        legend = "", 
                        y2label = "", 
                        y1label= "", 
                        xlabel = "", 
                        ylabel = "", 
                        title = ""):
        '''
        Description:
            It plot an animated plot of two different measurements to make a comparison.
        Input:
            filename: File name path to be saved on the machine.
            dataframe: If a dataframe isn't passed, then it will be used self.data or self.summ.
            nFrame: number of frames to be created.
            nfps: frames per second to be recorded.
            nInterval: Delay between frames in milliseconds.
            step: how much points will be ploted on each frame.
            columns: A list with the columcolumns=[outTemCol,inTemCol,timeCol]ns to be ploted.
            summ: If True, It will be used dataframe self.summ. If False, it will be used self.data.
            xlabel: x-axis label
            ylabel: y-axis label
            y1label: legend for the 1st measurement
            y2label: legend for the 2nd measurement
            title: title for the plot
        '''
        
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import pylab as pl
        import numpy as np
        import pandas as pd
        
        if type(dataframe) != pd.core.frame.DataFrame:
            if summ:
                dataframe = self.summ
            else:
                dataframe = self.data
        
        # get values
        y1, y2, t = dataframe[columns[0]].values, dataframe[columns[1]].values, dataframe[columns[2]].values
    
        # remove nan from y1 and y2
        fltr = ~np.isnan(y1)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        fltr = ~np.isnan(y2)
        y1, y2, t = y1[fltr], y2[fltr], t[fltr]
        
        if 'Time' in columns[2]:
            t = t - t.min()
        
        fig = plt.figure(figsize = (24,16))
        ax = fig.add_subplot(1, 1, 1)
    
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
        line = list()
        ax1, = ax.plot(t, y1, 'darkblue', label = y1label)
        ax2, = ax.plot(t, y2, 'lime', label = y2label)
        line.append(ax1)
        line.append(ax2)
        pl.legend(loc='lower right')
        pl.title(title)
    
        def init():  # only required for blitting to give a clean slate.
            line[0].set_data([], [])
            line[1].set_data([], [])
            return line
    
        def animate(i):
            line[0].set_data(t[:i*step], y1[:i*step])
            line[1].set_data(t[:i*step], y2[:i*step])
            return line
    
        ani = animation.FuncAnimation(
            fig, animate, init_func=init, interval=nInterval, blit=True, save_count=50, frames=nFrames)
    
        ani.save(fileName, fps=nfps, extra_args=['-vcodec', 'libx264'])
    
        plt.show()