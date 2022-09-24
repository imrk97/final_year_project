## Title: conversation.py
## Name : 
## @author : Rahul Manna
## Created on : 2020-05-18 14:11:23
## Description : 

import os
import random
import speech_recognition as sr
import pyttsx3
#from gtts import gTTS
#import playsound
import vlc
import time

AUDIO_DIR = "audio"

class speech_text():
    def __init__(self):
        #For listen
        self.text = ""   ####
        self.t_s = text_speech()
        self.recognizer = sr.Recognizer()


    def listen(self,isFemale=False,give_response=True):
        #print("listening...")
        while self.text == "":
            if give_response:
                vlc.MediaPlayer("tune/alert.mp3").play()
                time.sleep(0.8)
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source,duration=1)
                audio = self.recognizer.listen(source)
                try:
                    self.text = self.recognizer.recognize_google(audio,language="en-in")
                    #text = self.recognizer.recognize_sphinx(audio)
                    print(self.text)
                except:
                    self.text = ""
            if self.text == "" and give_response == True:     # Voice command was not captured
                if isFemale:
                    reply = []
                    reply.append(random.choice([327,328,329]))
                    self.t_s.speak_female(reply)
                else:
                    self.t_s.speak_male(random.choice(["Sorry, I did not get you","Please repeat what you are saying","Sorry, I could not hear you"]))
        msg = self.text.lower()
        self.text = ""
        return msg

class text_speech():
    def __init__(self):
        #For speak_male
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate',160)
        self.engine.getProperty('volume')
        self.engine.setProperty('volume',1)
        
    def speak_female(self,msg_id_list,isFast=False):#msg_id_list is a list of id referring particular audio file
        for msg_id in msg_id_list:
            if os.path.isfile(f'{AUDIO_DIR}/{msg_id}.mp3'):
                p = vlc.MediaPlayer(f'{AUDIO_DIR}/{msg_id}.mp3')
                p.play()
                time.sleep(0.2)
                length = p.get_length()/1000
                if isFast:
                    time.sleep(length-(length/1.85))
                    p.stop()
                else:
                    time.sleep(length)
                    p.stop()
            else:
                print(f'Missing audio file : {AUDIO_DIR}/{msg_id}.mp3')

    def speak_male(self,message):
        self.engine.say(message)
        self.engine.runAndWait()
    
    '''def save_audio(self,message,filename):
        self.engine.save_to_file(message,f'{AUDIO_DIR}/{filename}.mp3')
        self.engine.runAndWait()'''

"""class text_speech():
    def speak(self,message):
        self.engine = gTTS(text=message,lang="en")
        self.engine.save("file.mp3")
        playsound.playsound("file.mp3")
        time.sleep(playsound)"""