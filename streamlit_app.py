import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    # Convert PESEX_mean to reflect the correct percentage of males
    df['PESEX_mean'] = (2 - df['PESEX_mean']) * 100

    # Simplify and aggregate categorical variables annually
    # Race
    df['White'] = df['PTDTRACE_1']
    df['Black'] = df['PTDTRACE_2']
    df['Native American'] = df['PTDTRACE_3']
    df['Asian'] = df['PTDTRACE_4']
    df['Other Race'] = df[['PTDTRACE_' + str(i) for i in range(5, 27)]].sum(axis=1)

    # Education
    df['No Diploma'] = df[['PEEDUCA_' + str(i) for i in range(31, 39)] + ['PEEDUCA_-1']].sum(axis=1)
    df['High School Degree'] = df[['PEEDUCA_' + str(i) for i in range(39, 41)]].sum(axis=1)
    df['Higher Education Degree'] = df[['PEEDUCA_' + str(i) for i in range(41, 47)]].sum(axis=1)

    # Marital Status
    df['Married'] = df[['PEMARITL_' + str(i) for i in [1, 2, 5]]].sum(axis=1)
    df['Not Married'] = df[['PEMARITL_' + str(i) for i in [-1, 3, 4, 6]]].sum(axis=1)

    # Employment Status
    df['Employed'] = df[['PEMLR_' + str(i) for i in [1, 2]]].sum(axis=1)
    df['Unemployed'] = df[['PEMLR_' + str(i) for i in [-1, 3, 4, 6, 7]]].sum(axis=1)
    df['Retired'] = df['PEMLR_5']

    # Household Income
    df['Less than $5,000'] = df['HEFAMINC_1']
    df['$5,000 to $25,000'] = df[['HEFAMINC_' + str(i) for i in range(2, 8)]].sum(axis=1)
    df['$25,000 to $50,000'] = df[['HEFAMINC_' + str(i) for i in range(8, 12)]].sum(axis=1)
    df['$50,000 to $150,000'] = df[['HEFAMINC_' + str(i) for i in range(12, 16)]].sum(axis=1)
    df['$150,000 or more'] = df['HEFAMINC_16']

    # Aggregating categorical data by year
    aggregation_columns = ['White', 'Black', 'Native American', 'Asian', 'Other Race', 'No Diploma', 'High School Degree', 'Higher Education Degree', 'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired', 'Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', '$50,000 to $150,000', '$150,000 or more']
    annual_data = df.groupby(['Year', 'City'])[aggregation_columns].sum().reset_index()
    for col in aggregation_columns:
        annual_data[col] = annual_data[col] / annual_data[aggregation_columns].sum(axis=1) * 100

    return df, annual_data

data, annual_data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city for monthly data
city_data = data[data['City'] == selected_city]
# Filter data for annual aggregated data
annual_city_data = annual_data[annual_data['City'] == selected_city]

# Numeric variables
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

# Categorical count variables - Stacked Bar Charts for annual data
categorical_groups = {
    'Race': ['White', 'Black', 'Native American', 'Asian', 'Other Race'],
    'Education Level': ['No Diploma', 'High School Degree', 'Higher Education Degree'],
    'Marital Status': ['Married', 'Not Married'],
    'Employment Status': ['Employed', 'Unemployed', 'Retired'],
    'Household Income': ['Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', '$50,000 to $150,000', '$150,000 or more']
}

for group_name, categories in categorical_groups.items():
    st.subheader(f'{group_name} Distribution Over Time (Annual)')
    fig, ax = plt.subplots()
    for category in categories:
        ax.bar(city_data['Year'], city_data[category], bottom=city_data[categories[:categories.index(category)]].sum(axis=1), label=category)
    ax.set_title(f'Annual {group_name} Distribution')
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend(title='Categories')
    ax.grid(True)
    st.pyplot(fig)
