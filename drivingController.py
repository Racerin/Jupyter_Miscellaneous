#https://www.youtube.com/watch?v=eLTLtUVuuy4

import cv2
import numpy as np

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    canny = cv2.Canny(blur, 50,150)
    return canny

def roi(image):
    height = image.shape[0]
    polygons = np.array([[(200, height), (1100, height), (550, 250)]])
    mask = np.zeros_like(image)
    cv2.fillpoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

image = cv2.imread('test image.jpg')
laneImage = np.copy(image)
canny = canny(laneImage)
croppedImage = roi(laneImage)
thresholdLineCount, emptyHolder = 100, np.array([])
lines = cv2.HoughLinesP(croppedImage, 2, np.pi/180, thresholdLineCount, emptyHolder, minLineLength=40, maxLineGap=300)
cv2.imshow("My Image", croppedImage)
cv2.waitKey(0)