import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd, soundfile as sf
import time, threading, logging, bestOf, scipy.ndimage, skimage, random, cv2, math, os
from multiprocessing import Process, Pipe
from PIL import Image, ImageGrab
from pynput.keyboard import Key, KeyCode, Controller as keyboardController, Listener as keyboardListener
from pynput.mouse import Button as mouseButton, Controller as mouseController, Listener as mouseListener

logging.basicConfig(level=logging.DEBUG,
#filename= 'output.txt',
format='%(asctime)s - %(levelname)s - %(message)s')

#Global variables
#resolution setter
resolution = bestOf.getResolution()
#resource directory
resourceDirectory = os.path.join(os.getcwd(), 'game resources')
#global variables
cancel = False
continueQ = True
pauseIt = False
enemyNotification = False
processes = []
#https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Pipe
parent_conn, child_conn = Pipe()
parent_conn.send([cancel, continueQ, pauseIt])
#image capture boxes and their resize
fishBalanceLine = bestOf.boxScale((1134,736,1425,737), targetResolution=resolution)
fishBalancePeakThreshold = bestOf.scale(200, 1440, resolution[1])
fishBalanceStdThreshold = bestOf.scale(20, 1440, resolution[1])
uai = bestOf.userArtificialInput()
bobbinMouseBox = bestOf.boxScale([0,0,144,144], targetResolution=resolution)
enemyNameBox = bestOf.boxScale((400,15,660,70), targetResolution=resolution)
exampleEnemyTagBGR = cv2.imread(os.path.join(resourceDirectory,"albion enemy tag.png"))
exampleEnemyTag = cv2.cvtColor(exampleEnemyTagBGR, cv2.COLOR_BGR2RGB)
center = bestOf.pixelScale((1280,690), targetResolution=resolution)
#threads and processes
bobbinScanThread = None

class Fishing:
    cancelIt = False
    fgbgUse = False
    processIt = False
    mouseClickPos = None

    fishBalanceLine = bestOf.boxScale((1134,736,1425,737), targetResolution=resolution)
    fishBalancePeakThreshold = bestOf.scale(200, 1440, resolution[1])
    fishBalanceStdThreshold = bestOf.scale(20, 1440, resolution[1])
    bobbinMouseBox = bestOf.boxScale([0,0,144,144], targetResolution=resolution)
    center = bestOf.pixelScale((1280,690), targetResolution=resolution)
    #detecting fish
    fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50, detectShadows = False)
    distances = []
    sampleAmount = 5
    sampleTimeDF = 1
    maxRatio = 0
    npImz = np.zeros(resolution)
    st = time.monotonic()
    elapseTime = 60
    #balance


    def __init__(self, processIt=False):
        self.processIt = processIt
        detectProcess = Process(target=self.__detectFish)
    #auxiliary functions
    def resetDetectFish(self):
        self.distances = []
        self.maxRatio = 0
        self.fgbg.clear()
    def circlePos(self, point, r=None):
        #returns 2 x,y coord pair for a line intersecting 2 circles that are concentric
        px,py = point
        cx, cy = self.center
        if not r:
            #r = (0, max(resolution))
            r = (min(center)/2, max(resolution))
        elif isinstance(r, (float, int)):
            r = (0, r)
        minR, maxR = r
        rad = math.atan2(py-cy, px-cx)
        #calc for max point
        xMax = (maxR * math.cos(rad)) + cx
        yMax = (maxR * math.sin(rad)) + cy
        #calc for min point
        xMin = (minR * math.cos(rad)) + cx
        yMin = (minR * math.sin(rad)) + cy
        return ((int(xMin), int(yMin)), (int(xMax), int(yMax)))

    def castRod(self):
        pass
    def detectFish(self):
        if self.processIt:
            pass
        else:
            self.__detectFish()
    def __detectFish(self, mousePos=None):
        logging.info('Fish hook detection began')
        self.resetDetectFish()
        self.detectFishStartTime = time.monotonic()
        #main loop
        while not self.cancelIt:
            if not mousePos:
                mousePos = uai.mouse.position
            imz = ImageGrab.grab()
            npImz = np.array(imz)
            hsv = cv2.cvtColor(npImz, cv2.COLOR_RGB2HSV)
            #mask1: colour limits and filter for hsv image
            lowSat, lowValue, maxCh = 80, 100, 256
            lowerHSVRed = np.array([0,lowSat,lowValue])
            upperHSVRed = np.array([5, maxCh, maxCh])
            lowerHSVBlue = np.array([160, lowSat, lowValue])
            upperHSVBlue = np.array([181, maxCh, maxCh])
            #cv2 hsv range: h(0-180), s(0-255), v(0-255)
            maskGradualRed = cv2.inRange(hsv, lowerHSVRed, upperHSVRed)
            maskGradualBlue = cv2.inRange(hsv, lowerHSVBlue, upperHSVBlue)
            mask1 = cv2.bitwise_or(maskGradualRed, maskGradualBlue)
            #mask 2
            preMask = np.zeros_like(npImz)
            endPoints = self.circlePos(mousePos)
            cv2.line(preMask, endPoints[0], endPoints[1], (255,255,255), 200)
            mask2 = preMask[:,:,0]
            #create intermittent final mask
            maskInter = cv2.bitwise_and(mask1, mask2)#, mask3)
            #mask3
            if self.fgbgUse:
                mask3 = self.fgbg.apply(npImz)
                maskInter = cv2.bitwise_and(maskInter, mask3)
            #labels: to get a specific cluster of pixels
            countNum, labels = cv2.connectedComponents(maskInter)
            #if colours detected, save the distance
            if countNum > 1:
                unique, counts = np.unique(labels, return_counts=True)
                #determine the number if pixels per cluster
                counts = counts.tolist()
                indices = range(countNum)
                sortedIndices = [x for _,x in sorted(zip(counts,indices))]
                #avoid the 0's cluster and go to next largest pixel cluster
                maxSizeIndex = sortedIndices[-2]
                largeClusterPixels = sorted(counts)[-2]
                #RESET Condition: if the amount of bobber pixels detected is too small, reset the check
                if largeClusterPixels < 5:
                    self.resetDetectFish()
                    continue
                comX, comY = scipy.ndimage.center_of_mass(maskInter, labels=labels, index=maxSizeIndex)
                #store the y-component to use for calculations
                self.distances.append(comY)
            #when enough time passed
            if self.detectFishStartTime + self.sampleTimeDF > time.monotonic() and len(self.distances) > self.sampleAmount:
                #checking conditions
                partSampleStd = np.array(self.distances[-self.sampleAmount:-1]).std()
                wholeSampleStd = np.array(self.distances).std()
                ratio = partSampleStd/wholeSampleStd
                #debugging ratio
                if self.maxRatio < ratio:
                    maxRatio = ratio
                    logging.debug(f"maxRatio: {maxRatio}")
                #when standard deviation of part sample > whole sample, fish bit bobber
                if ratio > 1.2:
                    time.sleep(1)
                    #initiate bobber balance
                    self.balance()
                    time.sleep(2)
                    self.resetDetectFish()
        else:
            cv2.imwrite("bobber mask.png", cv2.cvtColor(npImz, cv2.COLOR_RGB2BGR))

    def balance(self):
        logging.info("Balancing Now.")
        #press button to engage balancing.
        uai.clickMouse()
        #wait a moment for balance bar to surely pop up.
        waitForBalanceBarTime = 1
        startTime = time.monotonic()
        #physics rigid body object (displacement, velocity, accereation)
        bobbinObject = bestOf.RigidObject(1)
        #box to check inside of for balance bar (a slither)
        box = fishBalanceLine
        while not cancel:
            #per loop, look for balance bar and respond accordingly
            imgLine = ImageGrab.grab(bbox=box)
            npLine = np.array(imgLine)
            linear = npLine[:,:,1].flatten()    #looking at green channel
            peak = np.argmax(linear)
            stdz = np.std(linear)
            #balance it
            if stdz > fishBalanceStdThreshold and np.max(linear) > fishBalancePeakThreshold:
                #fraction of peak position out of total position
                xPortion = peak/(box[2] - box[0])
                #displacement added to bob object
                bobbinObject.value = xPortion
                #velocity multiplied by factor
                velocityFactor = 1*bobbinObject.velocity
                #if bob higher than critical point, release the mouse
                if bobbinObject.value > (0.9-velocityFactor):   #system with displacement and velocity input
                    uai.mouse.release(mouseButton.left)
                    time.sleep(0.01)
                else:
                    uai.mouse.press(mouseButton.left)
                    time.sleep(0.1)
            #if didnt see bar while still setting up (time), check again
            elif (time.monotonic() - startTime) < waitForBalanceBarTime:
                continue
            #bob balancing done/not detected
            else:
                if (time.monotonic() - startTime) > 3 or bobbinObject.value < 0.1:
                    response = "Fishing done."
                else:
                    response = "Fishing failed."
                logging.info(response)
                uai.mouse.release(mouseButton.left)
                #EXTENSION
                #time.sleep(1.9)
                time.sleep(3)
                if continueQ and cancel==False:
                    longClickThread = threading.Thread(target=uai.clickMouse, args=(None,1))
                    longClickThread.start()
                break

'''def fishingCalibrate():
    #converts pixel of bobber position to normalized direction vector
    def pos2NormDirVector(pos):
        npPos = np.array(pos)
        #direction vector
        npDir = npPos - np.array(center)
        npNormDir = npDir/np.array(resolution)
        return npNormDir
    def normDirVector2Pos(normVec):
        #converts normalized direction vector to pixel position on screen
        npDir = np.array(normVec)
        np.array(resolution)
        npPos = npDir + np.array(center)
        pos = tuple(npPos.astype('int32'))
        return pos
    #get displacement values of fishing float
    #motion: start from top and arcs left of player to buttom
    magni = 200
    angles = range(0,math.pi, math.pi/10)
    holdDown = range(0.2,1.2,0.2)
    #center
    normalCenter = (center[0]/resolution[0], center[1]/resolution[1])
    for ang in angles:
        if cancel:
            break
        for holding in holdDown:
            if cancel:
                break
            x = (math.sin(ang) * magni)//1
            y = (math.cos(ang) * magni)//1
            possy = (center[0] - x, center[1] + y)
            uai.clickMouse(pos=possy,dur=holding)
            #wait for float to appear
            time.sleep(0.3)
            #determine float location
            floatPos = (0,0)
            #normalize float to screen to then get positions for any screen
            normalPos = (floatPos[0]/resolution[0], floatPos[1]/resolution[1])
            normalVec = (normalCenter[0] - normalPos[0], normalPos[1] - normalCenter[1])    #incomplete
            #store the normalized values
def flowerBudDetect():
    #http://amin-ahmadi.com/cascade-trainer-gui/
    #cascade file
    fileName = "flower bud.xml"
    flowerBudCascade = cv2.CascadeClassifier(os.path.join(resourceDirectory, fileName))
    #images
    imz = ImageGrab.grab()
    npImz = np.array(imz)
    cvImz = cv2.cvtColor(npImz, cv2.COLOR_RGB2GRAY)
    buds = flowerBudCascade.detectMultiScale(cvImz, scaleFactor=1.3, minNeighbors=5,
    minSize=(24,24), maxSize=(48,48))
    for (x,y,w,h) in buds:
        cv2.rectangle(cvImz, (x,y), (x+w, y+h), 255, 2)
        print(x,y)
    cv2.imshow('IDGAF',cvImz)
    cv2.waitKey(0)'''

def enemyNotify():
    #searching for speaker playback device
    devices = sd.query_devices()
    device = None
    for dev in devices:
        if 'speaker' in dev['name'].lower() and dev['max_output_channels'] > 0:
            device = dev
            break
    #if device was found
    if device:
        #setup sound device and sound
        sd.default.samplerate = device['default_samplerate']
        sd.default.device = device['name']
        soundFileName = 'fog horn.wav'
        sound, fs = sf.read(soundFileName, dtype='float32')
        #setup template
        threshold = 0.6
        templateBGR = cv2.imread(os.path.join(resourceDirectory, "albion hostile icon.png"))
        #using gradient template to get 
        template = cv2.Canny(templateBGR, 50,50)
        global enemyNotification
        while enemyNotification:
            #get and transform screen image
            imz = ImageGrab.grab()
            npImz = np.array(imz)
            npImz = cv2.cvtColor(npImz, cv2.COLOR_RGB2BGR)
            scan = cv2.Canny(npImz, 50,50)
            match = cv2.matchTemplate(scan, template, cv2.TM_CCOEFF_NORMED)
            if np.max(match) > threshold:
                sd.play(sound)
                time.sleep(5)
                #time.sleep(sound.size/sd.default.samplerate)
    else:
        logging.info("Sound device not found.")
    logging.debug("Enemy detection stopped.")

#move player and auto attack hostile npc
def roamHunt():
    logging.info("The hunt is ON.")
    #initiate walking in the direction of mouse
    randomPos = uai.mouse.position
    currentDirVector = randomPos - np.array(center)
    intervalTime = 15
    #skills variables
    skillButtons = ['1','2','3','r','4','f']
    skillsCooldown = np.array([3,10,15,45,30,30]) + 0.3
    skillsCountUse = np.zeros(6)
    skillTimes = skillsCooldown + time.monotonic() 
    #character auto walks when this key is pressed
    uai.typeKeyboard('`')
    st = time.monotonic()
    attacking = False
    while not cancel:
        pauseFunc()
        #check for enemy icon near top left
        imz = ImageGrab.grab(bbox=enemyNameBox)
        npImz = np.array(imz)
        threshold = 0.3
        res = cv2.matchTemplate(npImz[:,:,0], exampleEnemyTag[:,:,0], cv2.TM_CCOEFF_NORMED)
        #if icon is detected, press space to attack
        if np.max(res) > threshold:
            if attacking == False:  #switching on attack
                randomPos = uai.mouse.position
                logging.debug("Attack")
                uai.clickMouse(pos=center)
            #attack
            uai.keyboard.press(Key.space)
            uai.keyboard.release(Key.space)
            attacking = True
            #skills activation
            for i in range(6):
                if i == 2 and time.monotonic() > skillTimes[i]:  #3 charge attack
                    if skillsCountUse[0] >= 3:
                        #press button for 3rd skill
                        uai.typeKeyboard(skillButtons[2])
                        #set new cooldown time
                        skillTimes[2] = skillsCooldown[2] + time.monotonic()
                        skillsCountUse[2] += 1
                        logging.debug(f"skill 3 used")
                        #dont use multiple skills in quick use
                        time.sleep(0.5)
                        break
                elif i == 4:
                    #dont heal myeslf (TBD)
                    continue
                else:
                    #if skill ready to use, use it
                    if time.monotonic() > skillTimes[i]:
                        #press button for skill
                        uai.typeKeyboard(skillButtons[i])
                        #set new cooldown time
                        skillTimes[i] = skillsCooldown[i] + time.monotonic()
                        skillsCountUse[i] += 1
                        logging.debug(f"skill {i} used")
                        #dont use multiple skills in quick use
                        time.sleep(0.5)
                        break
        else:
            #attacking just finished
            if attacking:   #switching off attack
                logging.debug("Attack Finished")
                skillsCountUse = np.zeros_like(skillsCountUse)
                uai.clickMouse(buttun=mouseButton.right)
                uai.mouse.position = randomPos
                time.sleep(1)
                uai.typeKeyboard('`')
            attacking = False
            st = time.monotonic()
        #if not fighting, move about in random directions
        if (time.monotonic() - st) > intervalTime and not attacking:
            logging.debug("Change direction")
            #if interval time passed, change direction
            while not cancel:
                #try random direction again and again and make sure it only goes forward
                #(dot product of forward is > 0)
                randomPos = np.array([random.randint(1,x) for x in resolution])
                dirVector = randomPos - np.array(center)
                if np.vdot(dirVector, currentDirVector) > 0:
                    randomPos = tuple(randomPos)
                    break
            currentDirVector = dirVector
            uai.mouse.position = randomPos
            uai.typeKeyboard('`')
            st = time.monotonic()

def fishHooked(childConn=None):
    logging.info('Fish hook detection began')
    #measures absolute velocity and when it moves too much (by a ratio) the bob moved because of the fish
    distances = []
    sampleAmount = 8
    maxRatio = 0
    npImz = np.zeros(resolution)
    st = time.monotonic()
    elapseTime = 60
    #setting up main thread variables
    if not bool(childConn):
        global cancel, continueQ
    else:
        cancel, continueQ, pauseIt = childConn.recv()
    #return circle position
    def circlePos(point, center, resolution, r=None):
        #returns 2 x,y coord pair for a line intersecting 2 circles that are concentric
        px,py = point
        cx, cy = center
        if not r:
            #r = (0, max(resolution))
            r = (min(center)/2, max(resolution))
        minR, maxR = r
        rad = math.atan2(py-cy, px-cx)
        #caulc for max point
        xMax = (maxR * math.cos(rad)) + cx
        yMax = (maxR * math.sin(rad)) + cy
        #calc for min point
        xMin = (minR * math.cos(rad)) + cx
        yMin = (minR * math.sin(rad)) + cy
        return ((int(xMin), int(yMin)), (int(xMax), int(yMax)))
    #check differences
    fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50, detectShadows = False)
    #NOW, run the function
    while cancel == False and continueQ:
        pauseFunc()
        #detect a red enough bob in the box area on screen
        mousePos = uai.mouse.position
        #box used to detect bob only in it
        #box = bestOf.midPosition2Box(mousePos, bobbinMouseBox, resolution)
        #screen capture box position
        imz = ImageGrab.grab()
        npImz = np.array(imz)
        hsv = cv2.cvtColor(npImz, cv2.COLOR_RGB2HSV)
        #mask1: colour limits and filter for hsv image
        lowSat, lowValue, maxCh = 80, 100, 256
        lowerHSVRed = np.array([0,lowSat,lowValue])
        upperHSVRed = np.array([5, maxCh, maxCh])
        lowerHSVBlue = np.array([160, lowSat, lowValue])
        upperHSVBlue = np.array([181, maxCh, maxCh])
        #cv2 hsv range: h(0-180), s(0-255), v(0-255)
        maskGradualRed = cv2.inRange(hsv, lowerHSVRed, upperHSVRed)
        maskGradualBlue = cv2.inRange(hsv, lowerHSVBlue, upperHSVBlue)
        mask1 = cv2.bitwise_or(maskGradualRed, maskGradualBlue)
        #mask 2
        preMask = np.zeros_like(npImz)
        endPoints = circlePos(mousePos, center, resolution)
        cv2.line(preMask, endPoints[0], endPoints[1], (255,255,255), 200)
        mask2 = preMask[:,:,0]
        #mask3
        #mask3 = fgbg.apply(npImz)
        #create intermittent final mask
        maskInter = cv2.bitwise_and(mask1, mask2)#, mask3)
        #labels: to get a specific cluster of pixels
        countNum, labels = cv2.connectedComponents(maskInter)
        #if colours detected, save the distance
        if countNum > 1:
            #look at the labels
            unique, counts = np.unique(labels, return_counts=True)
            #determine the number if pixels per cluster
            counts = counts.tolist()
            #indices of each labeled cluster
            indices = range(countNum)
            sortedIndices = [x for _,x in sorted(zip(counts,indices))]
            #avoid the 0's cluster and go to next largest pixel cluster
            maxSizeIndex = sortedIndices[-2]
            #number of pixels of the largest cluster
            largeClusterPixels = sorted(counts)[-2]
            #if the amount of bobber pixels detected is too small, reset the check
            if largeClusterPixels < 5:
                distances = []
                #return
                continue
            comX, comY = scipy.ndimage.center_of_mass(maskInter, labels=labels, index=maxSizeIndex)
            #store the y-component to use for calculations
            distances.append(comY)
        #when enough distances collected, begin checks
        if len(distances) > sampleAmount:
            #checking conditions
            partSampleStd = np.array(distances[-sampleAmount:-1]).std()
            wholeSampleStd = np.array(distances).std()
            ratio = partSampleStd/wholeSampleStd
            #debugging ratio
            if maxRatio < ratio:
                maxRatio = ratio
                logging.debug(f"maxRatio: {maxRatio}")
            #when standard deviation of part sample > whole sample, fish bit bobber
            if ratio > 1.2:
                time.sleep(1)
                #initiate bobber balance
                #balanceProcess = Process(target=balance)
                balanceProcess = threading.Thread(target=balance)
                balanceProcess.start()
                balanceProcess.join()
                time.sleep(2)
                #resetting
                distances = []
                maxRatio = 0
        if bool(childConn):
            cancel, continueQ, pauseIt = childConn.recv()
    else:
        #cv2.imwrite("bobber mask.jpg", mask*250)
        cv2.imwrite("bobber mask.png", cv2.cvtColor(npImz, cv2.COLOR_RGB2BGR))

#player input controller to balance bob in fishing game
def balance():
    logging.info("Balancing Now.")
    #press button to engage balancing.
    uai.clickMouse()
    #wait a moment for balance bar to surely pop up.
    waitForBalanceBarTime = 1
    startTime = time.monotonic()
    #physics rigid body object (displacement, velocity, accereation)
    bobbinObject = bestOf.RigidObject(1)
    #box to check inside of for balance bar (a slither)
    box = fishBalanceLine
    while not cancel:
        #per loop, look for balance bar and respond accordingly
        imgLine = ImageGrab.grab(bbox=box)
        npLine = np.array(imgLine)
        linear = npLine[:,:,1].flatten()    #looking at green channel
        peak = np.argmax(linear)
        stdz = np.std(linear)
        #balance it
        if stdz > fishBalanceStdThreshold and np.max(linear) > fishBalancePeakThreshold:
            #fraction of peak position out of total position
            xPortion = peak/(box[2] - box[0])
            #displacement added to bob object
            bobbinObject.value = xPortion
            #velocity multiplied by factor
            velocityFactor = 1*bobbinObject.velocity
            #if bob higher than critical point, release the mouse
            if bobbinObject.value > (0.9-velocityFactor):   #system with displacement and velocity input
                uai.mouse.release(mouseButton.left)
                time.sleep(0.01)
            else:
                uai.mouse.press(mouseButton.left)
                time.sleep(0.1)
        #if didnt see bar while still setting up (time), check again
        elif (time.monotonic() - startTime) < waitForBalanceBarTime:
            continue
        #bob balancing done/not detected
        else:
            if (time.monotonic() - startTime) > 3 or bobbinObject.value < 0.1:
                response = "Fishing done."
            else:
                response = "Fishing failed."
            logging.info(response)
            uai.mouse.release(mouseButton.left)
            #EXTENSION
            #time.sleep(1.9)
            time.sleep(3)
            if continueQ and cancel==False:
                longClickThread = threading.Thread(target=uai.clickMouse, args=(None,1))
                longClickThread.start()
            break

def options(option = 1):
    if option == 1:
        print(
r'''Hi, welcome to albion bot. These are your controls.
Left Arrow: Cast the fishing line.
Up arrow:
Right Arrow:
Down Arrow: Cancel threads for a limited time (5 seconds).
'/': Toggle enemy detection.
Esc: Close the program. ''')


#pause the threads until keyboard thread unpauses
def pauseFunc(delta=1):
    global pauseIt
    while pauseIt:
        time.sleep(delta)
    return True
def cancelSequence():
    global cancel, continueQ, pauseIt
    cancel = True
    logging.info(f"cancel is {cancel}")
    time.sleep(5)
    cancel = False
    logging.info(f"cancel is {cancel}")

#keyboard and mouse thread callback functions
def on_pressK(key):
    global cancel
    if key == Key.down:
        cancelThread = threading.Thread(target=cancelSequence)
        cancelThread.start()
def on_releaseK(key):
    global cancel, enemyNotification, processes, child_conn
    if key == Key.esc:
        logging.debug('end it')
        cancel = True
        return False
    if key == Key.right:
        huntThread = threading.Thread(target=roamHunt)
        huntThread.start()
    if key == Key.up:
        logging.debug('casting rod')
        longClickThread = threading.Thread(target=uai.clickMouse, args=(None,1))
        longClickThread.start()
    if key == Key.left:
        bobbinScanThread = threading.Thread(target=fishHooked)
        #bobbinScanThread = Process(target=fishHooked, args=(child_conn,))
        #processes.append(bobbinScanThread)
        bobbinScanThread.start()
    if key == KeyCode.from_char("/"):
        enemyNotification = not enemyNotification
        if enemyNotification:
            logging.debug("enemy detection on")
            #en = Process(target=enemyNotify)
            en = threading.Thread(target=enemyNotify)
            en.start()
def releaseAll():
    uai.mouse.release(mouseButton.left)
    #uai.mouse.release(mouseButton.right)
    for p in processes:
        try:
            if p.is_alive():
                p.terminate()
        except:
            print(f"Process {p.name} cancel failed?")

def mane():
    options()
    kl = keyboardListener(on_press=on_pressK, on_release=on_releaseK)
    kl.start()
    kl.join()
    releaseAll()
    logging.debug("finished")