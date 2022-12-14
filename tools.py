import smtplib
from email.mime.text import MIMEText
import os


def send_email(sender_email_address,
               sender_email_password,
               recipient_email_address,
               content):
    try:
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = 'Reminder Robot'
        message['To'] = recipient_email_address
        message['Subject'] = 'Too less moderators'

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email_address, sender_email_password)
        server.sendmail(sender_email_address, [recipient_email_address, sender_email_address], message.as_string())
        server.quit()
        result = True
    except Exception as e:
        result = False
        print(e)
    return result


def split_csv_by_rows(df, unit_no, save_dir):
    data_no = df.shape[0]
    times = int(data_no / unit_no)

    start_row_index = 0
    for i in range(times + 1):
        end_row_index = start_row_index + unit_no
        data = df.iloc[start_row_index:end_row_index, :]
        data_name = f'{start_row_index + 1}-{end_row_index}.csv'
        file_path = os.path.join(save_dir, data_name)
        if i < times:
            data.to_csv(file_path, index=False)
            start_row_index = end_row_index
        else:
            data.to_csv(file_path, index=False)




