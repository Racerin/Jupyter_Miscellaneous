import numpy as np
from PIL import ImageGrab, Image
import matplotlib.pyplot as plt
import cv2, logging, time

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s')

def imageManip():
    #creation
    imz = cv2.imread('monkey face.png', cv2.IMREAD_COLOR)
    #data
    infoStr = f"dimensions {imz.shape}, "
    logging.debug(infoStr)
    #drawing on image
    #https://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html
    #image, start, end, colour, thickness
    cv2.line(imz, (0,0), (150,150), (0,255,0), 15)  
    #image, circle center, radius, colour, (-1 = fill inside, else thickness)
    cv2.circle(imz, (100,50), 20, (0,0,100), -1)
    #image, top left, buttom right, colour, thickness
    cv2.rectangle(imz, (15,25), (200,150), (0,0,255), 15)
    #
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(imz,'Monkey titling',(0,130), font, 1, (200,255,155), 2, cv2.LINE_AA)
    #display image
    cv2.imshow('Title of window', imz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def foregroundExtract():
    imz = cv2.imread(r'C:\Users\Administrator\Pictures\albion test 8.png')
    #imz = cv2.imread(r'C:\Users\Administrator\Pictures\albion test 5.png')
    mask = np.zeros(imz.shape[:2], np.uint8)
    backgroundModel = np.zeros((1,65), np.float64)
    foregroundModel = np.zeros((1,65), np.float64)
    # box surrounding foreground image
    rect = (1177,378,1439,691)
    #rect = (2010, 630, 2154, 774)
    st = time.monotonic()
    cv2. grabCut(imz, mask, rect, backgroundModel, foregroundModel, 5, cv2.GC_INIT_WITH_RECT)
    print("Piece of code duration", time.monotonic() - st)
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    imz = imz*mask2[:,:,np.newaxis]

    plt.imshow(imz)
    plt.colorbar()
    plt.show()

def colourFiltering():
    imz = cv2.imread(r'C:\Users\Administrator\Pictures\albion test 2.png')
    hsv = cv2.cvtColor(imz, cv2.COLOR_BGR2HSV)
    #colour limits and filter
    lower = np.array([0,50,100])
    upper = np.array([5,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    res = cv2.bitwise_and(imz, imz, mask=mask)
    
    #cv2.imshow('Mask',mask)
    cv2.imshow('res',res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def featureMatchingHomography():
    screenshot = cv2.imread(r'C:\Users\Administrator\Pictures\albion test 2.png')
    inScreenshot = cv2.imread(r'C:\Users\Administrator\Pictures\albion float1.png')
    #detector
    st = time.monotonic()
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(screenshot, None)
    kp2, des2 = orb.detectAndCompute(inScreenshot, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)   #bruteforce: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
    matches = bf.match(des1,des2)
    matches = sorted(matches, key = lambda x:x.distance)
    print("Duration", time.monotonic() - st)
    #display
    display = cv2.drawMatches(screenshot, kp1, inScreenshot, kp2, matches[:10], None, flags=2)
    cv2.imshow("Compare", display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def mogBackgroundReduction():
    #setup
    fgbg = cv2.createBackgroundSubtractorMOG2()
    fgmask = None
    #time organisation
    captureDuration = 10
    startW8 = 3
    count = 0
    time.sleep(startW8)
    st = time.monotonic()
    #capture action
    while time.monotonic() < (st + captureDuration):
        #screen capture
        imz = ImageGrab.grab()
        npImz = np.array(imz)
        #TBD: do any other modifications to npImz here
        #update movement capture
        fgmask = fgbg.apply(npImz)
        #imcrement
        count += 1
    #resolve and display
    print("Count", count, "Average frame time", (time.monotonic() - st)/count, 
    "max colour depth", np.max(fgmask))
    saveIt = True
    if saveIt:
        #organise image to then save it for stationary mask
        reversedBinary = np.where(fgmask>0,0,255)
        cv2.imwrite('mcnigg.jpg', reversedBinary)
    cv2.imshow("Changes", fgmask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    #imageManip()
    #foregroundExtract()
    #colourFiltering()
    #featureMatchingHomography()
    mogBackgroundReduction()