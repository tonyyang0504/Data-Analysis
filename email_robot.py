# coding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


my_sender = 'themainrobot0504@gmail.com'
my_user = 'firstrobot0504@outlook.com'


def mail():
    ret =  True
    # try:
    msg = MIMEText('reminder', 'plain', 'utf-8')
    msg['From'] = formataddr(['Email Robot', my_sender])
    msg['To'] = formataddr(['Recipient', my_user])
    msg['Subject'] = 'Proxies expiry date reminder'

    server = smtplib.SMTP('smtp.gmail.com', 465)
    # server = smtplib.SMTP()
    # server.connect('smtp.gmail.com', 465)
    server.login(my_sender, 'Themainone')
    server.sendmail(my_sender, [my_user, ], msg.as_string())
    # server.quit()
    # except Exception:
    #     ret = False
    return ret


if __name__ == '__main__':
    ret = mail()
    if ret:
        print('OK')
    else:
        print('Failed')