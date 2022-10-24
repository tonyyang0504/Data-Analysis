import pandas as pd
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jarvee_logs import GroupJoiner, Publishing, Bump


st.set_page_config(layout="wide")

st.cache(suppress_st_warning=True)
def simplify_index(df):
    simplified_df = df.copy()
    simplified_df.index = simplified_df.index.map(lambda x: x.split('.')[-1])
    
    return simplified_df

st.cache(suppress_st_warning=True)
def data_normalized(df, columns=None):
    if isinstance(df, pd.core.frame.DataFrame):
        max_rate = df[columns].max()
        min_rate = df[columns].min()
        df_normalized = df[(df[columns] > min_rate) & (df[columns] < max_rate)]
    elif isinstance(df, pd.core.frame.Series):
        max_rate = df.max()
        min_rate = df.min()
        df_normalized = df[(df > min_rate) & (df < max_rate)]
    
    return df_normalized

st.cache(suppress_st_warning=True)
def subplots_bar(df):
    rows = df.shape[1]
    fig = make_subplots(rows=rows,
                        cols=1,
                        subplot_titles=df.columns)
    for row in range(rows):
        fig.add_trace(go.Bar(x=df.index, y=df.iloc[:, row]), row=row + 1, col=1)
   
    fig.update_layout(height=800)

    st.plotly_chart(fig)

st.cache(suppress_st_warning=True)
def subplots_box(df):
    cols = df.shape[1]
    fig = make_subplots(rows=1,
                        cols=cols,
                        subplot_titles=df.columns)
    for col in range(cols):
        fig.add_trace(go.Box(y=df.iloc[:, col]), row=1, col=col + 1)
   
    fig.update_layout(height=800)

    st.plotly_chart(fig)

st.cache(suppress_st_warning=True)
def plot_bars(df):
    fig = px.bar(df, barmode='group', height=500, width=800)

    st.plotly_chart(fig)

@st.cache(suppress_st_warning=True)
def concat_uploaded_data(files):
    if files:
            df_list = []
            name_list = []
            for file in files:
                name = file.name.split('_')[0]
                if name not in name_list:
                    df = pd.read_csv(file)
                    df['Robot'] = name
                    df_list.append(df)
                    name_list.append(name)
                else:
                    continue
            df = pd.concat(df_list)
            st.success(f'👏You have uploaded {len(df_list)} files successfully.👏')
            return df
    else:
        st.error('💥Please upload one file at least or select default files from sidebar to analyze💥')
        st.stop()

@st.cache(suppress_st_warning=True)
def concat_default_data(path, files):
    if files:
            df_list = []
            for file in files:
                name = file.split('_')[0]
                df = pd.read_csv(os.path.join(path, file))
                df['Robot'] = name
                df_list.append(df)
            df = pd.concat(df_list)
            return df
    else:
        st.error('💥Please upload one file at least or select default files from sidebar to analyze💥')
        st.stop()
        
@st.cache(suppress_st_warning=True)
def open_dataframe(data):
    df = st.dataframe(data)
    return df

@st.cache(suppress_st_warning=True)
def confirm_activity(activity_selectbox, data):
    if activity_selectbox == 'Group Joiner':
        activity = GroupJoiner(data)
    elif activity_selectbox == 'Publishing':
        activity = Publishing(data)
    elif activity_selectbox == 'Bump':
        activity = Bump(data)

    return activity

st.cache(suppress_st_warning=True)
def count_by_robot(activity):
    count_error = activity.count_error_by_robot()
    count_total = activity.count_total_by_robot()
    count_df = pd.concat([count_error, count_total], axis=1).fillna(0).astype('int64')
    count_df.columns = ['Error', 'Total']
    count_df.insert(0, 'Finished', count_df['Total'] - count_df['Error'])
    count_df['Error Rate'] = (count_df['Error'] / count_df['Total']).round(2)

    return count_df

st.cache(suppress_st_warning=True)
def count_by_account(activity):
    count_error = activity.count_error_by_account()
    count_total = activity.count_total_by_account()
    count_df = pd.concat([count_error, count_total], axis=1).fillna(0).astype('int64')
    count_df.columns = ['Error', 'Total']
    count_df.insert(0, 'Finished', count_df['Total'] - count_df['Error'])
    count_df['Error Rate'] = (count_df['Error'] / count_df['Total']).round(2)
    return count_df

st.cache(suppress_st_warning=True)
def open_data_analysis(activity, urls, type=None):
    return DataAnalysis(activity=activity, urls=urls, type=type)
    
def fetch_data(mode):
    if mode == 'Customized Data':
        st.info('📤Please upload one file at least📤')
        uploaded_files = st.file_uploader('👇👇👇👇👇👇👇👇👇👇', accept_multiple_files=True)
        files = [file for file in uploaded_files if file.name.endswith('.csv') or file.name.endswith('.txt')]
        return concat_uploaded_data(files)
    elif mode == 'Default Data':
        path = 'D:/data_analysis/group_joiner_logs'
        files = {file for file in os.listdir(path) if file.endswith('.csv') or file.endswith('.txt')}
        return concat_default_data(path=path, files=files)
    else:
        st.error('Please select the data mode')

class DataAnalysis(object):
    def __init__(self, activity, urls, type=None):
        self.activity = activity
        self.type = type
        self.urls = urls

    st.cache(suppress_st_warning=True)
    def logs_related(self):
        df = self.activity.logs_related()

        return df

    st.cache(suppress_st_warning=True)
    def df_specified_total(self):
        df = self.activity.df_specified_total(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def df_specified_error(self):
        df = self.activity.df_specified_error(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def count_specified_by_robot(self):
        df = self.activity.count_specified_by_robot(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def count_specified_by_account(self):
        df = self.activity.count_specified_by_account(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def count_specified_urls_total(self):
        df = self.activity.count_specified_urls_total(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def count_specified_urls_total_by_robot(self):
        df = self.activity.count_specified_urls_total_by_robot(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def count_specified_urls_total_by_account(self):
        df = self.activity.count_specified_urls_total_by_account(self.urls)

        return df

    st.cache(suppress_st_warning=True)
    def error_distribution_by_robot(self):
        df = self.activity.error_distribution_by_robot()

        return df
    
    st.cache(suppress_st_warning=True)
    def error_distribution_by_account(self):
        df = self.activity.error_distribution_by_account()

        return df

st.cache(suppress_st_warning=True)
def main():
    st.title('🎊Jarvee Logs Analysis App🎉')
    st.sidebar.info('🍩Please select the mode of logs🍧')
    mode_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Customized Data', 'Default Data'))

    st.sidebar.warning('🪂Please select an activity🚴')
    activity_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Group Joiner', 'Publishing', 'Bump'))

    st.sidebar.success('🔎Please select the type of data🔍')
    type_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Robot', 'Account'))

    data = fetch_data(mode_selectbox)

    url_file = pd.read_csv('D:/data_analysis/links/group links.csv')
    urls = set(url_file['GroupLink'])

    st.info('🍅Original Data🍎')
    col1, col2 = st.columns(2)
    with col1:
        original_data_checkbox = st.checkbox('👈Click on me to see the original data👇')

    with col2:
        st.download_button(
                        label='♻️📥Click me to download the file📥♻️',
                        data=data.to_csv(),
                        file_name='The Original Data.csv',
                        mime='txt/csv')

    if original_data_checkbox:
        st.dataframe(data)

    activity = confirm_activity(activity_selectbox, data)
    data_analysis = open_data_analysis(activity=activity, urls=urls, type=type_selectbox)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'🐶{activity_selectbox} Logs🐻')
        # logs_related = activity.logs_related()
        logs_related = data_analysis.logs_related()

        col1, col2 = st.columns(2)

        with col1:
            activity_logs_checkbox = st.checkbox(f'👈Click on me to see {activity_selectbox.lower()} logs👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=logs_related.to_csv(),
                                file_name=f'{activity_selectbox} Data.csv',
                                mime='txt/csv')

        if activity_logs_checkbox:
            st.dataframe(logs_related)

    st.success(f'🍆Number of {activity_selectbox}🥕')

    if type_selectbox == 'Robot':
        numbers = count_by_robot(activity)
    else:
        numbers = count_by_account(activity)

    col1, col2 = st.columns(2)

    with col1:
        n_activity_checkbox = st.checkbox(f'👈Click on me to see the result👇')

    with col2:
        st.download_button(
                            label=f'♻️📥Click me to download the result📥♻️',
                            data=numbers.to_csv(),
                            file_name=f'Number of {activity_selectbox} by {type_selectbox}.csv',
                            mime='txt/csv')

    if n_activity_checkbox:
        st.dataframe(numbers)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'🐝Data of {activity_selectbox} Joined Specified Groups🐜')

        # df_specified_total = activity.df_specified_total(urls)
        df_specified_total = data_analysis.df_specified_total()
        col1, col2 = st.columns(2)

        with col1:
            total_logs_checkbox = st.checkbox(f'👈Click on me to see the total logs👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=df_specified_total.to_csv(),
                                file_name=f'Total Logs of {activity_selectbox} Joined Specified Groups.csv',
                                mime='txt/csv')

        if  total_logs_checkbox:
            st.dataframe(df_specified_total)

        # df_specified_error = activity.df_specified_error(urls)
        df_specified_error = data_analysis.df_specified_error()
        col1, col2 = st.columns(2)

        with col1:
            error_logs_checkbox = st.checkbox(f'👈Click on me to see the error logs👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=df_specified_error.to_csv(),
                                file_name=f'Error Logs of {activity_selectbox} Joined Specified Groups.csv',
                                mime='txt/csv')

        if error_logs_checkbox:
            st.dataframe(df_specified_error)

        if type_selectbox == 'Robot':
            # count_specified = activity.count_specified_by_robot(urls)
            count_specified = data_analysis.count_specified_by_robot()
        else:
            # count_specified = activity.count_specified_by_account(urls)
            count_specified = data_analysis.count_specified_by_account()
            
        col1, col2 = st.columns(2)

        with col1:
            count_specified_checkbox = st.checkbox(f'👈Click on me to see the data by {type_selectbox.lower()}👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=count_specified.to_csv(),
                                file_name=f'Number of {activity_selectbox} Joined Specified Groups.csv',
                                mime='txt/csv')

        if count_specified_checkbox:
            st.dataframe(count_specified)

        st.error(f'🙈Number of {activity_selectbox} Joined Selected Groups🙊')

        urls_selected = st.multiselect('👇👇👇👇👇👇👇👇👇👇', urls)

        if urls_selected:
            data_analysis_specified = open_data_analysis(activity=activity, urls=urls_selected, type=type_selectbox)
            if type_selectbox == 'Robot':
                # count_selected = activity.count_specified_by_robot(urls_selected)
                count_selected = data_analysis_specified.count_specified_by_robot()
                st.dataframe(count_selected)
            else:
                # count_selected = activity.count_specified_by_account(urls_selected)
                count_selected = data_analysis_specified.count_specified_by_account()
                st.dataframe(count_selected)
                
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=count_selected.to_csv(),
                                file_name=f'Number of {activity_selectbox} Joined Selected Groups by {type_selectbox.lower()}.csv',
                                mime='txt/csv')

        st.success(f'🥪Number of joined the specified groups🍔')

        # count_specified_urls_total = activity.count_specified_urls_total(urls)
        count_specified_urls_total = data_analysis.count_specified_urls_total()

        col1, col2 = st.columns(2)

        with col1:
            count_specified_urls_total_checkbox = st.checkbox(f'👈Click on me to see the number of joined the groups👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=count_specified_urls_total.to_csv(),
                                file_name=f'Number of Joined Specified Groups.csv',
                                mime='txt/csv')

        if count_specified_urls_total_checkbox:
            st.dataframe(count_specified_urls_total)

        if type_selectbox == 'Robot':
            # count_specified_urls = activity.count_specified_urls_total_by_robot(urls)
            count_specified_urls = data_analysis.count_specified_urls_total_by_robot()
        else:
            # count_specified_urls = activity.count_specified_urls_total_by_account(urls)
            count_specified_urls = data_analysis.count_specified_urls_total_by_account()

        col1, col2 = st.columns(2)

        with col1:
            count_specified_urls_checkbox = st.checkbox(f'👈Click on me to see the result by {type_selectbox.lower()}👇')

        with col2:
            st.download_button(
                                label=f'♻️📥Click me to download the result📥♻️',
                                data=count_specified_urls.to_csv(),
                                file_name=f'Number of Joined Specified Groups by {type_selectbox}.csv',
                                mime='txt/csv')

        if count_specified_urls_checkbox:
            st.dataframe(count_specified_urls)

        st.info('🎨Data Visualization🧩')
        
        if type_selectbox == 'Robot':
            # error_distribution = activity.error_distribution_by_robot().unstack().fillna(0)
            error_distribution = data_analysis.error_distribution_by_robot().unstack().fillna(0)
        else:
            # error_distribution = activity.error_distribution_by_account().unstack().fillna(0)
            error_distribution = data_analysis.error_distribution_by_account().unstack().fillna(0)
            error_distribution.index = error_distribution.index.map(lambda x: '_'.join(x))

        codes = st.multiselect(f'Display the rate of selected error codes on {type_selectbox.lower()}',
                                error_distribution.columns.unique(),
                                )

        codes_selected = error_distribution.loc[:, codes]

        if codes:
            plot_bars(codes_selected.T)

        robots = st.multiselect(f'Display error distribution on the selected {type_selectbox.lower()}',
                                    error_distribution.index.unique()
                                    )
        robots_selected = error_distribution.loc[robots, :]

        if robots:
            plot_bars(robots_selected.T)


main()

