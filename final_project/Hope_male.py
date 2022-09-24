## Title: Hope_male.py
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
    curr_hour = int(datetime.datetime.now().hour)
    if curr_hour >= 0 and curr_hour < 12:
        msg = "Good Morning"
    elif curr_hour >= 12 and curr_hour < 18:
        msg = "Good Afternoon"
    elif curr_hour >= 18 and curr_hour > 0:
        msg = "Good Evening"
        
    return msg

def run():
    s_t = speech_text()
    t_s = text_speech()

    date_today = date.today()

    stemmer = PorterStemmer()

    #Objects to be found
    objects = ["toothbrush","tooth brush","hair dryer","teddy bear","scissors","vase","clock","book","cell phone","mobile",
                "remote","controller","mouse","potted plant","cake","donut","pizza","carrot","broccoli","orange","sandwitch",
                "apple","banana","bowl","spoon","fork","knife","bottle","cup","tie","handbag","umbrella","backpack","car"]

    try:
        with open("data/response.json") as file:
            data = json.load(file)
            print("[INFO] Response file found.")

        with open("data/data.pickle", "rb") as f:
            words,labels,feature,output = pickle.load(f)
            print("[INFO] Data file found.\n------Loading...")
    except:
        print("[INFO] Some data files are missing.\n[ALERT] Aborting...")
        t_s.speak_male("Fatal error, data files are not found. Aborting system...")
        print("[INFO] Please make sure both 'data.pickle' and 'response.json' are present in the folder 'data'")
        sys.exit()

    try:
        interpreter = tflite.Interpreter(model_path="tflite_model/model.tflite")
    except:
        print("[INFO] Model not found.\n[ALERT] Aborting...")
        t_s.speak_male("Fatal error, Model not found. Aborting system...")
        print("[INFO] Please make sure 'model.tflite' is present in the folder 'tflite_model'")
        sys.exit()

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    floating_model = input_details[0]['dtype'] == np.float32

    #Answer when confidence score is very less
    no_answer = ["I do not have an answer for this.", "I never thought that way.", "I never heard the words you said, please ask a different question."]

    #Make 'user' directory if not exists
    if not os.path.exists(f'{USER_DIRECTORY}'):
        os.mkdir(f'{USER_DIRECTORY}')

    #Initial greeting
    text = greetMe()
    text = text + " How can I help you?"
    t_s.speak_male(text)

    #Conversation
    while True:
        print("listening...")
        msg = s_t.listen()                  # Get voice command from user
        query = msg[:]                      # Copy the command
        print("User : ",msg)

        if 'reset' in msg.split() or 'delete' in msg.split() or 'erase' in msg.split():
            reset_data()
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
            reply = ""
            for intent in data:
                if intent["tag"] == res_label:
                    if res_label == "date":
                        reply = str(random.choice(intent["responses"])).format(date_today.strftime("%d %B %Y"))
                    elif res_label == "year":
                        reply = str(random.choice(intent["responses"])).format(date_today.year)
                    elif res_label == "day":
                        reply = str(random.choice(intent["responses"])).format(date_today.strftime("%A"))
                    elif res_label == "time":
                        time_now = datetime.datetime.now()
                        reply = str(random.choice(intent["responses"])).format(time_now.strftime("%I:%M %p"))
                    else:
                        reply = random.choice(intent["responses"])
                        break

            t_s.speak_male(reply)
            print("Bot : ",reply,results[max_confidence_idx])
            
            if res_label == "search":
                obj = ""
                for x in objects:
                    if x in query:
                        obj = x[:]
                        break
                if obj == "":
                    t_s.speak_male("Sorry! I do not recognise the object you asked for...")
                    print("Bot : Sorry! I do not recognise the object you asked for...")
                else:
                    #Found the name of the object
                    #Iintiating object detection algorithm
                    #os.system('python3 TFLite_detection_webcam.py --object_to_found='+obj)
                    ####object_finder.finder(obj)
                    t_s.speak_male("Here is your "+obj)      #Returned the object to the user
                    
            elif res_label == "goodbye":                    # Quit Bot
                break
        else:                                               # Cound not find a desirable output
            reply = random.choice(no_answer)
            t_s.speak_male(reply)
            print("Bot : ", reply, results[max_confidence_idx])
