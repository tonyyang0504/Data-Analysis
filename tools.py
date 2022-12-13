import smtplib
from email.mime.text import MIMEText


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
        server.sendmail(sender_email_address, [recipient_email_address, sender_email_password], message.as_string())
        server.quit()
        result = True
    except Exception as e:
        result = False
        print(e)
    return result




