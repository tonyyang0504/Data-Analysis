import pandas as pd
import streamlit

import streamlit_tools
from streamlit_tools import *


st.set_page_config(layout='wide')


def concat_df(total_df, partial_df):
    df = pd.concat([total_df, partial_df], axis=1)
    df.columns = ['total', 'partial']
    df['partial / total'] = df['partial'].values / df['total'].values
    return df


st.title('🎊Facebook Group Analysis App🎉')

st.success('🐼Group members information🐻')
group_info = pd.read_csv('group_info.csv')
group_info['fetched date'] = pd.to_datetime(group_info['fetched time']).dt.normalize()
group_info['admin id'] = group_info['link'].apply(lambda x: x.split('&')[0].split('=')[-1])
group_info_duplicated = group_info.drop_duplicates(['admin id', 'group id'], keep='last', ignore_index=True)
group_admins = group_info_duplicated.groupby(['group id'])['admin id'].unique()
group_admins_count = group_info_duplicated.groupby(['group id'])['admin id'].count()
group_members_count = group_info_duplicated.drop_duplicates('group id', keep='last', ignore_index=True)['number of members']
group_members_daily_count = group_info.groupby(['fetched date', 'group id'])['number of members'].apply(lambda x: x.unique()[-1])
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
plot_line(plot_group_members_daily_count)

st.error('🐪Group posts information🦘')
total_posts = pd.read_csv('group_posts.csv')
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

st.info('🐧Posts data daily🐥')
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

total_posts_daily_statistics_check_words = 'Statistics of total posts daily'
total_posts_daily_statistcs_data = posts_daily_count.unstack()['number of total posts daily'].T.describe()
total_posts_daily_statistics_file_name = 'statistics of total posts daily.csv'
layout(total_posts_daily_statistics_check_words,
       total_posts_daily_statistcs_data,
       total_posts_daily_statistics_file_name)
plot_bar(total_posts_daily_statistcs_data.drop(index='count'))

outside_posts_daily_count_check_words = 'Number of outside posts daily'
outside_posts_daily_count_data = posts_daily_count.unstack()['number of outside posts daily'].T
outside_posts_daily_count_file_name = 'number of outside posts daily.csv'
layout(outside_posts_daily_count_check_words,
       outside_posts_daily_count_data,
       outside_posts_daily_count_file_name)
plot_area(outside_posts_daily_count_data)

outside_posts_daily_statistics_check_words = 'Statistics of outside posts daily'
outside_posts_daily_statistcs_data = posts_daily_count.unstack()['number of outside posts daily'].T.describe()
outside_posts_daily_statistics_file_name = 'statistics of outside posts daily.csv'
layout(outside_posts_daily_statistics_check_words,
       outside_posts_daily_statistcs_data,
       outside_posts_daily_statistics_file_name)
plot_bar(outside_posts_daily_statistcs_data.drop(index='count'))

outside_by_total_posts_daily_rate_check_words = 'Rate of outside posts daily by total'
outside_by_total_posts_daily_rate_data = posts_daily_count.unstack()['outside posts daily / total posts daily'].T
outside_by_total_posts_daily_rate_file_name = 'the rate of outside posts daily by total.csv'
layout(outside_by_total_posts_daily_rate_check_words,
       outside_by_total_posts_daily_rate_data,
       outside_by_total_posts_daily_rate_file_name)
plot_bar(outside_by_total_posts_daily_rate_data)

outside_by_total_posts_daily_rate_statistics_check_words = 'Statistics of outside posts daily by total rate'
outside_by_total_posts_daily_rate_statistics_data = posts_daily_count.unstack()[
                                                    'outside posts daily / total posts daily'].T.describe()
outside_by_total_posts_daily_rate_statistics_file_name = 'statistics of outside posts daily by total rate.csv'
layout(outside_by_total_posts_daily_rate_statistics_check_words,
       outside_by_total_posts_daily_rate_statistics_data,
       outside_by_total_posts_daily_rate_statistics_file_name)
plot_bar(outside_by_total_posts_daily_rate_statistics_data.drop(index='count'))

st.warning('🐬Posts data🐋')
outside_posts_count = outside_posts.groupby(['group id'])['post id'].count()
outside_posts_count.rename('number of outside posts', inplace=True)
total_posts_count = total_posts.groupby(['group id'])['post id'].count()
total_posts_count.rename('number of total posts', inplace=True)
posts_count = pd.concat([outside_posts_count, total_posts_count], axis=1)
posts_count['outside posts / total posts'] = posts_count['number of outside posts'].\
                                                        div(posts_count['number of total posts'])
total_posts_count_check_words = 'Number of total posts'
total_posts_count_data = posts_count[['number of total posts']].T
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
outside_posts_count_data = posts_count[['number of outside posts']].T
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
outside_posts_by_total_rate_data = posts_count[['outside posts / total posts']].T
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
total_profiles_count_data = profiles_count[['number of total profiles posted']].T
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
outside_profiles_count_data = profiles_count[['number of outside profiles posted']].T
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
outside_profiles_by_total_rate_data = profiles_count[['outside profiles posted / total profiles posted']].T
outside_profiles_by_total_rate_file_name = 'rate of outside profiles posted by total.csv'
layout(outside_profiles_by_total_rate_check_words,
       outside_profiles_by_total_rate_data,
       outside_profiles_by_total_rate_file_name)
plot_bar(outside_profiles_by_total_rate_data)

outside_profiles_by_total_rate_statistics_check_words = 'Statistics of outside profiles posted by total rate'
outside_profiles_by_total_rate_statistics_data = profiles_count[['outside profiles posted / total profiles posted']].describe()
outside_profiles_by_total_rate_statistics_file_name = 'statistics of outside profiles posted by total rate.csv'
layout(outside_profiles_by_total_rate_statistics_check_words,
       outside_profiles_by_total_rate_statistics_data,
       outside_profiles_by_total_rate_statistics_file_name)
plot_bar(outside_profiles_by_total_rate_statistics_data.drop(index='count'), color_discrete_sequence=['blue'])

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