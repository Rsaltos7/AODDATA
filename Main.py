import streamlit as st
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import csv

# Change filenames to the names of the files that you uploaded
## Note: These files will be used for all graphs in this assignment
filename = "https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv"
windfile = "https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv"
siteName="Turlock CA USA"
SampleRate = "1h"
WindSampleRate = "3h"
StartDate='2023-07-01 00:00:00'
EndDate='2023-07-07 23:59:59'
AOD_min = 0.0
AOD_max = 0.3
graphScale= 0.65

# Load the AERONET data and make US/PAC time its index.
df = pd.read_csv(filename,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)


plt.figure(figsize=(20*graphScale,10*graphScale))
plt.plot(df.loc[StartDate:EndDate,"AOD_675nm"].resample(SampleRate).mean(),'.r',label="AOD_675nm-AOD")
plt.plot(df.loc[StartDate:EndDate,"AOD_500nm"].resample(SampleRate).mean(),'.g',label="AOD_500nm-AOD")
plt.plot(df.loc[StartDate:EndDate,"AOD_440nm"].resample(SampleRate).mean(),'.b',label="AOD_440nm-AOD")

plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
#Change the range on Y here if needed
plt.ylim(AOD_min,AOD_max)
plt.legend()
plt.show()
Wdf = pd.read_csv(windfile, parse_dates={'datetime':[1]}, low_memory=False)
datetime_utc=pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace = True)
# Note that we're making a copy of Wdf as WNDdf (Wind Dataframe)
WNDdf= Wdf.loc[StartDate:EndDate,'WND'].str.split(pat=',', expand= True)
## Cut on the Data that has both Valid Windspeed and Direction.
WNDdf= WNDdf.loc[WNDdf[4]=='5']
WNDdf= WNDdf.loc[WNDdf[1]=='5']
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) # Magnitude
                 *np.sin(np.float64(row[0]) # Angle
                               *(np.pi/180)))
    Ydata.append(np.float64(row[3])*np.cos(np.float64(row[0])*(np.pi/180)))
WNDdf[5], WNDdf[6] = Xdata, Ydata # Appending these new Coordinates to the Wind Data Frame

# Creating Figure and main Axis
## Using a 16x9 aspect ratio
fig, axes = plt.subplots(1,1, figsize=(16*graphScale,9*graphScale)) # plt.subplots(nrows, ncolumns, *args) # axs will be either an individual plot or an array of axes
try:
    ax = axes[0,0] # If axes is a 2D array of axes, then we'll use the first axis for this drawing.
except:
    try:
        ax = axes[0] # If axes is a 1D array of axes, then we'll use the first axis for this drawing.
    except:
        ax = axes # If axes is just a single axis then we'll use it directly.

# Initializing main Axis and plot
fig.autofmt_xdate() ## Note: With multiple plots, this removes the x-axis identifiers for plots not in the bottom row
ax.grid(which='both',axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Drawing the Data onto the graph
ax.set_ylabel("Wind Mag m/s")
maxWind = np.sqrt((WNDdf[6].loc[StartDate:EndDate].astype(float).max()/10)**2+
                  (WNDdf[5].loc[StartDate:EndDate].astype(float).max()/10)**2)
ax.set_ylim(0,maxWind)
windHandle = ax.quiver(WNDdf[5].resample(WindSampleRate).mean().index,maxWind-1,
                -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(WindSampleRate).mean().div(10),
                -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(WindSampleRate).mean().div(10),
                color='b',label='Wind Vector',width=0.005)

# Displaying the legend and reorganizing everything to fit nicely
## Note: plot1 is the handle for the data plot we created
plt.legend(handles = [windHandle], loc = 'best')
plt.tight_layout() # Adjusts the boundaries of the figures to ensure everything fits nicely. Can define pads as we we see fit.
plt.show()
Tdf = Wdf.loc[StartDate:EndDate,'TMP'].str.split(pat=',', expand = True)
## Replacing +9999 values with nan, +9999 indicates "missing data"
Tdf.replace('+9999', np.nan, inplace = True)

fig, axes = plt.subplots(1,1, figsize=(16*graphScale,9*graphScale)) # plt.subplots(nrows, ncolumns, *args) # axs will be either an individual plot or an array of axes
try:
    ax = axes[0,0] # If axes is a 2D array of axes, then we'll use the first axis for this drawing.
except:
    try:
        ax = axes[0] # If axes is a 1D array of axes, then we'll use the first axis for this drawing.
    except:
        ax = axes # If axes is just a single axis then we'll use it directly.

# Initializing main Axis and plot
fig.autofmt_xdate() ## Note: With multiple plots, this removes the x-axis identifiers for plots not in the bottom row
ax.set_title(siteName + ' ' + filename[0:4] + ' Temperature')
ax.grid(which='both',axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Drawing the Temperature Data onto the graph.
ax.set_ylabel('Temperature °C')
ax.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).min()//1,
            Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).max()//1) # Auto Calculating
temperatureHandle, = ax.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10), '.r-',label='Temperature',figure=fig) # handle, label = ax2.plot()

# Displaying the legend and Reorganizing everything to fit nicely
## Note: temperatureHandle is the handle for the data plot we created.
plt.legend(handles = [temperatureHandle], loc = 'best')
plt.tight_layout() # Adjusts the boundaries of the figures to ensure everything fits nicely. Can define pads as we we see fit.
plt.show()
