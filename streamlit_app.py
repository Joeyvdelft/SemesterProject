import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    # Adjusting PESEX_mean to reflect the correct percentage of males
    df['PESEX_mean'] = (2 - df['PESEX_mean']) * 100

    # Simplify and group categorical variables
    # Race
    df['White'] = df['PTDTRACE_1']
    df['Black'] = df['PTDTRACE_2']
    df['Native American'] = df['PTDTRACE_3']
    df['Asian'] = df['PTDTRACE_4']
    df['Other Race'] = df[[f'PTDTRACE_{i}' for i in range(5, 27)]].sum(axis=1)

    # Education
    df['No Diploma'] = df[[f'PEEDUCA_{i}' for i in list(range(31, 39)) + [-1]]].sum(axis=1)
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
    df['$5,000 to $25,000'] = df[[f'HEFAMINC_{i}' for i in range(2, 8)]].sum(axis=1)
    df['$25,000 to $50,000'] = df[[f'HEFAMINC_{i}' for i in range(8, 12)]].sum(axis=1)
    df['$50,000 to $150,000'] = df[[f'HEFAMINC_{i}' for i in range(12, 16)]].sum(axis=1)
    df['$150,000 or more'] = df['HEFAMINC_16']

    # Annual aggregation of categorical data
    aggregation_columns = ['White', 'Black', 'Native American', 'Asian', 'Other Race', 
                           'No Diploma', 'High School Degree', 'Higher Education Degree', 
                           'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired', 
                           'Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', 
                           '$50,000 to $150,000', '$150,000 or more']
    yearly_data = df.groupby(['Year', 'City'])[aggregation_columns].sum().reset_index()
    
    # Convert counts to percentages
    for col in aggregation_columns:
        yearly_data[col] = yearly_data[col] / yearly_data[aggregation_columns].sum(axis=1) * 100

    return df, yearly_data

data, yearly_data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city
city_data = data[data['City'] == selected_city]
annual_city_data = yearly_data[yearly_data['City'] == selected_city]

# Displaying Numeric variables
st.header("Average Age and Gender Ratio Over Time")
fig, ax1 = plt.subplots()
ax1.plot(city_data['Date'], city_data['PRTAGE_mean'], marker='o', color='blue', label='Average Age')
ax1.set_xlabel('Date')
ax1.set_ylabel('Average Age', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(True)

ax2 = ax1.twinx()
ax2.plot(city_data['Date'], city_data['PESEX_mean'], marker='o', color='red', label='Percentage of Males')
ax2.set_ylabel('Percentage of Males', color='red')
ax2.tick_params(axis='y', labelcolor='red')

fig.tight_layout()
st.pyplot(fig)

# Displaying Categorical variables - Annual Stacked Bar Charts
st.header("Annual Categorical Data Distribution")
for category in ['Race', 'Education Level', 'Marital Status', 'Employment Status', 'Household Income']:
    fig, ax = plt.subplots()
    categories = [col for col in annual_city_data.columns if col.startswith(category)]
    bottom = None
    for cat in categories:
        ax.bar(annual_city_data['Year'], annual_city_data[cat], bottom=bottom, label=cat.replace(category + ' ', ''))
        bottom = annual_city_data[cat] if bottom is None else bottom + annual_city_data[cat]
    ax.set_title(f'{category} Distribution Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend(title='Categories')
    ax.grid(True)
    st.pyplot(fig)
