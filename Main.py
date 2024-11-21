import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

filename = '20190101_20191231_Modesto (1).tot_lev20'
windfile = 'Modesto_Wind_2019_Jan_Dec_72492623258.csv'
weatherFile = 'Wind_Data/Modesto_Weather_Feb_2019.csv'
StartDate='2019-06-11 00:00:00'
EndDate='2019-06-13 23:59:59'
sampleRate = '1h'
windSampleRate = sampleRate

# Load the AERONET data and make US/PAC time its index.
df = pd.read_csv(filename,skiprows = 6, parse_dates={'datetime':[0,1]})
datetime_utc=pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace = True)

# Set the Columns that has the AOD Total and replace -999 with nan in visible wavelengths.
AODTotalColumns=range(3,173,8)
#for iWaveLength in df.columns[AODTotalColumns]: print(iWaveLength)
#Replaces all -999 values with nan so invalid entries does not affect resample.mean()
df['AOD_380nm-Total'].replace(-999.0, np.nan, inplace = True)
df['AOD_440nm-Total'].replace(-999.0, np.nan, inplace = True)
df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace = True)
df['AOD_675nm-Total'].replace(-999.0, np.nan, inplace = True)
    
# Load NOAA data and make US/PAC time its index.
# Wdf = Weather Data Frame
Wdf = pd.read_csv(windfile, parse_dates={'datetime':[1]}, low_memory=False)
datetime_utc=pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac= pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace = True)
# Note that we're making a copy of Wdf as WNDdf (Wind Data frame)
WNDdf= Wdf.loc[StartDate:EndDate,'WND'].str.split(pat=',', expand= True)
## Cut on the Data that has both Valid Windspeed and Direction.
WNDdf= WNDdf.loc[WNDdf[4]=='5']
WNDdf= WNDdf.loc[WNDdf[1]=='5']

# Converting the Cardinal Coordinates to Cartesian using x=r*sinΘ and y=r*cosΘ
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) # Magnitude
                 *np.sin(np.float64(row[0]) # Angle
                               *(np.pi/180)))
    Ydata.append(np.float64(row[3])*np.cos(np.float64(row[0])*(np.pi/180)))
WNDdf[5], WNDdf[6] = Xdata, Ydata # Appending these new Coordinates to the Wind Data Frame

# Tdf = Temperature Data Frame
## Splitting Temperature from the Weather Data Frame and expanding the string into individual columns
Tdf = Wdf.loc[StartDate:EndDate,'TMP'].str.split(pat=',', expand = True)
## Replacing +9999 values with nan, +9999 indicates "missing data"
Tdf.replace('+9999', np.nan, inplace = True)

# Creating Figure and main Axis
## Note: Technically, we can draw multiple, side-by-side, graphs using this method.
## Using a 16x9 aspect ratio
fig, axes = plt.subplots(1,1, figsize=(16*.65,9*.65)) # plt.subplots(nrows, ncolumns, *args) # axs will be either an individual plot or an array of axes
try:
    ax = axes[0,0] # If axes is a 2D array of axes, then we'll use the first axis for this drawing.
except:
    try:
        ax = axes[0] # If axes is a 1D array of axes, then we'll use the first axis for this drawing.
    except:
        ax = axes # If axes is just a single axis then we'll use it directly.

# Initializing main Axis and plot
fig.autofmt_xdate() ## Note: With multiple plots, this removes the x-axis identifiers for plots not in the bottom row 
ax.set_title("Modesto 2019: AOD, Wind Speed, and Temperature")
ax.grid(which='both',axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Drawing the first pieces of data (AOD_500nm-Total) onto the graph
ax.set_ylabel("AOD_500nm-Total")
plot1, = ax.plot(df.loc[StartDate:EndDate,'AOD_500nm-Total'].resample(sampleRate).mean(),'ok-',label='AOD_500nm-Total', figure=fig) # handle, label = ax.plot()

# Adding a new Axis sharing the same xaxis as before and drawing the second piece of data.
ax2 = ax.twinx()
ax2.spines.right.set_position(('axes', 1.05)) # Adjusting the position of the "spine" or y-axis to not overlap with the next pieces of data
ax2.set_ylabel('Temperature °C')
ax2.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).min()//-1,Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).max()//1) # Auto Calculating
ax2.set_ylim(18,41) # Manual Setting
plot2, = ax2.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10), '.r-',label='Temperature',figure=fig) # handle, label = ax2.plot()

# Adding a new Axis sharing the same xaxis as the previous two and drawing the thrid piece of data
ax3 = ax.twinx()
#ax3.spines.right.set_position(('axes', 1)) # Adjusting the position of the "spine" or y-axis (Only needed if we want to move this y-axis)
ax3.set_ylabel("Wind Mag m/s")
ax3.set_ylim(WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).min()//1, WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).max()//1) # Auto Calculating
ax3.set_ylim(1,8) # Manual Setting
plot3 = ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index,
                   np.sqrt( (WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() / 
                WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size())**2 + 
                (WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() / 
                WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size())**2
                )/10,
                -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10), 
                -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                color='b',label='Wind Vector')
#testString = 'Temperature: ' + str(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).max()//1) + '/' + str(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).min()//1) + '\nPercipiation: ' + str(5)
#ax.text(0.5, 0.5, testString, transform=ax.transAxes, fontsize=10, bbox= dict(boxstyle='round', facecolor='cyan', alpha=0.5))

# Displaying the legend and Reorganizing everything to fit nicely
## Note: plot1 and plot2 are the handles for the data we created and plot3, the quiver, is handled differently.
plt.legend(handles = [plot1, plot2, plot3], loc = 'best')
plt.tight_layout() # Adjusts the boundaries of the figures to ensure everything fits nicely. Can define pads as we we see fit. 
# Example: plt.tight_layout(pad=n, h_pad=n2, w_pad=n3, rect=tuple) where n# are floats and tuple is a tubple of integers (0,0,1,1)

# Optional, saving the plot to a file as a .png.
## Note: You must save the plot before calling plt.show(), additionally, you must have the relative directory setup otherwise this will produce a "soft" error.
## Change 'False' in the if-statement to True to enable saving the plot as a png
if False:
    filename = 'Modesto_' + str(pd.Timestamp.now().strftime('%Y-%m-%d_%H%M%S'))# + StartDate + '_' + EndDate
    location = 'graphs\\Modesto 2019\\' + filename
    plt.savefig(location) # Saves the plot to a .png file.

plt.show()
