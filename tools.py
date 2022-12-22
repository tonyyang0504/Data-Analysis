import smtplib
from email.mime.text import MIMEText
import os
import zipfile
import shutil
import numpy as np


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


def compress_file(dir):
    z = zipfile.ZipFile('zipfiles.zip', 'w', zipfile.ZIP_DEFLATED)
    for file in os.listdir(dir):
        z.write(os.path.join(dir, file))
    z.close()


def delete_files_and_subdirs(path):
    ls = os.listdir(path)
    for i in ls:
        i_path = os.path.join(path, i)
        if os.path.isdir(i_path):
            shutil.rmtree(i_path)
        else:
            os.remove(i_path)


def delete_files(path):
    ls = os.listdir(path)
    for i in ls:
        i_path = os.path.join(path, i)
        if os.path.isdir(i_path):
            delete_files_and_subdirs(i_path)
        else:
            os.remove(i_path)


def value_replacement(df, targeted_values):
    replacement = df.copy()
    for value in targeted_values:
        replacement = replacement.applymap(lambda x: np.nan if x == value else x)
    return replacement





