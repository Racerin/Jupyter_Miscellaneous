import cv2, pytesseract, time, json, re, os, random, string, enchant, threading

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"


def loadJson(jsonFileName="json postgrad text.txt"):
    with open(jsonFileName, 'r') as jsonFile:
        jsonText = jsonFile.readlines()
        print(jsonText)
    dic = json.load(jsonText)
    return dic
def saveDict(dic, fileName):
    text = json.dumps(dic, indent=0)
    with open(fileName, 'w+') as jsonFile:
        jsonFile.writelines(text)
def randomTextImage2Dict():
    randomInt = random.randint(0, 1000)
    #get image
    folderPath = "C:\\Users\\drsba\\Desktop\\report pictures"
    imagePath = os.path.join(folderPath, f"{randomInt}.jpg")
    img = cv2.imread(imagePath)
    #scan image for dict
    dic = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    return dic

def lineText(dic, lineNums):
    lines = dic['block_num']
    texts = dic['text']
    assert all([lineNum in lines for lineNum in lineNums])
    assert len(texts) == len(lines)
    lineText = []
    for lineNum in lineNums:
        lineText += [text for i, text in enumerate(texts) if lines[i] == lineNum]
    finalText = " ".join(lineText)
    return finalText

def main1():
    dic = randomTextImage2Dict()
    ln = lineText(dic, [3])
    print(ln)

if __name__ == "__main__":
    main1()