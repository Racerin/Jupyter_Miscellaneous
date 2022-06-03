import logging, time, cv2, ctypes, multiprocessing, os, pynput
import numpy as np
from PIL import ImageGrab
from pynput.keyboard import Key, KeyCode, Controller as keyboardController, Listener as keyboardListener
from pynput.mouse import Button as mouseButton, Controller as mouseController, Listener as mouseListener

logging.basicConfig(level=logging.DEBUG,
#filename= 'output.txt',
format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)  #end all logging messages

SendInput = ctypes.windll.user32.SendInput
#https://stackoverflow.com/questions/53643273/how-to-keep-pynput-and-ctypes-from-clashing
#KEYS: http://www.penticoff.com/nb/kbds/ibm104kb.htm

class RigidObject:
    #Object that returns value, velocity or acceleration
    constantDeltaTime = False

    def __init__(self, value=1, velocity=0, acceleration=0, deltaTime=None):
        self.__value = value
        if isinstance(value, (float, int)):
            assert isinstance(velocity, (float, int)), "Velocity is incorrect value type."
            assert isinstance(acceleration, (float, int)), "Acceleration is incorrect value type."
            self.velocity = velocity
            self.acceleration = acceleration
            self.clock = time.monotonic()
            if deltaTime == None:
                self.deltaTime = 0
            else:
                #deltaTime cannot be changed
                self.constantDeltaTime = True
                self.deltaTime = deltaTime
        elif isinstance(value, (np.ndarray)):
            if isinstance(velocity, np.ndarray):
                assert velocity.shape == value.shape, f"The arrays are of the wrong size. {value.shape} vs {velocity.shape}"
                self.velocity = velocity
            if isinstance(acceleration, np.ndarray):
                assert acceleration.shape == value.shape, f"The arrays are of the wrong size. {value.shape} vs {acceleration.shape}"
                self.acceleration = acceleration
            #deltaTime initiation logic
            if deltaTime == None:
                self.deltaTime = np.zeros_like(value)
            elif isinstance(deltaTime, np.ndarray):
                self.deltaTime = deltaTime
            else:
                raise ValueError("'deltaTime' is not a numpy array.")

        else:
            logging.error("This variable is not accepted")
            raise ValueError

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, newValue):
        newClock = time.monotonic()
        if self.constantDeltaTime == False:
            self.deltaTime = newClock - self.clock
        self.clock = newClock
        deltaValue = newValue - self.value
        self.velocity = deltaValue/self.deltaTime
        deltaVelocity = self.velocity - self.velocity
        self.acceleration = deltaVelocity/self.deltaTime
        self.__value = newValue

#MISCELLANEOUS DECORATORS
def timeit(method):
    def timed(*args, **kwargs):
        ts = time.monotonic()
        result = method(*args, **kwargs)
        te = time.monotonic()
        timeDiff = te - ts
        min, sec = divmod(timeDiff, 60)
        print(f"The function '{method}' took {min} minutes and {sec} seconds to complete.")
        return result
    return timed

def ignoreError(method, IgnoreExceptions=[Exception]):
    #automatically ignore errors
    def cap(*args, **kwargs):
        result = None
        try:
            result = method(*args, **kwargs)
        except Exception as e:
            checks = [isinstance(e, exc) for exc in IgnoreExceptions]
            if not any(checks):
                raise e
        return result
    return cap


#COMPUTER VISION
'''class ImageMatcher:
    image = None    #original image, in rgb or monotonic
    templateImage = None
    scanImage = None
    multiprocessIt = False
    imageFolder = os.getcwd()
    threshold = 0.9

    #enumerations
    #image scan type
    METHOD_NORMAL = 0 #rgb image
    METHOD_CANNY = 1
    #scan result
    
    def __init__(self, image, threshold=0.9, myScanMethod=ImageMatcher.METHOD_NORMAL, multiprocessIt=False):
        #obtain template image
        if isinstance(image, str):
            #search for image in directory
            bgr = cv2.imread(image)
            self.image = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        self.threshold = threshold
        self.myScanMethod = myScanMethod
        self.multiprocessIt = multiprocessIt
    def scan(self, scan=None, bbox=None, method=cv2.CV_TM_SQDIFF_NORMED):
        #determine if there is an image in scan
        if not scan:
            #if no scan image given, screen capture
            if bbox:
                imz = ImageGrab.grab(bbox=bbox)
            else:
                imz = ImageGrab.grab()
            scanImage = np.array(imz)
        assert isinstance(scan, np.ndarray), "There is no numpy array"
        #setup conditions for scanning image
        resultImage = cv2.matchTemplate(scan, self.templateImage, method)
    def saveImage(self, fileName, image=None, convert2bgr=None):
        assert isinstance(fileName, str), "The fileNmae is not a string"
        if not image:
            #save original image by default
            toSave = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        else:
            if convert2bgr:
                #convert image by cv2.COLOR_**** enumerations
                toSave = cv2.cvtColor(image, convert2bgr)
            else:
                toSave = image
        fullImageFileName = os.path.join(self.imageFolder, fileName)
        cv2.imwrite(fullImageFileName, toSave)
    def imageResize(self, newResolution, oldResolution=(2560,1440)):
        pass
    @staticmethod
    def imageChannels(image):
        assert isinstance(image, np.ndarray), "This is not a numpy array."
        shape = image.shape
        if shape.size == 3:
            channels = shape[-1]
        elif shape.size == 2:
            print("Rare occurence of channels appearing")
            channels = 1
        else:
            raise Exception("The dimensions of this image in search of channels is off.")
        return channels'''
class BarProgress():
    #detects quantity of pixels in colour range out of bbox
    def __init__(self, bbox, lowColor, highColor):
        self.bbox = bbox
        self.lowColor, self.highColor = lowColor, highColor

    def scan(self):
        img = ImageGrab.grab(bbox=self.bbox)
        npScan = np.array(img)
        img_hsv = cv2.cvtColor(npScan, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(img_hsv, self.lowColor, self.highColor)
        total = img_hsv.size
        count = mask.sum()
        fraction = count/total
        return fraction

def getResolution():
    resTemp = np.array(ImageGrab.grab()).shape
    resolution = resTemp[1], resTemp[0]
    return resolution
def boxScale(box, targetResolution, templateResolution=(2560,1440), scaleBox=True):
    scaleFactor = (targetResolution[0]/templateResolution[0], targetResolution[1]/templateResolution[1])
    left = (scaleFactor[0] * box[0])//1
    top = (scaleFactor[1] * box[1])//1
    xDiff = box[2] - box[0]
    yDiff = box[3] - box[1]
    if scaleBox:
        #whether to scale the internals of the box
        xDiff *= scaleFactor[0]
        yDiff *= scaleFactor[1]
        #must be atleast 1 pixel wide/high
        xDiff = max(xDiff//1, 1)
        yDiff = max(yDiff//1, 1)
    newBox = left, top, left+xDiff, top+yDiff
    #print(f"scaleFactor{scaleFactor}, left {left}, top {top}, xDiff {xDiff}, yDiff {yDiff}")
    return newBox
def boxTranslate(box, displacement, resolution = None, squeeze = False):
    assert isinstance(displacement, tuple), "Displacement is not a tuple"
    assert len(displacement) == 2, "displacement is not the right size array"
    assert isinstance(box, tuple), "box is not a tuple"
    assert len(box) == 2, "box is not the right size array"
    displace = displacement * 2     #double the tuple size
    newBox = [displace[i] + box[i] for i in range(4)]
    if resolution != None:
        #if resolution included, check and maybe tune the box
        assert isinstance(resolution, tuple), "resolution is not a tuple"
        assert len(resolution) == 2, "resolution is not the right size array"
        resa = resolution * 2
        booly = [newBox[i] <= resa[i] for i in range(4)]
        if any(booly):
            #if any dimension is out of range, check to parameters
            if squeeze:
                #if squeeze, squeeze the box to fit in resolution
                if newBox[0] > displacement[0] or newBox[1] > displacement[1]:
                    raise ValueError(f"The box cannot be squeezed. resolution{resolution}, box{newBox}")
                else:
                    #make the box fit
                    right = min(box[2], resolution[0])
                    buttom = min(box[3], resolution[1])
                    oldNewBox = newBox
                    newBox = (newBox[0], newBox[1], right, buttom)
                    raise Warning(f"The box was resized. {oldNewBox} to {newBox}")
            else:
                #else, throw away the box
                raise ValueError(f"The new box is out of range. resolution{resolution}, box{newBox}")
    return newBox
def pixelScale(pixel, targetResolution, templateResolution=(2560,1440), scaleAxis=(True, True)):
    scaleFactor = (targetResolution[0]/templateResolution[0], targetResolution[1]/templateResolution[1])
    newPixel = [0,0]
    for i in range(2):
        if scaleAxis[i]:
            newPixel[i] = int(scaleFactor[i] * pixel[i])
    return tuple(newPixel)

def scale(variable, currentSize, newSize):
    newVariable = variable * (newSize/currentSize)
    return newVariable

bestOfMatch = lambda scan, template: np.max(cv2.matchTemplate(scan, template, cv2.TM_CCOEFF_NORMED))
locationOfMax = lambda a: np.unravel_index(np.argmax(a, axis=None), a.shape)
locationOfMin = lambda a: np.unravel_index(np.argmin(a, axis=None), a.shape)

def resizeImage(img, finalResolution):
    shape = img.shape
    w,h = shape[1], shape[0]
    #scale factor
    sf = np.array(finalResolution) / np.array([w,h])

    final = cv2.resize(img, finalResolution, sf[0], sf[1], cv2.INTER_CUBIC)
    return final

def calcAspectRatio(resolution):
    ratio = 0,0
    endInd = min(resolution) + 1
    for i in range(1, endInd):
        xq, xr = divmod(size[0], i)
        yq, yr = divmod(size[1], i)
        if xr==0 and yr==0:
            ratio = (xq, yq)
    return ratio

def matchThresholdClusters(img, template, threshold):
    match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    mask = match >= threshold
    count = numberOfContours(mask)
    return count

def numberOfContours(mask):
    image, contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = len(contours)
    return count

#image extraction
def saveImageBox(directory, nameTag='image', res=(72,72)):
    import os
    #image array setup
    uai = userArtificialInput()
    boxRes = (0, 0, res[0], res[1])
    box = midPosition2Box(uai.mouse.position, box=boxRes)
    imz = ImageGrab.grab(bbox=box)
    npImz = np.array(imz)
    npFinal = cv2.cvtColor(npImz, cv2.COLOR_RGB2GRAY)
    #directory stuff
    dirFolder = os.path.join(directory, nameTag)
    if not os.path.exists(dirFolder):
        os.makedirs(dirFolder)
    howMany = len(os.listdir(dirFolder))
    fileName = nameTag + f"{howMany}" + ".png"
    dir = os.path.join(dirFolder, fileName)
    #save image
    cv2.imwrite(dir, npFinal)
    logging.debug(f"Took a picture of {nameTag}")

#auxiliary code, convert middle position to box with middle position
def nearMidBoxCenterOfGravity(mask, box):
    import scipy
    assert len(box) % 2 == 0 and len(box) < 5
    #x, y positions of center
    x, y = 0, 0
    if len(box) == 2:
        x, y = box
    else:
        dx, dy = [box[2 + i] - box[i] for i in range(2)]
        x, y = dx/2, dy/2
    #center of mass of labels
    lbl, quantity = scipy.ndimage.label(mask)
    print("lbl", np.bincount(lbl.flatten()))
    coms = scipy.ndimage.measurements.center_of_mass(mask, lbl, range(1, quantity))
    diff = lambda cood: ((cood[1] - y)**2) + ((cood[0] - x)**2)
    print(coms, "coms")
    '''for com in coms:
        print(type(com))
        print(diff(com))'''
    comSorted = coms.sort(key = diff)
    print(comSorted, "sorted center of mass")
    return comSorted[0]

def imageResize(npImz, originalSize, newSize):
#resize image according to simple factor
    #image resolution in x,y
    resolution = npImz.shape[1], npImz.shape[0]
    #ratio of new image size dimension to old size dimension (for both x and y)
    sizeFactor = newSize/originalSize
    fx = sizeFactor
    fy = sizeFactor
    #how much to scale the image picture by (the same amount as sizeFactor)
    dsize = [(sizeFactor * resolution[i])//1 for i in range(2)]
    #https://www.tutorialkart.com/opencv/python/opencv-python-resize-image/
    newImg = cv2.resize(npImz, dsize, fx, fy, interpolation=cv2.INTER_AREA)
    return newImg

#positioning image capture box
def midPosition2Box(position, box, resolution=None):
#create box with position at the middle of the box
    dx12 = (box[2] - box[0])//2
    dy12 = (box[3] - box[1])//2
    x,y = position
    newBox = [x-dx12, y-dy12, x+dx12, y+dy12]
    if resolution:
        newBox[0] = max(min(newBox[0], resolution[0]-(dx12*2)), 0)
        newBox[1] = max(min(newBox[1], resolution[1]-(dy12*2)), 0)
        newBox[2] = max(min(newBox[2], resolution[0]), (dx12*2))
        newBox[3] = max(min(newBox[3], resolution[1]), (dy12*2))
    return tuple(newBox)
    
def highest(npScan, template):
    res = cv2.matchTemplate(npScan, template, cv2.TM_CCOEFF_NORMED)
    return np.max(res)

#COMPUTER INPUTS
class userArtificialInput:
    mouse = mouseController()
    keyboard = keyboardController()

    #default mouse and keyboard pressing functions
    def clickMouse(self, pos=None, dur=0.1, buttun=mouseButton.left):
        #logging.debug(pos, "Pos")
        if pos != None:
            self.mouse.position = pos
        self.mouse.release(buttun)
        self.mouse.press(buttun)
        time.sleep(dur)
        self.mouse.release(buttun)

    def clickImage(self, icon, threshold, checkDuration=0, box=None):
        #TBD: detect icon under difference conditions. eg. gradient
        startTime = time.monotonic()
        while True:
            startTimeLoop = time.monotonic()
            leftStart, topStart = 0, 0
            if box:
                imz = ImageGrab.grab(bbox=box)
                #coordinates used to select icon if detected
                leftStart, topStart = box[0], box[1]
                #to be reviewed
            else:
                #simply check entire image
                imz = ImageGrab.grab()
            npScan = np.array(imz)
            template = cv2.cvtColor(icon, cv2.COLOR_BGR2RGB)
            res = cv2.matchTemplate(npScan, template, cv2.TM_CCOEFF_NORMED)
            if np.max(res) > threshold:
                #position of best match
                y,x = np.unravel_index(np.argmax(res), res.shape)
                h,w,_ = template.shape
                #position mouse at center of icon
                position = (x + w//2 + leftStart, y + h//2 + topStart)
                #click the icon
                self.clickMouse(pos=position)
                logging.debug("Image clicked.")
                return True
            #time checks
            endTime = time.monotonic()
            workTime = endTime - startTimeLoop
            #checkDuration += workTime
            #if time has runned out, end the loop (do-while loop)
            if endTime - startTime > checkDuration:
                #print(endTime-startTime, "duration")
                return False

    def typeKeyboard(self, key, dur=0.1):
        if isinstance(key, str) and len(key) == 1:
            self.keyboard.release(key)
            self.keyboard.press(key)
            time.sleep(dur)
            self.keyboard.release(key)

    def pixelData(self):
        pos = self.mouse.position
        bbox = (pos[0], pos[1], pos[0]+1, pos[1]+1)
        img = ImageGrab.grab(bbox=bbox)
        rgb = np.array(img)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        strang = f"HSV: {hsv}, RGB: {rgb}, Position: {pos}"
        print(strang)

#NEXT
#look at top of script for more info, SendInput
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



