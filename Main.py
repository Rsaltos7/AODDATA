import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
StartDate='2023-07-01'
EndDate='2023-07-07'

   # URL for the wind data file
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
windSampleRate = '3h'
     # Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)
# Streamlit widgets for dynamic date range selection
st.title = "Wind Vectors (Magnitude and Direction)"  # Fixing title assignment to a string
start_date = st.date_input("Select Start Date", pd.to_datetime('2023-07-01'))
end_date = st.date_input("Select End Date", pd.to_datetime('2023-07-07'))

# Assuming Wdf, StartDate, EndDate, siteName, filename, SampleRate are defined earlier
Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
Tdf.replace('+9999', np.nan, inplace=True)

# Create subplots (2x2 layout, adjust as needed)
fig, axes = plt.subplots(1, 1, figsize=(13, 8))
#ax = axes[0, 0]  # Use the first subplot for this specific plot

# Format the figure and axis
fig.autofmt_xdate()
ax.set_title("Temperature")
ax.grid(which='both', axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Major ticks: 1 day
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))  # Minor ticks: every 3 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Prepare temperature data
temp_data = Tdf.loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10)
ax.set_ylabel('Temperature (°C)')
temp_data.min() - 1  # Add a small buffer below minimum #y_min =1
temp_data.max() + 1  # Add a small buffer above maximum #y_max =24
#y_min = temp_data.min() - 1  # A small buffer below the minimum value
#y_max = temp_data.max() + 1  # A small buffer above the maximum value
ax.set_ylim(y_min, y_max)


# Plot the data
ax.plot(temp_data, '.r-', label='Temperature')

# Add legend and finalize layout
#ax.legend(handles=[temperatureHandle], loc='best')
plt.tight_layout()  # Adjust layout to prevent overlaps

# Display the figure
st.pyplot(fig)
st.write("Temperature Data:", temp_data)
