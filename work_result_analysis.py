import pandas as pd
import os
import streamlit as st
from jarvee_website_app import *


def fetch_files(path, name_list):
    files_dict = {}
    for name in name_list:
        dict = {}
        for root, dirs, files in os.walk(os.path.join(path, name)):
            if files:
                date = root.split('\\')[-1]
                dict[date] = files
        files_dict[name] = dict
    return files_dict


def fetch_data(path, files):
    data_list = []
    for name, files_dict in files.items():
        df_list = []
        for key, value in files_dict.items():
            files_path = os.path.join(path, name, key)
            df = concat_default_data(files_path, value)
            df = df.copy()
            df['Export Date'] = key
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        df['Name'] = name
        data_list.append(df)
    data = pd.concat(data_list, ignore_index=True)
    return data


st.title('🎊Daily Work Result Analysis App🎉')

base_path = os.getcwd()
path = os.path.join(base_path, 'work_result')

url_file = pd.read_csv('./links/group links.csv')
urls = set(url_file['GroupLink'])
name_list = os.listdir(path)

files = fetch_files(path, name_list)
data = fetch_data(path, files)

daily_data = data.groupby(['Export Date', 'Name'])

st.success('🐼Number of Joined Specified Groups per person per day🐻‍')
daily_data_list = []
for i in list(daily_data):
    activity = confirm_activity('Group Joiner',i[1])
    data_analysis = open_data_analysis(activity=activity, urls=urls, type='Robot')
    result = data_analysis.count_specified_by_robot()
    result['Export Date'] = i[0][0]
    result['Name'] = i[0][1]
    daily_data_list.append(result)
df = pd.concat(daily_data_list)

dn_result = df.groupby(['Export Date', 'Name']).sum()[['Finished', 'Error', 'Total']]
check_words = '👈Click on me to see the data per person per day👇'
file_name = 'Number of Joined Specified Groups per person daily.csv'
layout(check_words=check_words, data=dn_result, file_name=file_name)
plot_bars(dn_result.unstack(fill_value=0)['Finished'])

st.info('🐢Number of Joined Specified Groups per day🦖')
date_result = df.groupby(['Export Date']).sum()[['Finished', 'Error', 'Total']]
check_words = '👈Click on me to see the data per day👇'
file_name = 'Number of Joined Specified Groups per day.csv'
layout(check_words=check_words, data=date_result, file_name=file_name)
plot_bars(date_result['Finished'])

st.warning('🍏Number of Joined Specified Groups per person🍑')
name_result = df.groupby(['Name']).sum()[['Finished', 'Error', 'Total']]
check_words = '👈Click on me to see the data per person👇'
file_name = 'Number of Joined Specified Groups per person.csv'
layout(check_words=check_words, data=name_result, file_name=file_name)
plot_bars(name_result['Finished'])

st.error('🥪Number of joined the specified groups🍔')
daily_data_list = []
for i in list(daily_data):
    activity = confirm_activity('Group Joiner',i[1])
    data_analysis = open_data_analysis(activity=activity, urls=urls, type='Robot')
    result = data_analysis.count_specified_urls_total()
    daily_data_list.append(result)
urls_data = pd.concat(daily_data_list)
urls_data = urls_data.groupby('Url').sum()

check_words = f'👈Click on me to see the number of joined the groups👇'
file_name = f'Number of Joined Specified Groups.csv'
layout(check_words=check_words, data=urls_data, file_name=file_name)
urls_data = simplify_index(urls_data, '/')
plot_bars(urls_data)