# coding: utf-8
from facebook_scraper import get_posts, get_group_info
import pandas as pd
import time
import datetime
import os


def df_to_csv(data, file_name):
    if not os.path.exists(f'C:/Facebook Group Scraper/{file_name}.csv'):
        data.to_csv(f'C:/Facebook Group Scraper/{file_name}.csv', index=False, encoding='utf-8')
    else:
        data.to_csv(f'C:/Facebook Group Scraper/{file_name}.csv', index=False, header=False, mode='a', encoding='utf-8')


def main(group_ids: list, cookies_files: list):
    counts = 0
    for group_id in group_ids:
        if counts % 5 == 0:
            cookies_file = cookies_files[int(counts / 5)]
        print(cookies_file, datetime.datetime.now())

        try:
            group_info = get_group_info(
                group_id,
                cookies=f'C:/Facebook Group Scraper/cookies_formatted/{cookies_file}'
                )
            
            admins_df = pd.DataFrame(group_info['admins'])
            admins_df['group id'] = group_id
            admins_df['number of members'] = group_info['members']
            admins_df['fetched time'] = datetime.datetime.now()
            print(admins_df)
            df_to_csv(admins_df, 'group_info')

            counts += 1
            print(f'completed {counts} times', datetime.datetime.now())
            time.sleep(3600)
        except Exception as e:
            print(e, group_id, datetime.datetime.now())
            group_ids.append(group_id)
            time.sleep(3600)
            continue


if __name__ == '__main__':
    report = pd.read_excel('C:/Facebook Group Scraper/Final report.xlsx')
    group_ids = report.iloc[:, 3]
    group_ids = group_ids.map(lambda x: x.strip('/').split('/')[-1]).tolist()
    cookies_files = os.listdir('C:/Facebook Group Scraper/cookies_formatted')

    while True:
        main(group_ids, cookies_files)
