# -*- coding: utf-8 -*-

import os
import requests
import schedule
import datetime
import pandas as pd


def generate_data_url(base_url, page_number, limit=100):
    offset = page_number * limit - limit
    url = base_url + '?sort=id&order=desc&offset=' + str(offset) + f'&limit={limit}'
    return url


def scrape_data(return_df=True):
    print(f'A new task is starting.', datetime.datetime.now())

    file_path = './total_data.csv'
    if os.path.exists(file_path):
        df_old = pd.read_csv(file_path)
        max_id = df_old['id'].max()
    else:
        df_old = pd.DataFrame()
        max_id = 0

    login_url = 'https://good.gd999.in/HjyZmOnRuT.php/index/login'
    data_base_url = 'https://good.gd999.in/HjyZmOnRuT.php/customer/lists/index'
    headers = {'x-requested-with': 'XMLHttpRequest'}
    data = {'username': ' aji1213', 'password': 'qq112233'}

    session = requests.session()
    session.post(login_url, data=data)

    df_list = []
    count = 1

    while True:
        try:
            url = generate_data_url(data_base_url, count)
            r = session.get(url, headers=headers).json()
            df = pd.DataFrame(r['rows'])

            if not any(df):
                break

            if max_id in df['id'].values:
                df = df[df['id'] > max_id]
                df_list.append(df)
                count += 1
                break
            else:
                df_list.append(df)
                count += 1
        except Exception as e:
            print(e)
            break

    df_list.append(df_old)

    total_data = pd.concat(df_list, ignore_index=True)
    total_data.drop_duplicates('id', inplace=True, ignore_index=True)
    total_data.to_csv(file_path, index=False)
    print(f'The task was carried out successfully, the total number of page scraped: {count}.', datetime.datetime.now())

    if return_df is True:
        return total_data


if __name__ == '__main__':
    schedule.every().day.at('23:23').do(scrape_data)

    while True:
        schedule.run_pending()
