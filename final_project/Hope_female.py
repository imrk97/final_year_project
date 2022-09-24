## Title: Hope_female.py
## Name : 
## @author : Rahul Manna
## Created on : 2020-05-18 12:18:49
## Description : 

import os
import sys
import time
import tflite_runtime.interpreter as tflite
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from modules.user_info_management import reset_data
from modules.conversation import speech_text, text_speech
from num2words import num2words
import numpy as np
import json
import pickle
import random
import datetime
from datetime import date
#import object_finder

USER_DIRECTORY = "user"

#Greetings at begining
def greetMe():
    msg = []
    curr_hour = int(datetime.datetime.now().hour)
    if curr_hour >= 0 and curr_hour < 12:
        #msg = "Good Morning"
        msg.append(263)
    elif curr_hour >= 12 and curr_hour < 18:
        #msg = "Good Afternoon"
        msg.append(264)
    elif curr_hour >= 18 and curr_hour > 0:
        #msg = "Good Evening"
        msg.append(265)
    
    return msg

def run():
    s_t = speech_text()
    t_s = text_speech()

    date_today = date.today()

    stemmer = PorterStemmer()

    reply = []

    #Objects to be found
    objects = {"toothbrush": 291 ,"tooth brush": 292 ,"hair dryer": 293 ,"teddy bear": 294 ,"scissors": 295 ,"vase": 296 ,
                "clock": 297 ,"book": 298 ,"cell phone": 299 ,"mobile": 300 ,"remote": 301 ,"controller": 302 ,"mouse": 303 ,
                "potted plant": 304 ,"cake": 305 ,"donut": 306 ,"pizza": 307 ,"carrot": 308 ,"broccoli": 309 ,"orange": 310 ,
                "sandwitch": 311 ,"apple": 312 ,"banana": 313 ,"bowl": 314 ,"spoon": 315 ,"fork": 316 ,"knife": 317 ,"bottle": 318 ,
                "cup": 319 ,"tie": 320 ,"handbag": 321 ,"umbrella": 322 ,"backpack": 323 ,"car": 324}

    try:
        with open("data/response.json") as file:
            data = json.load(file)
            print("[INFO] Response file found.")

        with open("data/data.pickle", "rb") as f:
            words,labels,feature,output = pickle.load(f)
            print("[INFO] Data file found.\n------Loading...")
    except:
        print("[INFO] Some data files are missing.\n[ALERT] Aborting...")
        #t_s.speak_now("Fatal error, data files are not found. Aborting system...")
        t_s.speak_female([325])
        print("[INFO] Please make sure both 'data.pickle' and 'response.json' are present in the folder 'data'")
        sys.exit()

    try:
        interpreter = tflite.Interpreter(model_path="tflite_model/model.tflite")
    except:
        print("[INFO] Model not found.\n[ALERT] Aborting...")
        #t_s.speak_now("Fatal error, Model not found. Aborting system...")
        t_s.speak_female([326])
        print("[INFO] Please make sure 'model.tflite' is present in the folder 'tflite_model'")
        sys.exit()

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    floating_model = input_details[0]['dtype'] == np.float32

    #Answer when confidence score is very less
    #no_answer = ["I do not have an answer for this.", "I never thought that way.", "I never heard the words you said, please ask a different question."]
    no_answer = [288,289,290]

    print("before")

    #Make 'user' directory if not exists
    if not os.path.exists(f'{USER_DIRECTORY}'):
        os.mkdir(f'{USER_DIRECTORY}')

    #Initial greeting
    msg_list = greetMe()
    t_s.speak_female(msg_list)
    #time.sleep(0.3)
    t_s.speak_female([285])  #How can I help you?

    #Conversation
    while True:
        reply = []
        print("listening...")
        msg = s_t.listen(isFemale=True)                  # Get voice command from user
        query = msg[:]                      # Copy the command
        print("User : ",msg)

        if 'reset' in msg.split() or 'delete' in msg.split() or 'erase' in msg.split():
            reset_data(isFemale=True)
            msg = s_t.listen()                  # Get voice command from user
            query = msg[:]                      # Copy the command
            print("User : ",msg)

        msg = word_tokenize(msg)
        msg = [stemmer.stem(w.lower()) for w in msg if w!='?']

        bag = [0 for _ in range(len(words))]

        for i, wrd in enumerate(words):
            if wrd in msg:
                bag[i] = 1

        input_data = np.array(bag)

        if floating_model:
            input_data = np.float32(input_data)

        interpreter.set_tensor(input_details[0]['index'],[input_data])    #Feeding input to the model
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])

        results = np.squeeze(output_data)
        max_confidence_idx = np.argmax(results)                          #Output from model
        res_label = labels[max_confidence_idx]
        #print(labels[max_confidence_idx])

        # Found a desirable output label
        if results[max_confidence_idx] > 0.85:
            reply = []
            for intent in data:
                if intent["tag"] == res_label:
                    if res_label == "date":
                        #reply = str(random.choice(intent["responses"])).format(date_today.strftime("%d %B %Y"))
                        reply.append(random.choice(intent["response_id"]))
                        dt = date_today.strftime("%d %B %Y")
                        d,m,y = dt.split()
                        t_s.speak_female(reply)
                        reply[0] = num2words(int(d),to='ordinal')
                        reply.append("of")
                        #t_s.speak_female(reply,isFast=True)
                        reply.append(m)
                        reply.append(y)
                        t_s.speak_female(reply,isFast=True)
                    elif res_label == "year":
                        #reply = str(random.choice(intent["responses"])).format(date_today.year)
                        reply.append(random.choice(intent["response_id"]))
                        yr = date_today.year
                        reply.append(yr)
                        t_s.speak_female(reply,isFast=True)
                    elif res_label == "day":
                        #reply = str(random.choice(intent["responses"])).format(date_today.strftime("%A"))
                        reply.append(random.choice(intent["response_id"]))
                        dt = date_today.strftime("%A")
                        reply.append(dt)
                        t_s.speak_female(reply,isFast=True)
                    elif res_label == "time":
                        time_now = datetime.datetime.now().strftime("%I %M %p")
                        #reply = str(random.choice(intent["responses"])).format(time_now.strftime("%I:%M %p"))
                        reply.append(random.choice(intent["response_id"]))
                        h,m,mer = time_now.split()
                        if h!=0:    reply.append(int(h))
                        else:   reply.append(12)
                        if m!=0:    reply.append(int(m))
                        reply.append(mer)
                        t_s.speak_female(reply,isFast=True)                        
                    else:
                        #reply = random.choice(intent["responses"])
                        reply.append(random.choice(intent["response_id"]))
                        t_s.speak_female(reply)
                        print(intent["tag"],reply,type(reply[0]))
                        break

            print("Bot : ",reply,results[max_confidence_idx])
            
            if res_label == "search":
                reply = []
                obj = ""
                obj_id = -1
                for x in objects.keys():
                    if x in query:
                        obj = x[:]
                        obj_id = objects[x]
                        break
                if obj == "":
                    reply.append(286)
                    t_s.speak_female(reply)
                    #t_s.speak_now("Sorry! I do not recognise the object you asked for...")
                    print("Bot : Sorry! I do not recognise the object you asked for...")
                else:
                    #Found the name of the object
                    #Iintiating object detection algorithm
                    #os.system('python3 TFLite_detection_webcam.py --object_to_found='+obj)
                    ####object_finder.finder(obj)
                    #t_s.speak_now("Here is your "+obj)      #Returned the object to the user
                    reply.append(287)
                    reply.append(obj_id)
                    t_s.speak_female(reply,isFast=True)
                    
            elif res_label == "goodbye":                    # Quit Bot
                break
        else:                                               # Cound not find a desirable output
            reply = []
            #reply = random.choice(no_answer)
            reply.append(random.choice(no_answer))
            t_s.speak_female(reply)
            #t_s.speak_now(reply)
            print("Bot : ", reply, results[max_confidence_idx])
