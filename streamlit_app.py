import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])

    # Correcting PESEX_mean
    df['PESEX_mean'] = (df['PESEX_mean'] - 1) * 100  # Convert to percentage of males

    # Group data by Year for categorical variables
    df['Year'] = df['Date'].dt.year
    categorical_columns = [col for col in df.columns if 'PTDTRACE_' in col or 'PEEDUCA_' in col or 'PEMARITL_' in col or 'PEMLR_' in col or 'HEFAMINC_' in col]
    df[categorical_columns] = df.groupby('Year')[categorical_columns].transform('sum')

    # Reducing categories for each categorical variable
    # Race
    df['White'] = df['PTDTRACE_1']
    df['Black'] = df['PTDTRACE_2']
    df['Native American'] = df['PTDTRACE_3']
    df['Asian'] = df['PTDTRACE_4']
    df['Other Race'] = df[[f'PTDTRACE_{i}' for i in range(5, 27)]].sum(axis=1)

    # Education
    df['No Diploma'] = df[[f'PEEDUCA_{i}' for i in range(31, 39)] + ['PEEDUCA_-1']].sum(axis=1)
    df['High School Degree'] = df[['PEEDUCA_39', 'PEEDUCA_40']].sum(axis=1)
    df['Higher Education'] = df[[f'PEEDUCA_{i}' for i in range(41, 47)]].sum(axis=1)

    # Marital Status
    df['Married'] = df[['PEMARITL_1', 'PEMARITL_2', 'PEMARITL_5']].sum(axis=1)
    df['Not Married'] = df[['PEMARITL_-1', 'PEMARITL_3', 'PEMARITL_4', 'PEMARITL_6']].sum(axis=1)

    # Employment Status
    df['Employed'] = df[['PEMLR_1', 'PEMLR_2']].sum(axis=1)
    df['Unemployed'] = df[['PEMLR_-1', 'PEMLR_3', 'PEMLR_4', 'PEMLR_6', 'PEMLR_7']].sum(axis=1)
    df['Retired'] = df['PEMLR_5']

    # Household Income
    df['Less than 5,000 USD'] = df['HEFAMINC_1']
    df['Between 5,000 and 25,000 USD'] = df[[f'HEFAMINC_{i}' for i in range(2, 8)]].sum(axis=1)
    df['Between 25,000 and 50,000 USD'] = df[[f'HEFAMINC_{i}' for i in range(8, 12)]].sum(axis=1)
    df['Between 50,000 and 150,000 USD'] = df[[f'HEFAMINC_{i}' for i in range(12, 16)]].sum(axis=1)
    df['150,000 USD or More'] = df['HEFAMINC_16']

    return df.drop(columns=categorical_columns + ['Date'])  # Drop original categorical columns

data = load_data()

selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())
city_data = data[data['City'] == selected_city]

st.title('Demographic Trends Analysis')
st.write(f"Data visualization for {selected_city}")

st.header("Average Age Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Year'], city_data['PRTAGE_mean'], marker='o')
ax.set_title('Average Age Over Time')
ax.set_xlabel('Year')
ax.set_ylabel('Average Age')
ax.grid(True)
st.pyplot(fig)

st.header("Percentage of Male Population Over Time")
fig, ax = plt.subplots()
ax.plot(city_data['Year'], city_data['PESEX_mean'], marker='o', color='b')
ax.set_title('Percentage of Male Population Over Time')
ax.set_xlabel('Year')
ax.set_ylabel('Percentage of Males')
ax.grid(True)
st.pyplot(fig)

categorical_vars = ['White', 'Black', 'Native American', 'Asian', 'Other Race', 'No Diploma', 'High School Degree', 'Higher Education', 'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired']
for var in categorical_vars:
    st.subheader(f'{var} Distribution Over Time')
    fig, ax = plt.subplots()
    city_data.set_index('Year')[var].plot(kind='bar', stacked=True, ax=ax)
    ax.set_title(f'{var} Distribution Over Time')
    ax.set_ylabel('Counts')
    st.pyplot(fig)
