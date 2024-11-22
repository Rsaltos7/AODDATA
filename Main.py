import streamlit as st
import numpy as np
import pandas as pd
import csv
import matplotlib.dates as mdates
# Change filenames to the names of the files that you uploaded
filename = "https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv"
windfile = "https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/Modesto_Wind_2023%20(2).csv"
siteName = "Turlock CA USA"
SampleRate = "1h"
WindSampleRate = "3h"
StartDate = '2023-07-01 00:00:00'
EndDate = '2023-07-07 23:59:59'
AOD_min = 0.0
AOD_max = 0.3
graphScale = 0.65

# Load the AERONET data and make US/PAC time its index.
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime': [0, 1]})
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)

# Plot AOD data using Streamlit
st.title("Aerosol Optical Depth (AOD) Data")

# Resample AOD data
AOD_675nm = df.loc[StartDate:EndDate, "AOD_675nm"].resample(SampleRate).mean()
AOD_500nm = df.loc[StartDate:EndDate, "AOD_500nm"].resample(SampleRate).mean()
AOD_440nm = df.loc[StartDate:EndDate, "AOD_440nm"].resample(SampleRate).mean()

# Create line chart for AOD data
st.line_chart(AOD_675nm, use_container_width=True)
st.line_chart(AOD_500nm, use_container_width=True)
st.line_chart(AOD_440nm, use_container_width=True)

# Display wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Process wind data
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']
WNDdf = WNDdf.loc[WNDdf[1] == '5']
Xdata, Ydata = [], []
for _, row in WNDdf.iterrows():
    Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * sin(Angle)
    Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))  # Magnitude * cos(Angle)

WNDdf[5], WNDdf[6] = Xdata, Ydata  # Append new coordinates to the DataFrame

# Display wind data using Streamlit
wind_data = pd.DataFrame({
    'Wind X': WNDdf[5].astype(float),
    'Wind Y': WNDdf[6].astype(float)
}, index=WNDdf.index)

st.write("Wind Vector Data (X and Y components)")
st.line_chart(wind_data[['Wind X', 'Wind Y']], use_container_width=True)

# Temperature data processing and display
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Display Temperature data
temperature = Tdf[0].astype(float).resample(SampleRate).mean() / 10  # Convert to Celsius
st.write("Temperature Data")
st.line_chart(temperature, use_container_width=True)
