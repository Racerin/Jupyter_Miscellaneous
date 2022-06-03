from functools import partial
import PIL, os, pynput, json, sounddevice, time, matplotlib, math, random, scipy
from scipy import signal
import colorsys as coloursys
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageGrab, ImageFilter
from pynput.keyboard import Key, Listener
from pynput.mouse import Button as mouseButton, Controller as mouseController
 
class GatherPixInfo:
    motherDir = ''
    resWidth = 2560
    resHeight = 1440
    ctrlDown = False
    imgDown = False
    def __init__(self):
        self.resWidth, self.resHeight = screenResolution()
        self.mouse = mouseController()
        self.kc = pynput.keyboard.KeyCode
 
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, nm):
        if isinstance(nm, str):
            self.__name = nm
        else:
            print("Please enter a variable of type 'String'.")
    @name.deleter
    def name(self):
        print("There shouldn't be any reason to delete the name.")
        del self.name
 
    def captureSquImg(self, boxWidth=400, boxHeight=None):
        #error correction
        assert isinstance(boxWidth, int), 'Box width must be an interger.'
        boxWidth = int(boxWidth)
        boxHeight = boxHeight if isinstance(boxHeight, int) else boxWidth
        #image capture
        img = ImageGrab.grab()
        #mouse position
        x,y = self.mouse.position
        #Setting the points for cropped image
        left =      clamp(x - boxWidth/2, 0, self.resWidth - boxWidth)
        top =       clamp(y - boxWidth/2, 0, self.resHeight - boxWidth)
        right =     clamp(x + boxWidth/2, boxWidth, self.resWidth)
        bottom =    clamp(y + boxWidth/2, boxWidth, self.resHeight)
        #crop the image
        img1 = img.crop((left, top, right, bottom))
        #save the image
        pixDir = createFolder(os.path.join(self.motherDir, "1stgather"), setcwd=False)
            #return string of the number of files in the folder
        picName = str(len(os.listdir(pixDir)) + 1) +'.jpeg'
        picDir = os.path.join(pixDir, picName)
        img1.save(picDir, 'JPEG')
     
    def gatherPixKeysMonitor(self, key, keyDown = True):
        if keyDown:
            if key == self.kc(char='-'):
                self.dashDown = True
            if key == self.kc(char='=') and not self.imgDown:
                self.captureSquImg()
                self.imgDown = True
            else:
                print('{0} pressed'.format(key))
        else:
            if key == self.kc(char='-'):
                self.dashDown = False
            if key == self.kc(char='='):
                self.imgDown = False
            else:
                print('{0} released'.format(key))
 
    def keyboardMonitor(self):
        def on_press(key):
            self.gatherPixKeysMonitor(key)
            #print(f'The key type is {type(key)}')
 
        def on_release(key):
            self.gatherPixKeysMonitor(key, keyDown=False)
            if key == Key.esc:
                # Stop listener
                return False
             
        # Collect events until released
        with Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()
 
 
             
def pictureDataGather():
    #mother function
    infoHolder = GatherPixInfo()
    #access/create default albion folder and changes current working directory
    infoHolder.motherDir = createFolder()
    #picture gathering functions runned inside this function
    infoHolder.keyboardMonitor()
 
class Fishing:
    folderName = 'albionCheatFish'
    jsonFileName = 'jay son.txt'
    blue = (0,0,255)
    def __init__(self):
        self.cancel = False
 
    def run(self):
        '''
        Initiate Fishing bot
        '''
        print("Initiating")
        #verify function setup
        self.verifyFunc = colourPass(ImageGrab.grab(), colour=(255,0,0))
        #image organise
        self.boxSize = 128, 72
        self.mouse = mouseController()
        self.mousePos = self.mouse.position
        self.boxLocation = (self.mousePos[0]-self.boxSize[0]//2, self.mousePos[1]-self.boxSize[1]//2, self.mousePos[0]+self.boxSize[0]//2, self.mousePos[1]+self.boxSize[1]//2)
        self.rnm = random.randrange
        #main execute
        self.centroids = []
        self.deviationLimit = 8
        self.balanceDeviantLimit = 40
        self.fishMeterPullTime = 2
        self.fishMeterReleaseTime = 6
        print("Reached the beginning of loop")
        while True and not self.cancel:
            #cast fishing rod
            self.castRod()
            #confirm cast into water
            if self.recogniseFish2():
            #engage catching fish
                #self.balanceSimple()
                self.balance3()
            #reset fishing
            time.sleep(2.5)
 
    def castRod(self, startupTime=4, duration=1.5):
        #time to place mouse
        print("Begin castRod")
        time.sleep(startupTime)
        pos = [num + self.rnm(3) for num in self.mousePos]
        self.mouse.position = pos
        #check to see if there is holding down
        self.mouse.release(mouseButton.left)
        time.sleep(0.05)
        #hold down LB to cast
        self.mouse.press(mouseButton.left)
        time.sleep(duration)
        self.mouse.release(mouseButton.left)
        #time taken for float to appear (can be optimized)
        time.sleep(0.8)
        #done
        print("End castRod")
    def recogniseFish(self):
        print("Start recoginising if fish.")
        ans = False
        toStartTime = time.monotonic()
        holdDown = True
        #while time.monotonic()-toStartTime < 20 and holdDown and not self.cancel:
        while holdDown and not self.cancel:
            imz = ImageGrab.grab(bbox=self.boxLocation)
            pixz = pixelAccumm(imz, self.verifyFunc, step=3)
            #average of all the x's and y's pixels for a given picture
            if len(pixz) == 0:
                x = 0
                y = 0
            else:
                x = sum([x[0] for x in pixz])/len(pixz)
                y = sum([x[1] for x in pixz])/len(pixz)
            average = (x,y)
            self.centroids.append(average)
            holdDown = not self.recogniseProcessPixels()
        print(time.monotonic() - toStartTime, "How long it took to recognise fish.")
        ans = True
        return ans
    def recogniseFish2(self):
        print("Start recoginising if fish.")
        ans = False
        toStartTime = time.monotonic()
        holdDown = True
        #colour = (255,0,0)
        #template = [[colour]]
        templateImg = Image.open("float in water.jpg")
        npTemplate = np.array(templateImg)
        #npTemplate = np.array(template)
        imz = ImageGrab.grab(bbox=self.boxLocation)
        npImz = np.asarray(imz)
        #dic = myCorr2D(npImz, npTemplate, 0.9, maxValue=256,channels=[0,1,2])
        dic = corr2D(npImz, npTemplate, 0.9)
        yHold = dic["yPeak"]
        while holdDown and not self.cancel:
            imz = ImageGrab.grab(bbox=self.boxLocation)
            npImz = np.asarray(imz)
            dik = corr2D(npImz, npTemplate, 0.9, channels="R")
            y = dik["yPeak"]
            print(abs(y-yHold), "y Drift away.")
            holdDown = abs(y-yHold) < self.deviationLimit
        print(time.monotonic() - toStartTime, "How long it took to recognise fish.")
        ans = True
        return ans
    def recogniseProcessPixels(self, startToWatch=4):
        #Process the list of pixel-cluster (((centroids))) according to thresshold to see if the pixels moved enought (fish bit line)
        #a list of centroids must build up before processing begins (bad if fish caught quickly)
        if len(self.centroids) > startToWatch:  
            #y-displacement would be used to determine whether the fish bit the float
            y = [a[1] for a in self.centroids]
            self.mean = np.mean(y)
            lastY = y[-1] 
            if abs(lastY-self.mean) > self.deviationLimit:
            #if the displacement supercedes the thresshold, fish should be recognised
                print("fish suppose to be recognized.")
                print("Thresshold reached", abs(lastY-self.mean))
                return True
            else:
                return False
    def balance(self):
        print("Balancing Now.")
        #initiate 1st press
        holdDown = True
        box = (1133, 733, 1427, 740)
        scale = box[2] - box[0]
        #press button to engage balancing.
        self.mouse.press(mouseButton.left)
        time.sleep(0.5)
        self.mouse.release(mouseButton.left)
        #wait a moment for balance bar to surely pop up.
        time.sleep(0.2)
        #begin analysing bar
        #process a pixel thick line of balance bar.
        comparePixelLine = ImageGrab.grab(bbox=box)
        comparePixelLine.save("fishing balance bar.jpeg", format="JPEG")
        #verifyFunc2 = colourPassHSV(comparePixelLine, (244,219,189), (0.8,0.8,0.8), reducedSize=None)
        verifyFunc2 = colourPass2(comparePixelLine, (200, 200, 200), reducedSize=None, colourPercentileLimit=99.2, useImageFilter=True)
        #time checking to know when to give up balancing
        lastPullTime = time.monotonic()
        lastReleaseTime = time.monotonic()
        pixelMagX = 1
        while holdDown and not self.cancel:
            pic = ImageGrab.grab(bbox=box)
            pixelz = pixelAccumm2(pic, verifyFunc2)
            #pic.save("fishing balance bar.jpeg", format="JPEG")
            #default to release if pixels cannot be found
            length = len(pixelz)
            print(length, "Number of pixels detected.")
            if length == 0:
                pixelMagX = 1
            else:
                #pixel = pixelz[0]
                #x = pixel[0]
                xAvg = sum([x[0] for x in pixelz])/length
                pixelMagX = xAvg/scale
            print(pixelMagX, "pixelMagX")
            if pixelMagX < 0.80:
                #pull the rod, therefore click
                self.mouse.press(mouseButton.left)
                print("button holding down")
                lastPullTime = time.monotonic()
                #time.sleep(0.1)
                #self.mouse.release(mouseButton.left)
            else:
                #release the rod
                print("button letting go.")
                lastReleaseTime = time.monotonic()
                self.mouse.release(mouseButton.left)
                #time.sleep(0.2)
            lastPullDur = time.monotonic() - lastPullTime
            lastReleaseDur = time.monotonic() - lastReleaseTime
            print(lastPullDur, lastReleaseDur, "This is lastPullDur, lastReleaseDur.")
            if lastPullDur>self.fishMeterPullTime or lastReleaseDur>self.fishMeterReleaseTime:
                #fishing is done
                self.mouse.release(mouseButton.left)
                print("fishing end.")
                print("Was pulling whole time.") if lastPullDur>self.fishMeterPullTime else print("Was releasing whole time.")
                holdDown = False
    def balanceSimple(self):
        print("Balancing Now.")
        #initiate 1st press
        holdDown = True
        monPixl = (1388, 737)
        box = (monPixl[0],monPixl[1],monPixl[0] + 1,monPixl[0] + 1)
        #press button to engage balancing.
        self.mouse.press(mouseButton.left)
        time.sleep(0.5)
        self.mouse.release(mouseButton.left)
        #wait a moment for balance bar to surely pop up.
        time.sleep(0.2)
        #begin analysing bar
        #take the monitor pixel colour
        keepImg = ImageGrab.grab(bbox=box)
        keepColour = keepImg.getpixel((0,0))
        #time checking to know when to give up balancing
        lastPullTime = time.monotonic()
        lastReleaseTime = time.monotonic()
        pixelMagX = 1
        while holdDown and not self.cancel:
            tic = ImageGrab.grab(bbox=box)
            ticColour = tic.getpixel((0,0))
            #default to release if pixels cannot be found
            if dotColour(ticColour, keepColour) < 0.80:
                #pull the rod, therefore click
                self.mouse.press(mouseButton.left)
                print("button holding down")
                lastPullTime = time.monotonic()
                #time.sleep(0.1)
                #self.mouse.release(mouseButton.left)
            else:
                #release the rod
                print("button letting go.")
                lastReleaseTime = time.monotonic()
                self.mouse.release(mouseButton.left)
                time.sleep(0.2)
            lastPullDur = time.monotonic() - lastPullTime
            lastReleaseDur = time.monotonic() - lastReleaseTime
            print(lastPullDur, lastReleaseDur, "This is lastPullDur, lastReleaseDur.")
            if lastPullDur>self.fishMeterPullTime or lastReleaseDur>self.fishMeterReleaseTime:
                #fishing is done
                self.mouse.release(mouseButton.left)
                print("fishing end.")
                print("Was pulling whole time.") if lastPullDur>self.fishMeterPullTime else print("Was releasing whole time.")
                holdDown = False
 
    def balance3(self):
        print("Balancing Now.")
        #initiate 1st press
        holdDown = True
        box = (1187, 662, 1374, 756)
        #press button to engage balancing.
        self.mouse.press(mouseButton.left)
        time.sleep(0.1)
        self.mouse.release(mouseButton.left)
        #wait a moment for balance bar to surely pop up.
        time.sleep(0.2)
        #begin analysing bar
        #obtain template
        template = Image.open("float balance.jpg")
        npTemplate = np.array(template)
        #time checking
        lastPullTime = time.monotonic()
        lastReleaseTime = time.monotonic()
        while holdDown and not self.cancel:
            boxy = ImageGrab.grab(bbox=box)
            boxArray = np.array(boxy)
            print(boxArray.shape, "Shape of boxArray")
            dic = corr2D(boxArray, npTemplate, 0.9)
            exx = dic["xPeak"]
            xPortion = exx/(box[2] - box[0])
            print(xPortion, "xPortion")
            if xPortion < 0.6:
                #pull the rod, therefore click
                self.mouse.press(mouseButton.left)
                print("button holding down")
                lastPullTime = time.monotonic()
                #time.sleep(0.1)
                #self.mouse.release(mouseButton.left)
            else:
                #release the rod
                print("button letting go.")
                lastReleaseTime = time.monotonic()
                self.mouse.release(mouseButton.left)
                #time.sleep(0.2)
            lastPullDur = time.monotonic() - lastPullTime
            lastReleaseDur = time.monotonic() - lastReleaseTime
            print(lastPullDur, lastReleaseDur, "This is lastPullDur, lastReleaseDur.")
            if lastPullDur>self.fishMeterPullTime or lastReleaseDur>self.fishMeterReleaseTime:
                #fishing is done
                self.mouse.release(mouseButton.left)
                print("fishing end.")
                print("Was pulling whole time.") if lastPullDur>self.fishMeterPullTime else print("Was releasing whole time.")
                holdDown = False
 
    def balance2(self):
        print("Balancing Now.")
        #initiate 1st press
        holdDown = True
        #box = (1171, 736, 1388, 737)
        box = (1172, 736, 1360, 737)
        #press button to engage balancing.
        self.mouse.press(mouseButton.left)
        time.sleep(0.5)
        self.mouse.release(mouseButton.left)
        #wait a moment for balance bar to surely pop up.
        time.sleep(0.2)
        #begin analysing bar
        #process a pixel thick line of balance bar.
        comparePixelLine = ImageGrab.grab(bbox=box)
        #comparePixelLine.save("fishing balance bar.jpeg", format="JPEG")
        #pixelLine.thumbnail((1, 100))
        compareArray = np.array(comparePixelLine)
        compareGreenArray = compareArray[0,:,1]
        bestArray = self.removeOutliers(compareGreenArray, 1)
        compareBarMean = np.mean(bestArray)
        print(compareBarMean, "This is compareBarMean")
        lastPullTime = time.monotonic()
        lastReleaseTime = time.monotonic()
        while holdDown and not self.cancel:
            pixelLine = ImageGrab.grab(bbox=box)
            #pixelLine.thumbnail((1, 100))
            array = np.array(pixelLine)
            greenArray = array[0,:,1]
            worstValueDiff = np.amax(abs(greenArray-compareBarMean))
            print(worstValueDiff, "This is worstValueDiff.")
            if worstValueDiff > self.balanceDeviantLimit:
                #pull the rod, therefore click
                self.mouse.press(mouseButton.left)
                print("button holding down")
                lastPullTime = time.monotonic()
                #time.sleep(0.1)
                self.mouse.release(mouseButton.left)
            else:
                #release the rod
                print("button letting go.")
                lastReleaseTime = time.monotonic()
                self.mouse.release(mouseButton.left)
                time.sleep(0.2)
            lastPullDur = time.monotonic() - lastPullTime
            lastReleaseDur = time.monotonic() - lastReleaseTime
            print(lastPullDur, lastReleaseDur, "This is lastPullDur, lastReleaseDur.")
            if lastPullDur>self.fishMeterPullTime or lastReleaseDur>self.fishMeterReleaseTime:
                #fishing is done
                self.mouse.release(mouseButton.left)
                print("fishing end.")
                print("Was pulling whole time.") if lastPullDur>self.fishMeterPullTime else print("Was releasing whole time.")
                holdDown = False
 
    def removeOutliers(self, a, outlierConstant):
        upper_quartile = np.percentile(a, 75)
        lower_quartile = np.percentile(a, 25)
        IQR = (upper_quartile - lower_quartile) * outlierConstant
        quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
        resultList = []
        for y in a.tolist():
            if y >= quartileSet[0] and y <= quartileSet[1]:
                resultList.append(y)
        return resultList
 
    def updateJson(self, dic):
        pass
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
def dotProduct(vectorA, vectorB):
    length = len(vectorA)
    assert len(vectorB) == length, 'These vectors are not the same length.'
    assert all(isinstance(a, (int, float)) for a in vectorA) and all(isinstance(b, (int, float)) for b in vectorB), "These arrays contain a non-numeric value."
    product = sum([vectorA[i]*vectorB[i] for i in range(length)])
    return product
def productOut(tuple):
    ans = 1
    for d in tuple:
        i *= d
    return ans
def dotColourDistribute(sample, colour):
    if isinstance(sample, np.ndarray):
        sample = sample.tolist()
    #creates a normalized dot product from colours
    #convert RGB 0-255 to normalized-distributed format
    colourNormalized = distribution(colour, defaultNum=0)
    sampleNormalized = distribution(sample, defaultNum=0)
    #find the dotProduct of the normalized vectors
    ans = dotProduct(colourNormalized, sampleNormalized)
    return ans
def dotColour(sample, colour):
    #creates a normalized dot product from colours
    #convert RGB 0-255 to normalized format
    colourNormalized = [i/255 for i in colour]
    sampleNormalized = [i/255 for i in sample]
    #find the dotProduct of the normalized vectors
    ans = dotProduct(colourNormalized, sampleNormalized)
    return ans
def colourCompare(colour, sample, neutral=(0,0,0)):
    sampleDot = dotColourDistribute(sample, colour)
    neutralDot = dotColourDistribute(neutral, colour)
    #if sample colour is closer to colour than neutral colour
    return sampleDot>neutralDot
def distribution(sample, defaultNum=1):
    #returns a tuple of floats with each member representing the weight of its input value of the total.
    assert all(isinstance(a, (int, float)) for a in sample), f"{a for a in sample if not isinstance(a,(int,float))} are not numeric elements."
    if sum(sample) == 0:
        ans = [defaultNum for i in sample]
    else:
        ans = [a/sum(sample) for a in sample]
    return ans
def colourIntensityProduct(colour):
    #multiply-out the elements of the normalized colours
    colourNormalized = [i/255 for i in colour]
    ans = productOut(colourNormalized)
    return ans
 
def colourIntensity(colour):
    #sum the elements of colour and normalize
    ans = sum(colour)/(len(colour)*255)
    return ans
def myCorr2D(npScan, npTemplate, thresshold, maxValue = 1, channels=None):
    startTime = time.monotonic()
    #define sub functions
    def what2Do(scan, subTemp):
        #processes to find the correlation
        #error checking
        assert scan.shape == subTemp.shape, f"The shapes don't equate. {scan.shape} vs {subTemp.shape}"
        #find the difference
        diff = (scan - subTemp) 
        #the smaller the diff, the greater the correlation
        normRev = 1 - (diff/maxValue)
        #the average of the correlations in matrix
        avgBoxCorr = normRev.mean()
        #return the assign value for that position in result matrix
        return avgBoxCorr
    def createDict(products):
        hProd,wProd = products.shape
        print(products.shape, "product shape")
        coordinates = []
        countPixels = 0
        for h in range(hProd):
            for w in range(wProd):
                if products[h,w] > thresshold:
                    coordinates.append((h,w))
                    countPixels += 1
        #print(products, "Products values")
        xAvg, yAvg = 0,0
        if len(coordinates) > 0:
            xAvg = sum((tup[0] for tup in coordinates))//countPixels
            yAvg = sum((tup[1] for tup in coordinates))//countPixels
        dictionaire = {
            "xAverage":xAvg,
            "yAverage":yAvg,
            "count":countPixels
            }
        print(dictionaire, "dictionaire")
        print(products, "products")
        print(products.max(), "The highest in products", products.mean(), "The mean of products")
        return dictionaire
 
    #which channels to process
    channelInd = [0] if channels==None else channels
    #obtain all the dimensions for each ndarray
    imgH, imgW, imgD = npScan.shape
    tempH, tempW, tempD = npTemplate.shape
    #resultH, resultW = imgH-tempH+1, imgW-tempW+1
    resultH, resultW = imgH-tempH, imgW-tempW
    print(npScan.shape, npTemplate.shape, resultH, resultW, "shape of grids; npScan, npTemplate and product")
    #product matrix made
    products = np.ones((resultH, resultW))
    #iterate for each npTemplate box in npScan box
    for ch in channelInd:
        for h in range(resultH):
            for w in range(resultW):
                #get the subScan to then compare against
                #print(h,w,"h.w, ", tempH, tempW, "template h.w")
                subScan = npScan[h:(h+tempH), w:(w+tempW), ch]
                #The average correlation of the matrices to then assign to a point
                avgAtPoint = what2Do(npTemplate[:,:,ch], subScan)
                products[h,w] *= avgAtPoint
    dict = createDict(products)
    print(time.monotonic() - startTime, "This is how long myCorr2D to complete.")
    return dict
 
def corr2D(npScan, npTemplate, thresshold, channels=[0,1,2]):
    assert np.ndim(npScan) == np.ndim(npTemplate), f"The dimensions don't equate. Shapes: {npScan.shape} vs {npTemplate.shape}"
    startTime = time.monotonic()
    '''npScan = npScan/255
    npTemplate = npTemplate/255'''
    channelNum = []
    if 'r' in channels.lower():
        channelNum.append(0)
    if 'g' in channels.lower():
        channelNum.append(1)
    if 'b' in channels.lower():
        channelNum.append(2)
    #do something
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
def pixelAccumm(img, verifyFunc, step=1):
    #each pixel is compared in img to see if the pixel passes or fail according to verifyFunc
    #iterate through each pixel
    width, height = img.size
    allPixel = []
    #img.save("goaty.jpeg", "JPEG")
    #iterate through each pixel
    for b in range(0, height, step):
        for a in range(0, width, step):
            pixel = (a,b)
            if verifyFunc(img, pixel):
                allPixel.append(pixel)
    return allPixel
def pixelAccumm2(img, verifyFunc, step=1):
    #each pixel is compared in img to see if the pixel passes or fail according to verifyFunc
    #iterate through each pixel
    width, height = img.size
    allPixel = []
    #iterate through each pixel
    for a in range(0, width, step):
        pixel = (a,0)
        if verifyFunc(img, pixel):
            allPixel.append(pixel)
    return allPixel
def colourPass(imgCalibrate, colour, reducedSize=(128,72), colourPercentileLimit=80, intensityPercentileLimit=50):
    #TBD. Change colour thresshold
    '''
    return a function that returns a bool on 
    whether a pixel colour is above the percentile
    for intensity, colour
    '''
    #image conditioning
    if isinstance(reducedSize, tuple):
        imgCalibrate.thumbnail(reducedSize)
    #numpy array of image(grid)
    imgArray = np.array(imgCalibrate)
    #grid to column with colour dimension
    flatWithColour = imgArray.reshape(imgArray.size//3, 3)
    colourIdeal = [dotColourDistribute(x, colour) for x in flatWithColour]
    colourIdeal.sort()
    intensityFlat = [sum(x) for x in flatWithColour]
    intensityFlat.sort()
    #get percentile value for respective percentile
    percentileColour = np.percentile(colourIdeal,colourPercentileLimit)
    percentileIntensity = np.percentile(intensityFlat, intensityPercentileLimit)
    print(percentileColour, percentileIntensity, "PercentileColour, PercentileIntensity.")
    #the return function to use to verify
    def ansFunc(funcImg, pixel):
        pixelColour = funcImg.getpixel(pixel)
        #red colour of pixel
        colourAmount = dotColourDistribute(pixelColour, colour)
        intensityAmount = sum(pixelColour)
        ans = colourAmount>percentileColour and  intensityAmount>percentileIntensity
        return ans
    return ansFunc
def colourPass2(imgCalibrate, colour, reducedSize=(128,72), colourPercentileLimit=80, useImageFilter = False):
    #TBD. Change colour thresshold
    '''
    return a function that returns a bool on 
    whether a pixel colour is above the percentile
    for intensity, colour
    '''
    sqrtMagColour = lambda x,y: np.linalg.norm(np.array(x) - np.array(y))
    #image conditioning
    if isinstance(reducedSize, tuple):
        imgCalibrate.thumbnail(reducedSize)
    if useImageFilter:
        imgCalibrate = imageEdgeConditioning(imgCalibrate)
    #numpy array of image(grid)
    imgArray = np.array(imgCalibrate)
    #grid to column with colour dimension
    flatWithColour = imgArray.reshape(imgArray.size//3, 3)
    colourIdeal = [sqrtMagColour(x, colour) for x in flatWithColour]
    colourIdeal.sort()
    #get percentile value for respective percentile
    percentileColour = np.percentile(colourIdeal,colourPercentileLimit)
    print(percentileColour, "PercentileColour, PercentileIntensity.")
    #the return function to use to verify
    def ansFunc(funcImg, pixel):
        if useImageFilter:
            funcImg = imageEdgeConditioning(funcImg)
        pixelColour = funcImg.getpixel(pixel)
        #red colour of pixel
        colourAmount = sqrtMagColour(pixelColour, colour)
        ans = colourAmount>percentileColour
        return ans
    return ansFunc
def imageEdgeConditioning(img):
    #convert thick-enough rgb image to edges image and returns a slither of it in the middle
    w,h = img.size
    imgCalibrate = img.resize((w, 10))
    imgCalibrate = imgCalibrate.filter(ImageFilter.FIND_EDGES)
    box = (0, h//2, w, h//2+1)
    imgCalibrate = imgCalibrate.crop(box=box)
    return imgCalibrate
def colourPassHSV(imgCalibrate, colour, hsvPercentileLimits, reducedSize=(128,72)):
    #TBD. Change colour thresshold
    '''
    return a function that returns a bool on 
    whether a pixel colour is above the percentile
    for intensity, colour
    '''
    #converts rgb list/tuple/np.array to HSV np.array
    npArrayHSV = lambda x: np.array(rgb_to_hsv(x[0],x[1],x[2]))
    normalizedColour = np.array(colour)/256
    #np array of hsv colours
    hsvColour = npArrayHSV(normalizedColour)
    print(colour, "colour")
    print(hsvColour, "hsvColour")
    #image conditioning
    if isinstance(reducedSize, tuple):
        imgCalibrate.thumbnail(reducedSize)
    imgCalibrate = imgCalibrate.convert(mode="HSV")
    #numpy array of image(grid) in HSV format
    imgArray = np.array(imgCalibrate)
    imgDiffs = imgArray - hsvColour
    coeffs = [[] for i in range(3)]
    length = len(imgDiffs)
    for i in range(length):
        channel = imgDiffs[i]
        thress = np.percentile(channel, hsvPercentileLimits[i]*100)
        coeffs[i] = thress
    print(coeffs, "HSV Limiting Coefficients.")
    #the return function to use to verify
    def ansFunc(funcImg, pixel):
        #get pixel colour
        pixelColour = funcImg.getpixel(pixel)
        #get hsv colour
        hsvPixel = rgb_to_hsv(pixelColour[0], pixelColour[0], pixelColour[0])
        #multiply each element by each other
        dotMultiAns = np.multiply(np.array(hsvPixel), hsvColour)
        print(dotMultiAns, "dotMultiAns")
        boolys = [dotMultiAns[i]>coeffs[i] for i in range(len(dotMultiAns))]
        print(boolys, "boolys")
        ans = all(boolys)
        return ans
    return ansFunc
def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v
 
def showPixels(pixelPack):
    new = Image.new(mode="RGB",size=(128,128))
    [new.putpixel(pixel, (250,250,250)) for pixel in pixelPack if isinstance(pixel, tuple)]
    new.show()
def sortedPixels(allPixels, step):
    #check cv2.contour, histogram2d, 
    if len(allPixels) > 0:
        #initiate pixelClusters by removing one valid pixel and putting it in the list of the cluster
        pixelClusters = [[allPixels.pop(0)]]
        length = len(pixelClusters)
        while length > 0:
            length -= 1
            pixelCritique = allPixels.pop(0)
            for cluster in pixelClusters:   #cluster is a list of pixels
                holderCluster = None
                for pixel in cluster:   #pixel
                    if pixelClose(pixel, pixelCritique, step):
                        if isinstance(holderCluster, list):
                            #if pixel match and holderCluster exist, combine clusters and add pixel
                            holderCluster += cluster
                            holderCluster.append(pixelCritique)
                        else:
                            #if holderCLuster dont exist, assign to it and also add pixel to cluster
                            cluster.append(pixelCritique)
                            holderCluster = cluster
                    else:
                        #if pixel dont match, create new cluster
                        pixelClusters.append([pixelCritique])
    else:
        raise Exception("No pixels were captured.")
    return pixelClusters
def loopDifference(centerNumber, number, loopLimit=1, negativeIncluded=True):
    #returns the closest a number is to the center number given 'number' is a loop (0<x<1, 0=1)
    minArray = [abs(centerNumber-number), abs(centerNumber-(number + loopLimit))]
    if negativeIncluded:
        minArray.append(abs(centerNumber - (number-loopLimit)))
    ans = min(minArray)
    return ans
 
def pixelClose(p1, p2, step=1):
    diff = [p1[i] - p2[i] for i in range(len(p1))]
    squMag = sum([i**2 for i in diff])
    ans = squMag <= step**2
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
     
 
     
     
         
             
 
if __name__ == '__main__':
    #pictureDataGather()
    obj = Fishing()
    obj.run()