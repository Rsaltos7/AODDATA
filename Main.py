import numpy as np
import pandas as pd
import matplotlib as plt
import dates as mdates
import patches as mpatches
import streamlit as st

# Streamlit file upload widgets
st.title("AOD, Wind Speed, and Temperature Visualization")
filename = st.text_input('Enter the URL for AERONET Data', 
                        'https://raw.githubusercontent.com/Rsaltos7/AODDATA/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1%20(1).lev15')
windfile = st.text_input('Enter the URL for Wind Data', 
                         'https://github.com/Rsaltos7/AODDATA/blob/main/Modesto_Wind_2023%20(2).csv')
weatherFile = windfile  # Assuming same as windfile
StartDate = st.text_input('Start Date', '2019-06-11 00:00:00')
EndDate = st.text_input('End Date', '2019-06-13 23:59:59')
sampleRate = st.text_input('Sample Rate', '1h')
windSampleRate = sampleRate

# Load the AERONET data and make US/PAC time its index.
@st.cache_data
def load_data():
    df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime': [0, 1]})
    datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    df.set_index(datetime_pac, inplace=True)

    # Replace -999 with NaN in the columns of interest
    df['AOD_380nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_440nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_500nm-Total'].replace(-999.0, np.nan, inplace=True)
    df['AOD_675nm-Total'].replace(-999.0, np.nan, inplace=True)
    
    return df

df = load_data()

# Load NOAA data and make US/PAC time its index.
@st.cache_data
def load_wind_data():
    Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
    datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
    datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
    Wdf.set_index(datetime_pac, inplace=True)

    # Filtering and processing wind data
    WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)
    WNDdf = WNDdf.loc[WNDdf[4] == '5']
    WNDdf = WNDdf.loc[WNDdf[1] == '5']

    Xdata, Ydata = [], []
    for _, row in WNDdf.iterrows():
        Xdata.append(np.float64(row[3]) * np.sin(np.float64(row[0]) * (np.pi / 180)))
        Ydata.append(np.float64(row[3]) * np.cos(np.float64(row[0]) * (np.pi / 180)))
    WNDdf[5], WNDdf[6] = Xdata, Ydata
    return WNDdf, Wdf

WNDdf, Wdf = load_wind_data()

# Load temperature data
@st.cache_data
def load_temperature_data():
    Tdf = Wdf.loc[StartDate:EndDate, 'TMP'].str.split(pat=',', expand=True)
    Tdf.replace('+9999', np.nan, inplace=True)
    return Tdf

Tdf = load_temperature_data()

# Create plot using Matplotlib
def plot_data():
    fig, ax = plt.subplots(figsize=(16 * .65, 9 * .65))
    fig.autofmt_xdate()
    ax.set_title("Modesto 2019: AOD, Wind Speed, and Temperature")
    ax.grid(which='both', axis='both')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    # Plot AOD_500nm-Total data
    ax.set_ylabel("AOD_500nm-Total")
    ax.plot(df.loc[StartDate:EndDate, 'AOD_500nm-Total'].resample(sampleRate).mean(), 'ok-', label='AOD_500nm-Total')

    # Plot Temperature data
    ax2 = ax.twinx()
    ax2.spines['right'].set_position(('axes', 1.05))
    ax2.set_ylabel('Temperature °C')
    ax2.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).min() // -1,
                 Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10).max() // 1)
    ax2.set_ylim(18, 41)
    ax2.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(sampleRate).mean().div(10), '.r-', label='Temperature')

    # Plot Wind data as vectors (using Quiver)
    ax3 = ax.twinx()
    ax3.set_ylabel("Wind Mag m/s")
    ax3.set_ylim(WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).min() // 1,
                 WNDdf[3].loc[StartDate:EndDate].astype(float).div(10).max() // 1)
    ax3.set_ylim(1, 8)

    ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index,
               np.sqrt(
                   (WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                    WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size()) ** 2 +
                   (WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).sum() /
                    WNDdf.loc[StartDate:EndDate].resample(windSampleRate).size()) ** 2
               ) / 10,
               -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
               -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
               color='b', label='Wind Vector')

    plt.legend(loc='best')
    plt.tight_layout()

    st.pyplot(fig)  # Streamlit rendering the plot

# Generate plot
plot_data()
