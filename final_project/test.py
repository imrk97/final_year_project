import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone(device_index=0) as source:
    recognizer.adjust_for_ambient_noise(source,duration=1)
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio,language="en-in")
    print(text)