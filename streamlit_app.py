import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    # Correct the PESEX_mean to reflect the correct percentage of males
    df['PESEX_mean'] = (df['PESEX_mean'] - 1) * -100 - 100

    # Monthly data for mean age and gender
    monthly_data = df[['Date', 'City', 'PRTAGE_mean', 'PESEX_mean']].copy()

    # Aggregate other data annually and recode variables
    # Recoding categorical variables
    race_columns = [f'PTDTRACE_{i}' for i in range(1, 27)]
    education_columns = [f'PEEDUCA_{i}' for i in range(31, 47)] + ['PEEDUCA_-1']
    marital_columns = [f'PEMARITL_{i}' for i in range(1, 7)] + ['PEMARITL_-1']
    employment_columns = [f'PEMLR_{i}' for i in range(1, 8)] + ['PEMLR_-1']
    income_columns = [f'HEFAMINC_{i}' for i in range(1, 17)]

    df['White'] = df['PTDTRACE_1']
    df['Black'] = df['PTDTRACE_2']
    df['Native American'] = df['PTDTRACE_3']
    df['Asian'] = df['PTDTRACE_4']
    df['Other Race'] = df[race_columns[4:]].sum(axis=1)

    df['No Diploma'] = df[education_columns[:8]].sum(axis=1)
    df['High School Degree'] = df[education_columns[8:10]].sum(axis=1)
    df['Higher Education Degree'] = df[education_columns[10:]].sum(axis=1)

    df['Married'] = df[['PEMARITL_1', 'PEMARITL_2', 'PEMARITL_5']].sum(axis=1)
    df['Not Married'] = df[['PEMARITL_-1', 'PEMARITL_3', 'PEMARITL_4', 'PEMARITL_6']].sum(axis=1)

    df['Employed'] = df[['PEMLR_1', 'PEMLR_2']].sum(axis=1)
    df['Unemployed'] = df[['PEMLR_-1', 'PEMLR_3', 'PEMLR_4', 'PEMLR_6', 'PEMLR_7']].sum(axis=1)
    df['Retired'] = df['PEMLR_5']

    df['Less than $5,000'] = df['HEFAMINC_1']
    df['$5,000 to $25,000'] = df[income_columns[1:7]].sum(axis=1)
    df['$25,000 to $50,000'] = df[income_columns[7:11]].sum(axis=1)
    df['$50,000 to $150,000'] = df[income_columns[11:15]].sum(axis=1)
    df['$150,000 or More'] = df['HEFAMINC_16']

    # Group by Year and City, summing up the new categories
    yearly_data = df.groupby(['Year', 'City']).sum().reset_index()
    for col in ['White', 'Black', 'Native American', 'Asian', 'Other Race', 'No Diploma', 'High School Degree', 
                'Higher Education Degree', 'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired', 
                'Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', '$50,000 to $150,000', '$150,000 or More']:
        yearly_data[col] = yearly_data[col] / yearly_data[col].sum() * 100  # Convert counts to percentages

    # Combine monthly and yearly data
    final_data = monthly_data.merge(yearly_data, on=['Year', 'City'])

    return final_data

data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]

# Header
st.title('Demographic Trends Analysis')
st.write(f"Data visualization for {selected_city}")

# Numeric variables
st.header("Monthly Average Age and Gender Ratio")
fig, axs = plt.subplots(2, figsize=(10, 10))
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

# Categorical count variables - Stacked Bar Charts (Annual)
st.header("Annual Categorical Distribution")
categories = {
    'Race': ['White', 'Black', 'Native American', 'Asian', 'Other Race'],
    'Education Level': ['No Diploma', 'High School Degree', 'Higher Education Degree'],
    'Marital Status': ['Married', 'Not Married'],
    'Employment Status': ['Employed', 'Unemployed', 'Retired'],
    'Household Income': ['Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', '$50,000 to $150,000', '$150,000 or More']
}
for group_name, cats in categories.items():
    fig, ax = plt.subplots()
    bottom = None
    for category in cats:
        ax.bar(city_data['Year'], city_data[category], bottom=bottom, label=category)
        bottom = city_data[category] if bottom is None else bottom + city_data[category]
    ax.set_title(f'{group_name} Distribution Over Time (Annual)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend(title='Categories')
    ax.grid(True)
    st.pyplot(fig)
