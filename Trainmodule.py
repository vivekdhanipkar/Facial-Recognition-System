import os
import cv2
import numpy as np 
from PIL import Image
#recognizer = cv2.createLBPHFaceRecognizer()
# from tkinter import messagebox
import image_encry_decry as ied       
recognizer = cv2.face.LBPHFaceRecognizer_create()

path = 'static/dataset/'
path_encrypt="static/dataset/"

import os
    
from os import listdir
from os.path import isfile, join
def encrypt_dataset(key_):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    print(onlyfiles)

    
    for i in onlyfiles:
        ied.encrypt_image(i,key_)

def all_clear():
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    print(onlyfiles)
    

    
    for i in onlyfiles:
        os.remove(path+i)
        
    
def decrypt_dataset(key_):
    onlyfiles = [f for f in listdir(path_encrypt) if isfile(join(path_encrypt, f))]
    print(onlyfiles)
    if(len(onlyfiles)>0):
        for i in onlyfiles:
            ied.decrypt_image(i,key_)

if not os.path.exists('./recognizer'):
    os.makedirs('./recognizer')


def getImagesWithID():
  imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
  print(imagePaths)
  faces = []
  IDs = []
  for imagePath in imagePaths:
    faceImg = Image.open(imagePath).convert('L')
    faceNp = np.array(faceImg,'uint8')
    print(os.path.split(imagePath)[-1].split('.')[2])
    ID = int(os.path.split(imagePath)[-1].split('.')[2])
    faces.append(faceNp)
    IDs.append(ID)
  return np.array(IDs), faces

def train1():
    Ids, faces = getImagesWithID()
    recognizer.train(faces,Ids)
    recognizer.save('recognizer/trainingData.yml')
   