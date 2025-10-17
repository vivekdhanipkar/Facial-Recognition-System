from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask.globals import session
import re, os
import os.path
from os import path
import pickle, random, cv2
from dbConnection import DatabaseConnection
dc = DatabaseConnection()
# import API.composeMail as SendMail
# import API.readingMails as ReadMail
import Trainmodule
import FaceRecognation
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser
import glob
import os
import pickle
# import email_read as er
import json

import flask, flask.views
from markupsafe import Markup

from joblib import dump, load
import pickle
from flask import jsonify
import math
import sklearn
now = datetime.now()
action  = "open"
date = now.strftime("%Y-%m-%d %H:%M:%S")
import random

def action_selection():
    # Your list of strings
    string_list = ["open", "close"]
    # Select a random string from the list
    return random.choice(string_list)

def spamcheck(sentence):
    IMG_DataPath = os.path.join(os.getcwd(),'static/files')
    print(sentence)
    clf = load(IMG_DataPath+"/text-classifier.mdl")
    ss=sentence.split()
    with open(IMG_DataPath+"/mySavedDict.txt", "rb") as myFile:
        myNewPulledInDictionary = pickle.load(myFile)
    d=myNewPulledInDictionary
    features = []
    for word in d:
        features.append(ss.count(word[0]))
    resp = clf.predict([features])
    n=0
    return resp


app = Flask(__name__, template_folder='template')
app.secret_key = '5FBFBE176D56EF6F97E92972C8CD1'

app.config.update(
    DUMPING_DIR = os.path.join(os.getcwd(),'DUMPING'),
    IMG_DataPath = os.path.join(os.getcwd(),'static/dataset'),
    INBOX_FOLDER = "Inbox",
    DRAFTS_FOLDER = "Drafts",
    SPAM_FOLDER = "Spam",
    SENT_MAILS_FOLDER = "Sent"
)

def File_empty_check(fpath):  
    return len(os.listdir(fpath) ) == 0

def generate_frames(browser = True):
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
           
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # yield frame


def record_faces(name,password,mobile,email,type_):
    a=name
    path1 = app.config['IMG_DataPath']
    # model_detector='opencv_face_detector.pbtxt'
    imagePaths = [os.path.join(path1,f) for f in os.listdir(path1)]
    id=1
    ids = ""
    for imagePath in imagePaths:
        print(os.path.split(imagePath)[-1].split('.')[2])   # USer Pramod   2   .jpg
        ID = int(os.path.split(imagePath)[-1].split('.')[2])
        if ID>id:
            id=ID
    if not os.path.exists(path1):
        os.makedirs(path1)
    face_cascade = cv2.CascadeClassifier('haar.xml')
    camera = cv2.VideoCapture(0)
    cap = camera
    
    sampleNum = id+20
    while True:
      ret, img = cap.read()
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      faces = face_cascade.detectMultiScale(gray, 1.3, 5)
      for (x,y,w,h) in faces:
        id = id+1
        cv2.imwrite(app.config['IMG_DataPath']+"/User."+str(a)+"."+str(id)+".jpg",gray[y:y+h,x:x+w])
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 2)
        ids = ids+","+str(id)
        cv2.waitKey(100)
      cv2.waitKey(1)
      if id > sampleNum:
         break
    ids.lstrip(',')
    dc.db_register(id, name, email, mobile, password,type_,ids)
    cap.release()
    Trainmodule.train1()
    return redirect(url_for('login_nav'))

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect(url_for('Mailinbox'))
    else:
        return redirect(url_for('login_nav')) 

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(browser=True), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login_nav_cred',methods=['GET', 'POST'])
def login_nav_cred():
    if 'username' not in session:
        return render_template('login_credentials.html')
    else:
        return redirect(url_for('Mailinbox'))

@app.route('/login_nav',methods=['GET', 'POST'])
def login_nav():
    if 'username' not in session:
        global action
        action = action_selection()
        return render_template('login.html',action = action)
    else:
        return redirect(url_for('Mailinbox'))

@app.route('/encry_nav',methods=['GET', 'POST'])
def encry_nav():
    if 'username' not in session:
        return render_template('login.html')
    else:
        return render_template('encryptdecrypt.html')

@app.route('/encrypt_decrypt_faces',methods=['GET', 'POST'])
def encrypt_decrypt_faces():
    if 'username' not in session:
        return render_template('login.html')
    else:
        key = request.form['key']
        key_,status_=dc.get_key_status()
        msg=""
        if status_=="encrypted":
            if key==key_:
                Trainmodule.decrypt_dataset(key)
                dc.update_status(key,"decrypted")
                msg="Decrypted Successfully.."
            else:
                msg="Invalid decryption key.."
        if status_=="decrypted":
            Trainmodule.encrypt_dataset(key)
            dc.update_status(key,"encrypted")
            msg="Encrypted Successfully.."
    flash(msg)
    return render_template('encryptdecrypt.html',messages=msg)
@app.route('/clear_all',methods=['GET', 'POST'])
def clear_all():
    if 'username' not in session:
        return render_template('login.html')
    else:
        Trainmodule.all_clear()
        dc.clear_all()
        flash("All Dataset Cleared Successfully..")
        return render_template('admin_home.html')   

@app.route('/facialLogin', methods=['GET', 'POST'])
def facialLogin():
    # camera.release()
    global action
    person,morphing = FaceRecognation.mark_attend(action)
    if person>0:
        usr_email,usr_pass,type_ = dc.db_facial_login(person)
        if type_ == "criminal":
            msg='Alert! Person Detected from CRIMINAL database.'
            flash(msg)
            #return redirect(url_for('login'))
            return redirect(url_for('login_nav'))
        if not morphing:
            msg='Alert! Morphing detected.'
            flash(msg)
            #return redirect(url_for('login'))
            return redirect(url_for('login_nav'))
        session['username'] = usr_email
        session['password'] = usr_pass
        return redirect(url_for('Mailinbox'))

    else:
        return redirect(url_for('login'))
      
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        msg = '' 
        if request.method == 'POST':
            name = request.form['name'] 
            password = request.form['password'] 
            email = request.form['email']
            mobile = request.form['contactNo']
            type_ = request.form['type']
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
                msg = 'Invalid email address !'
                flash(msg)   
            elif not re.match(r'[A-Za-z0-9]+', name): 
                msg = 'Username must contain only characters and numbers !'
                flash(msg)   
            else: 
                try:
                    record_faces(name,password,mobile,email,type_)
                    msg = 'You have successfully registered!' 
                    flash(msg)
                    return redirect(url_for('MailinboxAdmin'))
                except Exception as e:
                    print(e)
        return render_template('register.html')  
    else:
        return render_template('login.html')  
    

@app.route('/register_nav', methods=['GET','POST'])
def register_nav(): 
    return render_template('register.html') 

@app.route('/login', methods=['GET','POST'])
def login(): 
    if 'username' not in session:
        if request.method == 'POST':
            username=request.form['username']
            password = request.form['password']
            if username == "admin@gmail.com" and password == "admin":
                session['username'] = username.lower()
                return redirect(url_for('MailinboxAdmin'))
            # out=dc.db_login(username,password)
            # if "yes"==out:
            #     session['username'] = username.lower()
            #     session['password'] = password
            #     flash("Login Success")
            #     return redirect(url_for('Mailinbox'))
            else:
                msg='login Failed'
                flash(msg)
                return redirect(url_for('login'))
        return render_template('login.html')  
    else:
        return redirect(url_for('MailinboxAdmin'))
   
@app.route('/ComposeMail', methods=['GET','POST'])
def ComposeMail(): 
    if request.method == 'POST':
        recipentID =  request.form['recipentID']
        Subject = request.form['Subject']
        Body = request.form['detail']
        tableName =  "send_receive"
        # SendMail.email_reporting(session['username'], session['password'],recipentID,Subject,Body)
        # _to, _from,_subject,_date,_dataFile,_folderName,tablename
        dc.db_insert(recipentID, session['username'], Subject, date ,Body ,app.config['SENT_MAILS_FOLDER'],tableName)
        flash("Mail Send to "+recipentID+" Successfully")
        return render_template('composeMail.html')
    else:
        return render_template('composeMail.html')
    

@app.route('/UserStat', methods=['GET','POST'])
def UserStat(): 
    return redirect(url_for('MailinboxAdmin'))
    # return render_template('admin_home.html')


@app.route('/ComposeMail_Draft', methods=['GET','POST'])
def ComposeMail_Draft(): 
    if request.method == 'POST':
        ID = request.form['ID']
        recipentID =  request.form['recipentID']
        Subject = request.form['Subject']
        Body = request.form['detail']
        tableName = "send_received"
        # SendMail.email_reporting(session['username'], session['password'],recipentID,Subject,Body)
        dc.db_insert(recipentID, session['username'], Subject, date ,Body ,app.config['SENT_MAILS_FOLDER'],tableName)
        flash("Message Send to "+recipentID+" Successfully")
        # dc.db_DropByID(tableName,ID)
        return render_template('composeMail.html')
    else:
        return render_template('composeMail.html')

import os
@app.route('/Mailinbox')
def Mailinbox():
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
        data = dc.db_read_inbox("send_receive",app.config['INBOX_FOLDER'],session['username'])
      
        count=0
        for i in data:
           
            resp=spamcheck(i[5][3:len(i[5])-4])
          
            if resp[0]==1:
                 count=count+1
                 print("count"+str(count))
        if count!=0:
            percentages=count/len(data)*100
        else:
            percentages=50

        return render_template('inbox.html' ,ValueOut=percentages, Usename=session['username'],data=data , location = '/'.join(""))

@app.route('/MailinboxAdmin')
def MailinboxAdmin():
    # data = [
    # (1, 'John Doe', 'john@example.com', '1234567890', 'password1'),
    # (2, 'Jane Smith', 'jane@example.com', '9876543210', 'password2'),
    
    # ]
    data  = dc.get_users()
    print(data)
    session['username'] = "admin@gmail.com"
    return render_template('admin_home.html' , Usename=session['username'], data = data )
       
@app.route('/Mailsent')
def Mailsent():
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
        tableName = "send_receive"
        data = dc.db_read(tableName,app.config['SENT_MAILS_FOLDER'],session['username'])
        return render_template('sent.html', data = data )


@app.route('/check')
def check():
    if 'username' in session:
        return render_template('check.html')
    else:
        return redirect(url_for('login_nav'))

    

@app.route('/OpenFile/<string:data>/<string:subject>/<string:emailid>')
def OpenFile(data,subject,emailid):
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
            File = data
            print(data,subject,emailid)
            #EmailID = request.form['EmailID']
            #Subject = request.form['Subject']
            location = os.path.join(app.config['DUMPING_DIR'],session['username'][0:6])
            if location:
                data=er.open_email(location,File)
                return render_template('viewMsg.html', Email = emailid, Subject = subject,data=data)
            else:
                return render_template('viewMsg.html', Email = emailid, Subject = subject,data="No Record")
                
                

@app.route('/spamCompute', methods=['GET','POST'])
def spamCompute():
    
    sentence = request.form['sentence']
    resp=spamcheck(sentence)
    if resp[0]==0:
        error="Ham Email detected. Go ahead"
        flash('Ham Email detected. Go ahead!')
        return render_template('check.html',error=sentence)
        n=20
    if resp[0]==1:
        error ="Alert!..Spam Email Detected."
        flash('Alert!..Spam Email Detected.!')
        print(error)
        return render_template('check.html',error=sentence)
        n==-59
    

@app.route('/MailDrafts' , methods=['GET','POST'])
def MailDrafts():
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
        tableName = "send_receive"
        if request.method == 'POST':
            recipentID =  request.form['recipentID']
            Subject = request.form['Subject']
            Body = request.form['detail']
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            dc.db_insert(recipentID, session['username'], Subject, date ,Body ,app.config['DRAFTS_FOLDER'],tableName)
        else:
            pass
        return render_template('drafts.html', data = dc.db_read(tableName,app.config['DRAFTS_FOLDER'],session['username']) )

@app.route('/DraftEdit/<string:DraftID>')
def DraftEdit(DraftID):
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
        tableName = session['username'][0:6]
        session['draft'] = DraftID
        return redirect(url_for('draftttt'))

    
@app.route('/draftttt')
def draftttt():
    if 'username' not in session:
        return redirect(url_for('login_nav'))
    else:
        tableName = "send_receive"
        draftid=session['draft']
        return render_template('composeMailEdit.html', Value = dc.db_read_by_id(tableName,draftid))


@app.route('/Logout')
def Logout():
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('index')) 
   
if __name__ == '__main__':  
    app.run(debug=True)
