#python ocr pdf
# https://www.pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/    #could do

import numpy as np
from PIL import Image
import cv2, pytesseract, time, os, glob, re, imutils, json, logging, enchant
import pytesseractDataSupportLib as pdsl

english = enchant.Dict("en_GB")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

logging.basicConfig(level=logging.DEBUG,
#filename= 'pytesseract OCR check logging.txt',
format='%(asctime)s - %(levelname)s - %(message)s')

def scan(imgPath):
    imz = cv2.imread(imgPath)
    text = pytesseract.image_to_string(imz, lang='eng')
    print(text)

def scoreEnglish(text):
    checkFor = ['the',  'that', 'of', 'for', 'by', 'with']
    findList = [re.findall(x, text) for x in checkFor]
    sumOf = [len(x) for x in findList]
    score = sum(sumOf)
    return score
def scoreEnglish2(text):
    words = re.findall(r"\w+", text)
    length = len(words)
    score = max(0, length)
    if score:
        start = 0
        for word in words:
            start += 1 if english.check(word.lower()) else 0
        score = start/length
    return score

def organiseImages():
    #TBD: resize images before processing
    #sorts the database of pictures of post grad reports
    folderDir = r"C:\Users\drsba\Desktop\report pictures extra"
    allDic = {}
    globPattern = folderDir + r"\*.jpg"
    #obtain file path of each picture
    picturesList = glob.glob(globPattern)
    picturesList.sort()
    #logging
    length = len(picturesList)
    logging.debug(f'{length}, number of pictures')
    for i, picturePath in enumerate(picturesList):
        try:
            #obtain file name
            fileName = os.path.basename(picturePath)
            #logging
            logging.debug(f"currently doing {fileName}, ({i}/{length})")
            #initiation
            dictionaryList = []
            scoreList = []
            image = cv2.imread(picturePath)
            for j in range(4):
                #rotate image
                angle = j * 90
                rotated = imutils.rotate_bound(image, angle)
                #dictionary
                dic = pytesseract.image_to_data(rotated, lang='Lat', output_type=pytesseract.Output.DICT)
                dictionaryList.append(dic)
                #score the text
                textList = dic['text']
                text = ' '.join(textList)
                scoreList.append(scoreEnglish2(text))
            #final decisions
            maxScore = max(scoreList)
            idealIndex = scoreList.index(maxScore)
            #best image orientation
            finalImage = imutils.rotate_bound(image, idealIndex * 90)
            #rename pictures to sequenced numbers
            newFileName = f"{i}.jpg"
            newFilePath = os.path.join(folderDir, newFileName)
            cv2.imwrite(newFilePath, finalImage)
            #os.rename(picturePath, newFilePath)
            eleDict = {newFileName:dic}
            allDic.update(eleDict)
        except pytesseract.pytesseract.TesseractError as te:
            logging.error(f"{te}, file: {fileName}")
        except FileExistsError as fe:
            logging.error(f"{fe}, file: {fileName}, i guess it already existed")

    #save json file of text for each image
    jsonText = json.dumps(allDic, indent=4)
    with open('json postgrad text.txt', 'w+') as jsonFile:
        jsonFile.writelines(jsonText)

def drawBoxes():
    defImg = cv2.imread("postgrad2.jpg")
    img = np.copy(defImg)
    lang = 'eng'
    d = pytesseract.image_to_data(defImg, lang=lang, output_type=pytesseract.Output.DICT)
    nBoxes = len(d['level'])
    for i in range(nBoxes):
        x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 1)
    cv2.imshow('Image', img)
    cv2.waitKey(0)

    #text = d['text']
    '''text = ' '.join(text)
    text = scoreEnglish(text)'''
    #text = pytesseract.image_to_string(defImg, lang=lang)
    text = pytesseract.image_to_data(defImg, lang=lang, output_type=pytesseract.Output.DICT)
    text = text.keys()
    logging.debug(text)

if __name__ == "__main__":
    st = time.monotonic()
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_141927.jpg"
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_142413.jpg"
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_142413.jpg"
    imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "pdf ocr try.png"
    #scan(imgDir)
    organiseImages()
    #drawBoxes()
    deltaTime = time.monotonic() - st
    print(f"The duration was {deltaTime}")