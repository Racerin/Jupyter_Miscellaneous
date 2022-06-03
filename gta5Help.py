import time, logging, cv2, os, threading, random, bestOf, multiprocessing, ctypes, pynput, math
import numpy as np
import sounddevice as sd
import soundfile as sf
from PIL import ImageGrab
from pynput.keyboard import Key, KeyCode, Listener as keyboardListener
from pynput.mouse import Button as mouseButton, Controller as mouseController

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)  #end all logging messages

closeIt = False
workEnable = True
uai = bestOf.userArtificialInput()

#https://stackoverflow.com/questions/53643273/how-to-keep-pynput-and-ctypes-from-clashing
#KEYS: http://www.penticoff.com/nb/kbds/ibm104kb.htm
SendInput = ctypes.windll.user32.SendInput
#key input number
W = 0x11
A = 0x1E
S = 0x1F
D = 0x20
Enter = 28
Esc = 1

# Actuals Functions
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def tapKey(hexKeyCode, duration=0):
    ReleaseKey(hexKeyCode)
    PressKey(hexKeyCode)
    time.sleep(duration/2)
    ReleaseKey(hexKeyCode)
    time.sleep(duration/2)

#keyboard and mouse thread callback functions
def on_press(key):
    pass
def on_release(key):
    global closeIt
    #print(key)
    #if key == Key.esc:
    if key == KeyCode.from_char("`"):
        closeIt = True
        return False
    if key == Key.f17:
        logging.debug("Wrestle Thread")
        wT = threading.Thread(target=wrestle)
        wT.start()
    if key == Key.f18:
        logging.debug("Random walking around")
        randomWalkT = threading.Thread(target=randomWalkAround)
        randomWalkT.start()
    '''if key == Key.f15:
        logging.debug("Horizon variance")
        randomWalkT = threading.Thread(target=flightControl)
        randomWalkT.start()'''
    if key == Key.f1:
        displayOptions()
    if key == KeyCode.from_char("-"):
        releaseSpecifics()
    if key == Key.space:
        logging.debug("Wrestle Thread closed")
        ttofwT = threading.Thread(target=temporaryTurnOffWrestleMe)
        ttofwT.start()
    if key == Key.f19:
        logging.debug("Spin wheel started.")
        spinWheelT = threading.Thread(target=spinWheel)
        spinWheelT.start()
    if key == Key.f20:
        logging.debug("Car Modified started.")
        #modifyCarT = threading.Thread(target=modifyCar)
        #modifyCarT.start()
        modifyCarSequenced()
        #modifyCar()
    if key == Key.f16:
        logging.debug("swimming straight started.")
        swimmingT = threading.Thread(target=swimming)
        swimmingT.start()
    if key == Key.f15:
        logging.debug("Helicopter forward started.")
        helicopterForward()
    if key == Key.f14:
        logging.debug("Normal Forward started.")
        normalForward()
    if key == Key.f13:
        logging.debug("Helicopter descent started.")
        helicopterDescend()

bestCompare = lambda scan, template: np.max(cv2.matchTemplate(scan, template, cv2.TM_CCOEFF_NORMED))
maxLocation = lambda a: np.unravel_index(np.argmax(a, axis=None), a.shape)

def helicopterForward():
    PressKey(W)
    PressKey(29) #left ctrl
    PressKey(80) #keypad 2
def normalForward():
    PressKey(W)
def helicopterDescend():
    PressKey(42)    #left shift
    PressKey(72)    #keypad 8

def flightControl():
    def highEnough():
        bbox = (0, 720, 2500, 721)
        imz = ImageGrab.grab(bbox=bbox)
        scan = np.array(imz)
        mono = cv2.cvtColor(scan, cv2.COLOR_RGB2GRAY)
        var = np.var(mono)
        print(f"Image variance. {var}")
    
    while not closeIt or workEnable:
        highEnough()
        time.sleep(1)

def modifyCar():
    threshold = 0.7
    sleep = lambda: time.sleep(0.01)
    sleepTime = 0.01
    boxLocation = [30, 160, 600, 500]
    imageDir = os.path.join(os.getcwd(), 'game resources')
    screenShotDir = os.path.join(os.getcwd(), 'gta 5 car garage screenshots')
    #functions
    toScan = lambda: np.array(ImageGrab.grab(bbox=boxLocation))
    scan = toScan()
    highest = lambda template: np.max(cv2.matchTemplate(scan, template, cv2.TM_CCOEFF_NORMED))
    maxPos = lambda template: maxLocation( cv2.matchTemplate(scan, template) )
    jay = lambda fileName: os.path.join(imageDir, fileName)
    createTemplate = lambda fileName: cv2.cvtColor(cv2.imread(jay(fileName)), cv2.COLOR_BGR2RGB)
    triggered = lambda npa: highest(npa) > threshold
    #move = lambda i=3: ([tapKey(W) for i in range(random.randint(1, i))])
    move = lambda: tapKey(W)
    #image holder
    sure = createTemplate('gta 5 car warehouse confirm.png')
    sorry = createTemplate('gta 5 car warehouse sorry.png')
    sorry2 = createTemplate('gta 5 car warehouse sorry2.png')
    dFree = createTemplate('gta 5 car warehouse FREE deselected.png')
    free = createTemplate('gta 5 car warehouse FREE selected.png')
    selected = createTemplate('gta 5 car warehouse selected.png')
    #direction bool
    forward = True
    scanRepeats = 0
    limit = 10
    #looping
    counter = 0
    while scanRepeats < limit and (not closeIt or workEnable):
        counter += 1
        time.sleep(0.1)
        scan = toScan()
        #action taking
        if triggered(sure):
            print('we got the (are you sure) display.')
            tapKey(Enter, duration=sleepTime)
            scanRepeats = 0
            forward = True
        #if none of the above for a good amount of time, kill function
        else:
            if forward:
                logging.debug("forward")
                #if highest(sorry2) > threshold:
                if triggered(free):
                    tapKey(Enter, duration=sleepTime)
                    forward = False
                elif triggered(sorry2):
                    forward = False
                elif triggered(dFree):
                    #move to new position
                    move()
                else:
                    tapKey(Enter, duration=sleepTime)
            else:
                logging.debug("backward")
                tapKey(Esc, duration=sleepTime)
            scanRepeats += 1
            #flip for flipping sake
            if scanRepeats % 7 == 0:
                forward = not forward

def typeSequence(dictCode, sequence, sleepTime=0.01):
    keys = list(dictCode.keys())
    for letter in sequence:
        for key in keys:
            if letter == key:
                button = dictCode[key]
                tapKey(button, duration=sleepTime)
                break

def modifyCarSequenced():
    #sequence = 'ff fdfbf ffffbbbf ff fuufufbbf dffffdfbbbbf ffffdfbbbbf'
    sequence = 'ff fdfbf ffffbbbf ff fuufufbbf ffufuffbbbbf ffufuffbbbbf'
    dictCode = {
        'f':Enter,
        'b':Esc,
        'd':S,
        'u':W,
    }
    typeSequence(dictCode, sequence)

def lesterSequence():
    sequence = 'u ure lllde'
    dictCode = {
        'e':Enter,
        #arrow keys
        'u':100,
        'r':103,
        'l':101,
        'd':102,
    }
    typeSequence(dictCode, sequence, sleepTime=0.1)

def taxiSequence():
    sequence = 'u ure llllde'
    dictCode = {
        'e':Enter,
        #arrow keys
        'u':100,
        'r':103,
        'l':101,
        'd':102,
    }
    typeSequence(dictCode, sequence, sleepTime=0.1)

class SelfDriving():
    bbox = (40,1165,394,1391)
    purpleLow = (130, 155, 230)
    purpleHigh = (145, 175, 255)
    yellowLow = (18, 155, 230)
    yellowHigh = (30, 170, 250)
    greenLow = None
    greenHigh = None
    #roadColorLow = (100, 50, 40)
    #roadColorHigh = (100, 10, 130)
    #roadColorLow = (100, 10, 40)
    #roadColorHigh = (120, 50, 130)
    roadColorLow = (100, 10, 40)
    roadColorHigh = (120, 50, 130)
    size = 3
    kernel = np.ones((size,size), np.uint8)
    def __init__(self):
        pass
        #self.purpleScanner = bestOf.BarProgress(self.bbox, self.purpleLow, self.purpleHigh)
    def scan(self):
        img = ImageGrab.grab(bbox=self.bbox)
        self.npScan = np.array(img)
        return self.npScan

    def mask(self, lowerColor, higherColor):
        self.scan()
        hsv = cv2.cvtColor(self.npScan, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lowerColor, higherColor)
        return mask
    def purpleMask(self):
        mask = self.mask(self.purpleLow, self.purpleHigh)
        return mask
    def yellowMask(self):
        mask = self.mask(self.purpleLow, self.purpleHigh)
        return mask
    def yellowPurpleMask(self):
        pMask = self.purpleMask()
        yMask = self.yellowMask()
        mask = cv2.bitwise_and(pMask, yMask)
        return mask
    def roadMask(self):
        mask = self.mask(self.roadColorLow, self.roadColorHigh)
        return mask

    def cursorAngle(self):
        self.scan()
        crop = self.npScan[155:195, 160:195]

        #create black and white border image
        borders = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        ret, borders = cv2.threshold(borders, 20, 255, cv2.THRESH_BINARY)
        borders = cv2.bitwise_not(borders)
        thick =  cv2.dilate(borders, self.kernel, iterations = 1)
        arg = np.transpose(np.nonzero(thick))
        if arg.size > 0:
            hold = cv2.fitLine(arg, cv2.DIST_L2,0,0.01,0.01)
            [vx,vy,x,y] = hold
            angle = math.atan2(vy, vx)
            degree = angle * 180 / math.pi
            print(degree)
        final = thick
        cv2.imshow('duff', final)
        return angle

    def main(self):
        while True:
            #mask = cv2.bitwise_or(self.purpleMask(), self.yellowMask())
            mask = self.roadMask()
            final = cv2.bitwise_and(self.npScan, self.npScan, mask=mask)
            cv2.imshow('duff', final)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def main2(self):
        #speed test
        oldMask = self.purpleMask()
        rows, cols = oldMask.shape
        rows_2, cols_2 = rows//2, cols//2     #half dimensions
        rowD, colD = rows_2 - 30, cols_2 - 30   #crop +- distance
        rowT, rowB = rows_2 - rowD, rows_2 + rowD
        colL, colR = cols_2 - colD, cols_2 + colD
        oldPos = np.array((rowT, colL))

        oldTime = time.monotonic()

        while True:
            try:
                time.sleep(0.2)
                newMask = self.purpleMask()

                crop = newMask[rowT:rowB, colL:colR]
                cv2.imshow('dock', crop)

                res = cv2.matchTemplate(oldMask, crop, cv2.TM_CCOEFF)

                _,_,_,oldP = cv2.minMaxLoc(res)
                newPos = np.array(oldP)
                deltaPos = newPos - oldPos

                newTime = time.monotonic()
                deltaTime = newTime - oldTime

                vel = deltaPos/deltaTime

                print(vel, 'velocity')
                #print(h)

                #update
                oldMask = newMask
                oldTime = newTime
                oldPos = newPos
                print("end")
            except:
                pass
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        #self.cursorAngle()

def swimming():
    PressKey(42)    #left shift press
    while not closeIt or workEnable:
        time.sleep(0.5)
        tapKey(W, duration=0.1)

def spinWheel():
    sImage = cv2.imread(r"C:\Users\Administrator\Dropbox\Python Codes\game resources\gta 5 S button.png")
    bbox = [100,25,160,85]
    template = cv2.cvtColor(sImage, cv2.COLOR_BGR2RGB)
    waitTime = 4.05
    #template = sImage
    while not closeIt or workEnable:
        st = time.monotonic()
        imz = ImageGrab.grab(bbox=bbox)
        npScan = np.array(imz)
        res = cv2.matchTemplate(npScan, template, cv2.TM_CCOEFF_NORMED)
        Edetected = np.max(res) > 0.95
        if Edetected:
            logging.debug("'S' Button detected.")
            et = time.monotonic()
            dt = et - st
            remainingWaitTime = waitTime - dt
            time.sleep(remainingWaitTime)
            tapKey(S)#, duration=0.1)
            logging.debug("Pressing 'S'")
            fet = time.monotonic()
            dt = fet - st
            logging.debug(f"The actual delta time was {dt}.")
            break
    logging.debug(f"The end of spinning wheel.")

def wrestle():
    logging.debug("Wrestle Start.")
    duration = 0.01
    global closeIt
    while not closeIt or workEnable:
        tapKey(A, duration=duration)
        tapKey(D, duration=duration)
    logging.debug("Wrestle Done")
#keep moving
def randomWalkAround():
    listy = (W,A,S,D)
    while not closeIt or workEnable:
        randomInt = random.randint(0,10)
        randomDuration = random.random()
        if randomInt in range(len(listy)):
            key = listy[randomInt]
            tapKey(key, duration=randomDuration)
        else:
            time.sleep(randomDuration)

#turns of wresting by making 'workEnable' false only for duration.
def temporaryTurnOffWrestleMe(duration=1):
    global workEnable
    workEnable = False
    time.sleep(duration)
    workEnable = True
def releaseWalk():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(S)
    ReleaseKey(D)
def releaseSpecifics():
    allThem = [
        range(2,12),
        range(16,26),
        range(30,39),
        (42,54,29),
        range(44,51),
    ]
    def ReleaseIt(something):
        for item in allThem:
            if isinstance(item, list):
                ReleaseIt(item)
            elif isinstance(item, int):
                ReleaseKey(item)
    ReleaseIt(allThem)

def releaseAll():
    excepts = [1]
    [ReleaseKey(i) for i in range(106) if i not in excepts]    #release all keys
def displayOptions():
    logging.info('''These are your options. Press:
F1 - to display options again
F17 - to initiate wrestling bot.
Space - to close wrestling bot.
F18 - to randomly move about.
F19 - to initiate 4 second delay to spin wheel.
F20 - to modify car quickly in car warehouse.
F13 - to descend in helicopter or swim simply.
F14 - to move forward normally.
F15 - to helicopter move forward.
 ` - to close program. ''')
#F15 - To get the variance of the horizon.

#main thread
def mane():
    logging.info("gta5Help.py began")
    displayOptions()
    kt = keyboardListener(on_press=on_press, on_release=on_release)
    kt.start()
    kt.join()
    releaseWalk()
    releaseAll()
    logging.info("Bye Bye.")

if __name__ == "__main__":
    mane()
