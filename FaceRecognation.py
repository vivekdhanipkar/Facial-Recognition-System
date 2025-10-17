import cv2
import numpy as np 
import sqlite3
from dbConnection import DatabaseConnection
db = DatabaseConnection()
import os

import datetime
import time 
from datetime import timedelta
from drowsiness_detection import slipping_detection
def mark_attend(action):
  name=""
  fname = "recognizer/trainingData.yml"
  if not os.path.isfile(fname):
    print("Please train the data first")
    exit(0)
  face_cascade = cv2.CascadeClassifier('haar.xml')
  os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
  cap = cv2.VideoCapture(0)
  recognizer = cv2.face.LBPHFaceRecognizer_create()
  recognizer.read(fname)
  while True:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # cv2.imshow('Face Recognizer',img)
    for (x,y,w,h) in faces:
      cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
      ids,conf = recognizer.predict(gray[y:y+h,x:x+w])
      #print(conf)
      print("ids:"+str(ids))
      nn=db.log(ids)  #it will return id
      for i in nn:
        name=i[0]

      morphing = slipping_detection(img,action)
      return ids,morphing
  else:
    print("Camera Busy")
  # cv2.destroyAllWindows()
  return name

