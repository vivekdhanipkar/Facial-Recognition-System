import sys
import imaplib
import getpass
from email import policy
from email.parser import BytesParser
import datetime
import json
import eml_parser, os, fnmatch
import dbConnection as db
import glob ,random


def json_serial(obj):
  if isinstance(obj, datetime.datetime):
      serial = obj.isoformat()
      return serial

def process_mailbox(M,OUTPUT_DIRECTORY,EMAIL_FOLDER):
    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print ("No messages found!")
        return
   

    if EMAIL_FOLDER == "Drafts":
        count = random.randint(1000,50000)
    else:
        count = 0

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print ("ERROR getting message", num)
            return
        print ("Writing message ", num)
        print(data[0][0])
      
        f = open('%s/%s.eml' %(OUTPUT_DIRECTORY,count), 'wb')
        f.write(data[0][1])
        count +=1
        f.close()
   

def readMails(username,pwd,mailFolder,Location,tableName):
    IMAP_SERVER = 'imap.gmail.com'
    EMAIL_ACCOUNT = username
    EMAIL_FOLDER = mailFolder
    OUTPUT_DIRECTORY = Location
    PASSWORD = pwd
   
    db.db_create(tableName)
    
    M = imaplib.IMAP4_SSL(IMAP_SERVER)
    M.login(EMAIL_ACCOUNT, PASSWORD)
    rv, data = M.select(EMAIL_FOLDER)
    if rv == 'OK':
        print ("Processing mailbox: ", EMAIL_FOLDER)
        process_mailbox(M,OUTPUT_DIRECTORY,EMAIL_FOLDER)
        file_list = os.listdir(OUTPUT_DIRECTORY)
        for i in file_list:
            with open(OUTPUT_DIRECTORY+"/"+i, 'rb') as fhdl:
                raw_email = fhdl.read()

            ep = eml_parser.EmlParser()
            parsed_eml = ep.decode_email_bytes(raw_email)
            kk=json.dumps(parsed_eml, default=json_serial)
            person_dict = json.loads(kk)
            from_=person_dict['header']['from']
            to_=person_dict['header']['to']
            subject_=person_dict['header']['subject']
            date_=person_dict['header']['date']
            ss=i.split("RFC822")
            # print(to_[0], from_, subject_, date_,ss[0])
            try:
                db.db_insert(to_[0], from_, subject_, date_,ss[0],mailFolder,tableName)

            except Exception as e:
                print(e)
    
    else:
        print ("ERROR: Unable to open mailbox ", rv)
    M.logout()


    # Developers Credits : Balchandra Samleti | Sheela Jadhav
    # NK Orchid College of Engineering & Technology, Solapur 













