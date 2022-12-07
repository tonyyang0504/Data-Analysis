# coding: utf-8
from facebook_scraper import get_group_info
import pandas as pd
import time
import datetime
import os
import logging


logging.basicConfig(filename='C:/Facebook Groups Members Robot/task_logs.txt',
                    format='%(asctime)s %(message)s', level=logging.CRITICAL)


def df_to_csv(data, file_name):
    if not os.path.exists(f'C:/Facebook Groups Members Robot/{file_name}.csv'):
        data.to_csv(f'C:/Facebook Groups Members Robot/{file_name}.csv', index=False)
    else:
        data.to_csv(f'C:/Facebook Groups Members Robot/{file_name}.csv', index=False, header=False, mode='a')


def main(group_ids: list, cookies_files: list, last_task_group_id=None):
    success_count = 0
    error_count = 0

    if last_task_group_id in group_ids:
        group_index = group_ids.index(last_task_group_id)
    else:
        group_index = None

    for index, group_id in enumerate(group_ids):
        if isinstance(group_index, int) and (index <= group_index):
            continue

        if (int(success_count / 5) + error_count) in range(len(cookies_files)):
            cookies_index = int(success_count / 5) + error_count
        else:
            cookies_index = int(success_count / 5) + error_count - len(cookies_files)
        cookies_file = cookies_files[cookies_index]
        print(f'Using {cookies_file} to conduct the task.', datetime.datetime.now())

        try:
            group_info = get_group_info(
                group_id,
                cookies=f'C:/Facebook Groups Members Robot/cookies_formatted/{cookies_file}'
                )

            df = pd.DataFrame(group_info['other_members'])
            base_url = 'https://www.facebook.com'
            df['link'] = df['link'].apply(lambda x: base_url + x.split('groupid')[0][:-1])
            df.columns = df.columns.str.capitalize()
            df['GroupName'] = group_info['name']
            df['GroupLink'] = base_url + '/groups/' + group_info['id']
            df['Username'] = group_info['members']
            df['CreatedDate'] = datetime.datetime.now()
            df['CreatedDate'] = df['CreatedDate'].dt.round('S')
            df_to_csv(df, 'group_members')

            success_count += 1
            print(f'Completed task on group {group_id}, total {success_count} times task completed successfully.', datetime.datetime.now())
            logging.critical(group_id)
            time.sleep(600)
        except Exception as e:
            error_count += 1
            group_ids.append(group_id)
            print(f'Error: "{e}" happened on group {group_id} task, failed to conduct task {error_count} times totally.', datetime.datetime.now())
            time.sleep(600)
            continue


if __name__ == '__main__':
    report_path = 'C:/Facebook Groups Members Robot/groups_links.csv'
    cookies_files_path = 'C:/Facebook Groups Members Robot/cookies_formatted'
    task_logs_path = 'C:/Facebook Groups Members Robot/task_logs.txt'

    report = pd.read_csv(report_path, encoding='ANSI')
    group_ids = report['GroupLink'].apply(lambda x: x.split('/')[-1]).tolist()
    cookies_files = os.listdir(cookies_files_path)
    with open(task_logs_path, 'r') as f:
        lines = f.readlines()
        if lines:
            last_task_group_id = lines[-1].split(' ')[-1].strip('\n')
        else:
            last_task_group_id = None


    while True:
        main(group_ids, cookies_files, last_task_group_id)
