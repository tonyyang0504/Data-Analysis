import pandas as pd

from streamlit_tools import *


st.set_page_config(layout="wide")


def fetch_files(path, name_list):
    files_dict = {}
    for name in name_list:
        dict_ = {}
        for root, dirs, files in os.walk(os.path.join(path, name)):
            if files:
                date = root.split('\\')[-1]
                dict_[date] = files
        files_dict[name] = dict_
    return files_dict


def fetch_data(path, files):
    data_list = []
    for name, files_dict in files.items():
        df_list = []
        for key, value in files_dict.items():
            files_path = os.path.join(path, name, key)
            df = concat_default_data(files_path, value)
            df = df.copy()
            df['Export Date'] = key.split('/')[-1]
            df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        df['Name'] = name
        data_list.append(df)
    data = pd.concat(data_list, ignore_index=True)
    return data


def main():
    st.title('🎊Daily Work Result Analysis🎉')

    base_path = os.getcwd()
    path = os.path.join(base_path, 'work_result')

    url_file = pd.read_csv('./links/group links.csv')
    urls = set(url_file['GroupLink'])
    name_list = [name.split('/')[-1] for name in os.listdir(path)]

    files = fetch_files(path, name_list)
    data = fetch_data(path, files)
    pd.set_option('expand_frame_repr', False)

    daily_data = data.groupby(['Export Date', 'Name'])

    st.success('🐼Number of Joined Specified Groups per person daily🐻‍')
    daily_data_list = []
    for i in list(daily_data):
        activity = confirm_activity('Group Joiner', i[1])
        data_analysis = open_data_analysis(activity=activity, urls=urls, type_='Robot')
        result = data_analysis.count_specified_by_robot()
        result['Export Date'] = i[0][0]
        result['Name'] = i[0][1]
        daily_data_list.append(result)
    df = pd.concat(daily_data_list)

    dn_result = df.groupby(['Export Date', 'Name']).sum()[['Finished', 'Error', 'Total']]
    check_words = '👈Click on me to see the total_posts per person daily👇'
    file_name = 'Number of Joined Specified Groups per person daily.csv'
    layout(check_words=check_words, data=dn_result, file_name=file_name)
    plot_bar(dn_result.unstack(fill_value=0)['Finished'])

    st.info('🐢Number of Joined Specified Groups per day🦖')
    date_result = df.groupby(['Export Date']).sum()[['Finished', 'Error', 'Total']]
    check_words = '👈Click on me to see the total_posts per day👇'
    file_name = 'Number of Joined Specified Groups per day.csv'
    layout(check_words=check_words, data=date_result, file_name=file_name)
    plot_bar(date_result['Finished'], color=date_result.index)

    st.warning('🦅Number of Joined Specified Groups per person🦇')
    name_result = df.groupby(['Name']).sum()[['Finished', 'Error', 'Total']]
    check_words = '👈Click on me to see the total_posts per person👇'
    file_name = 'Number of Joined Specified Groups per person.csv'
    layout(check_words=check_words, data=name_result, file_name=file_name)
    plot_bar(name_result['Finished'], color=name_result.index)

    st.error('🐪Number of joined the specified groups🦘')
    daily_data_list = []
    for i in list(daily_data):
        activity = confirm_activity('Group Joiner', i[1])
        data_analysis = open_data_analysis(activity=activity, urls=urls, type_='Robot')
        result = data_analysis.count_specified_urls_total()
        daily_data_list.append(result)
    urls_data = pd.concat(daily_data_list)
    urls_data = urls_data.groupby('Url').sum()

    check_words = f'👈Click on me to see the number of joined the groups👇'
    file_name = f'Number of Joined Specified Groups.csv'
    layout(check_words=check_words, data=urls_data, file_name=file_name)
    urls_data = simplify_index(urls_data, '/')
    plot_bar(urls_data, color_discrete_sequence=['red'])

    st.success('🐧Group report results🐥')
    report = pd.read_excel('./Final report.xlsx', index_col=3)
    member_no = report.iloc[:, 8:-1].dropna(how='all')
    member_no.index = member_no.index.map(lambda x: x.strip('/')).rename('Url')
    check_words = '👈Click on me to see the report👇'
    file_name = 'Groups report.csv'
    layout(check_words=check_words, data=member_no, file_name=file_name)
    plot_report = simplify_index(member_no, '/').T
    plot_report.index.rename('Date', inplace=True)
    plot_line(plot_report)

    st.info('🐬Daily change of member of groups🐋')
    daily_change = member_no.diff(axis=1).dropna(how='all', axis=1)
    check_words = '👈Click on me to see the daily change👇'
    file_name = 'Daily change of member of groups.csv'
    layout(check_words=check_words, data=daily_change, file_name=file_name)
    plot_daily_change = simplify_index(daily_change, '/').T
    plot_bar(plot_daily_change)

    st.warning('🦫Number of outside posts🦦')
    post_outside = report.iloc[:, -1]
    post_outside.index = post_outside.index.map(lambda x: x.strip('/')).rename('Url')
    post_outside.rename('Outside Post', inplace=True)
    check_words = '👈Click on me to see the number of oustside posts👇'
    file_name = 'Number of outside posts.csv'
    layout(check_words=check_words, data=post_outside, file_name=file_name)
    post_outside = simplify_index(post_outside, '/')
    plot_bar(post_outside, color_discrete_sequence=['purple'])


if __name__ == '__main__':
    main()
