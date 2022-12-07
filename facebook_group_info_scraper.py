# coding: utf-8
from facebook_scraper import get_group_info
import pandas as pd
import time
import datetime
import os
import logging


logging.basicConfig(filename='C:/Facebook Group Scraper/task_logs.txt', format='%(asctime)s %(message)s', level=logging.ERROR)


def df_to_csv(data, file_name):
    if not os.path.exists(f'C:/Facebook Group Scraper/{file_name}.csv'):
        data.to_csv(f'C:/Facebook Group Scraper/{file_name}.csv', index=False, encoding='utf-8')
    else:
        data.to_csv(f'C:/Facebook Group Scraper/{file_name}.csv', index=False, header=False, mode='a', encoding='utf-8')


def main(group_ids: list, cookies_files: list, last_task_group_id=None):
    success_count = 0
    error_count = 0

    if last_task_group_id in group_ids:
        group_index = group_ids.index(last_task_group_id)
    else:
        group_index = None
        print('last task index:', group_index, 'last task group id:', last_task_group_id)

    for  index, group_id in enumerate(group_ids):
        print('index:', index, 'group id:', group_id)
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
                cookies=f'C:/Facebook Group Scraper/cookies_formatted/{cookies_file}'
                )
            
            admins_df = pd.DataFrame(group_info['admins'])
            admins_df['group id'] = group_id
            admins_df['number of members'] = group_info['members']
            admins_df['fetched time'] = datetime.datetime.now()
            # print(admins_df)
            df_to_csv(admins_df, 'group_info')

            success_count += 1
            print(f'Completed task on group {group_id}, total {success_count} times task completed successfully.', datetime.datetime.now())
            logging.critical(group_id)
            time.sleep(3600)
        except Exception as e:
            error_count += 1
            group_ids.append(group_id)
            print(f'Error: "{e}" happened on group {group_id} task, failed to conduct task {error_count} times totally.', datetime.datetime.now())
            time.sleep(600)
            continue


if __name__ == '__main__':
    report_path = 'C:/Facebook Group Scraper/Final report.xlsx'
    cookies_files_path = 'C:/Facebook Group Scraper/cookies_formatted'
    task_logs_path = 'C:/Facebook Group Scraper/task_logs.txt'

    report = pd.read_excel(report_path)
    group_ids = report.iloc[:, 3]
    group_ids = group_ids.map(lambda x: x.strip('/').split('/')[-1]).tolist()
    cookies_files = os.listdir(cookies_files_path)
    with open(task_logs_path, 'r') as f:
        lines = f.readlines()
        if lines:
            last_task_group_id = lines[-1].split(' ')[-1].strip('\n')
        else:
            last_task_group_id = None


    while True:
        main(group_ids, cookies_files, last_task_group_id)
