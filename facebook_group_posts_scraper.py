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
            group_post = get_posts(
                group=group_id,
                extra_info=True,
                page_limit=None,
                cookies=f'C:/Facebook Group Scraper/cookies_formatted/{cookies_file}'
                )
            # group_info = get_group_info(group_id)

            result_list = []
            for post in group_post:
                result = {}
                result['post id'] =  post['post_id']
                result['post url'] = post['post_url']
                result['user id'] = post['user_id']
                result['username'] = post['username']
                result['comments'] = post['comments']
                result['reactions'] = post['reactions']
                result['likes'] = post['likes']
                result['shares'] = post['shares']
                result['shared user id'] = post['shared_user_id']
                result['shared username'] = post['shared_username']
                result['shared post url'] = post['shared_post_url']
                result['published time'] = post['time']
                result['fetched time'] = datetime.datetime.now()
                result_list.append(result)
            
            pd.set_option('expand_frame_repr', False)
            post_df = pd.DataFrame(result_list)
            post_df.insert(0, 'group id', group_id)
            # post_df.insert(1, 'number of members', group_info['members'])
            print(post_df)
            df_to_csv(post_df, 'group_posts')

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