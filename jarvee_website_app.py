from unittest import result
import pandas as pd
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jarvee_logs import GroupJoiner, Publishing, Bump

pd.set_option('mode.chained_assignment', None)
st.set_page_config(layout="wide")

class DataAnalysis(object):
    def __init__(self, activity, urls=None, type=None):
        self.activity = activity
        self.type = type
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
            result =  function_by_robot()
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

def main():
    st.title('🎊Jarvee Logs Analysis App🎉')
    st.sidebar.info('🍩Please select the mode of logs🍧')
    mode_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Customized Data', 'Default Data'))

    st.sidebar.warning('🪂Please select an activity🚴')
    activity_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Group Joiner', 'Publishing', 'Bump'))

    st.sidebar.success('🔎Please select the type of data🔍')
    type_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Robot', 'Account'))

    data = fetch_data(mode_selectbox)

    url_file = pd.read_csv('./links/group links.csv')
    urls = set(url_file['GroupLink'])

    activity = confirm_activity(activity_selectbox, data)
    data_analysis = open_data_analysis(activity=activity, urls=urls, type=type_selectbox)

    st.info('🍅Original Data🍎')
    check_words = '👈Click on me to see the original data👇'
    file_name = 'The Original Data.csv'
    layout(check_words=check_words, data=data, file_name=file_name)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'🐶{activity_selectbox} Logs🐻')
        # logs_related = activity.logs_related()
        logs_related = data_analysis.logs_related()
        check_words = f'👈Click on me to see {activity_selectbox.lower()} logs👇'
        file_name = f'{activity_selectbox} Data.csv'
        layout(check_words=check_words, data=logs_related, file_name=file_name)

    st.success(f'🍆Number of {activity_selectbox}🥕')
    numbers = type_select(
                          type_selectbox,
                          count_by_robot,
                          count_by_account,
                          activity
                          )
    check_words = f'👈Click on me to see the result👇'
    file_name = f'Number of {activity_selectbox} by {type_selectbox}.csv'
    layout(check_words=check_words, data=numbers, file_name=file_name)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'🐝Data of {activity_selectbox} Joined Specified Groups🐜')

        # df_specified_total = activity.df_specified_total(urls)
        df_specified_total = data_analysis.df_specified_total()
        check_words = f'👈Click on me to see the total logs👇'
        file_name = f'Total Logs of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=df_specified_total, file_name=file_name)

        # df_specified_error = activity.df_specified_error(urls)
        df_specified_error = data_analysis.df_specified_error()
        check_words = f'👈Click on me to see the error logs👇'
        file_name = f'Error Logs of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=df_specified_error, file_name=file_name)

        count_specified = type_select(
                                      type_selectbox,
                                      data_analysis.count_specified_by_robot,
                                      data_analysis.count_specified_by_account
                                      )
        check_words = f'👈Click on me to see the data by {type_selectbox.lower()}👇'
        file_name = f'Number of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=count_specified, file_name=file_name)

        st.error(f'🙈Number of {activity_selectbox} Joined Selected Groups🙊')
        urls_selected = st.multiselect('👇👇👇👇👇👇👇👇👇👇', urls)

        if urls_selected:
            data_analysis_specified = open_data_analysis(activity=activity, urls=urls_selected, type=type_selectbox)
            count_selected = type_select(
                                         type_selectbox,
                                         data_analysis_specified.count_specified_by_robot,
                                         data_analysis_specified.count_specified_by_account
                                         )
            st.dataframe(count_selected)
                
            st.download_button(
                                label=f'♻📥Click me to download the result📥♻️',
                                data=count_selected.to_csv(),
                                file_name=f'Number of {activity_selectbox} Joined Selected Groups by {type_selectbox.lower()}.csv',
                                mime='txt/csv')

        st.success('🥪Number of joined the specified groups🍔')
        # count_specified_urls_total = activity.count_specified_urls_total(urls)
        count_specified_urls_total = data_analysis.count_specified_urls_total()
        check_words = f'👈Click on me to see the number of joined the groups👇'
        file_name = f'Number of Joined Specified Groups.csv'
        layout(check_words=check_words, data=count_specified_urls_total, file_name=file_name)

        count_specified_urls = type_select(
                                           type_selectbox,
                                           data_analysis.count_specified_urls_total_by_robot,
                                           data_analysis.count_specified_urls_total_by_account
                                           )
        check_words = f'👈Click on me to see the result by {type_selectbox.lower()}👇'
        file_name = f'Number of Joined Specified Groups by {type_selectbox}.csv'
        layout(check_words=check_words, data=count_specified_urls, file_name=file_name)

################################### Data Visualization ###################################
    st.info('🎨Data Visualization🧩')
    error_distribution = type_select(
                                     type_selectbox,
                                     data_analysis.error_distribution_by_robot,
                                     data_analysis.error_distribution_by_account
                                     )
    error_distribution = error_distribution.unstack().fillna(0)

    if type_selectbox != 'Robot':
        error_distribution.index = error_distribution.index.map(lambda x: '_'.join(x))

    codes = st.multiselect(f'🧋Display the rate of selected error codes on the {type_selectbox.lower()}🍫',
                            error_distribution.columns.unique(),
                            )

    codes_selected = error_distribution.loc[:, codes]

    if codes:
        plot_bars(codes_selected.T)

    robots = st.multiselect(f'🎁Display the error distribution on the selected {type_selectbox.lower()}🎈',
                                error_distribution.index.unique()
                                )
    robots_selected = error_distribution.loc[robots, :]

    if robots:
        plot_bars(robots_selected.T)

    if mode_selectbox == 'Default Data':
        st.success('Groups Report')
        df = pd.read_excel('./facebook_groups_report.xlsx')

        filtered = df.iloc[:,[3, -1]].dropna()
        filtered.iloc[:, 0] = filtered.iloc[:, 0].str.strip('/')
        filtered.columns = ['Url', 'Number of Record Url']

        count_specified_urls_finished = data_analysis.count_specified_urls_finished()
        count_specified_urls_finished = pd.DataFrame(count_specified_urls_finished)
        count_specified_urls_finished.reset_index(inplace=True)
        count_specified_urls_finished.columns = ['Url', 'Number of Finished Url']
        results = filtered.merge(count_specified_urls_finished)
        results['Diff'] = results['Number of Record Url'] - results['Number of Finished Url']
        results.set_index('Url', inplace=True)
        results = simplify_index(results, '/')
        plot_bars(results[['Number of Record Url', 'Number of Finished Url']])
        plot_bars(results['Diff'])

if __name__ == '__main__':
    main()

