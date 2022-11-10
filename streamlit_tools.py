import pandas as pd
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jarvee_logs import GroupJoiner, Publishing, Bump


class DataAnalysis(object):
    def __init__(self, activity, urls=None, type_=None):
        self.activity = activity
        self.type = type_
        self.urls = urls

    def logs_related(self):
        df = self.activity.logs_related()
        return df

    def df_specified_total(self):
        df = self.activity.df_specified_total(self.urls)
        return df

    def df_specified_error(self):
        df = self.activity.df_specified_error(self.urls)
        return df

    def count_specified_by_robot(self):
        df = self.activity.count_specified_by_robot(self.urls)
        return df

    def count_specified_by_account(self):
        df = self.activity.count_specified_by_account(self.urls)
        return df

    def count_specified_urls_total(self):
        df = self.activity.count_specified_urls_total(self.urls)
        return df

    def count_specified_urls_error(self):
        df = self.activity.count_specified_urls_error(self.urls)
        return df

    def count_specified_urls_finished(self):
        df = self.activity.count_specified_urls_finished(self.urls)
        return df

    def count_specified_urls_total_by_robot(self):
        df = self.activity.count_specified_urls_total_by_robot(self.urls)
        return df

    def count_specified_urls_total_by_account(self):
        df = self.activity.count_specified_urls_total_by_account(self.urls)
        return df

    def error_distribution_by_robot(self):
        df = self.activity.error_distribution_by_robot()
        return df

    def error_distribution_by_account(self):
        df = self.activity.error_distribution_by_account()
        return df


st.cache(suppress_st_warning=True)
def simplify_index(df, separate):
    simplified_df = df.copy()
    simplified_df.index = simplified_df.index.map(lambda x: x.split(separate)[-1])
    return simplified_df


st.cache(suppress_st_warning=True)
def data_normalized(df, columns=None):
    df_normalized = None
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
def plot_bar(df,title=None, x=None, y=None, color=None, color_discrete_sequence=None):
    fig = px.bar(df,
                 barmode='group',
                 height=600,
                 width=1000,
                 title=title,
                 x=x,
                 y=y,
                 color=color,
                 color_discrete_sequence=color_discrete_sequence)
    st.plotly_chart(fig)


def plot_line(df, title=None, x=None, y=None):
    fig = px.line(df, height=600, width=1000, title=title, x=x, y=y)
    st.plotly_chart(fig)


def plot_area(df, title=None, x=None, y=None):
    fig = px.area(df, height=600, width=1000, title=title, x=x, y=y)
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
        df = pd.concat(df_list, ignore_index=True)
        if len(df_list) > 1:
            st.success(f'👏You have uploaded {len(df_list)} files successfully.👏')
        else:
            st.success(f'👏You have uploaded {len(df_list)} file successfully.👏')
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
        df = pd.concat(df_list, ignore_index=True)
        return df
    else:
        st.error('💥Please upload one file at least or select default files from sidebar to analyze💥')
        st.stop()


@st.cache(suppress_st_warning=True)
def confirm_activity(activity_selectbox, data):
    activity = None
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
def open_data_analysis(activity, urls, type_=None):
    return DataAnalysis(activity=activity, urls=urls, type_=type_)


st.cache(suppress_st_warning=True)
def fetch_data(mode):
    if mode == 'Customized Data':
        st.info('📤Please upload one file at least📤')
        uploaded_files = st.file_uploader('👇👇👇👇👇👇👇👇👇👇', accept_multiple_files=True)
        files = [file for file in uploaded_files if file.name.endswith('.csv') or file.name.endswith('.txt')]
        return concat_uploaded_data(files)
    elif mode == 'Default Data':
        path = './group_joiner_logs'
        files = {file for file in os.listdir(path) if file.endswith('.csv') or file.endswith('.txt')}
        return concat_default_data(path=path, files=files)
    else:
        st.error('Please select the data mode')


st.cache(suppress_st_warning=True)
def type_select(type_, function_by_robot, function_by_account, activity=None):
    if type_ == 'Robot':
        if activity:
            result = function_by_robot(activity)
        else:
            result = function_by_robot()
    else:
        if activity:
            result = function_by_account(activity)
        else:
            result = function_by_account()
    return result


st.cache(suppress_st_warning=True)
def layout(check_words, data, file_name):
    col1, col2 = st.columns(2)
    with col1:
        checkbox = st.checkbox(check_words)
    with col2:
        st.download_button(
                            label='📥Click on me to download the result📥',
                            data=data.to_csv(),
                            file_name=file_name,
                            mime='txt/csv'
                            )
    if checkbox:
        st.dataframe(data)
