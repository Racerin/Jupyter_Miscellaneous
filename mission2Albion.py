from functools import partial
import os, json, sounddevice, time, math, random, scipy, threading, logging
import numpy as np
from PIL import Image, ImageGrab
from pynput.keyboard import Key, Listener as keyboardListener
from pynput.mouse import Button as mouseButton, Controller as mouseController, Listener as mouseListener

logging.basicConfig(level=logging.DEBUG,
filename= 'dotaHelp.txt',
format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Start of program")
#logging.disable(logging.CRITICAL)  #end all logging messages

def clusterFind(reservoir, threshold = 1):
    #reservoir - list of tuple pairs representing coordinates
    def diff(tup1, tup2):
        #returns true or not if tuples are within thresshold magnitude
        ind = range(len(tup1))
        c2 = sum(((tup1[i] - tup2[i])**2) for i in ind) #pythoagoras theorem
        return False if c2 > threshold**2 else True
    #container for each cluster found
    clusters = []
    while len(reservoir) > 0:
        first = reservoir.pop()
        activeCluster = [first]
        checkNum = 0
        while checkNum < len(activeCluster):
            tester = activeCluster[checkNum]
            for henny in reservoir:
                if diff(tester, henny):
                    activeCluster.append(henny)
                    reservoir.remove(henny)
            checkNum += 1
        clusters.append(activeCluster)
    logging.debug(len(clusters))

#fishing does not take into account depth to fishing area
class Fishing:
    folderName = 'albionCheatFish'
    jsonFileName = 'jay son.txt'
    cancel = False
    print("Initiating")
    #image organise
    boxSize = (128, 72)
    mouse = mouseController()
    #fishBalanceBox = (1187, 662, 1374, 756)
    fishBalanceLine = (1134,736,1425,737)
    fishBalancePeakThreshold = 200
    fishBalanceStdThreshold = 20
    rnm = random.randrange
    #main execute
    def __init__(self):
        '''
        Initiate Fishing bot
        '''
        self.deviationLimit = 8

    def run2(self):
        with keyboardListener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    def run(self):
        while True:
            self.fishIt()
    def fishIt(self):
        #cast fishing rod
        self.castRod()
        #confirm cast into water
        if self.fishBite():
            self.balance()
        #reset fishing
        time.sleep(2.5)

    def cancelCommand(self):
        self.cancel = True
        raise SystemExit
    def castRod(self, startupTime=2, duration=1.5):
        #time to place mouse
        print("Begin castRod")
        time.sleep(startupTime)
        pos = [num + self.rnm(3) for num in self.mouse.position]
        self.mouse.position = pos
        #check to see if there is holding down
        self.mouse.release(mouseButton.left)
        time.sleep(0.05)
        #hold down LB to cast
        self.mouse.press(mouseButton.left)
        time.sleep(duration)
        self.mouse.release(mouseButton.left)
        #done
        print("End castRod")
    def fishBite(self):
        mousePos = self.mouse.position
        boxLocation = (mousePos[0]-self.boxSize[0]//2, mousePos[1]-self.boxSize[1]//2, mousePos[0]+self.boxSize[0]//2, mousePos[1]+self.boxSize[1]//2)
        print("Start recoginising if fish.")
        time.sleep(2)
        ans = False
        toStartTime = time.monotonic()
        holdDown = True
        templateImg = Image.open("float in water.jpg")
        npTemplate = np.array(templateImg)
        imz = ImageGrab.grab(bbox=boxLocation)
        npImz = np.asarray(imz)
        dic = corr2D(npImz, npTemplate, channels=[0])
        yHold = dic["yPeak"]
        while holdDown and not self.cancel:
            imz = ImageGrab.grab(bbox=boxLocation)
            npImz = np.asarray(imz)
            dik = corr2D(npImz, npTemplate, channels=[0])
            y = dik["yPeak"]
            print(abs(y-yHold), "y Drift away.")
            holdDown = holdDown and abs(y-yHold) < self.deviationLimit# and dik["meanRoot"] > 25
        print(time.monotonic() - toStartTime, "How long it took to recognise fish.")
        ans = True
        return ans
    def balance(self):
        logging.info("Balancing Now.")
        #initiate 1st press
        holdDown = True
        #press button to engage balancing.
        self.clickMouse()
        #wait a moment for balance bar to surely pop up.
        time.sleep(0.2)
        #begin analysing bar
        while holdDown and not self.cancel:
            imgLine = ImageGrab.grab(bbox=self.fishBalanceLine)
            npLine = np.array(imgLine)
            linear = npLine[:,:,1].flatten()    #looking at green channel
            maxi = np.max(linear)
            wherePeak = np.where(linear==maxi)
            stdz = np.std(linear)
            if stdz > self.fishBalanceStdThreshold and wherePeak > self.fishBalancePeakThreshold:
                box = self.fishBalanceLine
                xPortion = wherePeak/(box[2] - box[0])
                if xPortion > 0.5:
                    self.mouse.release(mouseButton.left)
                else:
                    self.mouse.release(mouseButton.left)
                    self.mouse.press(mouseButton.left)
            else:
                logging.info("Fishing done.")
                holdDown = False
                self.mouse.release(mouseButton.left)

    def on_press(self, key):
        print(f"{key} pressed..")
        self.fishIt()
    def on_release(self, key):
        print(f"{key} released.")
        if key == Key.esc:
            pass
        else:
            #raise SystemExit
            self.fishIt()

    def clickMouse(self, pos=None, dur=0.1):
        logging.debug(pos, "Pos")
        if pos != None:
            self.mouse.position = pos
        self.mouse.release(mouseButton.left)
        self.mouse.press(mouseButton.left)
        time.sleep(dur)
        self.mouse.release(mouseButton.left)
            
    def updateJson(self, dic):
        #load json
        oldJson = self.loadJsonSettings()
        #get dict
        oldDict = json.loads(oldJson)
        #update dict with dic
        oldDict.update(dic)
        #save json
        folderPath = os.path.join(os.getcwd(), self.folderName)
        jsonDir = os.path.join(folderPath, self.jsonFileName)
        with open(jsonDir, 'w+', encoding='utf-8') as jsonFile:
            jsonStr = json.dumps(oldDict)
            jsonFile.write(jsonStr)

    def loadJsonSettings(self):
        #get directory for program and json file
        folderPath = os.path.join(os.getcwd(), self.folderName)
        #obtain json file directory
        jsonDir = os.path.join(folderPath, self.jsonFileName)
        jsonStr = ''
        #ensure file exists
        if os._exists(jsonDir):
            with open(jsonDir, 'r', encoding='utf-8') as jsonFile:
                jsonStr = jsonFile.read()
                #add values from json file to class object
                newDict = json.loads(jsonStr)
                for k, v in newDict:
                    setattr(self, k, v)
        else:
            #else just create json txt file
            with open(jsonDir, 'w+', encoding='utf-8') as jsonFile:
                pass
        return jsonStr


def corr2D(npScan, npTemplate, channels=[0,1,2], steps=1):
    startTime = time.monotonic()
    assert np.ndim(npScan) == np.ndim(npTemplate), f"The dimensions don't equate. Shapes: {npScan.shape} vs {npTemplate.shape}"
    #correlate
    chans = []
    for num in channels:
        npScanChannel = npScan[0:-1:steps, 0:-1:steps, num]
        npTemplateChannel = npTemplate[0:-1:steps, 0:-1:steps, num]
        ch = signal.correlate2d(npScanChannel - npScanChannel.mean(), npTemplateChannel - npTemplateChannel.mean(), mode="same")
        chans.append(ch)
    chanz = np.stack(chans)
    products = np.prod(chanz, axis=0)
    yPeak, xPeak = np.unravel_index(np.argmax(products), products.shape)  # find the match
    print(products.shape, "product shape")
    meanRoot = math.sqrt(np.amax(products)/products.size)
    dict = {
        "meanRoot":meanRoot,
        "xPeak":xPeak*steps,
        "yPeak":yPeak*steps
        }
    print(dict, "dict")
    print(time.monotonic()-startTime, "This is how long corr2D took to complete.")
    return dict
def corr2D3(npScan, npTemplate, channels=[0,1,2], steps=1):
    startTime = time.monotonic()
    assert np.ndim(npScan) == np.ndim(npTemplate), f"The dimensions don't equate. Shapes: {npScan.shape} vs {npTemplate.shape}"
    #correlate
    chans = []
    for num in channels:
        npScanChannel = npScan[:,:,num]
        npTemplateChannel = npTemplate[:,:,num]
        if isinstance(npTemplateChannel, np.ndarray):
            pass
        else:
            npTemplateChannel = npTemplate[:,num]
        ch = signal.correlate2d(npScanChannel - npScanChannel.mean(), npTemplateChannel - npTemplateChannel.mean(), mode="same")
        chans.append(ch)
    chanz = np.stack(chans)
    products = np.prod(chanz, axis=0)
    yPeak, xPeak = np.unravel_index(np.argmax(products), products.shape)  # find the match
    print(products.shape, "product shape")
    dict = {
        "xPeak":xPeak,
        "yPeak":yPeak
        }
    print(dict, "dict")
    print(time.monotonic()-startTime, "This is how long corr2D took to complete.")
    return dict

def corr2D2(npScan, npTemplate, thresshold, channels=[0,1,2]):
    startTime = time.monotonic()
    assert np.ndim(npScan) == np.ndim(npTemplate), f"The dimensions don't equate. Shapes: {npScan.shape} vs {npTemplate.shape}"
    #correlate
    chans = []
    for num in channels:
        npScanChannel = npScan[:,:,num]
        npTemplateChannel = npTemplate[:,:,num]
        if isinstance(npTemplateChannel, np.ndarray):
            pass
        else:
            npTemplateChannel = npTemplate[:,num]
        ch = signal.correlate2d(npScanChannel - npScanChannel.mean(), npTemplateChannel - npTemplateChannel.mean(), mode="same")
        chans.append(ch)
    chanz = np.stack(chans)
    products = np.prod(chanz, axis=0)
    hProd,wProd = products.shape
    yPeak, xPeak = np.unravel_index(np.argmax(products), products.shape)  # find the match
    print(products.shape, "product shape")
    coordinates = []
    countPixels = 0
    for h in range(hProd):
        for w in range(wProd):
            if products[h,w] > thresshold:
                coordinates.append((h,w))
                countPixels += 1
    xAvg, yAvg = 0,0
    if len(coordinates ) > 0:
        xAvg = sum((tup[0] for tup in coordinates))//countPixels
        yAvg = sum((tup[1] for tup in coordinates))//countPixels
    dict = {
        "xAverage":xAvg,
        "yAverage":yAvg,
        "xPeak":xPeak,
        "yPeak":yPeak,
        "count":countPixels
        }
    print(dict, "dict")
    print(time.monotonic()-startTime, "This is how long corr2D took to complete.")
    return dict

def createFolder(folderName = "albionCheatInfo", oldPath = os.getcwd(), setcwd = True):
    '''creates a folder and returns its path
    by default, creates folder of name 'folderName' in current directory 
    and changes 'current work directory' to that directory
    '''
    #new directory string
    newDir = os.path.join(oldPath, folderName)
    #if directory doesn't exist, create it
    try:
        os.makedirs(newDir)
    except FileExistsError:
        print(f"'{newDir}' existed already.")
    #set or dont set current work directory to new directory
    if setcwd:
        os.chdir(newDir)
    return newDir

def screenResolution():
    #return tuple of screen resolution
    im = ImageGrab.grab()
    return im.size
def clamp(num, minimum=0, maximum=1, throwError=False):
    #return a number clamped between minimum and maximum
    assert isinstance(num, (float, int)), 'This is not a number.'
    assert maximum>=minimum, 'The minimum is greater than the maximum.'
    oldNum = num
    num = max(minimum, num)
    num = min(maximum, num)
    if throwError and oldNum != num:
        raise ValueError(f'The number {oldNum} was clamped between {min} and {max}.')
    return num
def boxClamp(outerBox, innerBox):
    '''
    returns an inner box with geometry clamped in the larger box
    input arguments are tuples with elements:
    (left, top, right, buttom)
    '''
    innerBoxWidth = innerBox[2] - innerBox[0]
    innerBoxHeight = innerBox[3] - innerBox[1]
    outerBoxWidth = outerBox[2] - outerBox[0]
    outerBoxHeight = outerBox[3] - outerBox[1]
    widths = [innerBoxWidth, innerBoxHeight, outerBoxWidth, outerBoxHeight]
    for i in widths:
        assert i > 0, "The box dimension was not set up properly."
    assert outerBoxWidth >= innerBoxWidth, 'The inner box is wider than the outer box.'
    assert outerBoxHeight >= innerBoxHeight, 'The inner box is wider than the outer box.'
    #the return elements of tuple
    left =      clamp(innerBox[0], outerBox[0], outerBox[2] - innerBoxWidth)
    top =       clamp(innerBox[1], outerBox[1], outerBox[3] - innerBoxHeight)
    right =     clamp(innerBox[2], outerBox[0] + innerBoxWidth, outerBox[2])
    bottom =    clamp(innerBox[3], outerBox[1] + innerBoxHeight, outerBox[3])
    #NOT TESTED
    return (left, top, right, bottom)
def linearInterpolateArray(x, xArray, yArray):
    lowerX = None
    higherX = None
    lowerY = None
    higherY = None
    length = len(xArray)
    for i in range(length):
        numX = xArray[i]
        numY = yArray[i]
        if x > numX:
            lowerX = numX
            lowerY = numY
        elif x < numX:
            higherX = numX
            higherY = numY
        elif x == numX:
            return numY
        if isinstance(lowerX, (int, float)) and isinstance(higherX, (int, float)):
            y = linearInterpolate(x, lowerX, higherX, lowerY, higherY)
            return y
def linearInterpolate(x, x1 = None, x2 = None, y1 = None, y2 = None, xRange=None, yRange=None):
    xRange = xRange if isinstance(xRange, (float, int)) else x2-x1
    yRange = yRange if isinstance(yRange, (float, int)) else y2-y1
    y = yRange*(x-x1)/xRange + y1
    return y
def subPicGen(image=ImageGrab.grab(), subSize=72, overLap=0, dictQ=False, delAfter=True):
    rez = image.size
    gen = subResGen(rez, subSize, overLap)
    os.chdir(os.path.join(os.getcwd(), "dat"))
    for tup in gen:
        subImage = image.crop(tup)
        if dictQ:
            dict = {
                'image':subImage,
                'dimensions':tup
            }
            yield dict
        else:
            yield subImage
        subImage.close()
def subResGen(resolution, subSize, overLap=0):
    #create a generator that returns left, top, right, bottom resolution for each sub image of a bigger image
    #error correction
    if isinstance(subSize, tuple):
        assert all(isinstance(i, int) for i in subSize), "'subSize' does not contain all intergers."
        assert len(subSize) == 2, "subSize is not a 2 member tuple."
    elif isinstance(subSize, int):
        subSize = (subSize, subSize)
    else:
        raise TypeError("subSize is not an interger.")
    if isinstance(overLap, tuple):
        assert all(isinstance(i, int) for i in overLap), "'overLap' does not contain all intergers."
        assert len(overLap) == 2, "overLap is not a 2 member tuple."
    elif isinstance(overLap, int):
        overLap = (overLap, overLap)
    else:
        raise TypeError("overLap is not an interger.")
    if isinstance(resolution, tuple):
        assert all(isinstance(i, int) for i in resolution), "resolution does not contain all intergers."
        assert len(resolution) == 2, "resolution is not a 2 member tuple."
    else:
        raise TypeError("Resolution is not a tuple of intergers.")
    #iterate through columns then rows nested
    for a in range(0,resolution[1], subSize[1] - overLap[1]):
        top = a
        #bottom = min(top + subSize[1], resolution[1] - 1) 
        bottom = min(top + subSize[1], resolution[1]) 
        for b in range(0,resolution[0], subSize[0] - overLap[0]):
            left = b
            right = min(left + subSize[0], resolution[0] - 1) 
            ans = (left, top, right, bottom)
            yield ans
def loopDifference(centerNumber, number, loopLimit=1, negativeIncluded=True):
    #returns the closest a number is to the center number given 'number' is a loop (0<x<1, 0=1)
    minArray = [abs(centerNumber-number), abs(centerNumber-(number + loopLimit))]
    if negativeIncluded:
        minArray.append(abs(centerNumber - (number-loopLimit)))
    ans = min(minArray)
    return ans
def screenShotSpeedTest():
    #basically 70ms per image
    import time
    startTime = time.monotonic()
    for i in range(60):
        img = ImageGrab.grab()
        print(np.array(img))
    endTime = time.monotonic()
    diffTime = endTime-startTime
    print(diffTime)

## add points of bobbin for fishing
#store pixel values based on duration of hold down, angle and mouse position (mouse position used to save the bobbin location)
import json, math
fileName = 'albionFishThrow.json'
mouse = mouseController()
dic = {}
center = (1280,690)

def on_move(x, y):
    #print('Pointer moved to {0}'.format((x, y)))
    global dic
    dic.mousePosition = mouse.position()
def on_click(x, y, button, pressed):
    #print('{0} at {1}'.format('Pressed' if pressed else 'Released',(x, y)))
    global dic
    if pressed:
        dic.pressTime = time.monotonic()
    else:
        dic.releaseTime = time.monotonic()
def on_scroll(x, y, dx, dy):
    #print('Scrolled {0}'.format((x, y)))
    return False
def on_press(key):
    #print('{0} pressed'.format(key))
    if key.char == 'u':
        undoIt()
    if key.char == 'v':
        addIt()
    if key.char == 's':
        saveJson()
def on_release(key):
    print('{0} release'.format(key))
    if key == Key.esc:
        # Stop listener
        return False
def addIt():
    global dic
    dur = dic.releaseTime - dic.pressTime
    if dur > 0:
        pos = mouse.position
        angle = pixel2Angle(center, pos)
        dic.durations.append(dur)
        dic.angles.append(angle)
        print(f"Pixel position {pos}, angle {angle}, duration {dur}, Number of values {len(dic.angles)}. ")
    else:
        print(f"error in duration. {dur}")
def undoIt():
    global dic
    dic.durations.pop()
    dic.angles.pop()
def pixel2Angle(center, pixelPos):
    xDiff, yDiff = [pixelPos[i] - center[i] for i in range(2)]
    magnitude = math.sqrt((xDiff**2)+(yDiff**2))
    angle = math.acos(yDiff/magnitude)
    return angle
def loadJson():
    global dic
    try:
        f = open(fileName, 'r', encoding="utf-8")
        dic = json.load(f)
        f.close()
    except FileNotFoundError:
        dic = {
            'pressTime':0,
            'releaseTime':0,
            'mousePosition':(0,0),
            'angles':[],
            'durations':[]
        }
    except:
        raise
def saveJson():
    string = json.dumps(dic)
    with open(fileName, 'w', encoding="utf-8") as f:
        f.write(string)
def eventMouse():
    print("Mouse event started")
    with keyboardListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
    print("mouse event ended")
def eventKeyboard():
    print("keyboard event started")
    with mouseListener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    print("keyboard event ended")
'''def mane():
    print("started")
    loadJson()
    tm = threading.Thread(target=eventMouse)
    tk = threading.Thread(target=eventKeyboard)
    tm.start()
    tk.start()
    tm.join()
    tk.join()
    print("finished")'''
def mane():
    print("started")
    loadJson()
    print("onto the threads")
    with keyboardListener(on_move=on_move,on_click=on_click,on_scroll=on_scroll) as listenerM:
        with mouseListener(on_press=on_press,on_release=on_release) as listenerK:
            print("On the inside")
            #listenerK.join()
            print("escaping")
        #listenerM.join()
        print("escaping 2")
    print("finished")


    

    
    
        
            

if __name__ == '__main__':
    obj = Fishing()
    #obj.run()
    mane()

