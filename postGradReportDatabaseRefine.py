import numpy as np
import cv2, pytesseract, time, json, re, os, random, string, enchant, threading
from functools import partial

english = enchant.Dict("en_GB")

supervisorCorrectionList = [
    ["Mr. Stanley Lau", "stanley"],
    ["Professor Chanan Syan", "syan"],
    ["Mrs. Joel Ann Cook Walcott", "walcott"],
    ["Mr. Kendrick Burgess", "Burgess"],
    ["Mr. Daren Maynard", "Maynard", "Daren"],
    ["Mrs. Celia Gibbings", "Gibbings", "Celia"],
    ["Mrs. Antonia Popplewell", "Antonia", "Popplewell"],
    ["Dr. Godfrey Martin", "Godfrey"],
    ["Dr. Sydney Thomas", "sydney"],
    ["Dr. Hector Martin", "Hector"],
    ["Dr. Joseph Khan", "Khan"],
    ["Dr. Everson Peters", "Everson"],
    ["Dr. Leighton Ellis", "Leighton"],
    ["Mr. Kenrick Burgess", "Burgess"],
    ["Dr. Winston Lewis", "Winston"],
    ["Mr. Daren Maynard", "Maynard"],
    ["Dr. Michael Foley", "Foley"],
    ["Professor Winston H. Emeritus Suite", "suite"],
    ["Prof Kit Fai Pun", "pun", "Kit", "Fai"],
    ["Mr. John Gerard Agard", "Agard", "Gerard"],
    ["Ms. Muriel Lezama", "Lezama"],
    ["Dr. Manfred Jantzen", "Manfred", "Jantzen"],
    ["Dr. Ruel Ellis", "Ruel", "Ellis"]
]
dictionary = {}
saveDictFileName = "postGradReportDatabaseRefined.json"

#get the file
with open("postGradReportDatabase.json") as file:
    dictionary = json.loads(file.read())

def mane():
    startTime = time.monotonic()
    correctDict()
    #get information of the defective entries
    #defective(dictionary)
    #correct the dictionary now
    #correctDict()
    #OUTPUT
    #print outputs
    printStats(startTime)
    #SAVE, record the new dictionary
    saveDict(saveDictFileName)

def correctDict():
    for k,subDict in dictionary.items():
        #remove 'department' property
        if "Department" in subDict:
            del subDict["Department"]
        #convert years to intergers
        try:
            year = subDict["Year"]
            assert len(year) == 4
            subDict["Year"] = int(year)
        except:
            print(f"Didn't work out to convert year {year}.")
        #put in metadata key
        if not "Metadata" in subDict:
            subDict["Metadata"] = ""
        #put in ID key
        if not "ID" in subDict:
            subDict["ID"] = ""
        #Titlize student name
        subDict["Student Name"] = subDict["Student Name"].title()
        #put full stops after single letters of Student Name
        tempy = subDict["Student Name"]
        for m in re.finditer(r"\b[A-Z]\b", tempy):
            st, nd = m.start(), m.end()
            tempy = tempy[:st] + f"{tempy[st]}." + tempy[nd:]
        subDict["Student Name"] = tempy
        #subDict["Student Name"] = re.sub(r"\b\w\b", )
        #Titlize project title except for words not in the english dictionary
        projectTitle = subDict["Project Title"]
        #wordPattern = r"\b\w+\b"
        wordPattern = r"\w+"
        for match in re.finditer(wordPattern, projectTitle):
            word = match.group(0)
            if english.check(word.lower()):
                st, nd = match.start(), match.end()
                projectTitle = projectTitle[:st] + word.title() + projectTitle[nd:]
        subDict["Project Title"] = projectTitle
        #add 'executive summary' to metadata if exist
        exeSum = "executive summary"
        if exeSum in subDict["Abstract"].lower() and not exeSum in subDict["Metadata"].lower():
            subDict["Metadata"] += f",{exeSum.title()}"
        #Convert appropriate strings to list
        '''sup = subDict["Supervisor"]
        if len(sup) > 2:
            if sup[0] == "[" and sup[-1] == "]":
                sup = sup[1:-1]
                sups = re.split(r",", sup)
                sups = [" ".join(re.findall(r"\w", sup)).title() for sup in sups]
                subDict["Supervisor"] = sups'''
        #use unique supervisor names
        correctSupervisors(subDict)
    #rename key to 'year,studentname,id number' format
    for k,v in dictionary.items():
        studentDict = v
        newName = f'{v["Year"]},{v["Student Name"]},{v["ID"]}'
        #remove "," if it is the last string of newName
        newName = newName[:-1] if newName[-1] == ',' else newName
        del dictionary[k]
        dictionary.update({newName:studentDict})

def removeDefectives(dictionary):
    errorStudents = []
    for studentKey, studentDict in dictionary.items():
        errorCheckList = []
        #PMBoK
        pmbok = studentDict["Knowledge Areas"]
        length = len(pmbok)
        if length < 3:
            errorCheckList.append("K.A")
        #supervisor
        superv = studentDict["Supervisor"]
        chosenSupervisor = ""
        for tup in supervisorCorrectionList:
            #check through the supervisor list. 
            #If no words match, add to errors to check
            bestName = tup[0]
            for name in tup:
                lowerCase = name.islower()
                #if the checkword is lowercase, then check as lowercase
                scan = superv.lower() if lowerCase else superv
                if name in scan:
                    chosenSupervisor = bestName
        if not chosenSupervisor:
            errorCheckList.append("Supervisor")
        #abstract, valid words
        abstract = studentDict["Abstract"]
        ans = percentWords(abstract)
        if ans < 0.6:
            errorCheckList.append("Abstract might be corrupted.")
        #project title, valid words
        projectName = studentDict["Project Title"]
        ans = percentWords(projectName)
        if ans < 0.6:
            errorCheckList.append("Project might be corrupted.")
        #append errorStudent
        if errorCheckList:
            errorCheckList.insert(0, studentKey)
            errorStudents.append(errorCheckList)
        else:
            errorStudents.append([studentKey])
    #sort the list
    errorStudents = sorted(errorStudents, reverse=True)
    #save the data missing per person
    with open("personsMissingData.json", mode='w') as file:
        '''saveString = json.dumps(errorStudents)
        file.writelines(saveString)'''
        for listy in errorStudents:
            file.write(f"{listy}\n")
def correctSupervisors(diction):
    superv = diction["Supervisor"]
    if isinstance(superv, list):
        #cop out, supervisor not fixed, just left as list
        return superv
    breakOut = False
    for tup in supervisorCorrectionList:
        breakOut = False
        #check through the supervisor list. 
        #If no words match, add to errors to check
        bestName = tup[0]
        for name in tup:
            lowerCase = name.islower()
            #if the checkword is lowercase, then check as lowercase
            toScan = superv.lower() if lowerCase else superv
            if name in toScan:
                diction["Supervisor"] = bestName
                breakOut = True
                break
        if breakOut:
            break
    else:
        #if no supervisor matched, just set name as empty
        diction["Supervisor"] = ""
def saveDict(fileName):
    with open(fileName, mode='w') as file:
        saveString = json.dumps(dictionary)
        file.writelines(saveString)
def printStats(startTime):
    endTime = time.monotonic()
    duration = endTime - startTime
    #how many students
    option = 1
    if option == 1:
        #get all the supervisors uniqued
        supervisors = [v["Supervisor"] for v in list(dictionary.values())]
        uniqueSupervisors = list(set(supervisors))
        print(f"There were {len(supervisors)} supervisors and {len(uniqueSupervisors)} unique supervisors.")
    elif option == 2:
        uniquePropertyKeys = set()
        for student in dictionary.values():
            '''zet = set(student.keys())
            uniquePropertyKeys.add(zet)'''
            uniquePropertyKeys.add(frozenset(set(student.keys())))
        propertiesDict = {}
        uniquePropertyKeys = list(uniquePropertyKeys)
        [propertiesDict.update({propertyName,[]}) for propertyName in uniquePropertyKeys]
        print(len(propertiesDict), "summ")
        for propertyName in uniquePropertyKeys:
            for student in dictionary.values():
                if propertyName in student:
                    propertiesDict[propertyName].append(student[propertyName])
        for propertyName, vals in propertiesDict.items():
            print(f"The unique quantity of {propertyName} is {len(vals)}.")


    print(f"There were {len(dictionary.values())} students.")
    print(f"The refining took {duration} seconds.")
def percentWords(strung):
    words = re.findall(r"\S", strung)
    total = len(words)
    howManyWords = 0
    ans = 0
    for word in words:
        conditionedWord = word.lower().strip()
        howManyWords += 1 if english.check(conditionedWord) else 0
    try:
        ans = howManyWords/total
        return ans
    except ZeroDivisionError:
        return 0

if __name__ == "__main__":
    mane()