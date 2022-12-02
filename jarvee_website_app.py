from streamlit_tools import *

st.set_page_config(layout="wide")


def main():
    st.title('🎊Jarvee Logs Analysis App🎉')
    st.sidebar.info('🍩Please select the mode of logs🍧')
    mode_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Customized Data', 'Default Data'))

    st.sidebar.warning('🪂Please select an activity🚴')
    activity_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Group Joiner', 'Publishing', 'Bump'))

    st.sidebar.success('🔎Please select the type of total_posts🔍')
    type_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Robot', 'Account'))

    data = fetch_data(mode_selectbox)

    url_file = pd.read_csv('./links/group links.csv')
    urls = set(url_file['GroupLink'])

    activity = confirm_activity(activity_selectbox, data)
    data_analysis = open_data_analysis(activity=activity, urls=urls, type_=type_selectbox)

    st.info('🍅Original Data🍎')
    check_words = '👈Click on me to see the original total_posts👇'
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
        check_words = f'👈Click on me to see the total_posts by {type_selectbox.lower()}👇'
        file_name = f'Number of {activity_selectbox} Joined Specified Groups.csv'
        layout(check_words=check_words, data=count_specified, file_name=file_name)

        st.error(f'🙈Number of {activity_selectbox} Joined Selected Groups🙊')
        urls_selected = st.multiselect('👇👇👇👇👇👇👇👇👇👇', urls)

        if urls_selected:
            data_analysis_specified = open_data_analysis(activity=activity, urls=urls_selected, type_=type_selectbox)
            count_selected = type_select(
                                         type_selectbox,
                                         data_analysis_specified.count_specified_by_robot,
                                         data_analysis_specified.count_specified_by_account
                                         )
            st.dataframe(count_selected)
                
            st.download_button(
                                label=f'♻📥Click me to download the result📥♻️',
                                data=count_selected.to_csv(),
                                file_name=f'Number of {activity_selectbox} Joined Selected Groups '
                                          f'by {type_selectbox.lower()}.csv',
                                mime='txt/csv')

        st.success('🥪Number of joined the specified groups🍔')
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

    # ************************ Data Visualization ************************

    st.info('🎨Data Visualization🧩')
    error_distribution = type_select(
                                     type_selectbox,
                                     data_analysis.error_distribution_by_robot,
                                     data_analysis.error_distribution_by_account
                                     )
    error_distribution = error_distribution.unstack().fillna(0)

    if type_selectbox != 'Robot':
        error_distribution.index = error_distribution.index.map(lambda x: '_'.join(x))

    codes = st.multiselect(
                            f'🧋Display the rate of selected error codes on the {type_selectbox.lower()}🍫',
                            error_distribution.columns.unique(),
                            )

    codes_selected = error_distribution.loc[:, codes]

    if codes:
        plot_bar(codes_selected.T)

    robots = st.multiselect(
                            f'🎁Display the error distribution on the selected {type_selectbox.lower()}🎈',
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
