import pandas as pd

from streamlit_tools import *


def concat_df(total_df, partial_df):
    df = pd.concat([total_df, partial_df], axis=1)
    df.columns = ['total', 'partial']
    df['partial / total'] = df['partial'].values / df['total'].values
    return df

pd.set_option('expand_frame_repr', False)
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
total_posts['reactions'] = total_posts['like'].values + total_posts['love'].values + total_posts['haha'].values + total_posts['wow'].values
total_posts['likes'].fillna(0, inplace=True)
total_posts['likes'] = total_posts['likes'].astype('int64')
print(total_posts)

group_info = pd.read_csv('group_info.csv')
group_info['fetched date'] = pd.to_datetime(group_info['fetched time']).dt.normalize()
group_info['user id'] = group_info['link'].apply(lambda x: x.split('&')[0].split('=')[-1])
group_info_duplicated = group_info.drop_duplicates(['user id', 'group id'], keep='last', ignore_index=True)
group_info_admins = group_info_duplicated.groupby(['group id'])['user id'].unique()
group_info_count = group_info_duplicated.groupby(['group id'])['user id'].count()
print(group_info)
print(group_info_duplicated)
print(group_info_count)
print(group_info_admins)

exit()

direct_posts = total_posts[total_posts['shared user id'].isna()]
outside_posts_list = []
for outside_data in direct_posts.groupby('group id'):
    df = outside_data[1][~outside_data[1]['user id'].isin(group_info_admins[outside_data[0]])]
    outside_posts_list.append(df)
outside_posts = pd.concat(outside_posts_list, ignore_index=True)
print(outside_posts)

total_daily_posts_count = total_posts.groupby(['group id', 'published date'])['post id'].count()
outside_daily_posts_count = outside_posts.groupby(['group id', 'published date'])['post id'].count()
print(total_daily_posts_count)
print(outside_daily_posts_count)

daily_posts_count = concat_df(total_daily_posts_count, outside_daily_posts_count).fillna(0)
daily_posts_count = daily_posts_count.rename(columns={'total': 'number of total daily posts',
                                                      'partial': 'number of outside daily posts',
                                                      'partial / total': 'outside daily posts / total daily posts'})
print(daily_posts_count)
plot_area(daily_posts_count.unstack()['number of total daily posts'].T,
         title='number of total daily posts')
plot_area(daily_posts_count.unstack()['number of outside daily posts'].T,
         title='number of outside daily posts')
plot_bar(daily_posts_count.unstack()['outside daily posts / total daily posts'].T,
          barmode='group',
         title='outside daily posts / total daily posts')

total_profiles_unique = total_posts.groupby('group id')['user id'].unique()
total_profiles_count = total_profiles_unique.map(lambda x: len(x))
print(total_profiles_count)

outside_profiles_unique = outside_posts.groupby(['group id'])['user id'].unique()
outside_profiles_count = outside_profiles_unique.map(lambda x: len(x))
print(outside_profiles_count)

profiles_count = concat_df(total_profiles_count, outside_profiles_count)
profiles_count.rename(columns={'total': 'number of total profiles posted',
                               'partial': 'number of outside profiles posted',
                               'partial / total': 'outside profiles posted / total profiles posted'},
                      inplace=True)
print(profiles_count.T)
plot_bar(profiles_count[['number of total profiles posted']].T,
         title='number of total profiles posted')
plot_bar(profiles_count[['number of outside profiles posted']].T,
         title='number of outside profiles posted')
plot_bar(profiles_count[['outside profiles posted / total profiles posted']].T,
         title='outside profiles posted / total profiles posted')

outside_posts_count = outside_posts.groupby(['group id'])['post id'].count()
outside_posts_count.rename('number of outside posts', inplace=True)
total_posts_count = total_posts.groupby(['group id'])['post id'].count()
total_posts_count.rename('number of total posts', inplace=True)

posts_count = pd.concat([outside_posts_count, total_posts_count], axis=1)
posts_count['outside posts / total posts'] = posts_count['number of outside posts'].\
                                                        div(posts_count['number of total posts'])
print(posts_count)

plot_bar(posts_count[['number of total posts']].T,
         title='number of total posts')
plot_bar(posts_count[['number of outside posts']].T,
         title='number of outside posts')
plot_bar(posts_count[['outside posts / total posts']].T,
         title='outside posts / total posts')


reactions_and_comments = total_posts[['post id', 'reactions', 'comments']]
reactions_and_comments['post id'] = reactions_and_comments['post id'].astype('str')
reactions_and_comments.set_index('post id', inplace=True)
reactions_and_comments = reactions_and_comments[~(reactions_and_comments['reactions'] == 0)]
reactions_and_comments['comments / reactions'] = reactions_and_comments['comments'].values / \
                                                 reactions_and_comments['reactions'].values
print(reactions_and_comments)
plot_bar(reactions_and_comments[['comments']])
plot_bar(reactions_and_comments[['comments']], color_discrete_sequence=['green'])
plot_bar(reactions_and_comments[['comments / reactions']], color_discrete_sequence=['blue'])
