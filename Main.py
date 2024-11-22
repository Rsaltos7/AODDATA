import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Input parameters for user configuration
st.title("Temperature Data Visualization")
uploaded_file = st.file_uploader("Upload your temperature data CSV", type="csv")

if uploaded_file:
    # Load the CSV file
    Wdf = pd.read_csv(uploaded_file, parse_dates=['DATE'], index_col='DATE')
    Wdf.sort_index(inplace=True)

    # User inputs for StartDate, EndDate, and other parameters
    StartDate = st.date_input("Select Start Date", value=Wdf.index.min().date())
    EndDate = st.date_input("Select End Date", value=Wdf.index.max().date())
    SampleRate = st.selectbox("Select Sampling Rate", ['H', 'D', 'W'], index=1)  # Hourly, Daily, Weekly
    graphScale = st.slider("Adjust Graph Scale", 1.0, 5.0, 1.5)
    siteName = st.text_input("Site Name", value="Default Site")
    filename = st.text_input("Filename Prefix", value="Temperature_Data")

    # Process temperature data
    Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
    Tdf.replace('+9999', np.nan, inplace=True)

    # Plotting
    fig, axes = plt.subplots(1, 1, figsize=(16 * graphScale, 9 * graphScale))
    ax = axes  # Single axis

    # Setting up the axis
    fig.autofmt_xdate()
    ax.set_title(f"{siteName} {filename[:4]} Temperature")
    ax.grid(which='both', axis='both')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Drawing the temperature data
    ax.set_ylabel('Temperature °C')
    temp_data = Tdf[0].astype(float).resample(SampleRate).mean().div(10)  # Convert to numeric and scale
    ax.set_ylim(temp_data.min() // 1, temp_data.max() // 1)  # Auto calculate limits
    temperatureHandle, = ax.plot(temp_data, '.r-', label='Temperature', figure=fig)

    # Add legend and layout adjustment
    plt.legend(handles=[temperatureHandle], loc='best')
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)
