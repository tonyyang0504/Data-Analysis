from goodgd999_scraper import scrape_data
import streamlit as st
import pandas as pd


st.set_page_config(layout='wide')
st.title('🎊Goodgd999 Data Download App🎉')

st.error("Please select the data you'd like to download")
selected = st.selectbox(
    '👇👇👇👇👇👇👇👇👇👇',
    (
        'Existing data',
        'Latest data'
    )
)

file_path = './total_data.csv'
if selected == 'Existing data':
    st.download_button(
        label='📥Click on me to download the data📥',
        data=pd.read_csv(file_path).to_csv(index=False),
        file_name='total_data.csv',
        mime='txt/csv'
    )
    st.success('Existing data prepared, please click the button above to download')
else:
    st.download_button(
        label='📥Click on me to download the data📥',
        data=scrape_data().to_csv(index=False),
        file_name='total_data.csv',
        mime='txt/csv'
    )
    st.success('Latest data prepared, please click the button above to download')
