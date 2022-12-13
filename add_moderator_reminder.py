from tools import send_email
import pandas as pd


pd.set_option('expand_frame_repr', False)
def get_data(path):
    group_info = pd.read_csv(path)
    group_info['fetched date'] = pd.to_datetime(group_info['fetched time']).dt.normalize()
    group_info['admin id'] = group_info['link'].apply(lambda x: x.split('&')[0].split('=')[-1])
    group_info.sort_values('fetched date', inplace=True)

    grouped = group_info.groupby(['fetched date'])
    group_list = []
    for group in grouped:
        group_list.append(group[1])

    lastest_group_info = group_list[-1].drop_duplicates(['admin id', 'group id'], keep='last', ignore_index=True)
    lastest_group_count = lastest_group_info.groupby('group id').count()
    return lastest_group_count


def run(path, sender_email_address, sender_email_password, threshold):
    admins_count = get_data(path)
    df_reminder = admins_count[admins_count['admin id'] < 3]

