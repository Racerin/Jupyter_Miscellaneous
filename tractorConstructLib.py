import requests, re, json, functools, string, time, logging, urllib, types, collections


#bracketNumberPattern = r"[(]\d+\.?\d*[)]"
bracketNumberPattern = r"\( ?[0-9.]+ ?\)"
sectionsPattern = r'[A-Z and]{5,}:'
sectionsPattern = r'([A-Z ]|and):'
#sectionsPattern = r'(([A-Z ])|and)+:'

dbPerfPatt = r"DRAWBAR\s*PERFORMANCE"
ptoPerfPatt = r"POWER\s*TAKE-OFF\s*PERFORMANCE"
threePointHitchPerfPatt = r"THREE\s+POINT\s+HITCH\s+PERFORMANCE"
hydraulicPerfPatt = r"HYDRAULIC\s+PERFORMANCE"
perfPatt = r"[A-Z- ]+PERFORMANCE"
#fuelAndOilPatt = r"FUEL\s*and\s*OIL:"
#fuelAndOilPatt = r"CONSUMABLE"
fuelAndOilPatt = r"(\s*(FUEL|OIL|TIME)\s*){2,}"
enginePatt = r"ENGINE:\s+"
engineOperatingParametersPatt = r"ENGINE\s+OPERATING\s+PARAMETERS:"
chassisPatt = r"CHASSIS:\s+"
repairAndAdjustmentPatt = r"REPAIRS\s+AND\s+ADJUSTMENTS"
notePatt = r"NOTE\s*[0-9]*:"
remarksPatt = r"REMARKS:"
tiresAndWeightPatt = r"TIRES\s+AND\s+WEIGHT"
hitchDimensionsAsTestedPatt = r"HITCH\s+DIMENSIONS\s+AS\s+TESTED"
soundLevelPatt = r"TRACTOR\s+SOUND\s+LEVEL"
textSectionPatterns = {'fuel and oil':fuelAndOilPatt, 'engine':enginePatt, 'chassis':chassisPatt,
'repair and adjustment':repairAndAdjustmentPatt, 'note':notePatt, 'remarks':remarksPatt,
'tires and weight':tiresAndWeightPatt, 'three point hitch performance':threePointHitchPerfPatt,
'hitch dimension ad tested':hitchDimensionsAsTestedPatt, 'sound level':soundLevelPatt,
'engine operating parameters':engineOperatingParametersPatt,}
textSectionExceptionPatterns = [dbPerfPatt, ptoPerfPatt, threePointHitchPerfPatt, hydraulicPerfPatt]

tractorCompanies = ['AGCO', 'Case IH', 'Challenger', 'John Deere', 'Kubota', 'McCormick', 
                    'Massey Ferguson', 'New Holland', 'Bobcat', 'Buhler', 'Versatile', 
                    'Caterpillar', 'Cabela''s', 'CLAAS', 'Fendt', 'Hurlimann', 
                    'Valmet', 'White', 'SAME', 'TYM', 'FarmTrac', 'Zetor',]

'''def mostAbundantWord(strung, letterMin=5):
    allWords = re.findall(r"[a-zA-Z]+", strung)
    #allWords = re.findall(r"\w+", strung)
    uniqueWords = list(set(allWords))
    counter = [allWords.count(word) for word in uniqueWords]
    freqSortWords = [word for c,word in sorted(zip(counter, uniqueWords)) if len(word)>=letterMin]
    [print(c,word) for c,word in sorted(zip(counter, uniqueWords)) if len(word)>=letterMin]
    mostFreqWord = freqSortWords[-1]
    return mostFreqWord'''
def mostAbundantWord(strung, letterMin=4, letterMax=10):
    allWords = re.findall(r"[a-zA-Z]+", strung)
    allWords = [word for word in allWords if len(word) >= letterMin and len(word) < letterMax]
    mostFreqWord = collections.Counter(allWords).most_common(1)
    return mostFreqWord[0][0]

def extractBracketNumberFromText(strung):
    eachFloat = []
    for bracket in re.findall(bracketNumberPattern, strung):
        numStr = bracket[1:-1]
        try:
            num = float(numStr)
            eachFloat.append(num)
        except ValueError:
            continue
    return eachFloat
def bracketMatchToFloat(matchObject):
    try:
        stringBracket = matchObject.group(0)
        stringFloat = stringBracket[1:-1]
        num = float(stringFloat)
        return num
    except ValueError:
        return None

def stringDotProduct(strung, strPatt, caseSensitive=True):
    l1, l2 = len(strung), len(strPatt)
    #error checking, TBD
    if l1 < l2:
        return 0
    strung, strPatt = (strung, strPatt) if caseSensitive else (strung.lower(), strPatt.lower())
    #initiation
    diff = l1 - l2
    corrCounter = []
    #all possible linear combinations
    for a in range(diff + 1):
        corrCounterHold = 0
        subStrung = strung[a:a+l2]
        #
        for r in range(l2):
            corrCounterHold += 1 if subStrung[r] == strPatt[r] else 0
        corrCounter.append(corrCounterHold)
    highestCorrelation = max(corrCounter) / l2
    #print("Correlations", highestCorrelation, strung, "::::::::", strPatt)
    return highestCorrelation

def divideTextIntoSections(strung, sectionsPatt=sectionsPattern, extraAtStart=True):
    #Use a pattern to detect all sections of text and returns the extra split with the title|subString dict
    sectionTitles = re.findall(sectionsPatt, strung)
    subStrings = re.split(sectionsPatt, strung)
    #Get rid of text that are part of text exceptions
    for i, subString in enumerate(subStrings):
        for exceptPatt in textSectionExceptionPatterns:
            splits = re.split(exceptPatt, subString)
            subStrings[i] = splits[0]
            if len(splits) > 1:
                #if there is a split, replace the subString with the 1st part of the split
                #subStrings[i] = splits[0]
                print(exceptPatt)
    #now create dictionary of section titlekey to section text value
    try:
        assert len(sectionTitles) + 1 == len(subStrings)
        extraSubString = subStrings[0] if extraAtStart else subStrings[-1]
        alignedSubStrings = subStrings[1:] if extraAtStart else subStrings[:-1]
        pairs = { sectionTitles[i]:subStr for i, subStr in enumerate(alignedSubStrings) }
        pairs.update({'untitled':extraSubString})
    except AssertionError:
        print('These are the corresponding lengths', len(sectionTitles), len(subStrings))
        assert False
    except:
        print('These are the corresponding lengths', len(sectionTitles), len(subStrings))
        pairs = {'not': 'working'}
    #PRINT
    [print(x) for x in pairs.items()]
    return pairs

def parseSection(dict):
    #use a dictionary of text separated according to titles to do any final parsing of each section.
    ansDict = {}
    remainderSectionText=[]
    remainderTitles = []
    titleMatch = lambda pat,tit,cs=False: stringDotProduct(pat, tit, caseSensitive=cs) > 0.8    #to be used
    for title, sectionText in dict.items():
        if stringDotProduct(title, "parameters", caseSensitive=False) > 0.8:
            ansDict.update({"Engine Operating Parameters":sectionText})
        if stringDotProduct(title, "engine", caseSensitive=False) > 0.8:
            ansDict.update({"Engine":sectionText})
            #tempDict = finerParseSection("engine", sectionText)
            #ansDict.update(tempDict)
        elif stringDotProduct(title, "Location") > 0.8:
            ansDict.update({"Location of Test":sectionText})
        elif stringDotProduct(title, "Test") > 0.8:
            ansDict.update({"Dates of Test":sectionText})
        elif stringDotProduct(title, "OIL") > 0.8 or stringDotProduct(title, "TIME") > 0.8 or stringDotProduct(title, "FUEL") > 0.8:
            ansDict.update({"Fuel and Oil and Time":sectionText})
            #tempDict = finerParseSection("OIL", sectionText)
            #ansDict.update(tempDict)
        elif stringDotProduct(title, "chassis", caseSensitive=False) > 0.8:
            ansDict.update({"Chassis":sectionText})
            #tempDict = finerParseSection("chassis", sectionText)
            #ansDict.update(tempDict)
        elif stringDotProduct(title, "adjustments", caseSensitive=False) > 0.8:
            ansDict.update({"Repairs and Adjustments":sectionText})
        elif stringDotProduct(title, "remarks", caseSensitive=False) > 0.8:
            ansDict.update({"Remarks":sectionText})
        elif stringDotProduct(title, "note", caseSensitive=False) > 0.8:
            #there are multiple notes so number each.
            numStr = str(re.search(r"\d", title).groups())
            nm = " ".join(["Note", numStr])
            ansDict.update({nm:sectionText})
            #extra processing. there are multiple 'NOTEs'
        elif stringDotProduct(title, "fluids", caseSensitive=False) > 0.8:
            ansDict.update({"Consumable Fluids":sectionText})
        elif stringDotProduct(title, "category", caseSensitive=False) > 0.8:
            #ignore
            remainderSectionText.append(sectionText)
            remainderTitles.append("")
        else:
            remainderSectionText.append(sectionText)
            remainderTitles.append(title)
            #option, put into dictionary with default title
            ansDict.update({title:sectionText})
    #after parsing through each title
    print("These are the remaining titles", remainderTitles)
    #option, add collection of scrap text to dictionary
    remainingText = " ".join(remainderSectionText)
    ansDict.update({"remainder":remainingText})
    return ansDict

def parsePerformanceSections(dict):
    #use a dictionary of text separated according to titles to do any final parsing of each section.
    ansDict = {
        'drawbar':[],
    }
    remainderSectionText=[]
    remainderTitles = []
    insideOf = lambda pat, tit: pat in tit.lower()
    for title, sectionText in dict.items():
        if insideOf('drawbar', title):
            interList = extractDrawbarPerformance(sectionText)
            #print("How much in here?", len(interList))
            perfValues = [dic["values"] for dic in interList]   #for now
            #perfValues = interList
            new = ansDict["drawbar"] + perfValues
            ansDict['drawbar'] = new
        else:
            remainderTitles.append(title)
            remainderSectionText.append(sectionText)
    #just print the remaining titles
    #print("These are the remaining titles", remainderTitles)
    return ansDict

def extractDrawbarPerformance(strung, startIndex=0):
    #creates list of dictionaries with a 'title' and performance values
    numberMatches = [m for m in re.finditer(bracketNumberPattern, strung)]
    #NEXT: get numeric values of each dbPerformance by trying every sequenced combination of values
    thresholdPercent = 1
    checkLength = 5
    nums = [bracketMatchToFloat(m) for m in numberMatches]
    correctTuples = []
    rowMatches = []
    for i, brac in enumerate(nums[:-checkLength]):
        try:
            subNums = nums[i:i+checkLength]
            checkTup = subNums[:checkLength]
            power, pull, speed, fc1, fc2 = checkTup
            calcPower = pull * speed/3.6
            diff = abs(calcPower - power)
            ratio = diff/min(power, calcPower)
            if ratio < (thresholdPercent/100):
                #calculated power is close enough to recorded power
                #get corresponding matcObjects for each number
                ranger = range(i, i+checkLength)
                tempMatches = [numberMatches[j] for j in ranger]
                #store sorted values
                rowMatches.append(tempMatches)
                correctTuples.append(checkTup)
        except:
            continue
    print(f"Total count is {len(rowMatches)}.")
    #NEXT: get the text before each row values
    startIndex = 0
    befores = []
    for rowMatch in rowMatches:
        matchStart = rowMatch[0]
        matchEnd = rowMatch[-1]
        endInd = matchStart.start()
        #get the title
        title = strung[startIndex:endInd]
        befores.append(title)
        #condition for next iteration
        startIndex = matchEnd.end()
    #now, create list with dictionary of each row
    ansList = []
    for i, tup in enumerate( list( zip(befores,correctTuples) ) ):
        beforeText,row = tup
        tempDict = {'beforeText':beforeText, 'values':row}
        ansList.append(tempDict)
    #[print(x) for x in ansList]
    print("This is the amount of values in extract.", len(ansList))
    return ansList

