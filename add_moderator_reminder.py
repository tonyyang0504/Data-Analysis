from tools import send_email
import pandas as pd
import datetime
import logging


logging.basicConfig(filename='./task_logs.txt', format='%(asctime)s %(message)s', level=logging.ERROR)


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
    recipient_name = 'Rinz'
    recipient_email_address = 'rinzi27@live.com'
    df_reminder = admins_count[admins_count['admin id'] < threshold]
    group_base_url = 'https://www.facebook.com/groups/'
    groups_urls = list(map(lambda x: group_base_url + str(x), df_reminder.index))
    content = f"Dear {recipient_name}, \n\nThis email is to notify you that the " \
              f"number of the below groups' moderators is less than 2, please arrange more moderators " \
              f"for these groups to keep 3 or more moderators in every group, Thank you!\n\n" \
              f"Group urls: {groups_urls}\n\nBest Regards, \n\n Mr. Robot"

    try:
        if any(df_reminder):
            result = send_email(sender_email_address, sender_email_password, recipient_email_address, content)
            print(f'One email has been sent successfully. '
                  f'{datetime.datetime.now()}' if result else f'Failed to send a email. {datetime.datetime.now()}')
    except Exception as e:
        print(e, datetime.datetime.now())
        logging.error(e)


if __name__ == '__main__':
    sender_email_address = 'firstrobot0504@outlook.com'
    sender_email_password = 'Thefirstone'
    group_info_path = './group_info.csv'
    threshold_reminder = 3
    run(group_info_path, sender_email_address, sender_email_password, threshold_reminder)
