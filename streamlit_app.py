import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to load and cache data
@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    # Correcting male percentage calculation
    df['PESEX_mean'] = (df['PESEX_mean'] - 1) * -100

    # Simplifying and aggregating categories
    race_categories = {**{f'PTDTRACE_{i}': 'Other' for i in range(5, 27)}, 'PTDTRACE_1': 'White', 'PTDTRACE_2': 'Black', 'PTDTRACE_3': 'Native American', 'PTDTRACE_4': 'Asian'}
    edu_categories = {**{f'PEEDUCA_{i}': 'No Diploma' for i in range(31, 39)}, **{f'PEEDUCA_{i}': 'High School Degree' for i in range(39, 41)}, **{f'PEEDUCA_{i}': 'Higher Education Degree' for i in range(41, 47)}}
    marital_categories = {**{f'PEMARITL_{i}': 'Not Married' for i in [-1, 3, 4, 6]}, 'PEMARITL_1': 'Married', 'PEMARITL_2': 'Married', 'PEMARITL_5': 'Married'}
    employment_categories = {**{f'PEMLR_{i}': 'Unemployed' for i in [-1, 3, 4, 6, 7]}, 'PEMLR_1': 'Employed', 'PEMLR_2': 'Employed', 'PEMLR_5': 'Retired'}
    income_categories = {'HEFAMINC_1': 'Less than 5,000 USD', **{f'HEFAMINC_{i}': 'Between 5,000 and 25,000 USD' for i in range(2, 8)}, **{f'HEFAMINC_{i}': 'Between 25,000 and 50,000 USD' for i in range(8, 12)}, **{f'HEFAMINC_{i}': 'Between 50,000 and 150,000 USD' for i in range(12, 16)}, 'HEFAMINC_16': '150,000 USD or More'}
    
    for col, mapping in zip(['PTDTRACE', 'PEEDUCA', 'PEMARITL', 'PEMLR', 'HEFAMINC'], [race_categories, edu_categories, marital_categories, employment_categories, income_categories]):
        categories = [col + '_' + str(key) for key, value in mapping.items()]
        df[col] = df[categories].dot(df[categories].columns + ',').str.rstrip(',')
        for k, v in mapping.items():
            df[col] = df[col].str.replace(k, v, regex=False)
        df[col] = df[col].str.rstrip(',')

    # Aggregate yearly data for categorical variables
    categorical_data = df.groupby(['Year', 'City', 'PTDTRACE', 'PEEDUCA', 'PEMARITL', 'PEMLR', 'HEFAMINC']).size().reset_index(name='counts')
    categorical_data['percentage'] = categorical_data.groupby(['Year', 'City'])['counts'].transform(lambda x: x / x.sum() * 100)
    return df, categorical_data

data, categorical_data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]
categorical_city_data = categorical_data[categorical_data['City'] == selected_city]

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
st.header("Categorical Variable Distributions by Year")
for var in ['PTDTRACE', 'PEEDUCA', 'PEMARITL', 'PEMLR', 'HEFAMINC']:
    st.subheader(f'{var} Distribution Over Time')
    fig, ax = plt.subplots()
    pivot_df = categorical_city_data.pivot(index='Year', columns=var, values='percentage')
    pivot_df.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title(f'{var} Distribution Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend(title='Categories')
    st.pyplot(fig)
