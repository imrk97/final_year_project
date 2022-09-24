# Import packages
import os
import argparse
import cv2
import numpy as np
##import sys
import time
import ffmpeg
import face_recognition
##import speech_recognition as sr
##import pyaudio
from threading import Thread
import importlib.util
import RPi.GPIO as GPIO

pos_buffer_pixel_ob = 210
pos_buffer_pixel_person= 260

def finder(object_to_find):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21,GPIO.OUT) #Video Strem Indicator
    GPIO.setup(26,GPIO.OUT) #IN1
    GPIO.setup(11,GPIO.OUT) #IN2
    GPIO.setup(23,GPIO.OUT) #IN3
    GPIO.setup(17,GPIO.OUT) #IN4
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(11,GPIO.HIGH)
    GPIO.output(23,GPIO.HIGH)
    GPIO.output(17,GPIO.HIGH)

    def blink(count = 0, t = 0.5):
        for i in range (count):
            GPIO.output(21,GPIO.LOW)
            time.sleep(t)
            GPIO.output(21,GPIO.HIGH)
            time.sleep(t)
            

    def forward(press = 0.1):
        
        GPIO.output(26,GPIO.LOW)
        GPIO.output(23,GPIO.LOW)
        time.sleep(press)
        GPIO.output(26,GPIO.HIGH)
        GPIO.output(23,GPIO.HIGH)
        return

    def backward(press = 0.1):
        
        GPIO.output(11,GPIO.LOW)
        GPIO.output(17,GPIO.LOW)
        time.sleep(press)
        GPIO.output(11,GPIO.HIGH)
        GPIO.output(17,GPIO.HIGH)
        return

    def right(press = 0.1):
        
        GPIO.output(26,GPIO.LOW)
        GPIO.output(17,GPIO.LOW)
        time.sleep(press)
        GPIO.output(26,GPIO.HIGH)
        GPIO.output(17,GPIO.HIGH)
        return

    def left(press = 0.1):
        
        GPIO.output(23,GPIO.LOW)
        GPIO.output(11,GPIO.LOW)
        time.sleep(press)
        GPIO.output(23,GPIO.HIGH)
        GPIO.output(11,GPIO.HIGH)
        return

    def position(xmin,xmax,flag): # flag : 0 for object, 1 for person
            mean_position = int((xmin+xmax)/2)
            if(flag == 0):
                if(mean_position>=640-pos_buffer_pixel_ob and mean_position<=640+pos_buffer_pixel_ob) :
                    return "middle"
                if(mean_position<=640-pos_buffer_pixel_ob) :
                    return "left"
                if(mean_position>=640+pos_buffer_pixel_ob) :
                    return "right"
            else:
                if(mean_position>=640-pos_buffer_pixel_person and mean_position<=640+pos_buffer_pixel_person) :
                    return "middle"
                if(mean_position<=640-pos_buffer_pixel_person) :
                    return "left"
                if(mean_position>=640+pos_buffer_pixel_person) :
                    return "right"

    def log(flag, xmin, xmax, ymin, ymax, typ):
            file = open("log.txt", "a")
            if(flag==1):
                file.write("Forward")
            if(flag==2):
                file.write("Left")
            if(flag==3):
                file.write("Right")
            file.write(" xmin: %s" %str(xmin)+" xmax: %s" %str(xmax)+
                       " ymin: %s" %str(ymin)+" ymax: %s" %str(ymax)+
                       " area: %s  " %str((xmax-xmin)*(ymax-ymin))+ typ + "\n\n")
            file.close
            return
    
    try:
        
        #object_to_be_found = capture_audio()

        # If tensorflow is not installed, import interpreter from tflite_runtime, else import from regular tensorflow
        pkg = importlib.util.find_spec('tensorflow')
        if pkg is None:
            from tflite_runtime.interpreter import Interpreter
        else:
            from tensorflow.lite.python.interpreter import Interpreter


        class VideoStream:
            """Camera object that controls video streaming from the Picamera"""
            def __init__(self,resolution=(480,360),framerate=30):
                
                # Initialize the PiCamera and the camera image stream
                self.stream = cv2.VideoCapture("http://192.168.0.100:2525/video")
                ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                ret = self.stream.set(3,resolution[0])
                ret = self.stream.set(4,resolution[1])
                # It will set the output for visual confirmation of videostream
                #GPIO.output(21,GPIO.HIGH)
                    
                # Read first frame from the stream
                (self.grabbed, self.frame) = self.stream.read()

            # Variable to control when the camera is stopped
                self.stopped = False

            def start(self):
            # Start the thread that reads frames from the video stream
                Thread(target=self.update,args=()).start()
                return self

            def update(self):
                # Keep looping indefinitely until the thread is stopped
                while True:
                    # If the camera is stopped, stop the thread
                    if self.stopped:
                        # Close camera resources
                        self.stream.release()
                        return

                    # Otherwise, grab the next frame from the stream
                    (self.grabbed, self.frame) = self.stream.read()

            def read(self):
            # Return the most recent frame
                return self.frame

            def stop(self):
            # Indicate that the camera and thread should be stopped
                self.stopped = True


        ########    For face detection and recognition    ########
        face_cascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")

        known_faces = []

        for name in os.listdir('user'):
            for filename in os.listdir(f"user/{name}"):
                img = cv2.imread(f"user/{name}/{filename}")
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                face_locations = face_cascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=3)
                if len(face_locations) == 1:
                    encoding = face_recognition.face_encodings(img,face_locations)[0]
                    known_faces.append(encoding)    
                #print(len(face_locations))


        ########    For object detection and recognition    #######

        object_to_be_found = object_to_find
        MODEL_NAME = "sample_model"
        GRAPH_NAME = "detect.tflite"
        LABELMAP_NAME = "labelmap.txt"

        min_conf_threshold = 0.35

        resW, resH = 1280,720                 #args.resolution.split('x')
        imW, imH = int(resW), int(resH)

        # Get path to current working directory
        CWD_PATH = os.getcwd()

        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            labels = [line.strip() for line in f.readlines()]

        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == '???':
            del(labels[0])

        # Load the Tensorflow Lite model and get details
        interpreter = Interpreter(model_path=PATH_TO_CKPT)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]

        floating_model = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5

        # Initialize video stream
        videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
        reached_obj = 0
        reached_person = False

        while (reached_obj == 0):
        
            # Grab frame from video stream
            frame1 = videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            no_obj = 0
            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((scores[i] > 0.35) and (scores[i] <= 1.0)):
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                    if object_name == object_to_be_found :
                        no_obj = 1
                        # Relative position according to pixel
                        ymin = int(max(1,(boxes[i][0] * imH)))
                        xmin = int(max(1,(boxes[i][1] * imW)))
                        ymax = int(min(imH,(boxes[i][2] * imH)))
                        xmax = int(min(imW,(boxes[i][3] * imW)))
                        if(ymax<650):
                            if(position(xmin,xmax,0)=='middle'):
                                print("forward")
                                forward(0.07)
                                log(1,xmin,xmax,ymin,ymax,"ob")
                            if(position(xmin,xmax,0)=='left'):
                                print("left")
                                left(0.05)
                                log(2,xmin,xmax,ymin,ymax,"ob")
                            if(position(xmin,xmax,0)=='right'):
                                print("right")
                                right(0.05)
                                log(3,xmin,xmax,ymin,ymax,"ob")
                        else:
                            reached_obj = 1
                            GPIO.output(21,GPIO.LOW)
                            time.sleep(1)
                            GPIO.output(21,GPIO.HIGH)
                            time.sleep(1)
                    
            if(no_obj == 0):
                print(object_to_be_found + " not found")
                right(0.05)
                
        '''while (reached_person == 0):
            # Grab frame from video stream
            frame1 = videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            no_person = 0
            reached_person=0
            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((scores[i] > 0.5) and (scores[i] <= 1.0)):
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                    if object_name == "person" :
                        no_person = 1
                        # Relative position according to pixel
                        ymin = int(max(1,(boxes[i][0] * imH)))
                        xmin = int(max(1,(boxes[i][1] * imW)))
                        ymax = int(min(imH,(boxes[i][2] * imH)))
                        xmax = int(min(imW,(boxes[i][3] * imW)))
                        area = (xmax-xmin)*(ymax-ymin)
                        if(ymax<600):
                            if(position(xmin,xmax,1)=='middle'):
                                print("forward")
                                forward(0.1)
                                log(1,xmin,xmax,ymin,ymax,"person")
                            if(position(xmin,xmax,1)=='left'):
                                print("left")
                                left(0.07)
                                log(2,xmin,xmax,ymin,ymax,"person")
                            if(position(xmin,xmax,1)=='right'):
                                print("right")
                                right(0.07)
                                log(3,xmin,xmax,ymin,ymax,"person")
                        else:
                            reached_person = 1
                            print("work done")
                            
            if(no_person == 0):
                print("no person found")
                left(0.05)'''


        ########    For face detection and recognition    ########
        while reached_person == False:
            found_person = False
            frame = videostream.read()
            frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
            face_locations = face_cascade.detectMultiScale(frame_gray,scaleFactor=1.2,minNeighbors=3)
            face_encodings = face_recognition.face_encodings(frame,face_locations)
            for location,encoding in zip(face_locations,face_encodings):
                x,y,w,h = location
                results = face_recognition.compare_faces(known_faces,encoding,tolerance=0.45)
                #print(len(results))
                if True in results:     #Found a known face
                    found_person = True
                    #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                    # Bot movement
                    area = w * h
                    if area < 500:
                        pos = position(x,x+w,1)
                        if pos == 'middle':
                            print('middle')
                            forward(0.1)
                            log(1,x,x+w,y,y+h,"person")
                        elif pos == 'left':
                            print('left')
                            left(0.7)
                            log(2,x,x+w,y,y+h,"person")
                        elif pos == 'right':
                            print('right')
                            right(0.7)
                            log(3,x,x+w,y,y+h,"person")
                    elif area >= 500 and area <=600:
                        print("Reached person")
                        reached_person = True
                        videostream.stop()
                        break
                    else:
                        print("move back")
                        #backward()
            if found_person == False:
                print("Could not find user.\nSearching again...")
                left(0.5)

        raise Exception("Work Done")

    except:
        GPIO.cleanup()
        videostream.stop()
