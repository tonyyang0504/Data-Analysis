import pandas as pd
import streamlit
import streamlit.proto.openmetrics_data_model_pb2

import streamlit_tools
import numpy as np
from streamlit_tools import *
import numpy as np


def concat_df(total_df, partial_df):
    df = pd.concat([total_df, partial_df], axis=1)
    df.columns = ['total', 'partial']
    df['partial / total'] = df['partial'].values / df['total'].values
    return df


def value_replacement(df, targeted_values):
    replacement = df.copy()
    for value in targeted_values:
        replacement = replacement.applymap(lambda x: np.nan if x == value else x)
    return replacement



st.cache(suppress_st_warning=True)
def group_info(group_info_file):
    group_info = pd.read_csv(group_info_file)
    group_info['fetched date'] = pd.to_datetime(group_info['fetched time']).dt.normalize()
    group_info['admin id'] = group_info['link'].apply(lambda x: x.split('&')[0].split('=')[-1])
    return group_info


def group_info_analysis(group_info_data):
    st.success('🐼Group members information🐻')
    group_info_duplicated = group_info_data.drop_duplicates(['admin id', 'group id'], keep='last', ignore_index=True)
    group_admins = group_info_duplicated.groupby(['group id'])['admin id'].unique()
    group_admins_count = group_info_duplicated.groupby(['group id'])['admin id'].count()
    group_members_count = group_info_duplicated.drop_duplicates('group id', keep='last', ignore_index=True)['number of members']
    group_members_daily_count = group_info_data.groupby(['fetched date', 'group id'])['number of members'].apply(lambda x: x.unique()[-1])
    plot_group_members_daily_count = group_members_daily_count.unstack().fillna(method='ffill')

    group_info_duplicated_check_words = 'Group members information duplicated'
    group_info_duplicated_data = group_info_duplicated
    group_info_duplicated_file_name = 'group members information duplicated.csv'
    layout(group_info_duplicated_check_words,
           group_info_duplicated_data,
           group_info_duplicated_file_name)

    group_admins_check_words = "Group admins' id"
    group_admins_data = group_admins
    group_admins_file_name = "group admins' id.csv"
    layout(group_admins_check_words,
           group_admins_data,
           group_admins_file_name)

    group_admins_count_check_words = "Number of group admins"
    group_admins_count_data = group_admins_count
    group_admins_count_file_name = "number of group admins.csv"
    layout(group_admins_count_check_words,
           group_admins_count_data,
           group_admins_count_file_name)

    group_members_count_daily_check_words = "Number of group members daily"
    group_members_count_daily_data = plot_group_members_daily_count
    group_members_count_daily_file_name = "number of group members daily.csv"
    layout(group_members_count_daily_check_words,
           group_members_count_daily_data,
           group_members_count_daily_file_name)
    plot_line(group_members_count_daily_data)

    group_members_count_change_daily_check_words = "Number of group members change daily"
    group_members_count_change_daily_data = group_members_count_daily_data.diff(axis=0).dropna(how='all', axis=0)
    group_members_count_change_daily_file_name = "number of group members change daily.csv"
    layout(group_members_count_change_daily_check_words,
           group_members_count_change_daily_data,
           group_members_count_change_daily_file_name)
    plot_area(group_members_count_change_daily_data)
    multiselect_plot_bar('Number of selected groups members change daily',
                          group_members_count_change_daily_data)

    plot_hist(group_members_count_change_daily_data, title='Distribution of number of group members change daily')
    multiselect_plot_hist('Distribution of selected groups number of group members change daily',
                          group_members_count_change_daily_data)

    group_members_count_change_daily_statistics_check_words = 'Statistics of group members change daily'
    group_members_count_change_daily_statistcs_data = group_members_count_change_daily_data.describe()
    group_members_count_change_daily_statistics_file_name = 'statistics of group members change daily.csv'
    layout(group_members_count_change_daily_statistics_check_words,
           group_members_count_change_daily_statistcs_data,
           group_members_count_change_daily_statistics_file_name)
    plot_hist(group_members_count_change_daily_statistcs_data.loc['mean', :], title='Distribution of mean of group members change daily')
    multiselect_plot_bar('Statistics of selected groups group members change daily',
                         group_members_count_change_daily_statistcs_data.drop(index='count'))


st.cache(suppress_st_warning=True)
def group_posts_info(group_posts_file, group_info_data):
    group_admins = group_info_data.groupby(['group id'])['admin id'].unique()
    total_posts = pd.read_csv(group_posts_file)
    total_posts['published date'] = pd.to_datetime(total_posts['published time']).dt.date
    total_posts['fetched date'] = pd.to_datetime(total_posts['fetched time']).dt.normalize()
    total_posts.drop_duplicates('post id', keep='last', inplace=True, ignore_index=True)

    reactions = total_posts['reactions'].str.strip('{}').str.split(',', expand=True).iloc[:, 0:-1]
    reactions = reactions.applymap(lambda x: x.split(':')[-1] if isinstance(x, str) else x)
    reactions.fillna(0, inplace=True)
    reactions = reactions.astype('int64')
    reactions.columns = ['like', 'love', 'haha', 'wow']

    total_posts = pd.concat([total_posts, reactions], axis=1)
    total_posts['reactions'] = total_posts['like'].values + total_posts['love'].values + \
                               total_posts['haha'].values + total_posts['wow'].values
    total_posts['likes'].fillna(0, inplace=True)
    total_posts['likes'] = total_posts['likes'].astype('int64')

    direct_posts = total_posts[total_posts['shared user id'].isna()]
    outside_posts_list = []
    for outside_data in direct_posts.groupby('group id'):
        df = outside_data[1][~outside_data[1]['user id'].isin(group_admins[outside_data[0]])]
        outside_posts_list.append(df)
    outside_posts = pd.concat(outside_posts_list, ignore_index=True)
    return total_posts, outside_posts


def posts_data_display(total_posts, outside_posts):
    st.error('🐪Group posts information🦘')
    total_posts_check_words = 'Total posts information'
    total_posts_data = total_posts
    total_posts_file_name = 'total posts information.csv'
    layout(total_posts_check_words,
           total_posts_data,
           total_posts_file_name)

    outside_posts_check_words = 'Outside posts information'
    outside_posts_data = outside_posts
    outside_posts_file_name = 'outside posts informatio.csv'
    layout(outside_posts_check_words,
           outside_posts_data,
           outside_posts_file_name)


def posts_data_daily_analysis(total_posts, outside_posts):
    st.warning('🦊Posts data daily🐱')
    total_posts_daily_count = total_posts.groupby(['group id', 'published date'])['post id'].count()
    outside_posts_daily_count = outside_posts.groupby(['group id', 'published date'])['post id'].count()
    posts_daily_count = concat_df(total_posts_daily_count, outside_posts_daily_count).fillna(0)
    posts_daily_count = posts_daily_count.rename(columns={'total': 'number of total posts daily',
                                                          'partial': 'number of outside posts daily',
                                                          'partial / total': 'outside posts daily / total posts daily'})

    total_posts_daily_count_check_words = 'Number of total posts daily'
    total_posts_daily_count_data = posts_daily_count.unstack()['number of total posts daily'].T
    total_posts_daily_count_file_name = 'number of total posts daily.csv'
    layout(total_posts_daily_count_check_words,
           total_posts_daily_count_data,
           total_posts_daily_count_file_name)
    plot_area(total_posts_daily_count_data)
    multiselect_plot_line('Number of selected groups total posts daily',
                          total_posts_daily_count_data)

    plot_hist(total_posts_daily_count_data, title='Distribution of number of total posts daily')
    multiselect_plot_hist('Distribution of selected groups number of total posts daily',
                          total_posts_daily_count_data)

    total_posts_daily_statistics_check_words = 'Statistics of total posts daily'
    total_posts_daily_statistcs_data = total_posts_daily_count_data.describe()
    total_posts_daily_statistics_file_name = 'statistics of total posts daily.csv'
    layout(total_posts_daily_statistics_check_words,
           total_posts_daily_statistcs_data,
           total_posts_daily_statistics_file_name)
    plot_hist(total_posts_daily_statistcs_data.loc['mean', :], title='Distribution of mean of total posts daily')
    multiselect_plot_bar('Statistics of selected groups total posts daily',
                         total_posts_daily_statistcs_data.drop(index='count'))

    outside_posts_daily_count_check_words = 'Number of outside posts daily'
    outside_posts_daily_count_data = posts_daily_count.unstack()['number of outside posts daily'].T
    outside_posts_daily_count_file_name = 'number of outside posts daily.csv'
    layout(outside_posts_daily_count_check_words,
           outside_posts_daily_count_data,
           outside_posts_daily_count_file_name)
    plot_area(outside_posts_daily_count_data)
    multiselect_plot_line('Number of selected groups outside posts daily',
                          outside_posts_daily_count_data)

    plot_hist(outside_posts_daily_count_data, title='Distribution of number of outside posts daily')
    multiselect_plot_hist('Distribution of selected groups number of outside posts daily',
                          outside_posts_daily_count_data)

    outside_posts_daily_statistics_check_words = 'Statistics of outside posts daily'
    outside_posts_daily_statistcs_data = outside_posts_daily_count_data.describe()
    outside_posts_daily_statistics_file_name = 'statistics of outside posts daily.csv'
    layout(outside_posts_daily_statistics_check_words,
           outside_posts_daily_statistcs_data,
           outside_posts_daily_statistics_file_name)
    plot_hist(outside_posts_daily_statistcs_data.loc['mean', :], title='Distribution of mean of outside posts daily')
    multiselect_plot_bar('Statistics of selected groups outside posts daily',
                         total_posts_daily_statistcs_data.drop(index='count'))

    outside_by_total_posts_daily_rate_check_words = 'Rate of outside posts daily by total'
    outside_by_total_posts_daily_rate_data = posts_daily_count.unstack()['outside posts daily / total posts daily'].T
    outside_by_total_posts_daily_rate_file_name = 'the rate of outside posts daily by total.csv'
    layout(outside_by_total_posts_daily_rate_check_words,
           outside_by_total_posts_daily_rate_data,
           outside_by_total_posts_daily_rate_file_name)
    plot_bar(outside_by_total_posts_daily_rate_data)

    outside_by_total_posts_daily_rate_data_hist = value_replacement(outside_by_total_posts_daily_rate_data, [0, 1])
    plot_hist(outside_by_total_posts_daily_rate_data_hist, title='Distribution of rate of outside posts daily by total')
    multiselect_plot_hist('Distribution of rate of selected groups outside posts daily by total',
                          outside_by_total_posts_daily_rate_data_hist)

    outside_by_total_posts_daily_rate_statistics_check_words = 'Statistics of outside posts daily by total rate'
    outside_by_total_posts_daily_rate_statistics_data = outside_by_total_posts_daily_rate_data_hist.describe()
    outside_by_total_posts_daily_rate_statistics_file_name = 'statistics of outside posts daily by total rate.csv'
    layout(outside_by_total_posts_daily_rate_statistics_check_words,
           outside_by_total_posts_daily_rate_statistics_data,
           outside_by_total_posts_daily_rate_statistics_file_name)
    plot_hist(outside_by_total_posts_daily_rate_statistics_data.loc['mean', :], title='Distribution of mean of outside posts daily by total rate')
    multiselect_plot_bar('Statistics of selected groups outside posts daily by total rate',
                         outside_by_total_posts_daily_rate_statistics_data.drop(index='count'))


def posts_data_analysis(total_posts, outside_posts):
    st.success('🐬Posts data🐋')
    outside_posts_count = outside_posts.groupby(['group id'])['post id'].count()
    outside_posts_count.rename('number of outside posts', inplace=True)
    total_posts_count = total_posts.groupby(['group id'])['post id'].count()
    total_posts_count.rename('number of total posts', inplace=True)
    posts_count = pd.concat([outside_posts_count, total_posts_count], axis=1)
    posts_count['outside posts / total posts'] = posts_count['number of outside posts'].\
                                                            div(posts_count['number of total posts'])
    total_posts_count_check_words = 'Number of total posts'
    total_posts_count_data = posts_count[['number of total posts']].T.sort_values('number of total posts', axis=1)
    total_posts_count_file_name = 'number of total posts.csv'
    layout(total_posts_count_check_words,
           total_posts_count_data,
           total_posts_count_file_name)
    plot_bar(total_posts_count_data)

    total_posts_statistics_check_words = 'Statistics of total posts'
    total_posts_statistics_data = posts_count[['number of total posts']].describe()
    total_posts_statistics_file_name = 'statistics of total posts.csv'
    layout(total_posts_statistics_check_words,
           total_posts_statistics_data,
           total_posts_statistics_file_name)
    plot_bar(total_posts_statistics_data.drop(index='count'), color_discrete_sequence=['red'])

    outside_posts_count_check_words = 'Number of outside posts'
    outside_posts_count_data = posts_count[['number of outside posts']].T.sort_values('number of outside posts', axis=1)
    outside_posts_count_file_name = 'number of outside posts.csv'
    layout(outside_posts_count_check_words,
           outside_posts_count_data,
           outside_posts_count_file_name)
    plot_bar(outside_posts_count_data)

    outside_posts_statistics_check_words = 'Statistics of outside posts'
    outside_posts_statistics_data = posts_count[['number of outside posts']].describe()
    outside_posts_statistics_file_name = 'statistics of outside profiles posted.csv'
    layout(outside_posts_statistics_check_words,
           outside_posts_statistics_data,
           outside_posts_statistics_file_name)
    plot_bar(outside_posts_statistics_data.drop(index='count'), color_discrete_sequence=['green'])

    outside_posts_by_total_rate_check_words = 'Rate of outside posts by total'
    outside_posts_by_total_rate_data = posts_count[['outside posts / total posts'
                                                    ]].T.sort_values('outside posts / total posts', axis=1)
    outside_posts_by_total_rate_file_name = 'rate of outside posts posted by total.csv'
    layout(outside_posts_by_total_rate_check_words,
           outside_posts_by_total_rate_data,
           outside_posts_by_total_rate_file_name)
    plot_bar(outside_posts_by_total_rate_data)

    outside_posts_by_total_rate_statistics_check_words = 'Statistics of outside posts by total rate'
    outside_posts_by_total_rate_statistics_data = posts_count[['outside posts / total posts']].describe()
    outside_posts_by_total_rate_statistics_file_name = 'statistics of outside posts by total rate.csv'
    layout(outside_posts_by_total_rate_statistics_check_words,
           outside_posts_by_total_rate_statistics_data,
           outside_posts_by_total_rate_statistics_file_name)
    plot_bar(outside_posts_by_total_rate_statistics_data.drop(index='count'), color_discrete_sequence=['blue'])


def profiles_data_daily_analysis(total_posts, outside_posts):
    st.info('🐧Profiles posted data daily🐥')
    total_profiles_unique_daily = total_posts.groupby(['group id', 'published date'])['user id'].unique()
    outside_profiles_unique_daily = outside_posts.groupby(['group id', 'published date'])['user id'].unique()
    total_profiles_daily_count = total_profiles_unique_daily.map(lambda x: len(x))
    outside_profiles_daily_count = outside_profiles_unique_daily.map(lambda x: len(x))
    profiles_daily_count = concat_df(total_profiles_daily_count, outside_profiles_daily_count).fillna(0)
    profiles_daily_count.rename(columns={'total': 'number of total profiles posted daily',
                                         'partial': 'number of outside profiles posted daily',
                                         'partial / total': 'outside profiles posted daily / total profiles posted daily'},
                                inplace=True)

    total_profiles_daily_count_check_words = 'Number of total profiles posted daily'
    total_profiles_daily_count_data = profiles_daily_count.unstack()['number of total profiles posted daily'].T
    total_profiles_daily_count_file_name = 'number of total profiles posted daily.csv'
    layout(total_profiles_daily_count_check_words,
           total_profiles_daily_count_data,
           total_profiles_daily_count_file_name)
    plot_area(total_profiles_daily_count_data)
    multiselect_plot_line('Number of selected groups total profiles posted daily',
                          total_profiles_daily_count_data)

    plot_hist(total_profiles_daily_count_data, title='Distribution of number of total profiles posted daily')
    multiselect_plot_hist('Distribution of selected groups number of total profiles posted daily',
                          total_profiles_daily_count_data)

    total_profiles_daily_statistics_check_words = 'Statistics of total profiles posted daily'
    total_profiles_daily_statistcs_data = total_profiles_daily_count_data.describe()
    total_profiles_daily_statistics_file_name = 'statistics of total profiles posted daily.csv'
    layout(total_profiles_daily_statistics_check_words,
           total_profiles_daily_statistcs_data,
           total_profiles_daily_statistics_file_name)
    plot_hist(total_profiles_daily_statistcs_data.loc['mean', :], title='Distribution of mean of total profiles posted daily')
    multiselect_plot_bar('Statistics of selected groups total profiles posted daily',
                         total_profiles_daily_statistcs_data.drop(index='count'))

    outside_profiles_daily_count_check_words = 'Number of outside profiles posted daily'
    outside_profiles_daily_count_data = profiles_daily_count.unstack()['number of outside profiles posted daily'].T
    outside_profiles_daily_count_file_name = 'number of outside profiles posted daily.csv'
    layout(outside_profiles_daily_count_check_words,
           outside_profiles_daily_count_data,
           outside_profiles_daily_count_file_name)
    plot_area(outside_profiles_daily_count_data)
    multiselect_plot_line('Number of selected groups outside profiles posted daily',
                          outside_profiles_daily_count_data)

    plot_hist(outside_profiles_daily_count_data, title='Distribution of number of outside profiles posted daily')
    multiselect_plot_hist('Distribution of selected groups number of outside profiles posted daily',
                          outside_profiles_daily_count_data)

    outside_profiles_daily_statistics_check_words = 'Statistics of outside profiles posted daily'
    outside_profiles_daily_statistcs_data = outside_profiles_daily_count_data.describe()
    outside_profiles_daily_statistics_file_name = 'statistics of outside profiles posted daily.csv'
    layout(outside_profiles_daily_statistics_check_words,
           outside_profiles_daily_statistcs_data,
           outside_profiles_daily_statistics_file_name)
    plot_hist(outside_profiles_daily_statistcs_data.loc['mean', :], title='Distribution of mean of outside profiles posted daily')
    multiselect_plot_bar('Statistics of selected groups outside profiles posted daily',
                         outside_profiles_daily_statistcs_data.drop(index='count'))

    outside_by_total_profiles_daily_rate_check_words = 'Rate of outside profiles daily by total'
    outside_by_total_profiles_daily_rate_data = profiles_daily_count.unstack()['outside profiles posted daily / ' \
                                                                               'total profiles posted daily'].T
    outside_by_total_profiles_daily_rate_file_name = 'the rate of outside profiles daily by total.csv'
    layout(outside_by_total_profiles_daily_rate_check_words,
           outside_by_total_profiles_daily_rate_data,
           outside_by_total_profiles_daily_rate_file_name)
    plot_bar(outside_by_total_profiles_daily_rate_data)

    outside_by_total_profiles_daily_rate_data_hist = value_replacement(outside_by_total_profiles_daily_rate_data, [0, 1])
    plot_hist(outside_by_total_profiles_daily_rate_data_hist, title='Distribution of rate of outside_profiles daily by total')
    multiselect_plot_hist('Distribution of rate of selected groups outside _profiles daily by total',
                          outside_by_total_profiles_daily_rate_data_hist)

    outside_by_total_profiles_daily_rate_statistics_check_words = 'Statistics of outside profiles daily by total rate'
    outside_by_total_profiles_daily_rate_statistics_data =outside_by_total_profiles_daily_rate_data_hist.describe()
    outside_by_total_profiles_daily_rate_statistics_file_name = 'statistics of outside profiles daily by total rate.csv'
    layout(outside_by_total_profiles_daily_rate_statistics_check_words,
           outside_by_total_profiles_daily_rate_statistics_data,
           outside_by_total_profiles_daily_rate_statistics_file_name)
    plot_hist(outside_by_total_profiles_daily_rate_statistics_data.loc['mean', :], title='Distribution of mean of outside profiles daily by total rate')
    multiselect_plot_bar('Statistics of selected groups outside profiles daily by total rate',
                         outside_by_total_profiles_daily_rate_statistics_data.drop(index='count'))


def profiles_data_analysis(total_posts, outside_posts):
    st.success('🦫Profiles posted data🦦')
    total_profiles_unique = total_posts.groupby('group id')['user id'].unique()
    total_profiles_count = total_profiles_unique.map(lambda x: len(x))
    outside_profiles_unique = outside_posts.groupby(['group id'])['user id'].unique()
    outside_profiles_count = outside_profiles_unique.map(lambda x: len(x))
    profiles_count = concat_df(total_profiles_count, outside_profiles_count)
    profiles_count.rename(columns={'total': 'number of total profiles posted',
                                   'partial': 'number of outside profiles posted',
                                   'partial / total': 'outside profiles posted / total profiles posted'},
                          inplace=True)

    total_profiles_count_check_words = 'Number of total profiles posted'
    total_profiles_count_data = profiles_count[['number of total profiles posted'
                                                ]].T.sort_values('number of total profiles posted', axis=1)
    total_profiles_count_file_name = 'number of total profiles posted.csv'
    layout(total_profiles_count_check_words,
           total_profiles_count_data,
           total_profiles_count_file_name)
    plot_bar(total_profiles_count_data)

    total_profiles_statistics_check_words = 'Statistics of total profiles posted'
    total_profiles_statistics_data = profiles_count[['number of total profiles posted']].describe()
    total_profiles_statistics_file_name = 'statistics of total profiles posted.csv'
    layout(total_profiles_statistics_check_words,
           total_profiles_statistics_data,
           total_profiles_statistics_file_name)
    plot_bar(total_profiles_statistics_data.drop(index='count'), color_discrete_sequence=['red'])

    outside_profiles_count_check_words = 'Number of outside profiles posted'
    outside_profiles_count_data = profiles_count[['number of outside profiles posted'
                                                  ]].T.sort_values('number of outside profiles posted', axis=1)
    outside_profiles_count_file_name = 'number of outside profiles posted.csv'
    layout(outside_profiles_count_check_words,
           outside_profiles_count_data,
           outside_profiles_count_file_name)
    plot_bar(outside_profiles_count_data, title='number of outside profiles posted')

    outside_profiles_statistics_check_words = 'Statistics of outside profiles posted'
    outside_profiles_statistics_data = profiles_count[['number of outside profiles posted']].describe()
    outside_profiles_statistics_file_name = 'statistics of outside profiles posted.csv'
    layout(outside_profiles_statistics_check_words,
           outside_profiles_statistics_data,
           outside_profiles_statistics_file_name)
    plot_bar(outside_profiles_statistics_data.drop(index='count'), color_discrete_sequence=['green'])

    outside_profiles_by_total_rate_check_words = 'Rate of outside profiles posted by total'
    outside_profiles_by_total_rate_data = profiles_count[['outside profiles posted / total profiles posted'
                                                          ]].T.sort_values('outside profiles posted / total '
                                                                           'profiles posted', axis=1)
    outside_profiles_by_total_rate_file_name = 'rate of outside profiles posted by total.csv'
    layout(outside_profiles_by_total_rate_check_words,
           outside_profiles_by_total_rate_data,
           outside_profiles_by_total_rate_file_name)
    plot_bar(outside_profiles_by_total_rate_data)

    outside_profiles_by_total_rate_statistics_check_words = 'Statistics of outside profiles posted by total rate'
    outside_profiles_by_total_rate_statistics_data = profiles_count[['outside profiles posted / '
                                                                     'total profiles posted']].describe()
    outside_profiles_by_total_rate_statistics_file_name = 'statistics of outside profiles posted by total rate.csv'
    layout(outside_profiles_by_total_rate_statistics_check_words,
           outside_profiles_by_total_rate_statistics_data,
           outside_profiles_by_total_rate_statistics_file_name)
    plot_bar(outside_profiles_by_total_rate_statistics_data.drop(index='count'), color_discrete_sequence=['blue'])


def reactions_and_comments_analysis(total_posts):
    st.error('🙈Reactions and comments data🙊')
    reactions_and_comments = total_posts[['post id', 'reactions', 'comments']]
    reactions_and_comments['post id'] = reactions_and_comments['post id'].astype('str')
    reactions_and_comments.set_index('post id', inplace=True)
    reactions_and_comments = reactions_and_comments[~(reactions_and_comments['reactions'] == 0)]
    reactions_and_comments['comments / reactions'] = reactions_and_comments['comments'].values / \
                                                     reactions_and_comments['reactions'].values

    reactions_and_comments_check_words = 'Reactions and comments data per post'
    reactions_and_comments_data = reactions_and_comments
    reactions_and_comments_file_name = 'reactions and comments data per post.csv'
    layout(reactions_and_comments_check_words,
           reactions_and_comments_data,
           reactions_and_comments_file_name)


if __name__ == '__main__':
    group_info_file_path = './group_info.csv'
    group_post_file_path = './group_posts.csv'

    st.set_page_config(layout='wide')
    st.title('🎊Facebook Group Analysis App🎉')
    st.sidebar.success("🪂Select the section you'd like🚴")
    section_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇',
                                             ('Group Info',
                                              'Posts Data',
                                              'Profiles Posted Data',
                                              'Reactions and Comments'))

    group_info = group_info(group_info_file_path)
    total_posts, outside_posts = group_posts_info(group_post_file_path, group_info)


    if section_selectbox == 'Group Info':
        group_info_analysis(group_info)
    elif section_selectbox == 'Posts Data':
        posts_data_display(total_posts, outside_posts)
        posts_data_daily_analysis(total_posts, outside_posts)
        posts_data_analysis(total_posts, outside_posts)
    elif section_selectbox == 'Profiles Posted Data':
        posts_data_display(total_posts, outside_posts)
        profiles_data_daily_analysis(total_posts, outside_posts)
        profiles_data_analysis(total_posts, outside_posts)
    elif section_selectbox == 'Reactions and Comments':
        posts_data_display(total_posts, outside_posts)
        reactions_and_comments_analysis(total_posts)



