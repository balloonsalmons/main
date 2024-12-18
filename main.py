import streamlit as st
import pandas as pd

from pandas import Series, DataFrame
st.title('Yield Curve Dashboard')
st.subheader('Input CSV')
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader('DataFrame')

    with st.expander('About the data'):
        st.write('This is a list of all current brokered Certificates of Deposit (CDs) available through Fidelity')


    # Create and clean up the df
    # df = pd.read_csv("Fidelity_FixedIncome_SearchResults.csv")
    # Only care about these columns

    df = df[['Cusip', 'Description', 'Coupon', 'Coupon Frequency',
       'Maturity Date', 'Ask Yield to Worst',
         'Attributes']]
    # Drop invalid rows
    df = df.dropna(subset=['Coupon'])
    # Remove yields below 0
    df.drop(df.index[df['Ask Yield to Worst'] < 0], inplace=True)
    # Reformat maturity date
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'], format='%m/%d/%Y')
    # Days to Maturity Column
    df['days_to_maturity'] = (pd.to_datetime(df['Maturity Date'], errors='coerce')-(pd.Timestamp.today().normalize())).dt.days
    # Remove maturity more than 10y
    df.drop(df.index[df['days_to_maturity'] > 1825], inplace = True)

    # Add extra columns
    df['call_protected'] = df['Attributes'].str.contains('CP')
    df['fdic'] = df['Attributes'].str.contains('FDIC')
    df['survivor_option'] = df['Attributes'].str.contains('SO')

    #This creates a title
    st.header('Current Offerings')

    df_display = df
    st.write(df_display)

    st.subheader('Descriptive Statistics')
    st.write(df.describe())

    # Yield Slider
    st.subheader('Range slider')
    min_yield = (df_display['Ask Yield to Worst'].min())
    max_yield = (df_display['Ask Yield to Worst'].max())

    selected_yield = st.slider(
     'Yield Range',
     min_yield, max_yield, (min_yield, max_yield))

    df_display.drop(df_display.index[df_display['Ask Yield to Worst'] < min(selected_yield)], inplace=True)
    df_display.drop(df_display.index[df_display['Ask Yield to Worst'] > max(selected_yield)], inplace=True)

    # COUPON FREQUENCY
    # #Multi-selector
    options = st.multiselect(
     'Coupon Frequency',
    (set(df_display['Coupon Frequency']))
    ,(set(df_display['Coupon Frequency'])))

    df_display = df_display[df_display['Coupon Frequency'].isin(options)]

    # ATTRIBUTES
    st.header('Attributes')

    cp_check = st.checkbox('Call protected')
    fdic_check = st.checkbox('FDIC Insured')
    so_check =st.checkbox('Survivor Option')

    if cp_check == True:
        df_display = df_display[df_display['call_protected'] == True]

    # PLOT YIELD CURVE
    st.header('Yield Curve')
    chart_data = pd.DataFrame(
    df_display[["days_to_maturity", "Ask Yield to Worst"]], columns=['days_to_maturity', 'Ask Yield to Worst'])
    st.scatter_chart(chart_data, x = 'days_to_maturity', y = 'Ask Yield to Worst', height=500, use_container_width=True)
else:
  st.info('☝️ Upload a CSV file')
