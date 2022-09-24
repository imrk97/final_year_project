#sudo pip3 install python-vlc

import vlc
import os
import time

#vlc.MediaPlayer("audio/267.mp3").play()
os.environ["VLC_VERBOSE"] = str("-1")
p = vlc.MediaPlayer("tune/open.mp3")
p.play()
time.sleep(3)
print(p.get_length())
