import smtplib
import cris_logger as logger
import logging
import configparser
#subject ="error"
#body = "error"
config = configparser.ConfigParser()
config.read('config.ini')
gmail_user = config['gmail'].get('user')
gmail_password = config['gmail'].get('pass')

sent_from = gmail_user
to = config['gmail'].get('emailto')
subject = logger.subject
body = logger.body

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print ('Email sent!')
except Exception as e:
    logging.critical("EMAIL ERROR : " + str(e))
