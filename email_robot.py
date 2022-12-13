# coding: utf-8
import smtplib
import time
from email.mime.text import MIMEText
import pandas as pd
import datetime
import schedule


def mail(sender_email_adderss, sender_email_password, recipient_email_address, content):
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = 'Reminder Robot'
        msg['To'] = recipient_email_address
        msg['Subject'] = 'Proxies expiry reminder'

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email_adderss, sender_email_password)
        server.sendmail(sender_email_adderss, [recipient_email_address, sender_email_adderss], msg.as_string())
        server.quit()
        ret = True
    except Exception as e:
        ret = False
        print(e)
    return ret


def get_data(path):
    df = pd.read_excel(path)
    df['Expiry Date'] = pd.to_datetime(df['Expiry Date'])
    df['Today Date'] = datetime.date.today()
    df['Today Date'] = pd.to_datetime(df['Today Date'])
    df['Diff'] = df['Expiry Date'] - df['Today Date']
    return df


def run(path, sender_email_address, sender_email_password, threshold):
    proxies_info = get_data(path)
    df_reminder = proxies_info[proxies_info['Diff'] < threshold]
    try:
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
                    contents = f'Dear {recipient_name},\n\n'
                    for index in email_data.index:
                        username = email_data.loc[index, 'Username']
                        password = email_data.loc[index, 'Password']
                        expiry_date = email_data.loc[index, 'Expiry Date']
                        remaining_date = email_data.loc[index, 'Diff']
                        reamining_days = remaining_date.days
                        if reamining_days < 0:
                            content = f'The proxies (username: {username}, password: {password}) have expired, ' \
                                    f'and are overdue {abs(reamining_days)} days.\n'
                        else:
                            content = f'The proxies (username: {username}, password: {password}) will expire ' \
                                    f'on {expiry_date.date()}, there are only {remaining_date.days} days remaining.\n'
                        contents += content
                    contents += '\nPlease renew the bills for these proxies as soon as possible.' \
                                '\n\nBest Regards,\n\nMr Robot'
                if email_address:
                    send_email = mail(sender_email_address, sender_email_password, email_address, contents)
                    print(f'One email has been sent successfully. {datetime.datetime.now()}' if send_email else f'Failed to send a email. {datetime.datetime.now()}')
    except Exception as e:
        print(e, datetime.datetime.now())


if __name__ == '__main__':
    sender_email_address = 'firstrobot0504@outlook.com'
    sender_email_password = 'Thefirstone'
    path = './Proxies Information.xlsx'
    threshold_reminder = pd.Timedelta('7 days')
    # schedule.every().day.at('23:11').do(run, path, sender_email_address, password, threshold_reminder)
    # schedule.every().day.do(run, path, sender_email_address, password, threshold_reminder)

    while True:
        # schedule.run_pending()
        run(path, sender_email_address, sender_email_password, threshold_reminder)
        time.sleep(60 * 60 * 24)
