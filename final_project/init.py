import os
import time
from modules.user_info_management import register_user,reset_data
from modules.conversation import speech_text, text_speech
import Hope_female
import Hope_male
import vlc

USER_DIR = "user"
WAKE_UP = "hope"

s_t = speech_text()
t_s = text_speech()

if not os.path.isdir(USER_DIR):
    os.mkdir(USER_DIR)

#Check if the user is registered to the system
if len(os.listdir(f'{USER_DIR}')) == 0:
    p = vlc.MediaPlayer("tune/start.mp3").play()
    time.sleep(7)
    t_s.speak_male("Hello!")
    t_s.speak_male("Welcome to the Project, VASU.")
    t_s.speak_male("Voice Activated Support Utility.")
    t_s.speak_male("I can help you find different household items lying on, floor.")
    time.sleep(0.1)
    t_s.speak_male("To work properly, I would like to know some detail about you.")
    reg = register_user()

print("listening secretely...")

while True:
    text = s_t.listen(give_response=False)
    if WAKE_UP in text.split():
        try:
            with open("gender.txt","r") as f:
                st = f.read()
        except:
            st = ""
            print("file not found : gender.txt\nGenerating file : gender.txt")
            with open("gender.txt","w") as f:
                f.write("male")
            print("Running Hope_male")

        if st == "female":
            print("Found female")
            vlc.MediaPlayer("tune/open.mp3").play()
            time.sleep(3)
            Hope_female.run()
        else:           #if st == "male":
            print("Found male")
            vlc.MediaPlayer("tune/open.mp3").play()
            time.sleep(3)
            Hope_male.run()