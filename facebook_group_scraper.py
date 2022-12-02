from facebook_scraper import get_posts, get_group_info
import pandas as pd
import time
import datetime
import os


def df_to_csv(data, file_name):
    if not os.path.exists(f'./{file_name}.csv'):
        data.to_csv(f'./{file_name}.csv', index=False, encoding='utf-8')
    else:
        data.to_csv(f'./{file_name}.csv', index=False, header=False, mode='a', encoding='utf-8')


report = pd.read_excel('./Final report.xlsx')
group_ids = report.iloc[:, 3]
group_ids = group_ids.map(lambda x: x.strip('/').split('/')[-1])

counts = 0
admins_list = []
for group_id in group_ids:
    try:
        group_post = get_posts(
            group=group_id,
            extra_info=True,
            cookies='./cookies.txt'
        )
        # group_info = get_group_info(
        #     group_id,
        #     cookies='C:/Facebook Group Scraper/New Text Document.txt'
        # )

        result_list = []
        for post in group_post:
            result = {}
            result['post id'] = post['post_id']
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
            print(result)

        pd.set_option('expand_frame_repr', False)
        post_df = pd.DataFrame(result_list)
        post_df.insert(0, 'group id', group_id)
        print(post_df)
        df_to_csv(post_df, 'group_posts')

        # admins_df = pd.DataFrame(group_info['admins'])
        # admins_df['group id'] = group_id
        # admins_list.append(admins_df)
        # print(admins_df)

        counts += 1
        print(f'completed {counts} times')
        time.sleep(1800)
    except Exception as e:
        print(e, group_id)
        continue


