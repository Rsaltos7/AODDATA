import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import streamlit as st

# URLs for data
filename = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1%20(1).lev15'
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv'
weatherFile = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv'

# Streamlit inputs for the start and end date
StartDate = st.date_input("Start Date", pd.to_datetime('2019-06-11'))
EndDate = st.date_input("End Date", pd.to_datetime('2019-06-13'))

# Set sample rate
sampleRate = '1h'
windSampleRate = sampleRate

# Load the AERONET data and make US/PAC time its index.
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime':[0,1]})
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)

# Set the Columns that have the AOD Total and replace -999 with nan in visible wavelengths.
AODTotalColumns = range(3, 173, 8)
df['AOD_380nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_440nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace=True)
df['AOD_675nm-Total'].replace(-999.0, np.nan, inplace=True)

# Load NOAA data and make US/PAC time its index.
Wdf = pd.read_csv(windfile, parse_dates={'datetime':[1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Wind data extraction and processing
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']
WNDdf = WNDdf.loc[WNDdf[1] == '5']

# Convert Cardinal Coordinates to Cartesian
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))
    Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))
WNDdf[5], WNDdf[6] = Xdata, Ydata

# Temperature data processing
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Streamlit's plot
fig, ax = plt.subplots(figsize=(16 * .65, 9 * .65))

# Configure the axes
fig.autofmt_xdate()
ax.set_title("Modesto 2019: AOD, Wind Speed, and Temperature")
ax.grid(which='both', axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Plot the AOD data
ax.set_ylabel("AOD_500nm-Total")
plot1, = ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total'].resample(sampleRate).mean(), 'ok-', label='AOD_500nm-Total')

# Add Temperature plot (secondary axis)
ax2 = ax.twinx()
ax2.spines.right.set_position(('axes', 1.05))
ax2.set_ylabel('Temperature °C')
ax2.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).min() // -1, Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).max() // 1)
ax2.set_ylim(18, 41)  # Manually setting the limits
plot2, = ax2.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10), '.r-', label='Temperature')

# Add Wind data plot (third axis)
ax3 = ax.twinx()
ax3.set_ylabel("Wind Mag m/s")
ax3.set_ylim(WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).min() // 1, WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).max() // 1)
ax3.set_ylim(1, 8)  # Manually setting the limits
plot3 = ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index,
                   np.sqrt((WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                            WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size()) ** 2 +
                           (WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                            WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size()) ** 2) / 10,
                   -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                   -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                   color='b', label='Wind Vector')

# Display the legend
plt.legend(handles=[plot1, plot2, plot3], loc='best')

# Tighten the layout to prevent clipping
plt.tight_layout()

# Show plot in Streamlit
st.pyplot(fig)

# Additional Info/Links:
# https://matplotlib.org/2.0.2/users/recipes.html # ← Contains Additional information on useful plotting techniques
# https://matplotlib.org/3.4.3/gallery/ticks_and_spines/multiple_yaxis_with_spines.html # ← Use this format for graph handling
