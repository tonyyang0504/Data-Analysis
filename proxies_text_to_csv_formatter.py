import pandas as pd

file_name = 'Webshare 70 proxies.txt'
website_name = file_name.split(' ')[0]

df = pd.read_table(f'./{file_name}',
                   sep=':',
                   header=None,
                   names=['ip',
                          'port',
                          'proxy-username',
                          'proxy-password',
                          'accounts',
                          'tagname',
                          'rotate'])

ip_and_port = df.iloc[:, 0].map(str) + ':' + df.iloc[:, 1].map(str)
df.insert(0, 'proxy-ip:port', ip_and_port)
df.drop(['ip', 'port'], axis=1, inplace=True)
df['tagname'] = website_name
df.to_csv(f"./{file_name.split('.')[0]}.csv", index=False)