import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Correct calculation for PESEX_mean to reflect the percentage of males
    df['PESEX_mean'] = (2 - df['PESEX_mean']) * 100

    # Recoding and summing for yearly categorical data, keeping monthly data for mean variables
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month  # Retain Month for monthly data plotting

    # Aggregating monthly data into yearly and recoding variables
    # Race
    race_columns = [f'PTDTRACE_{i}' for i in range(1, 27)]
    df['White'] = df['PTDTRACE_1']
    df['Black'] = df['PTDTRACE_2']
    df['Native American'] = df['PTDTRACE_3']
    df['Asian'] = df['PTDTRACE_4']
    df['Other Race'] = df[race_columns[4:]].sum(axis=1)
    
    # Education
    df['No Diploma'] = df[[f'PEEDUCA_{i}' for i in range(31, 39)] + ['PEEDUCA_-1']].sum(axis=1)
    df['High School Degree'] = df[[f'PEEDUCA_{i}' for i in range(39, 41)]].sum(axis=1)
    df['Higher Education Degree'] = df[[f'PEEDUCA_{i}' for i in range(41, 47)]].sum(axis=1)
    
    # Marital Status
    df['Married'] = df[['PEMARITL_1', 'PEMARITL_2', 'PEMARITL_5']].sum(axis=1)
    df['Not Married'] = df[['PEMARITL_-1', 'PEMARITL_3', 'PEMARITL_4', 'PEMARITL_6']].sum(axis=1)
    
    # Employment Status
    df['Employed'] = df[['PEMLR_1', 'PEMLR_2']].sum(axis=1)
    df['Unemployed'] = df[['PEMLR_-1', 'PEMLR_3', 'PEMLR_4', 'PEMLR_6', 'PEMLR_7']].sum(axis=1)
    df['Retired'] = df['PEMLR_5']
    
    # Household Income
    df['Less than $5,000'] = df['HEFAMINC_1']
    df['Between $5,000 and $25,000'] = df[[f'HEFAMINC_{i}' for i in range(2, 8)]].sum(axis=1)
    df['Between $25,000 and $50,000'] = df[[f'HEFAMINC_{i}' for i in range(8, 12)]].sum(axis=1)
    df['Between $50,000 and $150,000'] = df[[f'HEFAMINC_{i}' for i in range(12, 16)]].sum(axis=1)
    df['$150,000 or More'] = df['HEFAMINC_16']
    
    # Aggregating categorical data by Year and City
    group_cols = ['Year', 'City'] + [col for col in df.columns if 'Race' in col or 'Education' in col or 'Marital' in col or 'Employment' in col or 'Income' in col]
    categorical_df = df[group_cols].groupby(['Year', 'City']).sum().reset_index()
    
    # Combine monthly data for mean variables separately
    mean_cols = ['Date', 'City', 'PRTAGE_mean', 'PESEX_mean']
    mean_df = df[mean_cols].copy()

    # Merge categorical yearly data with monthly mean data
    df = pd.merge(mean_df, categorical_df, on=['Year', 'City'])

    # Normalize categorical data to percentages
    cat_columns = df.columns[df.columns.str.contains('Race|Education|Marital|Employment|Income')]
    df[cat_columns] = df[cat_columns].div(df[cat_columns].sum(axis=1), axis=0) * 100

    return df

data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]

# Header
st.title('Demographic Trends Analysis')
st.write(f"Data visualization for {selected_city}")

# Numeric variables: Monthly data
st.header("Monthly Average Age and Gender Ratio")
fig, axs = plt.subplots(2, 1, figsize=(10, 10))
axs[0].plot(city_data['Date'], city_data['PRTAGE_mean'], marker='o')
axs[0].set_title('Average Age Over Time')
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Average Age')
axs[1].plot(city_data['Date'], city_data['PESEX_mean'], marker='o', color='b')
axs[1].set_title('Percentage of Male Population Over Time')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Percentage of Males')
for ax in axs:
    ax.grid(True)
st.pyplot(fig)

# Categorical count variables - Stacked Bar Charts
categorical_groups = {
    'Race': ['White', 'Black', 'Native American', 'Asian', 'Other Race'],
    'Education Level': ['No Diploma', 'High School Degree', 'Higher Education Degree'],
    'Marital Status': ['Married', 'Not Married'],
    'Employment Status': ['Employed', 'Unemployed', 'Retired'],
    'Household Income': ['Less than $5,000', 'Between $5,000 and $25,000', 'Between $25,000 and $50,000', 'Between $50,000 and $150,000', '$150,000 or More']
}

for group_name, categories in categorical_groups.items():
    st.subheader(f'{group_name} Distribution Over Time')
    fig, ax = plt.subplots()
    bottom = None
    for category in categories:
        ax.bar(city_data['Year'], city_data[category], bottom=bottom, label=category)
        bottom = city_data[category] if bottom is None else bottom + city_data[category]
    ax.set_title(f'{group_name} Distribution Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend(title='Categories')
    ax.grid(True)
    st.pyplot(fig)
