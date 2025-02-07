import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
st.header = "Turlock AOD"
StartDate = st.date_input("StartDate", datetime.date(2023, 7, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2023, 7, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Input GitHub URL for the first repository
file_url_1 = "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1.lev15"

# Function to load data from the given URL
def load_data(file_url):
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Failed to process the file from {file_url}: {e}")
        return None

# Load data from the first file
df_1 = None
if file_url_1:
    df_1 = load_data(file_url_1)

# Ensure data is loaded and columns are correct
if df_1 is not None:
    if 'AOD_400nm' not in df_1.columns or 'AOD_500nm' not in df_1.columns or 'AOD_675nm' not in df_1.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df_1.columns}")
    
    # Plot data from the first repository if columns are correct
    if 'AOD_440nm' in df_1.columns and 'AOD_500nm' in df_1.columns and 'AOD_675nm' in df_1.columns:
        
        # Plot AOD_440nm, AOD_500nm, and AOD_675nm as initial plot
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.k')

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        plt.title("AOD Turlock")  # Added title for AOD graph
        st.pyplot(plt.gcf())
        
        # Ask user to match wavelengths to positions
        st.text("\nMatch the wavelengths to the positions on the graph:")
        # Dropdown menus for user input with no default selection
        positions = ["Highest", "Medium", "Lowest"]

        # Create user input dropdowns for selecting wavelengths
        user_matches = {}
        for pos in positions:
            user_matches[pos] = st.selectbox(f"What Wavelength will have the {pos} measurment on the graph?", 
                                             options=["Select an option", "400 nm", "500 nm", "675 nm"], 
                                             key=pos)

        # Once the user submits, show the second graph (same as the first)
        if st.button("Submit"):
            # Plot the second graph (exact same as the first one)
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b', label="440 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="675 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            #plt.title("AOD Turlock")  # Added title for AOD graph
            st.pyplot(plt.gcf())

     # URL for the wind data file
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/72492623258.csv'
windSampleRate = '3h'
     # Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)
# Streamlit widgets for dynamic date range selection
st.title = "Wind Vectors (Magnitude and Direction)"  # Fixing title assignment to a string
#start_date = st.date_input("Select Start Date", pd.to_datetime('2023-07-07'))
#end_date = st.date_input("Select End Date", pd.to_datetime('2023-07-14'))
start_date = StartDateTime
end_date = EndDateTime

# Convert selected dates to strings and filter the data
StartDate = start_date.strftime('%Y-%m-%d 00:00:00')
EndDate = end_date.strftime('%Y-%m-%d 23:59:59')


# Filter by the user-selected date range
Wdf_filtered = Wdf.loc[StartDate:EndDate]

# Extract wind data (direction and speed) and filter valid observations
WNDdf = Wdf_filtered['WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

# Initialize lists for Cartesian components
Xdata, Ydata = [], []

# Calculate Cartesian components of wind vectors
for _, row in WNDdf.iterrows():
    magnitude = np.float64(row[3])  # Wind speed
    direction = np.float64(row[0])  # Wind direction
    Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
    Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

# Add Cartesian components to the DataFrame
WNDdf[5], WNDdf[6] = Xdata, Ydata


# Create a plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Wind Vector")  # Added title for Wind Vector graph
ax.set_xlabel("Time")
#ax2.set_ylim(AOD_min,AOD_max)

ax.yaxis.set_label_position('right')  # Move label to the right
ax.yaxis.set_ticks_position('right')  # Move ticks to the right
ax2 = ax.twinx()
ax2.set_ylim(AOD_min,AOD_max)
ax2.yaxis.set_label_position('left')  # Move label to the left
ax2.yaxis.set_ticks_position('left')  # Move ticks to the left

maxWind = np.sqrt((WNDdf[6].loc[StartDate:EndDate].astype(float).max()/10)**2+
                  (WNDdf[5].loc[StartDate:EndDate].astype(float).max()/10)**2)
ax.set_ylim(0,maxWind)
# Resample the data according to the wind sample rate and plot the wind vectors
ax.quiver(
    WNDdf[5].resample(windSampleRate).mean().index,maxWind-1,  # X-axis (time)
    -WNDdf[5].resample(windSampleRate).mean().div(10),  # X-component of arrows
    -WNDdf[6].resample(windSampleRate).mean().div(10),  # Y-component of arrows
    color='b',
    label ="Wind Vector"
   

)
plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b',label="AOD 440nm")
plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g',label="500nm")
plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r',label="675nm")
#plt.legend()
plt.legend(loc='upper left', bbox_to_anchor=(-0.2, 1))
ax.get_yaxis().set_visible(True)

# Display the legend and adjust layout
ax.legend(loc='best')
#plt.tight_layout()

# Display the plot in Streamlit
#st.pyplot(fig)



#Temp
Tdf = Wdf.loc[StartDate:EndDate,'TMP'].str.split(pat=',', expand = True)

# Replacing +9999 values with nan, +9999 indicates "missing data"
Tdf.replace('+9999', np.nan, inplace = True)
fig, axes = plt.subplots(1,1, figsize=(16,9)) # plt.subplots(nrows, ncolumns, *args) # axs will be either an individual plot or an array of axes
try:
    ax = axes[0,0] # If axes is a 2D array of axes, then we'll use the first axis for this drawing.
except:
    try:
        ax = axes[0] # If axes is a 1D array of axes, then we'll use the first axis for this drawing.
    except:
        ax = axes # If axes is just a single axis then we'll use it directly.

# Initializing main Axis and plot
fig.autofmt_xdate() ## Note: With multiple plots, this removes the x-axis identifiers for plots not in the bottom row
ax.set_title('Turlock AOD Modesto Wind Speed, and Temperature ')
ax.grid(which='both',axis='both')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3, tz='US/Pacific'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Drawing the first pieces of data (AOD_500nm-Total) onto the graph
ax.set_ylabel('AOD_500nm')
aodHandle, = ax.plot(df_1.loc[StartDate:EndDate, 'AOD_500nm'].resample(SampleRate).mean(),'ok-',label= 'AOD_500nm', figure=fig) # handle, label = ax.plot()
ax.set_ylim(AOD_min,AOD_max) # Manually set the values for the y-limit of the plot

# Adding a new Axis sharing the same xaxis as before and drawing the second piece of data.
ax2 = ax.twinx()
ax2.spines.right.set_position(('axes', 1.05)) # Adjusting the position of the "spine" or y-axis to not overlap with the next pieces of data
ax2.set_ylabel('Temperature °C')
ax2.set_ylim(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).min()//1,
            Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10).max()//1+3) # Auto Calculatingtemperature
temperatureHandle, = ax2.plot(Tdf[0].loc[StartDate:EndDate].astype(float).resample(SampleRate).mean().div(10), '.r-',label='Temperature',figure=fig) # handle, label = ax2.plot()

# Adding a new Axis sharing the same xaxis as the previous two and drawing the thrid piece of data
ax3 = ax.twinx()
ax3.set_ylabel("Wind Mag m/s")
ax3.set_ylim(0,maxWind)
windHandle = ax3.quiver(WNDdf[5].resample(windSampleRate).mean().index,maxWind-1,
                -WNDdf[5].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                -WNDdf[6].loc[StartDate:EndDate].astype(float).resample(windSampleRate).mean().div(10),
                color='b',label='Wind Vector',width=0.005)

# Displaying the legend and Reorganizing everything to fit nicely
## Note: plot1 and plot2 are the handles for the data we created and plot3, the quiver, is handled differently.
plt.legend(handles = [aodHandle, temperatureHandle, windHandle], loc = 'best')
plt.tight_layout() # Adjusts the boundaries of the figures to ensure everything fits nicely. Can define pads as we we see fit.


#Display the plot in Streamlit
st.pyplot(fig)
