import RPi.GPIO as GPIO
import termios, sys , tty
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(26,GPIO.OUT) #IN1
GPIO.setup(11,GPIO.OUT) #IN2
GPIO.setup(23,GPIO.OUT) #IN3
GPIO.setup(17,GPIO.OUT) #IN4
GPIO.output(26,GPIO.HIGH)
GPIO.output(11,GPIO.HIGH)
GPIO.output(23,GPIO.HIGH)
GPIO.output(17,GPIO.HIGH)


def forward(press = 0.1):
    GPIO.output(21,GPIO.HIGH)
    GPIO.output(26,GPIO.LOW)
    GPIO.output(23,GPIO.LOW)
    time.sleep(press)
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(23,GPIO.HIGH)
    GPIO.output(21,GPIO.LOW)
    return

def backward(press = 0.1):
    GPIO.output(21,GPIO.HIGH)
    GPIO.output(11,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    time.sleep(press)
    GPIO.output(11,GPIO.HIGH)
    GPIO.output(17,GPIO.HIGH)
    GPIO.output(21,GPIO.LOW)
    return

def right(press = 0.1):
    GPIO.output(21,GPIO.HIGH)
    GPIO.output(26,GPIO.LOW)
    GPIO.output(17,GPIO.LOW)
    time.sleep(press)
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(17,GPIO.HIGH)
    GPIO.output(21,GPIO.LOW)
    return

def left(press = 0.1):
    GPIO.output(21,GPIO.HIGH)
    GPIO.output(23,GPIO.LOW)
    GPIO.output(11,GPIO.LOW)
    time.sleep(press)
    GPIO.output(23,GPIO.HIGH)
    GPIO.output(11,GPIO.HIGH)
    GPIO.output(21,GPIO.LOW)
    return

def _getch():
   fd = sys.stdin.fileno()
   old_settings = termios.tcgetattr(fd)
   try:
      tty.setraw(fd)
      ch = sys.stdin.read(1)     #This number represents the length
   finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
   return ch

def test():
    for x in range():
        forward()
        print(x)
    return 0

counter=0;

while(counter<10000):
    
    getch = _getch()

    if(getch=="w"):
        forward()
        
    if(getch=="a"):
        left()
        
    if(getch=="s"):
        backward()
        
    if(getch=="d"):
        right()
        
    if(getch=="y"):
        test()

    if(getch=="p"):
        break
    
    
GPIO.cleanup()