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
    
    # Recoding Race categories
    race_categories = {f'PTDTRACE_{i}': 'Other Race' for i in range(5, 27)}
    race_categories.update({
        'PTDTRACE_1': 'White',
        'PTDTRACE_2': 'Black',
        'PTDTRACE_3': 'Native American',
        'PTDTRACE_4': 'Asian'
    })
    for old_cat, new_cat in race_categories.items():
        df[new_cat] = df.get(new_cat, 0) + df.pop(old_cat)

    # Recoding Education categories
    df['No Diploma'] = df[[f'PEEDUCA_{i}' for i in list(range(31, 39)) + [-1]]].sum(axis=1)
    df['High School Degree'] = df[[f'PEEDUCA_{i}' for i in range(39, 41)]].sum(axis=1)
    df['Higher Education Degree'] = df[[f'PEEDUCA_{i}' for i in range(41, 47)]].sum(axis=1)

    # Recoding Marital Status categories
    df['Married'] = df[['PEMARITL_1', 'PEMARITL_2', 'PEMARITL_5']].sum(axis=1)
    df['Not Married'] = df[['PEMARITL_-1', 'PEMARITL_3', 'PEMARITL_4', 'PEMARITL_6']].sum(axis=1)

    # Recoding Employment Status categories
    df['Employed'] = df[['PEMLR_1', 'PEMLR_2']].sum(axis=1)
    df['Unemployed'] = df[['PEMLR_-1', 'PEMLR_3', 'PEMLR_4', 'PEMLR_6', 'PEMLR_7']].sum(axis=1)
    df['Retired'] = df['PEMLR_5']

    # Recoding Household Income categories
    df['Less than $5,000'] = df['HEFAMINC_1']
    df['$5,000 to $25,000'] = df[[f'HEFAMINC_{i}' for i in range(2, 8)]].sum(axis=1)
    df['$25,000 to $50,000'] = df[[f'HEFAMINC_{i}' for i in range(8, 12)]].sum(axis=1)
    df['$50,000 to $150,000'] = df[[f'HEFAMINC_{i}' for i in range(12, 16)]].sum(axis=1)
    df['$150,000 or more'] = df['HEFAMINC_16']

    # Dropping all individual PTDTRACE_ columns as they are now aggregated into broader categories
    df.drop(columns=[col for col in df if col.startswith('PTDTRACE_')], inplace=True)

    # Aggregating categorical data by year and converting to percentages
    categorical_cols = ['White', 'Black', 'Native American', 'Asian', 'Other Race', 
                        'No Diploma', 'High School Degree', 'Higher Education Degree', 
                        'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired', 
                        'Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', 
                        '$50,000 to $150,000', '$150,000 or more']

    yearly_data = df.groupby(['Year', 'City'])[categorical_cols].sum().reset_index()

    for col in categorical_cols:
        yearly_total = yearly_data[categorical_cols].sum(axis=1)
        yearly_data[col] = yearly_data[col] / yearly_total * 100

    return df, yearly_data

data, yearly_data = load_data()

# Sidebar for selecting the city
selected_city = st.sidebar.selectbox('Select a City:', yearly_data['City'].unique())

# Filter data based on selected city for monthly numeric data and annual categorical data
monthly_city_data = data[data['City'] == selected_city]
annual_city_data = yearly_data[yearly_data['City'] == selected_city]

# Display monthly numeric data
st.header(f"Monthly Data for {selected_city}")
st.subheader("Average Age Over Time")
st.line_chart(monthly_city_data.set_index('Date')['PRTAGE_mean'])

st.subheader("Percentage of Male Population Over Time")
st.line_chart(monthly_city_data.set_index('Date')['PESEX_mean'])

# Display annual categorical data as stacked bar charts
st.header(f"Annual Categorical Data for {selected_city}")
categorical_cols = ['White', 'Black', 'Native American', 'Asian', 'Other Race', 
                    'No Diploma', 'High School Degree', 'Higher Education Degree', 
                    'Married', 'Not Married', 'Employed', 'Unemployed', 'Retired', 
                    'Less than $5,000', '$5,000 to $25,000', '$25,000 to $50,000', 
                    '$50,000 to $150,000', '$150,000 or more']

fig, ax = plt.subplots()
bottom = np.zeros(len(annual_city_data['Year']))
for col in categorical_cols:
    ax.bar(annual_city_data['Year'], annual_city_data[col], bottom=bottom, label=col)
    bottom += annual_city_data[col].values
ax.set_ylabel('Percentage')
ax.set_title('Categorical Data Distribution by Year')
ax.legend()
st.pyplot(fig)
