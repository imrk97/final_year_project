## Title: user_info_management.py
## Name : 
## @author : Rahul Manna
## Created on : 2020-07-27 18:43:51
## Description : 

import time
import sys
import os
import re
import random
import shutil
import cv2
import face_recognition
from modules.conversation import speech_text, text_speech
import vlc
import time

USER_DIRECTORY = "user"

class register_user():
    def __init__(self):
        self.s_t = speech_text()
        self.t_s = text_speech()
        name = self.get_name()
        self.get_picture(name)
        self.get_gender()
        self.t_s.speak_male("Congratulations! You are successfully registered to the system....")
        self.t_s.speak_male("Please wait while the system is being initiated.")
        time.sleep(2)


    def get_name(self):
        name = ""
        name_is_saved = False
        regex = r"(?:i am |i'm |myself |my name is |you can call me |it is |it's |this is |here's me |here is me |name is |the name is |)(\w+)(?:\w*)"
        self.t_s.speak_male("Please tell me your name.")
        while name_is_saved == False:
            text = self.s_t.listen()
            match = re.match(regex,text)
            if match != None:
                name = match.group(1).capitalize()
                #self.t_s.save_audio(name,name)
                self.t_s.speak_male("I have got your name as {}.".format(name))
                self.t_s.speak_male(random.choice(["Please say Yes to confirm","Do you confirm?"]))
                text = self.s_t.listen()
                if "yes" in text or "yeah" in text or "ok" in text or "okay" in text or "i do" in text or "i confirm" in text:
                    self.t_s.speak_male(random.choice(["Got it.","Alright!","Okay!"]))
                    name_is_saved = True
                    os.mkdir(f'{USER_DIRECTORY}/{name}')
                    return name
                else:
                    self.t_s.speak_male("Sorry for that, please say your name again.")
            else:
                self.t_s.speak_male("Sorry, I could not get your name, please repeat once again.")
        return ""
            
    def get_picture(self,user_name):
        saving_frame_count = -1
        curr_frame_count = 1
        saving_image = False
        face_cascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")

        image_count = 1
        self.t_s.speak_male("Now I would like to take some photographs of you. Please look at me.")
        '''known_faces = []        #encodings of known faces
        known_names = []

        for name in os.listdir(f'{USER_DIRECTORY}'):
            user_name = name
            for filename in os.listdir(f'{USER_DIRECTORY}/{name}'):
                img = face_recognition.load_image_file(f'{USER_DIRECTORY}/{name}/{filename}')
                encoding = face_recognition.face_encodings(img)[0]
                known_faces.append(encoding)
                known_names.append(name)
                break
                '''
        #Video capture
        cap = cv2.VideoCapture("http://192.168.0.100:2525/video")

        while image_count <= 6:
            ret,frame = cap.read()

            #cv2.imshow("Frame",frame)
            
            #img = frame
            
            ####No need for this part####
            #all_face_locations = face_recognition.face_locations(frame)
            #for location in all_face_locations:
            #    top,right,bottom,left = all_face_locations[0]
            #    cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)
            ####No need for this part####
            
            all_face_locations = []
            #while len(all_face_locations) != 1:
            #all_face_locations = face_recognition.face_locations(frame)

            all_face_locations = face_cascade.detectMultiScale(frame,scaleFactor=1.2,minNeighbors=3)
            
            if len(all_face_locations) < 1:
                print("Cannot detect any face")
                if curr_frame_count % 10 == 0:
                    self.t_s.speak_male("I cannot locate your face, please stay still for some moment")
            elif len(all_face_locations) > 1:
                if curr_frame_count % 10 == 0:
                    self.t_s.speak_male("Maybe one or more person are there except you, please make sure no one is there behind you.")
                    self.t_s.speak_male("This will help me recognise you properly.")
                print("More than one person detected")
            else:
                if saving_image == False:
                    ####play shutter sound####
                    vlc.MediaPlayer("tune/shutter.mp3").play()
                    time.sleep(0.8)
                    x,y,w,h = all_face_locations[0]
                    #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    print(len(all_face_locations))
                    #frame = cv2.fastNlMeansDenoisingColored(frame,None,10,10,7,21)
                    cv2.imwrite(f'{USER_DIRECTORY}/{user_name}/{image_count}.jpg',frame)
                    saving_image = True
                    saving_frame_count = curr_frame_count
                    image_count += 1
                else:
                    if curr_frame_count-saving_frame_count > 6:
                        saving_frame_count = -1
                        saving_image = False
                    

            #cv2.imshow("Original",frame)
            curr_frame_count += 1

        cap.release()
        #cv2.destroyAllWindows()

    def get_gender(self):
        f = open("gender.txt","r+")
        while True:
            self.t_s.speak_male("One last question...")
            self.t_s.speak_male("Would you like your assistant to have a male or female voice?")
            text = self.s_t.listen()
            if "female" in text:
                f.truncate()
                f.write("female")
                break
            elif "male" in text:
                f.truncate()
                f.write("male")
                break
        self.t_s.speak_male(random.choice(["Alright!","Sure! I'll keep that in mind."]))
        f.close()

def reset_data(isFemale=False):
    "Warning! This process will erase all your data from the system. Once again you have to register yourself."
    
    s_t = speech_text()
    t_s = text_speech()
    
    if isFemale:
        reply = []
        reply.append(330)
        reply.append(331)
        reply.append(332)
        t_s.speak_female(reply)
    else:
        #warning sound
        t_s.speak_male("This process will erase all your information from memory.")
        t_s.speak_male("You have to register yourself once again.")
        t_s.speak_male("Are you sure you want to delete all your data?")
    while True:
        if isFemale:
            t_s.speak_female([333])
        else:
            t_s.speak_male("Please say Yes to confirm this operation.")
        text = s_t.listen()
        if "yes" in text or "yeah" in text or "ok" in text or "okay" in text:
            if isFemale:
                t_s.speak_female([334])
            else:
                t_s.speak_male("Deleting your data...")
            
            for item in os.listdir(f'{USER_DIRECTORY}'):
                shutil.rmtree(f'{USER_DIRECTORY}/{item}')
            
            if isFemale:
                reply = []
                reply.append(335)
                reply.append(336)
                t_s.speak_female(reply)
            else:
                t_s.speak_male("All informations are deleted from the system.")
                t_s.speak_male("Switching to sleep mode.")
            sys.exit()
        else:
            if isFemale:
                t_s.speak_female([337])
            else:
                t_s.speak_male("Your data is not deleted.")
            break