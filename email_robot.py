# coding: utf-8
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import datetime


sender = 'firstrobot0504@outlook.com'
recipient = 'firstrobot0504@outlook.com'


def mail(sender, recipient, content):
    ret = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = 'Reminder Robot'
        msg['To'] = recipient
        msg['Subject'] = 'Proxies expiry date reminder'

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, 'Thefirstone')
        server.sendmail(sender, [recipient, ], msg.as_string())
        server.quit()
    except Exception:
        ret = False
    return ret


pd.set_option('expand_frame_repr', False)
proxies_info = pd.read_excel('./Proxies Information.xlsx')
proxies_info['Expiry Date'] = pd.to_datetime(proxies_info['Expiry Date'])
proxies_info['Today Date'] = datetime.date.today()
proxies_info['Today Date'] = pd.to_datetime(proxies_info['Today Date'])
proxies_info['Diff'] = proxies_info['Expiry Date'] - proxies_info['Today Date']

threshold_reminder = pd.Timedelta('5 days')
threshold_due = pd.Timedelta('0 days')
df_reminder = proxies_info[proxies_info['Diff'] < threshold_reminder]

if any(df_reminder):
    results = df_reminder.groupby('User')
    for result in list(results):
        recipient_name = result[0]
        filter_email = result[1].groupby('Email Address')
        email_address = None
        contents = None
        for email in list(filter_email):
            email_address = email[0]
            email_data = email[1]
            contents = f'Dear Mr {recipient_name},\n\n'
            for index in email_data.index:
                username = email_data.loc[index, 'Username']
                password = email_data.loc[index, 'Password']
                expiry_date = email_data.loc[index, 'Expiry Date']
                remaining_date = email_data.loc[index, 'Diff']
                abs_reamining_date = abs(int(str(remaining_date).split(' ')[0]))
                if remaining_date < threshold_due:
                    content = f'The proxies (username: {username}, password: {password}) have expired, ' \
                              f'and were overdue {abs_reamining_date} days.\n'
                else:
                    content = f'The proxies (username: {username}, password: {password}) will expire ' \
                              f'at {expiry_date}, there is only {remaining_date} remaining.\n'
                contents += content
            contents += '\nPlease renew the bills for these proxies as soon as possible.\n\nBest Regards,\n\nMr Robot'
            print(contents)

        if email_address:
            ret = mail(sender, email_address, contents)
            if ret:
                print('OK')
            else:
                print('Failed')
            print('OK' if ret else 'Failed')


if __name__ == '__main__':
    pass
