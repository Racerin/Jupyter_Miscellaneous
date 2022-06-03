#codes to help develope tractor text parser
from tractorDatabaseParsing import *
import tractorConstructLib as tcl
import math, bestOf

noError = bestOf.ignoreError
class Calculator():
    
    #a bunch of tractor formulas
    def normalizedGeometry(self):
        #normalize db height/lenth, wheelbase, cogHeight w.r.t wheelbase
        self.cog_length_normalized = self.cog_length / self.wheelbase
        self.cog_height_normalized = self.cog_height / self.wheelbasew
        self.drawbar_height_normalized = self.drawbar_height / self.wheelbase
        self.drawbar_length_normalized = self.drawbar_height / self.wheelbase

def randomTractorDict():
    with open("PDF URLs.json") as jsonFile:
        urls = jsonFile.readlines()
        randomURL = random.choice(urls).strip()
        print("This is the random url", randomURL)
        #hopefully a tractor url
        tractorDict = onlinePDF2Dict(randomURL)
        return tractorDict
def getAllTractorDicts(limit=None):
    allTractorDicts = []
    count = 0
    with open("PDF URLs.json") as jsonFile:
        for url in jsonFile:
            url = url.strip()
            try:
                tractorDict = onlinePDF2Dict(url)
                allTractorDicts.append(tractorDict)
                count += 1
            except:
                continue
            #limit the amount
            if isinstance(limit, (int, float)):
                if count >= limit:
                    break
    return allTractorDicts

def randomListElement(listy):
    length = len(listy)
    randomInd = random.randint(0, length)
    return listy[randomInd]

def similiarLetters(str1, str2):
    set1, set2 = set(str1), set(str2)
    length = len(set2)
    count = len([letter for letter in set1 if letter in set2])
    try:
        similiarity = count/length
        print("Similiarity", similiarity, "strings", str1, "**********", str2)
        return similiarity
    except ValueError:
        return 0
        
def selfFullingStringList(addString, threshold=0.8, currentSet=set(), criteria=lambda x:len(x)>=4):
    assert isinstance(addString, str)
    #make sure string meets criteria
    assert criteria(addString)
    if currentSet:
        toAdd = set()
        for strung in currentSet:
            score = []
            score.append(similiarLetters(strung, addString))
            score.append(similiarLetters(addString, strung))
            if max(score) >= threshold:
                #take out the compared string
                currentSet.remove(strung)
                pair = [strung, addString]
                #get the smaller, alphabetical string of the pair
                bestStrung = pair.sort()
                bestStrung = bestStrung.sort(key=len, reverse=True)
                toAdd.add(bestStrung[0])
        else:
            currentSet.update(toAdd)
    else:
        currentSet.add(addString)

def splitTextAccordingToPatterns(strung, patternList, exceptPattList=[], calcKeys=True):
    subStrings = [strung]
    for pattern in patternList:
        subStringHold = []
        for subString in subStrings:
            subStringHold += re.split(pattern, subString)
        subStrings = subStringHold
    #get the found pattern responses now
    if calcKeys:
        allKeys = [strung]
        for subString in subStrings:
            keysHold = []
            for key in allKeys:
                if key and subString:
                    keysHold += key.split(subString)
            allKeys = keysHold
        allKeys = [k for k in allKeys if re.findall(r"\S", k)]
    else:
        allKeys = []
    #now, remove the splits for exceptPattList
    if exceptPattList:
        for i, subString in enumerate(subStrings):
            for patt in exceptPattList:
                m = re.search(patt, subString)
                if m:
                    pos = m.start()
                    subStrings[i] = subString[:pos]
    #PRINTING
    '''for i,sub in enumerate(subStrings):
        if i >= 1:
            print(f"******* ALL THE KEYS {i+1}.", allKeys[i-1])
        print(f"******* HERE WE GO {i+1}.", sub)
    checkIfSectionMissing(allKeys)'''
    return (allKeys, subStrings)


def checkIfSectionMissing(caughtKeys):
    didntCatchPatts = []
    pattList = list(tcl.textSectionPatterns.values())
    keysSet = set(caughtKeys)
    for checkPatt in pattList:
        for key in caughtKeys:
            #correlate = similiarLetters(checkPatt, key)
            correlate = tcl.stringDotProduct(checkPatt, key)
            if correlate > 0.8:
                keysSet.discard(key)
                break
        else:
            didntCatchPatts.append(checkPatt)
    #PRINT
    print("Did not catch these patterns.", didntCatchPatts)
    print("All keys.", caughtKeys)
    print("Did not use these keys.", keysSet)

def finerParseSection(key, sectionText):
    ansDict = {}
    if key == "engine":
        pass
    if key == "OIL":
        pass
    if key == "chassis":
        pass
    if key == "remainder":
        pass
    return ansDict

def textSectioning(strung, patternList, exceptPattList=[]):
    indices = []
    for pattern in patternList+exceptPattList:
        matches = re.finditer(pattern, strung)
        [indices.append(m.start()) for m in matches]
    length = len(indices)
    texts = []
    for i, index in enumerate(indices):
        nextIndex = len(strung) if i == (length - 1) else indices[i+1]
        subString = strung[index:nextIndex]
        #remove any exception substring from current substring
        for exceptPatt in exceptPattList:
            m = re.search(exceptPatt, subString)
            if m:
                endInd = m.start()
                subString = subString[0:endInd]
        texts.append(subString)
    [print("******* HERE WE GOOOOO.",t) for t in texts]
            


def getTitles5(streng, listsOfNums, startIndex=0, removePatt=""):
    removePatt = r"\s"
    if removePatt:
        streng = re.sub(removePatt, "", streng)
    allStartInd = []
    allEndInd = []
    allKeys = []
    for numberList in listsOfNums:
        listOfPairs = []
        for numIndex,num in enumerate(numberList):
            strNum = str(num)
            findIter = re.finditer(strNum, streng)
            indices = [m.start(0) for m in findIter]
            myPairs = [(ind,numIndex) for ind in indices]
            listOfPairs += myPairs
        listOfPairs.sort()
        #now, check for sequenced bracket
        listLength = len(numberList)
        pairsLength = len(listOfPairs)
        indexCheck = list(range(listLength))
        for i in range(pairsLength-listLength):
            pairs = listOfPairs[i:i+listLength]
            numberIndices = [y for x,y in pairs]
            if indexCheck == numberIndices:
                positions = [x for x,y in pairs]
                allStartInd.append(positions[0])
                allEndInd.append(positions[-1])
                allKeys.append(str(numberList))
                break
    #now, get all titles (in-between text) of brackets
    allEndInd.insert(0, startIndex)
    indexPairs = list(zip(allEndInd, allStartInd))
    titles = [streng[st:nd] for st,nd in indexPairs]
    [print("THIS IS A TITLE.", tit) for tit in titles]
    print("This is the length", len(titles))

def timeit(method):
    def timed(*args, **kw):
        ts = time.monotonic()
        result = method(*args, **kw)
        te = time.monotonic()
        timeDiff = te - ts
        min, sec = divmod(timeDiff, 60)
        print(f"The function took {min} minutes and {sec} seconds to complete.")
        return result
    return timed

@timeit
def mane():
    # get a list of tractor from text file and do stuff
    options = 5
    tractor = randomTractorDict()
    print(f"These are the fields of the tractor. {list(tractor.keys())}")
    strung = tractor["text"]
    
    #main logic
    if options == 1:
        #write file for one tractor
        oneTractorFileName = "One tractor info.txt"
        #deleteFileIfExist(oneTractorFileName)
        with open(oneTractorFileName, 'w+') as file:
            file.write(strung)
    if options == 2:
        #trying out separating text into sub pieces
        #patterns = list(tcl.textSectionPatterns.values())
        patterns = [r'[A-Z and]+:']
        splitTextAccordingToPatterns(strung, patterns, tcl.textSectionExceptionPatterns)
    if options == 5:
        dict = tcl.divideTextIntoSections(strung)
        ans = tcl.parseSection(dict)
        #dict.update(ans)
    elif options == 3:
        numz = string2BracketNums(strung)
        getTitles5(strung, numz)
    elif options == 4:
        tcl.extractDrawbarPerformance(strung)

@timeit
def mane2():
    #create a list of text/dictionaries of tractor to use for stuff
    options = 4
    dictionaries = getAllTractorDicts()

    #MAIN LOGIC
    if options == 1:
        [print(dict.text) for dict in dictionaries if "text" in dict]
    elif options == 2:
    #goes through all tractors and gets/parse all info and saves to json file
        allTractors = []
        for tracDict in dictionaries:
            try:
                strung = tracDict["text"]
                dict = tcl.divideTextIntoSections(strung)
                ansDict = tcl.parseSection(dict)
                tracDict.update(ansDict)
                allTractors.append(tracDict)
            except:
                continue
        else:
            with open("all my tractors live in texas.json", mode="w+") as phil:
                json.dump(allTractors, phil)
    elif options == 3:
    #goes through all tractors and save all 'X PERFORMANCE' numbers to json file
        allTractors = {}
        for tracDict in dictionaries:
            try:
                strung = tracDict["text"]
                nm = getTractorNameFromDict(tracDict)
                dict = tcl.divideTextIntoSections(strung, sectionsPatt=tcl.perfPatt)
                #print(list(dict.keys()), "keys of tractor sections")
                interTracVals = tcl.parsePerformanceSections(dict)
                ansDict = {nm:interTracVals}
                if interTracVals:
                    allTractors.update(ansDict)
            except:
                print("something went wrong.")
                continue
        with open("performance numbers only.json", mode="w+") as phil:
            print(len(allTractors), "This is the number of all tractors")
            json.dump(allTractors, phil)
    elif options == 4:
        #save all the strings of each tractor
        allTractors = {}
        for tracDict in  dictionaries:
            try:
                strung = tracDict["text"]
                nm = getTractorNameFromDict(tracDict)
                if nm:
                    tempDict = {nm:strung}
                    allTractors.update(tempDict)
            except:
                continue
        with open("all tractor texts.json", mode="w+") as phil:
            print(len(allTractors), "This is the number of all tractors")
            json.dump(allTractors, phil)

@timeit
def mane3():
    #test certain logics
    #variables
    Wd = [20443, 20443, 583386386, 583386386]
    pull = [0, 0, 5000, 5000]
    #kinda start the loop from here
    GT = sum(pull) + Wc*math.sin(angle) + Rt
    nDriveWheels = 2
    for i in range(10):
        pull = [GT/nDriveWheels for i in range(4) if i in [3,4] ]
        ct = [pull[i]/Wd[i] for i in range(4)]
        print()
    
if __name__ == "__main__":
    mane3()