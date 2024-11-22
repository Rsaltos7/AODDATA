import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Title and file uploader
st.title("Temperature Data Visualization")
uploaded_file = st.file_uploader("Upload your temperature data CSV", type="csv")

if uploaded_file:
    # Load the data
    Wdf = pd.read_csv(uploaded_file, parse_dates=['DATE'], index_col='DATE')
    Wdf.sort_index(inplace=True)

    # User inputs for date range and other settings
    StartDate = st.date_input("Start Date", value=Wdf.index.min().date())
    EndDate = st.date_input("End Date", value=Wdf.index.max().date())
    SampleRate = st.selectbox("Sampling Rate", ['H', 'D', 'W'], index=1)  # Hourly, Daily, Weekly
    graphScale = st.slider("Graph Scale", 1.0, 5.0, 1.5)
    siteName = st.text_input("Site Name", value="Default Site")
    filename = st.text_input("Filename Prefix", value="Temperature_Data")

 Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
    Tdf.replace('+9999', np.nan, inplace=True)
# Remove obvious outliers (e.g., temperatures greater than 50°C or negative below reasonable thresholds)
Tdf = temp_data[(temp_data >= -50) & (temp_data <= 50)]

# Re-plot the filtered data
fig, ax = plt.subplots(figsize=(13, 8))
fig.autofmt_xdate()
ax.set_title("Temperature (Filtered)")
ax.grid(which='both', axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Major ticks: 1 day
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))  # Minor ticks: every 3 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Update y-axis range based on filtered data
filtered_y_min = filtered_temp_data.min() - 1  # Add a small buffer below minimum
filtered_y_max = filtered_temp_data.max() + 1  # Add a small buffer above maximum
ax.set_ylim(filtered_y_min, filtered_y_max)
ax.set_ylabel('Temperature (°C)')

# Plot the filtered temperature data
ax.plot(filtered_temp_data, '.r-', label='Filtered Temperature')

# Finalize layout and display
plt.tight_layout()
plt.show()

    
    # Process temperature data
    Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
    Tdf.replace('+9999', np.nan, inplace=True)

    # Prepare the figure
    fig, axes = plt.subplots(1, 1, figsize=(16 * graphScale, 9 * graphScale))
    ax = axes

    # Set up the plot
    fig.autofmt_xdate()
    ax.set_title(f"{siteName} {filename[:4]} Temperature")
    ax.grid(which='both', axis='both')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Plot temperature data
    ax.set_ylabel('Temperature (°C)')
    temp_data = Tdf[0].astype(float).resample(SampleRate).mean().div(10)  # Process and scale temperature
    #ax.set_ylim(temp_data.min() // 1, temp_data.max() // 1)  # Auto calculate Y-axis limits
    # Sidebar controls for adjusting y-axis limits
    st.sidebar.header("Adjust Y-axis Limits")
    y_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=50.0, value=17.0, step=0.5)
    y_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=50.0, value=24.0, step=0.5)
    temperatureHandle, = ax.plot(temp_data, '.r-', label='Temperature', figure=fig)

    # Add legend and adjust layout
    plt.legend(handles=[temperatureHandle], loc='best')
    plt.tight_layout()

    # Render the plot in Streamlit
    st.pyplot(fig)

else:
    st.info("Please upload a CSV file to visualize.")
