## Title: conversation.py
## Name : 
## @author : Rahul Manna
## Created on : 2020-05-18 14:11:23
## Description : 

import os
import vlc
import time
import random
import speech_recognition as sr
import pyttsx3
import ffmpeg
import RPi.GPIO as GPIO         #Audio Indicator

#from gtts import gTTS
#import playsound
import time
import random

AUDIO_DIR = "audio"

class speech_text():
    def __init__(self):
        #For listen
        self.text = ""   ####
        self.t_s = text_speech()
        self.recognizer = sr.Recognizer()

    def listen(self,isFemale=False):
        #print("listening...")
        while self.text == "":
            vlc.MediaPlayer("tune/alert.mp3").play()
            time.sleep(0.8)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(21,GPIO.OUT)
            GPIO.output(21,GPIO.HIGH)
            audio_input = ffmpeg.input("http://192.168.0.100:2525/audio.wav")
            audio_output = ffmpeg.output(audio_input, "file.mp3", ss=0, t=3)
            audio_output.run()
            GPIO.output(21,GPIO.LOW)
            GPIO.cleanup()
            os.system('ffmpeg -i file.mp3 -acodec pcm_s16le -ar 16000 out.wav')
            with sr.AudioFile('out.wav') as source:
                self.recognizer.adjust_for_ambient_noise(source,duration=1)
                audio = self.recognizer.listen(source)
                try:
                    self.text = self.recognizer.recognize_google(audio,language="en-in")
                    print(self.text)
                except:
                    self.text = ""
                    #self.speak("Sorry, I didn't get you")
                finally:
                    GPIO.cleanup()
                    os.system('rm -f file.mp3')
                    os.system('rm -f out.wav')
            if self.text == "":     # Voice command was not captured
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
        self.engine = pyttsx3.init("espeak")
        self.engine.setProperty('rate',160)
        self.engine.getProperty('volume')
        self.engine.setProperty('volume',1)
        #self.voices = self.engine.getProperty('voices')
        #self.engine.setProperty("voice", self.voices[17].id)

        #voices = self.engine.getProperty('voices')
        #c = 0
        #for voice in voices:
        #    c+=1
        #    print(c,". Voice:")
        #    print(" - ID: %s" % voice.id)
        #    print(" - Name: %s" % voice.name)
        #    print(" - Languages: %s" % voice.languages)
        #    print(" - Gender: %s" % voice.gender)
        #    print(" - Age: %s" % voice.age)

    def speak_female(self,msg_id_list,isFast=False):#msg_id_list is a list of id referring particular audio file
        for msg_id in msg_id_list:
            if os.path.isfile(f'{AUDIO_DIR}/{msg_id}.mp3'):
                p = vlc.MediaPlayer(f'{AUDIO_DIR}/{msg_id}.mp3')
                p.play()
                time.sleep(0.2)
                length = p.get_length()/1000
                if isFast:
                    time.sleep(length-(length/1.6))
                    p.stop()
                else:
                    time.sleep(length)
                    p.stop()
            else:
                print(f'Missing audio file : {AUDIO_DIR}/{msg_id}.mp3')

    def speak_male(self,message):
        self.engine.say(message)
        self.engine.runAndWait()

"""class text_speech():
    def speak(self,message):
        self.engine = gTTS(text=message,lang="en")
        self.engine.save("file.mp3")
        playsound.playsound("file.mp3")
        time.sleep(playsound)"""
