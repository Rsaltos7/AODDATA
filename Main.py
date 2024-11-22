import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title and file uploader
st.title("Temperature Data Visualization")
uploaded_file = st.file_uploader("Upload the processed temperature data CSV", type="csv")

if uploaded_file:
    # Load the data
    data = pd.read_csv(uploaded_file, parse_dates=['DATE'])
    
    # Display data preview
    st.write("### Data Preview", data.head())
    
    # Plot the data
    st.write("### Temperature Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['DATE'], data['TEMPERATURE'], label="Temperature", color='orange')
    ax.set_title("Daily Temperature Trends")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("Please upload a CSV file to proceed.")
