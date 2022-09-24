import face_recognition
import cv2
import os
from threading import Thread

face_cascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")

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

known_faces = []

for name in os.listdir('user'):
    for filename in os.listdir(f"user/{name}"):
        img = cv2.imread(f"user/{name}/{filename}")
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        face_locations = face_cascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=3)
        if len(face_locations) == 1:
            encoding = face_recognition.face_encodings(img,face_locations)[0]
            known_faces.append(encoding)    
        #print(len(face_locations))'''

# cap = cv2.VideoCapture("http://192.168.0.100:2525/video")
videostream = VideoStream(resolution=(480,360),framerate=30).start()

while True:
    frame = videostream.read()

    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    face_locations = face_cascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=3)
    face_encodings = face_recognition.face_encodings(frame,face_locations)
    for location,encoding in zip(face_locations,face_encodings):
        x,y,w,h = location
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        results = face_recognition.compare_faces(known_faces,encoding,tolerance=0.4)
        print(len(results))
        if True in results:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        else:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

    cv2.imshow("Frame",frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
videostream.stop()
cv2.destroyAllWindows()