import pandas as pd
import json
import time
import os


def convert_to_timestamp(x):
    if x != 'NaT':
        r = int(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
        return r
    else:
        return 0


def format_cookies(original_file, formatted_file):
    with open(f'./cookies_original/{original_file}', 'r', encoding='utf-8-sig') as f:
        df = f.read()

    df = json.loads(df)
    data = pd.DataFrame(df)
    data = data.loc[:, ['domain', 'httpOnly', 'path', 'secure', 'expires', 'name', 'value']]
    data['expires'] = pd.to_datetime(data['expires']).astype('str')
    data['expires'] = data['expires'].apply(lambda x: convert_to_timestamp(x[:18]))
    data['secure'], data['httpOnly'] = 'TRUE', 'TRUE'

    if not os.path.exists('./cookies_formatted'):
        os.makedirs('./cookies_formatted')

    data.to_csv(f'./cookies_formatted/{formatted_file}', index=False, header=False, sep='\t')


if __name__ == '__main__':
    files = os.listdir('./cookies_original')
    for file in files:
        format_cookies(file, file)

