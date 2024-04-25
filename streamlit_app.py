import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and cache data
@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['PESEX_mean'] = df['PESEX_mean'] * 100  # Convert to percentage of males
    return df

data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]

# Header
st.title('Demographic Trends Analysis')
st.write(f"Data visualization for {selected_city}")

# Numeric variable - Mean Age
st.header("Average Age Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Date'], city_data['PRTAGE_mean'], marker='o')
ax.set_title('Average Age Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Average Age')
ax.grid(True)
st.pyplot(fig)

# Gender ratio - Corrected percentage calculation
st.header("Percentage of Male Population Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Date'], city_data['PESEX_mean'], marker='o', color='b')
ax.set_title('Percentage of Male Population Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Percentage of Males')
ax.grid(True)
st.pyplot(fig)

# Categorical count variables - Stacked Bar Charts
categorical_vars = [col for col in data.columns if 'PTDTRACE_' in col or 'PEEDUCA_' in col or 'PEMARITL_' in col or 'PEMLR_' in col or 'HEFAMINC_' in col]
for var_prefix in ['PTDTRACE_', 'PEEDUCA_', 'PEMARITL_', 'PEMLR_', 'HEFAMINC_']:
    categories = [col for col in categorical_vars if col.startswith(var_prefix)]
    st.subheader(f'Distribution of {var_prefix[:-1]} Categories Over Time')
    fig, ax = plt.subplots()
    for category in categories:
        ax.bar(city_data['Date'], city_data[category], label=category, bottom=city_data[categories[:categories.index(category)]].sum(axis=1))
    ax.set_title(f'{var_prefix[:-1]} Distribution Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Counts')
    ax.legend(title='Categories')
    ax.grid(True)
    st.pyplot(fig)
