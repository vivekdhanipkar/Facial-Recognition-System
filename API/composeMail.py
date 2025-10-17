import smtplib , getpass

#for single email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# uname, pwd,recipentID,Subject,Body

def email_reporting(mymail,pwd,to,subject,BodyText): 

    EMAIL_ID = mymail
    print(EMAIL_ID)
    PWD = pwd
    print(PWD)
    #set up the SMTP server
    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.ehlo()

    # s.login("awsbalsamleti@gmail.com","Deep1920@") 
    s.login(str(EMAIL_ID),str(PWD))

    msg = MIMEMultipart() 
    msg['From']= EMAIL_ID
    msg['To']= to
    msg['Subject']= subject

    msg.attach(MIMEText(BodyText, 'html'))
    s.send_message(msg)
    print("Msg Sent..!")

# Note
# Go to this link and select Turn On
# https://www.google.com/settings/security/lesssecureapps

