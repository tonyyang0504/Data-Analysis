import pandas as pd
import os


unit_no = 70
df = pd.read_csv('./Webshare 500 proxies.csv')
print(df)
tagname = str(df['tagname'].unique()).strip("'[]'")
proxy_username = str(df['proxy-username'].unique()).strip("'[]'")

if not os.path.exists(f'./{tagname}_{proxy_username}'):
    os.makedirs(f'./{tagname}_{proxy_username}')

data_no = df.shape[0]
times = int(data_no / unit_no)

start_row_index = 0
for i in range(times + 1):
    end_row_index = start_row_index + unit_no
    data = df.iloc[start_row_index:end_row_index, :]
    if i < times:
        data.to_csv(f'./{tagname}_{proxy_username}/{start_row_index + 1}-{end_row_index}.csv', index=False)
        start_row_index = end_row_index
    else:
        data.to_csv(f'./{tagname}_{proxy_username}/{start_row_index + 1}-{start_row_index + len(data)}.csv', index=False)
