import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

@st.cache
def load_data():
    url = 'https://raw.githubusercontent.com/Joeyvdelft/SemesterProject/File/Processed.Demographic.Data.csv'
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    # Adjusting PESEX_mean to reflect the correct percentage of males
    df['PESEX_mean'] = (2 - df['PESEX_mean']) * 100
    
    # Create aggregated DataFrame for categorical variables
    categories = {
        'White': 'PTDTRACE_1',
        'Black': 'PTDTRACE_2',
        'Native American': 'PTDTRACE_3',
        'Asian': 'PTDTRACE_4',
        'Other Race': [f'PTDTRACE_{i}' for i in range(5, 27)],
        'No Diploma': [f'PEEDUCA_{i}' for i in range(31, 39)] + ['PEEDUCA_-1'],
        'High School Degree': [f'PEEDUCA_{i}' for i in range(39, 41)],
        'Higher Education Degree': [f'PEEDUCA_{i}' for i in range(41, 47)],
        'Married': ['PEMARITL_1', 'PEMARITL_2', 'PEMARITL_5'],
        'Not Married': ['PEMARITL_-1', 'PEMARITL_3', 'PEMARITL_4', 'PEMARITL_6'],
        'Employed': ['PEMLR_1', 'PEMLR_2'],
        'Unemployed': ['PEMLR_-1', 'PEMLR_3', 'PEMLR_4', 'PEMLR_6', 'PEMLR_7'],
        'Retired': 'PEMLR_5',
        'Less than 5,000': 'HEFAMINC_1',
        'Between 5,000 and 25,000': [f'HEFAMINC_{i}' for i in range(2, 8)],
        'Between 25,000 and 50,000': [f'HEFAMINC_{i}' for i in range(8, 12)],
        'Between 50,000 and 150,000': [f'HEFAMINC_{i}' for i in range(12, 16)],
        '150,000 or More': 'HEFAMINC_16'
    }
    
    for category, cols in categories.items():
        if isinstance(cols, list):  # If the category is represented by multiple columns
            df[category] = df[cols].sum(axis=1)
        else:
            df[category] = df[cols]

    # Drop the original columns to avoid duplication
    df.drop(columns=[col for col in df.columns if 'PTDTRACE_' in col or 'PEEDUCA_' in col or 'PEMARITL_' in col or 'PEMLR_' in col or 'HEFAMINC_' in col], inplace=True)

    # Group by Year and City, summing up the new categories and convert counts to percentages
    categorical_cols = list(categories.keys())
    yearly_data = df.groupby(['Year', 'City'])[categorical_cols].sum().reset_index()
    yearly_counts = yearly_data[categorical_cols].sum(axis=1)
    for col in categorical_cols:
        yearly_data[col] = yearly_data[col] / yearly_counts * 100

    return df, yearly_data

# Load monthly and yearly data
data, yearly_data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', data['City'].unique())

# Filter data based on selected city for monthly and yearly data
city_data = data[data['City'] == selected_city]
annual_city_data = yearly_data[yearly_data['City'] == selected_city]

# Numeric variables plots
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

# Plotting the categorical variables
category_mappings = {
    'Race': ['White', 'Black', 'Native American', 'Asian', 'Other Race'],
    'Education Level': ['No Diploma', 'High School Degree', 'Higher Education Degree'],
    'Marital Status': ['Married', 'Not Married'],
    'Employment Status': ['Employed', 'Unemployed', 'Retired'],
    'Household Income in $': ['Less than 5,000', 'Between 5,000 and 25,000', 'Between 25,000 and 50,000',
                         'Between 50,000 and 150,000', '150,000 or More']
}

st.header(f"Annual Categorical Data Distribution for {selected_city}")
for category_name, columns in category_mappings.items():
    st.subheader(f"{category_name} Distribution Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(annual_city_data['Year']))
    for col in columns:
        ax.bar(annual_city_data['Year'], annual_city_data[col], bottom=bottom, label=col)
        bottom += annual_city_data[col]
    ax.set_xlabel('Year')
    ax.set_ylabel('Percentage')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
