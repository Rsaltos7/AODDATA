import numpy as np  # Import NumPy for numerical operations
import pandas as pd  # Import pandas a data manipulation library also creates shorcut pd 
import matplotlib.pyplot as plt  # Import pyplot for plotting and makes shorcut py
import matplotlib.dates as mdates  # Imports matplotlib.dates for handling dates in plots and makes short cut mdates
import matplotlib.patches as mpatches  # Import patches for drawing shapes shorcuts it to mpatches
import csv  # Import CSV module for reading CSV files

# Define filenames for the data files
filename = '20190101_20191231_Modesto (1).tot_lev20'  # AERONET data file this case for modesto
windfile = 'Modesto_Wind_2019_Jan_Dec_72492623258.csv'  # Wind data file for modesto
StartDate = '2016-01-01 00:00:00'  # Start date for specific data points
EndDate = '2023-12-31 23:59:59'  # End date for specific data points

# Getting the name of the site from the first row of the AERONET data file
with open(filename) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')  # Create a CSV reader
    next(csvreader)  # Skip the first line (header)
    for line in csvreader:  # Read the next line
        siteName = line[0]  # Extract the site name
        break  # Exit the loop after getting the first line
print(siteName)  # Print the site name

# Load the AERONET data and convert datetime to US/Pacific timezone
df = pd.read_csv(filename, skiprows=6, parse_dates={'datetime': [0, 1]})  # Read AERONET data, combining first two columns into a datetime column
# Convert the combined datetime to UTC and then to US/Pacific timezone
datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')  
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
df.set_index(datetime_pac, inplace=True)  # Set the new datetime index for the DataFrame

# Load NOAA wind data and convert datetime to US/Pacific timezone
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)  # Read wind data, parsing the datetime column
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')  # Convert to UTC
datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')  # Convert to US/Pacific
Wdf.set_index(datetime_pac, inplace=True)  # Set the new datetime index for the wind DataFrame

# Create a copy of wind data and filter for valid wind speed and direction
WNDdf = Wdf.loc[StartDate:EndDate, 'WND'].str.split(pat=',', expand=True)  # Split 'WND' column into separate columns
# Filter for valid wind speed and direction
WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Keep only rows where the 4th column equals '5' (valid wind speed)
WNDdf = WNDdf.loc[WNDdf[1] == '5']  # Keep only rows where the 1st column equals '5' (valid wind direction)

# Replace -999 with NaN for AOD Total wavelengths in the AERONET data
AODTotalColumns = range(3, 173, 8)  # Define the range for AOD total columns
for iWaveLength in df.columns[AODTotalColumns]:
    df[iWaveLength].replace(-999.0, np.nan, inplace=True)  # Replace invalid AOD values with NaN

# Print out the available AOD Total columns
print(df.columns[AODTotalColumns], '\tSize: ', len(df.columns[AODTotalColumns]))

# Find the wavelength with the largest number of weekly entries
largest = [0, '']  # Initialize a list to track the largest entry count and corresponding wavelength
for i in df.columns[AODTotalColumns]:  
    if (df[i].mean() > 0):  # Check if the mean AOD is greater than zero
        # Calculate the maximum weekly entries
        if df.loc[StartDate:EndDate, iWaveLength].dropna().groupby([pd.Grouper(freq='W')]).size().max() > largest[0]:
            largest[0], largest[1] = df.loc[StartDate:EndDate, iWaveLength].dropna().groupby([pd.Grouper(freq='W')]).size().max(), i
print('The Wavelength ', largest[1], 'has the largest number of weekly entries at ', largest[0], ' entries.')  # Print the result
# Create the plot for AOD data availability
ax = plt.figure(figsize=(16 * .65, 9 * .65)).add_subplot(111)  # Set figure size and create a subplot
ax.set_title(siteName + ' Weekly AOD-Total Data Availability for ' + filename[13:17])  # Set the title of the plot

# Dynamically Adjusting Colors to increase the potential number of colors usable in the graph
vaildWavelengthsCount = 0  # Initialize count of valid wavelengths
for i in df.columns[AODTotalColumns]:
    if (df[i].mean() > 0):  # Count valid wavelengths
        vaildWavelengthsCount += 1

# Set color map for the plot
cm = plt.get_cmap('gist_rainbow')  # Get a rainbow color map
ax.set_prop_cycle(color=[cm(1. * i / vaildWavelengthsCount) for i in range(vaildWavelengthsCount)])  # Apply color cycle

# Plot the data availability on the graph
count, handlesList = 0, []  # Initialize count and handles for legend
# Plot wind data
dfGroup = WNDdf.loc[StartDate:EndDate, 1].dropna().groupby([pd.Grouper(freq='W')]).size()  # Group wind data by week
wind = ax.plot(dfGroup[dfGroup <= 24 * 7] / (24 * 7) * 100, '.', label='Wind', markersize=vaildWavelengthsCount * 1.5, c='k')  # Plot valid wind data
handlesList.append(wind[0])  # Add wind plot to handles list
ax.plot(dfGroup[dfGroup > 24 * 7] / (24 * 7) * 100, '.', label='Wind', markersize=vaildWavelengthsCount * 1.5, c='k')  # Plot wind data exceeding 100%

# Loop through each valid wavelength and plot AOD data
for iWaveLength in df.columns[AODTotalColumns]:  
    if (df[iWaveLength].mean() > 0):  # Check if the mean AOD is valid
        dfGroup = df.loc[StartDate:EndDate, iWaveLength].dropna().groupby([pd.Grouper(freq='W')]).size()  # Group AOD data by week
        dots = ax.plot(dfGroup[dfGroup <= 4 * 12 * 7] / (4 * 12 * 7) * 100, '.', label=iWaveLength, markersize=vaildWavelengthsCount * 3 - count * 2)  # Plot valid AOD data
        handlesList.append(dots[0])  # Add AOD plot to handles list
        # Plot data exceeding 100% availability on the 100% line
        ax.plot(dfGroup[dfGroup > 4 * 12 * 7] / dfGroup[dfGroup > 4 * 12 * 7] * 100, '.', markersize=vaildWavelengthsCount * 3 - count * 2, c=dots[0].get_color())  
        print('Dropped ', len(df.loc[StartDate:EndDate, iWaveLength]) - len(df.loc[StartDate:EndDate, iWaveLength].dropna()), ' NaN entries from ', iWaveLength)  # Print number of NaN entries dropped
        count += 1  # Increment the count of plotted wavelengths
# Formatting the graph for better visualization
plt.gcf().autofmt_xdate()  # Automatically format x-axis dates for better readability
plt.grid(which='major', axis='both')  # Add grid lines for major ticks
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7, tz='US/Pacific'))  # Set major x-axis ticks to every week
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=24, tz='US/Pacific'))  # Set minor x-axis ticks to every day
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # Format the major x-axis date labels
plt.ylim(0, 100)  # Set y-axis limits from 0 to 100%
plt.ylabel('Availability %')  # Set y-axis label
plt.legend(handles=handlesList, loc='best')  # Create legend with plotted handles
plt.tight_layout()  # Adjust layout to fit elements

# Optional: Save the plot to a file as a .png
