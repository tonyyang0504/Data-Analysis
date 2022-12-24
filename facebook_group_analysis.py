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


def group_info_transform(group_info_file):
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
    group_info_duplicated_file_name = f'{group_info_duplicated_check_words.lower()}.csv'
    layout(group_info_duplicated_check_words, group_info_duplicated_data, group_info_duplicated_file_name)

    group_admins_check_words = 'Group admins id'
    group_admins_data = group_admins
    group_admins_file_name = f'{group_admins_check_words.lower()}.csv'
    layout(group_admins_check_words, group_admins_data, group_admins_file_name)

    group_admins_count_check_words = 'Number of group admins'
    group_admins_count_data = group_admins_count
    group_admins_count_file_name = f'{group_admins_count_check_words.lower()}.csv'
    layout(group_admins_count_check_words, group_admins_count_data, group_admins_count_file_name)

    group_members_count_daily_check_words = 'Number of group members daily'
    group_members_count_daily_data = plot_group_members_daily_count
    group_members_count_daily_file_name = f'{group_members_count_daily_check_words.lower()}.csv'
    layout(group_members_count_daily_check_words, group_members_count_daily_data, group_members_count_daily_file_name)
    plot_line(group_members_count_daily_data)

    group_members_count_change_daily_check_words = 'Number of group members change daily'
    group_members_count_change_daily_data = group_members_count_daily_data.diff(axis=0).dropna(how='all', axis=0)
    group_members_count_change_daily_file_name = f'{group_members_count_change_daily_check_words.lower()}.csv'
    layout(group_members_count_change_daily_check_words, group_members_count_change_daily_data, group_members_count_change_daily_file_name)
    plot_area(group_members_count_change_daily_data)
    multiselect_plot_bar('Number of selected groups members change daily', group_members_count_change_daily_data)

    plot_hist(group_members_count_change_daily_data, title=f'Distribution of {group_members_count_change_daily_check_words.lower()}')
    multiselect_plot_hist(f'Distribution of selected groups {group_members_count_change_daily_check_words.lower()}',
                          group_members_count_change_daily_data)

    group_members_count_change_daily_statistics_check_words = 'Statistics of group members change daily'
    group_members_count_change_daily_statistcs_data = group_members_count_change_daily_data.describe()
    group_members_count_change_daily_statistics_file_name = f'{group_members_count_change_daily_statistics_check_words.lower()}.csv'
    layout(group_members_count_change_daily_statistics_check_words,
           group_members_count_change_daily_statistcs_data,
           group_members_count_change_daily_statistics_file_name)
    plot_hist(group_members_count_change_daily_statistcs_data.loc['mean', :],
              title=f'Distribution of mean of {group_members_count_change_daily_check_words.lower()}')
    multiselect_plot_box(f'Quartiles of selected groups {group_members_count_change_daily_check_words.lower()}',
                         group_members_count_change_daily_data)


st.cache(suppress_st_warning=True)
def group_posts_info(group_posts_file, group_info_data):
    group_admins = group_info_data.groupby(['group id'])['admin id'].unique()
    total_posts = pd.read_csv(group_posts_file)
    total_posts['published date'] = pd.to_datetime(total_posts['published time']).dt.date
    total_posts['fetched date'] = pd.to_datetime(total_posts['fetched time']).dt.normalize()
    total_posts.drop_duplicates('post id', keep='last', inplace=True, ignore_index=True)
    total_posts.drop('likes', axis=1, inplace=True)

    try:
        reactions = total_posts['reactions'].str.strip('{}').str.split(',', expand=True).iloc[:, 0:-1]
        reactions = reactions.applymap(lambda x: x.split(':')[-1] if isinstance(x, str) else x)
        reactions.fillna(0, inplace=True)
        reactions = reactions.astype('int64')
        reactions.columns = ['like', 'love', 'haha', 'wow']
        total_posts = pd.concat([total_posts, reactions], axis=1)
    except:
        total_posts['like'] = 0
        total_posts['love'] = 0
        total_posts['haha'] = 0
        total_posts['wow'] = 0

    total_posts['reactions'] = total_posts['like'].values + total_posts['love'].values + \
                               total_posts['haha'].values + total_posts['wow'].values

    direct_posts = total_posts[total_posts['shared user id'].isna()]
    outside_posts_list = []
    for outside_data in direct_posts.groupby('group id'):
        df = outside_data[1][~outside_data[1]['user id'].isin(group_admins[outside_data[0]])]
        outside_posts_list.append(df)
    outside_posts = pd.concat(outside_posts_list)
    own_posts = total_posts[~total_posts.index.isin(outside_posts.index)]
    outside_posts.reset_index(drop=True, inplace=True)
    own_posts.reset_index(drop=True, inplace=True)
    return total_posts, outside_posts, own_posts


def posts_data_display(total_posts, outside_posts, own_posts):
    st.error('🐪Group posts information🦘')
    total_posts_check_words = 'Total posts information'
    total_posts_data = total_posts
    total_posts_file_name = f'{total_posts_check_words.lower()}.csv'
    layout(total_posts_check_words, total_posts_data, total_posts_file_name)

    outside_posts_check_words = 'Outside posts information'
    outside_posts_data = outside_posts
    outside_posts_file_name = f'{outside_posts_check_words.lower()}.csv'
    layout(outside_posts_check_words, outside_posts_data, outside_posts_file_name)

    own_posts_check_words = 'Own posts information'
    own_posts_data = own_posts
    own_posts_file_name = f'{own_posts_check_words}.csv'
    layout(own_posts_check_words, own_posts_data, own_posts_file_name)


st.cache(suppress_st_warning=True)
def data_count(total_posts, outside_posts, data_type):
    total_count = pd.DataFrame()
    outside_count = pd.DataFrame()

    if data_type == 'profiles':
        total_unique = total_posts.groupby('group id')['user id'].unique()
        outside_unique = outside_posts.groupby(['group id'])['user id'].unique()
        total_count = total_unique.map(lambda x: len(x))
        outside_count = outside_unique.map(lambda x: len(x))
    elif data_type == 'posts':
        total_count = total_posts.groupby(['group id'])['post id'].count()
        outside_count = outside_posts.groupby(['group id'])['post id'].count()
    else:
        st.error('💥Please input correct data type💥')
        st.stop()

    count = concat_df(total_count, outside_count)
    count.rename(columns={'total': f'number of total {data_type}',
                          'partial': f'number of outside {data_type}',
                          'partial / total': f'outside {data_type} / total {data_type}'},
                 inplace=True)
    diff = count[f'number of total {data_type}'].values - count[f'number of outside {data_type}'].values
    count.insert(2, f'number of own {data_type}', diff)
    return count


st.cache(suppress_st_warning=True)
def data_daily_count(total_posts, outside_posts, data_type):
    total_daily_count = pd.DataFrame()
    outside_daily_count = pd.DataFrame()

    if data_type == 'profiles':
        total_unique_daily = total_posts.groupby(['group id', 'published date'])['user id'].unique()
        outside_unique_daily = outside_posts.groupby(['group id', 'published date'])['user id'].unique()
        total_daily_count = total_unique_daily.map(lambda x: len(x))
        outside_daily_count = outside_unique_daily.map(lambda x: len(x))
    elif data_type == 'posts':
        total_daily_count = total_posts.groupby(['group id', 'published date'])['post id'].count()
        outside_daily_count = outside_posts.groupby(['group id', 'published date'])['post id'].count()
    else:
        st.error('💥Please input correct data type💥')
        st.stop()

    daily_count = concat_df(total_daily_count, outside_daily_count).fillna(0)
    daily_count.rename(columns={'total': f'number of total {data_type} daily',
                                'partial': f'number of outside {data_type} daily',
                                'partial / total': f'outside {data_type} daily / total {data_type} daily'},
                       inplace=True)
    diff = daily_count[f'number of total {data_type} daily'].values - daily_count[f'number of outside {data_type} daily'].values
    daily_count.insert(2, f'number of own {data_type} daily', diff)
    return daily_count

def data_analysis(data, data_type):
    if data_type == 'posts':
        st.warning('🦊Posts data🐱')
    elif data_type == 'profiles':
        st.info('🐧Profiles posted data🐥')
    else:
        st.error('💥Please input correct data type💥')
        st.stop()

    total_count_check_words = f'Number of total {data_type}'
    total_count_data = data[[f'number of total {data_type}']].T.sort_values(f'number of total {data_type}', axis=1)
    total_count_file_name = f'{total_count_check_words.lower()}.csv'
    layout(total_count_check_words, total_count_data, total_count_file_name)
    plot_bar(total_count_data, title=total_count_check_words)
    plot_hist(total_count_data, title=f'Distribution of {total_count_check_words.lower()}')

    total_statistics_check_words = f'Statistics of total {data_type}'
    total_statistics_data = total_count_data.T.describe()
    total_statistics_file_name = f'{total_statistics_check_words.lower()}.csv'
    layout(total_statistics_check_words, total_statistics_data, total_statistics_file_name)
    plot_box(total_count_data.T, title=f'Quartiles of number of total {data_type}')

    outside_count_check_words = f'Number of outside {data_type}'
    outside_count_data = data[[f'number of outside {data_type}']].T.sort_values(f'number of outside {data_type}', axis=1)
    outside_count_file_name = f'{outside_count_check_words.lower()}.csv'
    layout(outside_count_check_words, outside_count_data, outside_count_file_name)
    plot_bar(outside_count_data, title=outside_count_check_words)
    plot_hist(outside_count_data, title=f'Distribution of {outside_count_check_words.lower()}')

    outside_statistics_check_words = f'Statistics of outside {data_type}'
    outside_statistics_data = outside_count_data.T.describe()
    outside_statistics_file_name = f'{outside_statistics_check_words.lower()}.csv'
    layout(outside_statistics_check_words, outside_statistics_data, outside_statistics_file_name)
    plot_box(outside_count_data.T, title=f'Quartiles of {outside_count_check_words.lower()}')

    own_count_check_words = f'Number of own {data_type}'
    own_count_data = data[[f'number of own {data_type}']].T.sort_values(f'number of own {data_type}',                                                               axis=1)
    own_count_file_name = f'{own_count_check_words.lower()}.csv'
    layout(own_count_check_words, own_count_data, own_count_file_name)
    plot_bar(own_count_data, title=own_count_check_words)
    plot_hist(own_count_data, title=f'Distribution of {own_count_check_words.lower()}')

    own_statistics_check_words = f'Statistics of own {data_type}'
    own_statistics_data = own_count_data.T.describe()
    own_statistics_file_name = f'{own_statistics_check_words.lower()}.csv'
    layout(own_statistics_check_words, own_statistics_data, own_statistics_file_name)
    plot_box(own_count_data.T, title=f'Quartiles of {own_count_check_words.lower()}')

    outside_by_total_rate_check_words = f'Rate of outside {data_type} by total'
    outside_by_total_rate_data = \
    data[[f'outside {data_type} / total {data_type}']].T.sort_values(f'outside {data_type} / total {data_type}', axis=1)
    outside_by_total_rate_file_name = f'{outside_by_total_rate_check_words.lower()}.csv'
    layout(outside_by_total_rate_check_words, outside_by_total_rate_data, outside_by_total_rate_file_name)
    plot_bar(outside_by_total_rate_data, title=f'Rate of outside {data_type} by total')
    plot_hist(outside_by_total_rate_data, title=f'Distribution of {outside_by_total_rate_check_words.lower()}')

    outside_by_total_rate_statistics_check_words = f'Statistics of outside {data_type} by total rate'
    outside_by_total_rate_statistics_data = outside_by_total_rate_data.T.describe()
    outside_by_total_rate_statistics_file_name = f'{outside_by_total_rate_statistics_check_words.lower()}.csv'
    layout(outside_by_total_rate_statistics_check_words, outside_by_total_rate_statistics_data, outside_by_total_rate_statistics_file_name)
    plot_box(outside_by_total_rate_data.T, title=f'Quartiles of outside {data_type} by total rate')


def data_daily_analysis(data, data_type):
    if data_type == 'posts':
        st.success('🐬Posts data daily🐋')
    elif data_type == 'profiles':
        st.success('🦫Profiles posted data daily🦦')
    else:
        st.error('💥Please input correct data type💥')
        st.stop()

    total_daily_count_check_words = f'Number of total {data_type} daily'
    total_daily_count_data = data.unstack()[f'number of total {data_type} daily'].T
    total_daily_count_file_name = f'{total_daily_count_check_words.lower()}.csv'
    layout(total_daily_count_check_words, total_daily_count_data, total_daily_count_file_name)
    plot_area(total_daily_count_data, title=total_daily_count_check_words)
    multiselect_plot_line(f'Number of selected groups total {data_type} daily', total_daily_count_data)
    plot_hist(total_daily_count_data, title=f'Distribution of {total_daily_count_check_words.lower()}')
    multiselect_plot_hist(f'Distribution of selected groups {total_daily_count_check_words.lower()}', total_daily_count_data)

    total_daily_statistics_check_words = f'Statistics of {total_daily_count_check_words.lower()}'
    total_daily_statistcs_data = total_daily_count_data.describe()
    total_daily_statistics_file_name = f'{total_daily_statistics_check_words.lower()}.csv'
    layout(total_daily_statistics_check_words, total_daily_statistcs_data, total_daily_statistics_file_name)
    plot_hist(total_daily_statistcs_data.loc['mean', :], title=f'Distribution of mean of {total_daily_count_check_words.lower()}')
    multiselect_plot_box(f'Quartiles of selected groups {total_daily_count_check_words.lower()}', total_daily_count_data)

    outside_daily_count_check_words = f'Number of outside {data_type} daily'
    outside_daily_count_data = data.unstack()[f'number of outside {data_type} daily'].T
    outside_daily_count_file_name = f'{outside_daily_count_check_words.lower()}.csv'
    layout(outside_daily_count_check_words, outside_daily_count_data, outside_daily_count_file_name)
    plot_area(outside_daily_count_data, title=outside_daily_count_check_words)
    multiselect_plot_line(f'Number of selected groups outside {data_type} daily', outside_daily_count_data)
    plot_hist(outside_daily_count_data, title=f'Distribution of {outside_daily_count_check_words.lower()}')
    multiselect_plot_hist(f'Distribution of selected groups {outside_daily_count_check_words.lower()}', outside_daily_count_data)

    outside_daily_statistics_check_words = f'Statistics of outside {data_type} daily'
    outside_daily_statistcs_data = outside_daily_count_data.describe()
    outside_daily_statistics_file_name = f'{outside_daily_statistics_check_words.lower()}.csv'
    layout(outside_daily_statistics_check_words, outside_daily_statistcs_data, outside_daily_statistics_file_name)
    plot_hist(outside_daily_statistcs_data.loc['mean', :], title=f'Distribution of mean of {outside_daily_count_check_words.lower()}')
    multiselect_plot_box(f'Quartiles of selected groups {outside_daily_count_check_words.lower()}', outside_daily_count_data)

    own_daily_count_check_words = f'Number of own {data_type} daily'
    own_daily_count_data = data.unstack()[f'number of own {data_type} daily'].T
    own_daily_count_file_name = f'{own_daily_count_check_words.lower()}.csv'
    layout(own_daily_count_check_words, own_daily_count_data, own_daily_count_file_name)
    plot_area(own_daily_count_data, title=own_daily_count_check_words)
    multiselect_plot_line(f'Number of selected groups own {data_type} daily', own_daily_count_data)
    plot_hist(own_daily_count_data, title=f'Distribution of {own_daily_count_check_words.lower()}')
    multiselect_plot_hist(f'Distribution of selected groups {own_daily_count_check_words.lower()}', own_daily_count_data)

    own_daily_statistics_check_words = f'Statistics of own {data_type} daily'
    own_daily_statistcs_data = own_daily_count_data.describe()
    own_daily_statistics_file_name = f'{own_daily_statistics_check_words.lower()}.csv'
    layout(own_daily_statistics_check_words, own_daily_statistcs_data, own_daily_statistics_file_name)
    plot_hist(own_daily_statistcs_data.loc['mean', :], title=f'Distribution of mean of {own_daily_count_check_words.lower()}')
    multiselect_plot_box(f'Quartiles of selected groups {own_daily_count_check_words.lower()}', own_daily_count_data)

    outside_by_total_daily_rate_check_words = f'Rate of outside {data_type} daily by total'
    outside_by_total_daily_rate_data = data.unstack()[f'outside {data_type} daily / total {data_type} daily'].T
    outside_by_total_daily_rate_file_name = f'{outside_by_total_daily_rate_check_words.lower()}.csv'
    layout(outside_by_total_daily_rate_check_words, outside_by_total_daily_rate_data, outside_by_total_daily_rate_file_name)
    plot_bar(outside_by_total_daily_rate_data, title=outside_by_total_daily_rate_check_words)
    outside_by_total_daily_rate_data_hist = value_replacement(outside_by_total_daily_rate_data, [0, 1])
    plot_hist(outside_by_total_daily_rate_data_hist, title=f'Distribution of {outside_by_total_daily_rate_check_words.lower()}')
    multiselect_plot_hist(f'Distribution of rate of selected groups {outside_by_total_daily_rate_check_words.lower()}',
                          outside_by_total_daily_rate_data_hist)

    outside_by_total_daily_rate_statistics_check_words = f'Statistics of outside {data_type} daily by total rate'
    outside_by_total_daily_rate_statistics_data = outside_by_total_daily_rate_data_hist.describe()
    outside_by_total_daily_rate_statistics_file_name = f'{outside_by_total_daily_rate_statistics_check_words.lower()}.csv'
    layout(outside_by_total_daily_rate_statistics_check_words,
           outside_by_total_daily_rate_statistics_data,
           outside_by_total_daily_rate_statistics_file_name)
    plot_hist(outside_by_total_daily_rate_statistics_data.loc['mean', :],
              title=f'Distribution of mean of {outside_by_total_daily_rate_check_words.lower()}')
    multiselect_plot_box(f'Quartiles of selected groups {outside_by_total_daily_rate_check_words.lower()}',
                          outside_by_total_daily_rate_data_hist)


def reactions_and_comments_analysis(total_posts):
    st.success('🙈Reactions and comments data🙊')
    reactions_and_comments = total_posts[['post id', 'reactions', 'comments']]
    reactions_and_comments['post id'] = reactions_and_comments['post id'].astype('str')
    reactions_and_comments.set_index('post id', inplace=True)
    reactions_and_comments = reactions_and_comments[~(reactions_and_comments['reactions'] == 0)]
    reactions_and_comments['comments / reactions'] = reactions_and_comments['comments'].values / \
                                                     reactions_and_comments['reactions'].values

    reactions_and_comments_check_words = 'Reactions and comments data per post'
    reactions_and_comments_data = reactions_and_comments
    reactions_and_comments_file_name = f'{reactions_and_comments_check_words.lower()}.csv'
    layout(reactions_and_comments_check_words,
           reactions_and_comments_data,
           reactions_and_comments_file_name)
    reactions_and_comments_data_hist = value_replacement(reactions_and_comments_data, [0]).T
    plot_hist(reactions_and_comments_data_hist.loc['reactions', :], title='Distribution of reactions')
    plot_hist(reactions_and_comments_data_hist.loc['comments', :], title='Distribution of comments')
    plot_hist(reactions_and_comments_data_hist.loc['comments / reactions', :], title='Distribution of rate of comments by reactions')

    reactions_and_comments_data_statistics_check_words = 'Statistics of reactions and comments'
    reactions_and_comments_data_statistics_data = reactions_and_comments_data.describe()
    reactions_and_comments_data_statistics_file_name = 'statistics of reactions and comments.csv'
    layout(reactions_and_comments_data_statistics_check_words,
           reactions_and_comments_data_statistics_data,
           reactions_and_comments_data_statistics_file_name)


def main():
    old_group_info_file_path = './groups_data/old_groups_data/group_info.csv'
    old_group_post_file_path = './groups_data/old_groups_data/group_posts.csv'
    new_group_info_file_path = './groups_data/new_groups_data/group_info.csv'
    new_group_post_file_path = './groups_data/new_groups_data/group_posts.csv'

    st.set_page_config(layout='wide')
    st.title('🎊Facebook Group Analysis App🎉')
    st.sidebar.error("🍩Select the groups you'd like🍧")
    data_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Old Groups', 'New Groups'))
    st.sidebar.success("🪂Select the section you'd like🚴")
    section_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇',
                                             ('Group Info Analysis',
                                              'Posts Data Analysis',
                                              'Profiles Posted Data Analysis',
                                              'Reactions and Comments Analysis'))
    if section_selectbox in ['Posts Data Analysis', 'Profiles Posted Data Analysis']:
        st.sidebar.info("🎨Select data type you'd like🧩")
        type_selectbox = st.sidebar.selectbox('👇👇👇👇👇👇👇👇👇👇', ('Data Analysis', 'Data Daily Analysis'))
    else:
        type_selectbox = None

    if data_selectbox == 'Old Groups':
        group_info = group_info_transform(old_group_info_file_path)
        total_posts, outside_posts, own_posts = group_posts_info(old_group_post_file_path, group_info)
    else:
        group_info = group_info_transform(new_group_info_file_path)
        total_posts, outside_posts, own_posts = group_posts_info(new_group_post_file_path, group_info)

    if section_selectbox == 'Group Info Analysis':
        group_info_analysis(group_info)
    elif section_selectbox == 'Posts Data Analysis':
        posts_data_display(total_posts, outside_posts, own_posts)
        if type_selectbox == 'Data Analysis':
            count = data_count(total_posts, outside_posts, 'posts')
            data_analysis(count, 'posts')
        elif type_selectbox == 'Data Daily Analysis':
            daily_count = data_daily_count(total_posts, outside_posts, 'posts')
            data_daily_analysis(daily_count, 'posts')
    elif section_selectbox == 'Profiles Posted Data Analysis':
        posts_data_display(total_posts, outside_posts, own_posts)
        if type_selectbox == 'Data Analysis':
            count = data_count(total_posts, outside_posts, 'profiles')
            data_analysis(count, 'profiles')
        elif type_selectbox == 'Data Daily Analysis':
            daily_count = data_daily_count(total_posts, outside_posts, 'profiles')
            data_daily_analysis(daily_count, 'profiles')
    elif section_selectbox == 'Reactions and Comments Analysis':
        posts_data_display(total_posts, outside_posts, own_posts)
        reactions_and_comments_analysis(total_posts)

    st.snow()


if __name__ == '__main__':
    main()



