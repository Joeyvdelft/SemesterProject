
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

data = load_data()

# Sidebar - City selection
city = st.sidebar.selectbox('Select City:', data['City'].unique())

# Main panel
st.title(f'Demographic Data Trends for {city}')
filtered_data = data[data['City'] == city]

# Plotting
for var in {variables}:
    st.subheader(f'Trend of {var}')
    fig, ax = plt.subplots()
    ax.plot(filtered_data['Date'], filtered_data[var], marker='o')
    ax.set_xlabel('Date')
    ax.set_ylabel(var)
    ax.set_title(f'Trend of {var} over Time')
    ax.grid(True)
    st.pyplot(fig)
