import time, logging, cv2, os, threading, bestOf
import numpy as np
import sounddevice as sd
import soundfile as sf
from PIL import ImageGrab
from pynput.keyboard import Key, KeyCode, Listener as keyboardListener
from pynput.mouse import Button as mouseButton, Controller as mouseController

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)  #end all logging messages

#global variables setup
resourceDirectory = os.path.join(os.getcwd(), 'game resources')
accept = cv2.imread(os.path.join(resourceDirectory,"dota accept button alone.png"))
techies = cv2.imread(os.path.join(resourceDirectory,"dota techies icon.png"))
uai = bestOf.userArtificialInput()
resolution = bestOf.getResolution()
banButtonLoc = bestOf.pixelScale((2000,950), resolution)
mapBox = 60,1080,360,1390
threshold = 0.9
mapWindowThread = None
closeIt = False
alarmIt = False

#creates a window containing a live feed of the dota map
def mapWindow(secondaryMonitorSize=(2560,1440)):
    global closeIt
    while not closeIt:
        #capture map image
        imz = ImageGrab.grab(bbox=mapBox)
        rgb = np.array(imz)
        npImz = cv2.cvtColor(rgb, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        #resize image
        '''h,w,_ = npImz.shape
        scale = 0.5
        fx = secondaryMonitorSize[0] * scale / w
        fy = secondaryMonitorSize[1] * scale / h
        resizedImage = cv2.resize(npImz, secondaryMonitorSize, fx=fx, fy=fy)'''
        #show image
        windowName = "Dota Map"
        cv2.namedWindow(windowName, flags=cv2.WINDOW_NORMAL)
        cv2.imshow(windowName, npImz) #resizedImage)
        #if closed, terminate image
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def selectPlaybackDevice(str="speaker", applyDefaults = True):
    devices = sd.query_devices()
    for device in devices:
        if 'speaker' in device['name'].lower() and device['max_output_channels'] > 0:
            #setup according to playback device
            if applyDefaults:
                sd.default.samplerate = device['default_samplerate']
                sd.default.device = device['name']
            # 'device' is a dictionary that contains: 
            # name, ,max_output_channels, default_samplerate, etc
            return device
       
#keyboard and mouse thread callback functions
def on_press(key):
    pass
def on_release(key):
    global closeIt
    if key == Key.esc:
        closeIt = True
        return False
    if key == KeyCode.from_char("\\"):
        #initiate map window
        global mapWindowThread
        mapWindowThread = threading.Thread(target=mapWindow, daemon=True)
        mapWindowThread.start()
    if key == KeyCode.from_char("]"):
        #toggle alarm
        global alarmIt
        alarmIt = not alarmIt
        ans = "ON" if alarmIt else "OFF"
        logging.debug(f"alarmIt is {ans}")
    
#main thread
def mane():
    logging.debug("Start")
    kl = keyboardListener(on_press=on_press, on_release=on_release)
    kl.start()
    global closeIt, mapWindowThread
    #click accept button and ban techies at the start of the game.
    while closeIt == False:
        #check for accept button
        acceptClicked = uai.clickImage(accept, threshold)
        if acceptClicked:
            logging.debug("Accept button detected.")
            time.sleep(3)
        #check techies
        techiesClicked = uai.clickImage(techies, threshold)
        if techiesClicked:
            time.sleep(0.2)
            #now click the ban button
            uai.clickMouse(pos=banButtonLoc)
            logging.debug("Techie ban detected button detected.")
            closeIt = True
        #saving computing power
        time.sleep(2)
    #setup and play notify sound as an alarm
    selectPlaybackDevice()
    #get sound file
    soundFileName = 'fire truck air horn.wav'
    sound, fs = sf.read(soundFileName, dtype='float32')
    #play sound then wait for the sound to end before the program ends
    if alarmIt:
        sd.play(sound)
        time.sleep(sound.size/sd.default.samplerate)
    closeIt = True
    #wait on map window
    try:
        mapWindowThread.join()
    except AttributeError:
        logging.error("'mapWindow' Thread was not active.")
    logging.debug('done')


if __name__ == "__main__":
    mane()
