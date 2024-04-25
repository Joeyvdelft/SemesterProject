import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and cache data
@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['PESEX_mean'] = (df['PESEX_mean'] - 1) * -100  # Convert to percentage of males
    return df

data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]

# Header
st.title('Demographic Trends Analysis')
st.write(f"Data visualization for {selected_city}")

# Numeric variable
st.header("Average Age Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Date'], city_data['PRTAGE_mean'], marker='o')
ax.set_title('Average Age Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Average Age')
ax.grid(True)
st.pyplot(fig)

# Gender ratio
st.header("Percentage of Male Population Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Date'], city_data['PESEX_mean'], marker='o', color='b')
ax.set_title('Percentage of Male Population Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Percentage of Males')
ax.grid(True)
st.pyplot(fig)

# Categorical count variables
categorical_vars = [col for col in data.columns if 'PTDTRACE_' in col or 'PEEDUCA_' in col or 'PEMARITL_' in col or 'PEMLR_' in col or 'HEFAMINC_' in col]
for var in categorical_vars:
    st.subheader(f'Distribution of {var} Over Time')
    fig, ax = plt.subplots()
    for cat in sorted(city_data[var].unique()):
        subset = city_data[city_data[var] == cat]
        ax.plot(subset['Date'], subset[var], marker='o', label=f'Category {cat}')
    ax.set_title(f'{var} over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Counts')
    ax.legend(title='Category')
    ax.grid(True)
    st.pyplot(fig)
