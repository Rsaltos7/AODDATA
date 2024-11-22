import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import streamlit as st

# Data URLs
filename = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1%20(1).lev15'
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv'
weatherFile = 'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv'

StartDate = '2023-06-11 00:00:00'
EndDate = '2023-06-13 23:59:59'
sampleRate = '1h'
windSampleRate = sampleRate

# Load the AERONET data and make US/PAC time its index.
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime':[0, 1]})

# Strip any leading or trailing spaces from the columns
df.columns = df.columns.str.strip()

# Convert to US/Pacific timezone
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)

# Print the columns and a few rows to check if the names match
print(df.columns)
print(df.head())

# Replace -999 values with NaN for the columns that are present
aod_columns = ['AOD_380nm-Total', 'AOD_440nm-Total', 'AOD_500nm-Total', 'AOD_675nm-Total']
for column in aod_columns:
    if column in df.columns:
        df[column].replace(-999.0, np.nan, inplace=True)

# Load NOAA wind data and make US/PAC time its index.
Wdf = pd.read_csv(windfile, parse_dates={'datetime':[1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Process the wind data
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']
WNDdf = WNDdf.loc[WNDdf[1] == '5']

# Convert wind speed and direction to Cartesian coordinates
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))
    Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))
WNDdf[5], WNDdf[6] = Xdata, Ydata

# Process temperature data
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Create the plot
fig, ax = plt.subplots(1, 1, figsize=(16 * 0.65, 9 * 0.65))

# Plot AOD data (AOD_500nm-Total)
ax.set_title("Modesto 2019: AOD, Wind Speed, and Temperature")
ax.grid(which='both', axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

ax.set_ylabel("AOD_500nm-Total")
plot1, = ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total'].resample(sampleRate).mean(), 'ok-', label='AOD_500nm-Total', figure=fig)

# Add a secondary axis for temperature
ax2 = ax.twinx()
ax2.spines['right'].set_position(('axes', 1.05))
ax2.set_ylabel('Temperature °C')

temperature_series = Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10)
ax2.set_ylim(temperature_series.min(), temperature_series.max())  # Set y-axis limits based on data
plot2, = ax2.plot(temperature_series, '.r-', label='Temperature', figure=fig)

# Add another axis for wind magnitude
ax3 = ax.twinx()
ax3.set_ylabel("Wind Mag (m/s)")

# Calculate the wind magnitude from Xdata and Ydata
wind_magnitude = np.sqrt((WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                          WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size())**2 +
                         (WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                          WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size())**2) / 10

ax3.set_ylim(wind_magnitude.min(), wind_magnitude.max())
plot3 = ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index,
                   -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                   -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                   color='b', label='Wind Vector')

# Display the legend
plt.legend(handles=[plot1, plot2, plot3], loc='best')
plt.tight_layout()

# Show the plot using Streamlit
st.pyplot(fig)

# Additional Info/Links:
# https://matplotlib.org/2.0.2/users/recipes.html # ← Contains Additional information on useful plotting techniques
# https://matplotlib.org/3.4.3/gallery/ticks_and_spines/multiple_yaxis_with_spines.html # ← Use this format for graph handling
