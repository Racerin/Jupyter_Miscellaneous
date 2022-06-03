from gta5Help import *
from bestOf import *


def makeWindow(title='image', size=(100,100)):
    cv2.namedWindow(title,cv2.WINDOW_AUTOSIZE)
    cv2.resizeWindow(title, size[0], size[1])
ifKey = lambda letter: cv2.waitKey(0) & 0xFF == ord(letter)

def main1():
    uai = userArtificialInput()
    #'cv2.waitKey(0)' is an input and '0xFF' is used to remove any trailing bits.
    while True:
        makeWindow()
        if ifKey('e'):
            uai.pixelData()
        if ifKey('q'):
            cv2.destroyAllWindows()
            break

def main2():
    sd = SelfDriving()
    sd.main2()

def testBboxColourMask():
    #initiating functions
    nothing = lambda x: None
    gtpt = lambda nm: cv2.getTrackbarPos(nm, "Tracking")

    makeWindow('Tracking', size=(500,500) )
    #cv2.namedWindow("Tracking")
    cv2.createTrackbar("LH", "Tracking", 0, 255, nothing)
    cv2.createTrackbar("LS", "Tracking", 0, 255, nothing)
    cv2.createTrackbar("LV", "Tracking", 0, 255, nothing)
    cv2.createTrackbar("UH", "Tracking", 255, 255, nothing)
    cv2.createTrackbar("US", "Tracking", 255, 255, nothing)
    cv2.createTrackbar("UV", "Tracking", 255, 255, nothing)

    cv2.createTrackbar("left", "Tracking", 0, 2560, nothing)
    cv2.createTrackbar("right", "Tracking", 100, 2560, nothing)
    cv2.createTrackbar("top", "Tracking", 0, 1440, nothing)
    cv2.createTrackbar("bottom", "Tracking", 100, 1440, nothing)

    #while ifKey('q'):
    while True:
        bbox = (gtpt('left'), gtpt('top'), gtpt('right'), gtpt('bottom'), )
        grab = ImageGrab.grab(bbox=bbox)
        frame = np.array(grab)
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lowerLimit = gtpt("LH"), gtpt("LS"), gtpt("LV")
        upperLimit = gtpt("UH"), gtpt("US"), gtpt("UV")

        mask = cv2.inRange(hsv, lowerLimit, upperLimit)
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        res = cv2.bitwise_and(bgr, bgr, mask=mask)

        #cv2.imshow("mask", mask)
        cv2.imshow("res", res)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()

#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
#https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html
if __name__ == "__main__":
    print("started")
    main2()
    #testBboxColourMask()
    print("done")