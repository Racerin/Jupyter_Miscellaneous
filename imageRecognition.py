from functools import partial
import PIL, os, json, sounddevice, time, matplotlib, math, random, scipy, logging, time
from scipy import signal
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageGrab, ImageFilter

logging.basicConfig(level=logging.DEBUG,
#filename= 'output.txt',
format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Start of program")
#logging.disable(logging.CRITICAL)  #end all logging messages

def decoratorCheckTime(func):
    def wrapper(*arg, **kwargs):
        startTime = time.monotonic()
        func(*arg, **kwargs)
        logging.info(f"This is how long it took. {time.monotonic() - startTime}")
    return wrapper
def decoratorForDuration(func, duration=1):
    def wrapper(*arg, **kwargs):
        startTime = time.monotonic()
        func(*arg, **kwargs)
        elapse = time.monotonic()-startTime
        if elapse >= duration:
            logging.info(f"This is how long it took. {elapse}")
        else:
            time.sleep(duration-elapse)
            logging.info(f"Waited {duration-elapse} seconds long.")
    return wrapper

def myCluster(list, verifyFunc):
    #a list of sets with each set containing pixels that touch each other
    clusters = []
    for pixel in list:
        clusters.append({})
        for pix in list:
            if verifyFunc(pixel, pix):
                clusters[-1].add(pix)
    #Now, using Sets, if a cluster has similiar member to another cluster, join them.
    howManyTimes = 0
    while True:
        howManyTimes += 1
        saveSize = len(clusters)
        popCluster = clusters.pop()
        for cluster in clusters:
            if popCluster.isdisjoint(cluster):
                clusters.remove(cluster)
                clusters.append(popCluster.union(cluster))
        if saveSize == len(clusters):
            break
    logging.info(howManyTimes)
    return clusters

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

def myCorrFormula(scan, subTemp, maxValue):
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
def createDict(products, thresshold):
    hProd,wProd = products.shape
    logging.info(products.shape, "product shape")
    coordinates = []
    countPixels = 0
    for h in range(hProd):
        for w in range(wProd):
            if products[h,w] > thresshold:
                coordinates.append((h,w))
                countPixels += 1
    #logging.info(products, "Products values")
    xAvg, yAvg = 0,0
    if len(coordinates) > 0:
        xAvg = sum((tup[0] for tup in coordinates))//countPixels
        yAvg = sum((tup[1] for tup in coordinates))//countPixels
    dictionaire = {
        "xAverage":xAvg,
        "yAverage":yAvg,
        "count":countPixels
        }
    logging.info(dictionaire, "dictionaire")
    logging.info(products, "products")
    logging.info(products.max(), "The highest in products", products.mean(), "The mean of products")
    return dictionaire

@decoratorCheckTime
def myCorr2D(npScan, npTemplate, thresshold, maxValue = 1, channels=None):
    #which channels to process
    channelInd = [0] if channels==None else channels
    #obtain all the dimensions for each ndarray
    imgH, imgW, imgD = npScan.shape
    tempH, tempW, tempD = npTemplate.shape
    resultH, resultW = imgH-tempH, imgW-tempW
    #product matrix made
    products = np.ones((resultH, resultW))
    #iterate for each npTemplate box in npScan box
    for ch in channelInd:
        for h in range(resultH):
            for w in range(resultW):
                #get the subScan to then compare against
                #logging.info(h,w,"h.w, ", tempH, tempW, "template h.w")
                subScan = npScan[h:(h+tempH), w:(w+tempW), ch]
                #The average correlation of the matrices to then assign to a point
                avgAtPoint = myCorrFormula(npTemplate[:,:,ch], subScan, maxValue)
                products[h,w] *= avgAtPoint
    dict = createDict(products, thresshold)
    return dict
    
def myCorr2D2(npScan, npTemplate, thresshold, maxValue = 1, channels=None):
    #which channels to process
    channelInd = [0] if channels==None else channels
    #obtain all the dimensions for each ndarray
    imgH, imgW, imgD = npScan.shape
    tempH, tempW, tempD = npTemplate.shape
    resultH, resultW = imgH-tempH, imgW-tempW
    #product matrix made
    #products = np.ones((resultH, resultW))
    products = np.ones_like(npTemplate, dtype=float)
    #iterate for each npTemplate box in npScan box
    for ch in channelInd:
        for h in range(resultH):
            for w in range(resultW):
                #get the subScan to then compare against
                #logging.info(h,w,"h.w, ", tempH, tempW, "template h.w")
                subScan = npScan[h:(h+tempH), w:(w+tempW), ch]
                #The average correlation of the matrices to then assign to a point
                avgAtPoint = myCorrFormula(subScan, npTemplate[:,:,ch], maxValue)
                products[h,w] *= avgAtPoint
    #dict = createDict(products, thresshold)
    #return dict
    return products