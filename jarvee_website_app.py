from streamlit_tools import *

st.set_page_config(layout="wide")


def main():
    st.title('๐Jarvee Logs Analysis App๐')
    st.sidebar.info('๐ฉPlease select the mode of logs๐ง')
    mode_selectbox = st.sidebar.selectbox('๐๐๐๐๐๐๐๐๐๐', ('Customized Data', 'Default Data'))

    st.sidebar.warning('๐ชPlease select an activity๐ด')
    activity_selectbox = st.sidebar.selectbox('๐๐๐๐๐๐๐๐๐๐', ('Group Joiner', 'Publishing', 'Bump'))

    st.sidebar.success('๐Please select the type of total_posts๐')
    type_selectbox = st.sidebar.selectbox('๐๐๐๐๐๐๐๐๐๐', ('Robot', 'Account'))

    data = fetch_data(mode_selectbox)

    url_file = pd.read_csv('./links/group links.csv')
    urls = set(url_file['GroupLink'])

    activity = confirm_activity(activity_selectbox, data)
    data_analysis = open_data_analysis(activity=activity, urls=urls, type_=type_selectbox)

    st.info('๐Original Data๐')
    check_words = '๐Click on me to see the original total_posts๐'
    file_name = 'The Original Data.csv'
    layout(check_words=check_words, data=data, file_name=file_name)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'๐ถ{activity_selectbox} Logs๐ป')
        # logs_related = activity.logs_related()
        logs_related = data_analysis.logs_related()
        check_words = f'๐Click on me to see {activity_selectbox.lower()} logs๐'
        file_name = f'{activity_selectbox} Data.csv'
        layout(check_words=check_words, data=logs_related, file_name=file_name)

    st.success(f'๐Number of {activity_selectbox}๐ฅ')
    numbers = type_select(
                          type_selectbox,
                          count_by_robot,
                          count_by_account,
                          activity
                          )
    check_words = f'๐Click on me to see the result๐'
    file_name = f'Number of {activity_selectbox} by {type_selectbox}.csv'
    layout(check_words=check_words, data=numbers, file_name=file_name)

    if activity_selectbox == 'Group Joiner':
        st.warning(f'๐Data of {activity_selectbox} Joined Specified Groups๐')

        # df_specified_total = activity.df_specified_total(urls)
        df_specified_total = data_analysis.df_specified_total()
        check_words = f'๐Click on me to see the total logs๐'
        file_name = f'Total Logs of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=df_specified_total, file_name=file_name)

        # df_specified_error = activity.df_specified_error(urls)
        df_specified_error = data_analysis.df_specified_error()
        check_words = f'๐Click on me to see the error logs๐'
        file_name = f'Error Logs of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=df_specified_error, file_name=file_name)

        count_specified = type_select(
                                      type_selectbox,
                                      data_analysis.count_specified_by_robot,
                                      data_analysis.count_specified_by_account
                                      )
        check_words = f'๐Click on me to see the total_posts by {type_selectbox.lower()}๐'
        file_name = f'Number of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=count_specified, file_name=file_name)

        st.error(f'๐Number of {activity_selectbox} Joined Selected Groups๐')
        urls_selected = st.multiselect('๐๐๐๐๐๐๐๐๐๐', urls)

        if urls_selected:
            data_analysis_specified = open_data_analysis(activity=activity, urls=urls_selected, type_=type_selectbox)
            count_selected = type_select(
                                         type_selectbox,
                                         data_analysis_specified.count_specified_by_robot,
                                         data_analysis_specified.count_specified_by_account
                                         )
            st.dataframe(count_selected)
                
            st.download_button(
                                label=f'โป๐ฅClick me to download the result๐ฅโป๏ธ',
                                data=count_selected.to_csv(),
                                file_name=f'Number of {activity_selectbox} Joined Selected Groups '
                                          f'by {type_selectbox.lower()}.csv',
                                mime='txt/csv')

        st.success('๐ฅชNumber of joined the specified groups๐')
        count_specified_urls_total = data_analysis.count_specified_urls_total()
        check_words = f'๐Click on me to see the number of joined the groups๐'
        file_name = f'Number of Joined Specified Groups.csv'
        layout(check_words=check_words, data=count_specified_urls_total, file_name=file_name)

        count_specified_urls = type_select(
                                           type_selectbox,
                                           data_analysis.count_specified_urls_total_by_robot,
                                           data_analysis.count_specified_urls_total_by_account
                                           )
        check_words = f'๐Click on me to see the result by {type_selectbox.lower()}๐'
        file_name = f'Number of Joined Specified Groups by {type_selectbox}.csv'
        layout(check_words=check_words, data=count_specified_urls, file_name=file_name)

    # ************************ Data Visualization ************************

    st.info('๐จData Visualization๐งฉ')
    error_distribution = type_select(
                                     type_selectbox,
                                     data_analysis.error_distribution_by_robot,
                                     data_analysis.error_distribution_by_account
                                     )
    error_distribution = error_distribution.unstack().fillna(0)

    if type_selectbox != 'Robot':
        error_distribution.index = error_distribution.index.map(lambda x: '_'.join(x))

    codes = st.multiselect(
                            f'๐งDisplay the rate of selected error codes on the {type_selectbox.lower()}๐ซ',
                            error_distribution.columns.unique()
                            )

    codes_selected = error_distribution.loc[:, codes]

    if codes:
        plot_bar(codes_selected.T)

    robots = st.multiselect(
                            f'๐Display the error distribution on the selected {type_selectbox.lower()}๐',
                            error_distribution.index.unique()
                            )
    robots_selected = error_distribution.loc[robots, :]

    if robots:
        plot_bar(robots_selected.T)

    # ************************ Comparison between Task Result and Real Data ************************

    if mode_selectbox == 'Default Data':
        st.success('Groups Report')
        df = pd.read_excel('./facebook_groups_report.xlsx')

        filtered = df.loc[:, ['Url', 'Number of Members']].dropna()
        filtered.iloc[:, 0] = filtered.iloc[:, 0].str.strip('/')

        count_specified_urls_finished = data_analysis.count_specified_urls_finished()
        count_specified_urls_finished = pd.DataFrame(count_specified_urls_finished)
        count_specified_urls_finished.reset_index(inplace=True)
        count_specified_urls_finished.columns = ['Url', 'Number of Finished Url']
        results = filtered.merge(count_specified_urls_finished)
        results['Diff'] = results['Number of Members'] - results['Number of Finished Url']
        results.set_index('Url', inplace=True)
        results = simplify_index(results, '/')
        plot_bar(results[['Number of Members', 'Number of Finished Url']])
        plot_bar(results['Diff'])


if __name__ == '__main__':
    main()
