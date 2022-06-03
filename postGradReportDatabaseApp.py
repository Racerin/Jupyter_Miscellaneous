import numpy as np
import cv2, pytesseract, time, json, re, os, random, string, enchant, threading
from functools import partial

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
english = enchant.Dict("en_GB")

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.config import Config
Window.clearcolor = (0.25,0.5,0.25,1)
Config.set('graphics', 'fullscreen', 1)
#Config.set('graphics', 'window_state', 'maximized')
Config.write()

knowledgeAreas = [
"Integration", "Scope", "Schedule", "Cost", "Quality",
"Resource", "Communications", "Risk", "Procurement", "Stakeholder"]
propertyKeys = ['Student Name', 'Project Title', 'ID', 'Metadata',
'Supervisor', 'Year', 'Abstract', 'Keywords', 'Knowledge Areas']
nameTitles = ["Dr.", "Mr.", "Mrs.", "Ms.", "Prof."]
saveTimeInterval = 15
settingsFileName = 'postGradReportDatabaseSettings.json'
databaseFileName = 'postGradReportDatabase.json'

def putNameTitleIn(name):
    for title in nameTitles:
        dotlessTitle = title[:-1]
        name.replace(dotlessTitle, title)
    return name
def binaryReducedVal(strung, errorIt=True):
    if strung == 'down':
        return True
    elif strung == 'normal':
        return False
    elif errorIt:
        raise(f"The value '{strung}' could not be reduced to a binary.")
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
def tryKeyDict(dictionary, myKeys):
    if isinstance(myKeys, str):
        #convert item to list of item
        mykeys = [myKeys]
    assert all((isinstance(key, str) for key in myKeys))
    keys = list(dictionary.keys())
    for key in keys:
        for myKey in myKeys:
            if myKey in key:
                return dictionary[key]
def capitalLines(strung):
    #return the biggest island of lines with only capital letters
    lines = re.split(r"\n+", strung)
    st, nd = 0, 0
    island = False
    finalStrung = ""
    #creating islands, with start and end position saved
    posTuples = []
    try:
        for i, line in enumerate(lines):
            currentIsland = line.isupper()
            nd = i
            if currentIsland:
                #positive change
                if not island:
                    st = i
            else:
                #negative change
                if island:
                    tup = (st, nd)
                    posTuples.append(tup)
            island = currentIsland
        else:
            #if island is still open, save one more island
            if island:
                tup = (st, nd)
                posTuples.append(tup)
                island = False
        islandSize = [nd-st for st, nd in posTuples]
        #sort islands according to size
        sortedIslands = [pos for diff, pos in sorted(zip(islandSize,posTuples))]
        stBest, ndBest = sortedIslands[-1]
        bestLines = [line for i, line in enumerate(lines) if i >= stBest and i < ndBest]
        finalStrung = '\n'.join(bestLines)
    except Exception as err:
        print(err)
    return finalStrung
def bestNameCheck(text, scoreLimit=1):
    #algoritm for detecting name in multiline text
    lines = re.split(r"\n", text)
    scores = [None] * len(lines)
    for i, line in enumerate(lines):
        allNonSpace = re.findall(r"\S+", line)
        nonWords = 0
        #find discrete words
        discretes = re.findall(r" \w+ ", f" {line} ")
        for discrete in discretes:
            if not english.check(discrete.lower().strip()):
                nonWords += 1
        totalCount = len(allNonSpace)
        try:
            score = (totalCount - nonWords)/totalCount
        except Exception as err:
            score = 1
            print(err)
        scores[i] = score
    sortedLines = [line for score, line in sorted(zip(scores, lines)) if isinstance(score, (float, int))]
    bestLine = sortedLines[0]
    wordList = re.findall(r"\w+", bestLine)
    bestName = ' '.join(wordList)
    return bestName
def wordExistInFile(word, caseSensitive=True, fileName='postGradReportDatabase.json'):
    if not word:
        return False
    try:
        with open(fileName, mode="r") as file:
            externalText = file.readlines()
            externalText = " ".join(externalText)
            if caseSensitive:
                word = word.lower()
                if word in externalText.lower():
                    return True
            else:
                if word in externalText:
                    return True
    except IOError as err:
        print("Was not able to check the file.")
        print(err)
def getStudentNameFromFile(listOfStudents=[], key="Student Name", fileName='postGradReportDatabase.json', recalculate=False):
    if not listOfStudents and not recalculate:
        listOfStudents = getAllKeyValues(key, fileName=fileName, recalculate=recalculate)
    return listOfStudents
def getSupervisorsFromFile(listOfSupervisors=[], key="Supervisor", fileName='postGradReportDatabase.json', recalculate=False):
    if not listOfSupervisors and not recalculate:
        listOfSupervisors = getAllKeyValues(key, fileName=fileName, recalculate=recalculate)
    return listOfSupervisors
def getAllKeyValues(key, fileName='postGradReportDatabase.json', recalculate=False):
    finalList = []
    dictionary = {}
    try:
        with open(fileName, mode='r') as file:
            dictionary = json.loads(file.read())
        for diction in list(dictionary.values()):
            valueOfKey = diction.get(key)
            if valueOfKey:
                finalList.append(valueOfKey)
        #filtering out falses.
        finalList = [x for x in finalList if bool(x)]
        #make the list unique
        finalList = list(set(finalList))
    except ValueError as err:
        print(f"Error with json. {err}")
    except Exception  as err:
        print(f"idk the problem.\n{err}")
    return finalList

class PMBOKSelect(StackLayout):
    size_hint = (0.3, 3)
    knowledgeAreasKeywords = [
        [], 
        ['investigat','review','impact'],
        ['time', 'years'],
        ['profit','economical','price','budget','afford','estimate'],
        ['effect','evaluat','impact'],
        ['PM', 'maturity', 'methodology', 'decision'],
        ['information','review'],
        ['danger','fail'],
        ['export', 'import'],
        ['effect','satisfy','customer']
    ]

    def __init__(self, **kwargs):
        super(PMBOKSelect, self).__init__(**kwargs)
        #controls buttons
        fontSize = '10sp'
        sizeHint = (0.3, 0.01)
        self.scanButton = Button(text='Scan', font_size=fontSize, size_hint=sizeHint)
        self.clearButton = Button(text='Clear', font_size=fontSize, size_hint=sizeHint)
        self.add_widget(self.scanButton)
        self.add_widget(self.clearButton)
        self.scanButton.bind(on_release=self.scanFunc)
        self.clearButton.bind(on_release=self.clearFunc)

        for i, title in enumerate(knowledgeAreas):
            #create toggle Button
            nam = str(i)
            setattr(self, nam, ToggleButton(text=title, size_hint=sizeHint, font_size=fontSize))
            obj = getattr(self, nam)
            #add widget
            self.add_widget(obj)
    @property
    def propertyVal(self):
        #by default, just return the text
        li = self.getList()
        return li
    def clearFunc(self, _=None):
        length = len(knowledgeAreas)
        for i in range(length):
            self.setToggle(i)
    def scanFunc(self, _=None, **kwargs):
        main = App.get_running_app()
        strung = main.gui.scanTextInput.text
        keywordsKnowledgeAreas = [[x]+y for x,y in zip(knowledgeAreas, self.knowledgeAreasKeywords)]
        for i, tup in enumerate(keywordsKnowledgeAreas):
            for keyword in tup:
                if keyword.lower() in strung.lower():
                    #set the toggle button ON
                    self.setToggle(i, value='down')
    def loadFunc(self, dictKnowAreas):
        #turn ON all knowledge areas that are in the list
        assert isinstance(dictKnowAreas, list)
        for dictKnowArea in dictKnowAreas:
            for i, area in enumerate(knowledgeAreas):
                if area.lower() in dictKnowArea.lower():
                    self.setToggle(i, 'down')

    def setToggle(self, index, value='normal'):
        #value options: 'normal', 'down'
        nam = str(index)
        obj = getattr(self, nam)
        obj.state = value
    def getButtonValues(self):
        objs = [getattr(self, str(i)) for i in range(len(knowledgeAreas))]
        buttonsState = [binaryReducedVal(obj.state) for obj in objs]
        return buttonsState
    def getList(self):
        #return list of titles of each toggle button engaged
        dressedKnowledgeAreas = [f"Project {x} Management" for x in knowledgeAreas]
        buttonsState = self.getButtonValues()
        pairs = zip(buttonsState, dressedKnowledgeAreas)
        finalList = [title for state, title in pairs if bool(state)]
        return finalList
        
class EditLayout(BoxLayout):
    orientation = 'vertical'
    size_hint=(0.1,0.2)
    padding = [5]*4
    spacing = 5
    def __init__(self, **kwargs):
        super(EditLayout, self).__init__(**kwargs)
        #properties
        self.reportKey = ""
        fontSize = '10sp'
        #widgets
        buttonsRow = BoxLayout(orientation='horizontal', spacing=self.spacing)
        self.editButton = Button(text="Edit It")
        self.deleteButton = Button(text="Delete")
        self.searchBar = TextInput(multiline=False, font_size=fontSize)
        self.searchButton = Button(text="Search")
        self.reportsDropdown = Spinner(font_size=fontSize)
        #add widgets
        buttonsRow.add_widget(self.editButton)
        buttonsRow.add_widget(self.deleteButton)
        self.add_widget(buttonsRow)
        self.add_widget(self.searchBar)
        self.add_widget(self.reportsDropdown)
        #add bindings
        self.reportsDropdown.bind(text=self.showSelectedValue)
        self.editButton.bind(on_release=self.editFunc)
        self.deleteButton.bind(on_release=self.deleteFunc)
        self.searchBar.bind(on_text_validate=self.searchFunc)
    def editFunc(self, instance=None):
        #takes k:v of each dictionary (loaded and current) and compares each property to then load them
        main = App.get_running_app()
        propLayout = main.gui.props
        oldReportDicts = main.loadDatabase()
        reportKey = self.reportKey
        if reportKey:
            main.clearAllFunc()
            oldReportDict = oldReportDicts[reportKey]
            set1, set2 = set(propertyKeys), set(oldReportDict.keys())
            commonPropertyKeys = list(set1.intersection(set2))
            for key in commonPropertyKeys:
                #load each property value into property.
                index = propertyKeys.index(key)     #indices are correlated
                # name =/= title =/= key. for properties
                name = PropertiesLayout.names[index]
                prop = getattr(propLayout, name)
                val = oldReportDict[key]
                prop.loadFunc(val)

    def deleteFunc(self, instance=None):
        #deletes the selected report
        main = App.get_running_app()
        reportDicts = main.loadDatabase()
        if self.reportKey:
            del reportDicts[self.reportKey]
            #save over dictionary
            main.saveJson(databaseFileName, reportDicts)

    def searchFunc(self, instance=None, val=None, caseSensitive=False):
        #search for matching student reports according to keyword in searchBar
        main = App.get_running_app()
        reportDicts = main.loadDatabase()
        keys = reportDicts.keys()
        searchKey = self.searchBar.text
        if not caseSensitive:
            keysLower = [key.lower() for key in keys]
            searchKey = searchKey.lower()
        #search for matches, ensure to return case sensitive results
        searchResults = [list(keys)[i] for i,key in enumerate(keysLower) if searchKey in key]
        '''lowerSearchResults = [key for key in keysLower if searchKey in key]
        searchResults = [list(keys)[i] for i,key in enumerate(lowerSearchResults)]'''
        sortedSearchResults = sorted(searchResults)
        #now sort results according to position of searchKey in keyword
        '''positionIndices = [key.index(searchKey) for key in sorted(lowerSearchResults)]
        sortedSearchResults = [x for i,x in sorted(zip(positionIndices, sortedSearchResults))]'''
        self.reportsDropdown.values = sortedSearchResults
    def showSelectedValue(self, spinner, text):
        #spinner.text = text
        self.reportKey = text
        #Clock.schedule_once(setattr(self.reportsDropdown, 'is_open', True), 0.5)#no work

class PropertiesLayout(RelativeLayout):
    labelNames = ['Student\nName', 'Project\nTitle', 'Student I.D.', 'Metadata',
    'Supervisor\nName', 'Year', 'Abstract', 'Keywords', 'Knowledge\nAreas']
    names = ['student', 'project', 'studentid', 'metadata',
    'supervisor', 'year', 'abstract', 'keywords', 'knowledgeAreas']

    def __init__(self, **kwargs):
        super(PropertiesLayout, self).__init__(**kwargs)
        
        assert len(self.labelNames) == len(propertyKeys)
        assert len(self.labelNames) == len(self.names)
        self.groups = list(zip(self.labelNames, propertyKeys, self.names))
        offset, width, height, top, border = 0.1, 0.3, 0.05, 0.95, 0.02
        for i, group in enumerate(self.groups):
            labelName, key, name = group
            #create a property layout
            if i == len(self.labelNames) - 1:
                #knowledgeAreas exception Widget
                propObj = PMBOKSelect(pos_hint={'top':top-i*offset, 'right':1-border})#, size_hint=(width, height))
            else:
                propObj = PropertyLayout()
                #modify Property Layout
                propObj.label.text = labelName
                propObj.size_hint = (width, height)
                propObj.pos_hint = {'top':top-i*offset,'right':1-border}
            setattr(propObj, 'name', name)
            setattr(self, name, propObj)
            #add widget
            self.add_widget(propObj)
    def propertiesValuesDict(self):
        ansDict = {}
        for i, group in enumerate(self.groups):
            #for each property, get its value and add to dictionary
            labelName, key, name = group
            prop = getattr(self, name)
            propertyVal = prop.propertyVal
            ansDict.update({key: propertyVal})
        #filter/reject dict if properties missing
        myKeys = list(ansDict.keys())
        authenticKeys = [authKey for i, authKey in enumerate(propertyKeys) for i in [0,1,4,5]]
        for myKey in myKeys:
            #if you cant find my keys in the authenticate keys, dont release the dictionary
            if not myKey in authenticKeys:
                self.main.hintPrint(f"This library is incomplete. '{myKey}' missing.")
                return {}
        return ansDict
    def scanAll(self):
        for name in self.names:
            #for each property, get its value and add to dictionary
            prop = getattr(self, name)
            scanFunc = partial(prop.scanFunc, scanIfOccupied=False)
            scanFunc()
    def propertiesClear(self):
        checknameCleared = False
        for name in self.names:
            prop = getattr(self, name)
            clearFunc = prop.clearFunc
            clearFunc()
            if not checknameCleared:
                try:
                    prop.indicatorCheckName('', False)
                except:
                    print("Didn't work. Try again in next iteration.")
    def stuNameOnText(self, instance, value):
        #check everytime for name in dictionary
        self.indicatorCheckName(value)

class PropertyLayout(GridLayout):
    rows = 1
    def __init__(self, **kwargs):
        super(PropertyLayout, self).__init__(**kwargs)
        self.scanValue = None
        fontSize = '10sp'
        #create widget
        self.label = Label(font_size=fontSize, halign='right')
        self.scanButton = Button(text='Scan', font_size=fontSize)
        self.infoInput = TextInput(font_size='10sp')#, size_hint=(None, 0.5))
        self.clearButton = Button(text='Clear', font_size=fontSize)
        self.selectButton = Button(text='Select', font_size=fontSize)
        self.displayButton = Button(text='Project', font_size=fontSize)
        #add widget
        self.add_widget(self.label)
        self.add_widget(self.scanButton)
        self.add_widget(self.infoInput)
        self.add_widget(self.clearButton)
        self.add_widget(self.selectButton)
        self.add_widget(self.displayButton)
        #bind callbacks
        self.scanButton.bind(on_release=self.scanFunc)
        self.clearButton.bind(on_release=self.clearFunc)
        self.selectButton.bind(on_release=self.funcSelect)
        self.displayButton.bind(on_release=self.funcDisplay)

    @property
    def propertyVal(self):
        myText = self.infoInput.text
        if isinstance(self.scanValue, list):
            #get list from text and return the list
            return self.phasesToList(myText)
        else:
            #by default, just return the text
            return myText
    def scanFunc(self, button=None, scanIfOccupied=True, solo=True):
        #scan main inputText and sets a scan value in respective infoInput
        keywordPatt = r'[Kk]ey[ ]*[Ww]ord[s]?\s*'
        infoInput = self.infoInput
        main = App.get_running_app()
        myText = infoInput.text
        #assigning other text
        otherText = main.gui.scanTextInput.text
        selectedText = main.gui.scanTextInput.selectedText
        otherText = selectedText if selectedText else otherText
        #myTitleLow = self.label.text.lower()
        myTitleLow = self.name
        #determine if coverpage or not
        abstract = 'abstract' in otherText.lower()
        #NB: scanValue does not mean text value. at any time
        scanValue = ''
        if myText and not scanIfOccupied:
            return scanValue
        #now, parse through myTitleLow by keywords to determine scan action
        if 'studentid' in myTitleLow:
            idNums = re.findall(r"\d{8,9}", otherText)
            if idNums:
                scanValue = idNums[-1]
        elif 'student' in myTitleLow:
            #sort myText out
            lines = re.split(r'\n+', otherText)
            name = ''
            for line in lines:
                match = re.search(r'student name', line.lower())
                if not match:
                    match = re.search(r'student', line.lower())
                if not match:
                    match = re.search(r'name[: ]', line.lower())
                if not match:
                    match = re.search(r'Submitted By[: ]', line.lower())
                if match:
                    if 'and' in match.string:
                        #exceptions. gets rid of 'name and ID
                        continue
                    name = self.nameScanCont(match)
                if name:
                    break
            if not name and not myText:
                if selectedText:
                    #if there was no 'student name' but there are a few words, put words as name
                    words = re.findall(r"\w+", otherText)
                    length = len(words)
                    if length <= 4:
                        name = " ".join(words)
                else:
                    name = bestNameCheck(otherText)
            scanValue = putNameTitleIn(scanValue)
            scanValue = name.title() if name else scanValue.title()
            self.indicatorCheckName(name)
            if solo:
                main.hintPrint(scanValue)
        elif 'project' in myTitleLow:
            #scan according to capital letters
            if not selectedText:
                tempVal = capitalLines(otherText)
                wordAmount = len(re.findall(r"\w+", tempVal))
                if wordAmount > 8:
                    scanValue = tempVal
            if not scanValue:
                #SCAN: return all text before these words
                searchForEnd = ['A Project Report', 'A Thesis', 'A Research']
                searchForStart = ['augustine', 'report title']
                startIndex, endIndex = 0, len(otherText)
                for search in searchForEnd:
                    if search in otherText:
                        endIndex = otherText.index(search)
                        break
                for search in searchForStart:
                    if search in otherText:
                        startIndex = otherText.index(search) + len(search) + 1
                        break
                scanValue = otherText[startIndex:endIndex].strip()
            #remainder option
            if not scanValue and selectedText:
                scanValue = otherText
        elif 'meta' in myTitleLow:
            pass
        elif 'supervisor' in myTitleLow:
            name = ''
            if not abstract:
                #look at supervisor names and see if name in line
                supervisorList = getSupervisorsFromFile()
                coverPageLines = re.split(r"\n+", otherText)
                breakOut = False
                for cpLine in coverPageLines:
                    if not cpLine:
                        break
                    for supervisor in supervisorList:
                        if supervisor in cpLine:
                            scanValue = supervisor
                            breakOut = True
                            break
                    if breakOut:
                        break
                #scan search now
                lines = otherText.splitlines()
                for line in lines:
                    match = re.search(r"supervisor['s]*\s+name", line.lower())
                    if not match:
                        match = re.search(r'supervisor[ :;.]*', line.lower())
                    if match:
                        name = self.nameScanCont(match, nameExcept=[])
                    if name:
                        break
            scanValue = putNameTitleIn(scanValue)
            scanValue = name.title() if name else scanValue.title()
        elif 'year' in myTitleLow:
            years = re.findall(r'20[0-9][0-9]', otherText)
            if years:
                scanValue = int(years[-1])
        elif 'abstract' in myTitleLow:
            #remove 'keyword' from otherText
            splitz = re.split(keywordPatt, otherText)
            length = len(splitz)
            if length >= 2:
                stringz = [splitz[i] for i in range(length) if i < (length - 1)]
                otherText = 'keyword'.join(stringz)
                #otherText = "keyword".join(splitz[:-2])
            #add otherText if 'abstract' in text, else append (excluding with abstract)
            if myText:
                scanValue = f'{myText}\n{otherText}'
            #elif abstract:
            else:
                #remove things before abstract
                m = re.search(r'abstract', otherText.lower())
                if m:
                    st = m.start()
                else:
                    st = 0
                newText = otherText[st:]
                scanValue = newText.strip()
            if otherText in myText and myText:
                scanValue = myText
        elif 'keyword' in myTitleLow:
            sections = re.split(keywordPatt, otherText)
            keywordList = []
            if len(sections) >= 2:
                strung = sections[-1]
                keywordList = self.phasesToList(strung, separator=r'[,;]')
            scanValue = keywordList
        else:
            raise(f'A keyword could not be found to fit inside of {myTitleLow}.')
        #place the scanned value inside of respective infoText
        infoInput.text = str(scanValue)
        #alternatively, save the value in the button or return the value
        setattr(self, 'scanValue', scanValue)
        return scanValue
        
    def loadFunc(self, val):
        self.infoInput.text = str(val)

    def nameScanCont(self, matchObj, nameExcept=['Mr', 'Mrs','Dr','Prof', 'professor']):
        finalName = ''
        line = matchObj.string
        nd = matchObj.end()
        remainder = line[nd:]
        foundNames = re.findall(r'\w+', remainder)
        #remove the name if nameExcept was found in it
        if foundNames:
            for foundName in foundNames:
                for exe in nameExcept:
                    if exe in foundName:
                        foundNames.remove(foundName)
                        break
        #make a single titled string of the remaining words
        if foundNames:
            foundNames = [name.title() for name in foundNames]
            finalName = ' '.join(foundNames)
        return finalName
    def phasesToList(self, text, separator=',', joiner=' ', wordPatt=r'[\w]+'):
        assert isinstance(separator, str)
        assert isinstance(joiner, str)
        phrases = re.split(separator, text)
        finalPhrases = []
        for phrase in phrases:
            words = re.findall(wordPatt, phrase)
            if words:
                phrase = joiner.join(words)
                finalPhrases.append(phrase)
        return finalPhrases
    def indicatorCheckName(self, word, turnOffIndicator=True):
        #booly = wordExistInFile(word, caseSensitive='False')
        intermStudentList = []
        if turnOffIndicator:
            intermStudentList = [name.lower() for name in getStudentNameFromFile()]
        booly = word.lower() in intermStudentList and turnOffIndicator
        state = 'down' if booly else 'normal'
        main = App.get_running_app()
        main.gui.nameIndicator.state = state

    def clearFunc(self, button=None):
        setattr(self.infoInput, 'text', '')
    def funcSelect(self, button):
        infoInput = self.infoInput
        main = App.get_running_app()
        myText = infoInput.text
        selectedText = main.gui.scanTextInput.selectedText
        otherText = selectedText if selectedText else main.gui.scanTextInput.text
        #append infoInput str
        if myText:
            finalStr = f"{myText}\n{otherText}"
        else:
            finalStr = otherText
        #set my value inside infoInput
        infoInput.text = finalStr
    def funcDisplay(self, button):
        #place my info onto scanTextInput
        infoInput = self.infoInput
        main = App.get_running_app()
        myText = infoInput.text
        if myText:
            #safeguard for clearing text by mistake
            main.gui.scanTextInput.text = myText


class MyBlock(FloatLayout):
    #create widgets
    #TBD: colours
    bd, bw, bh, bLn = 0.02, 0.1, 0.05, 0.55
    fileNameLabel = Label(text='X', pos_hint={'x':bLn, 'y':0.1}, size_hint=(bw, 0.05))
    #name indicator
    nameIndicator = ToggleButton(text='Name Indicator', pos_hint={'x':bLn, 'y':0.05}, size_hint=(bw, 0.05))
    #text boxes
    scanTextInput = TextInput(pos_hint={'x':bd, 'top':1-bd}, size_hint=(0.5, 0.75), font_size='12sp')
    hintBox = TextInput(pos_hint={'x':bd, 'y':bd}, size_hint=(0.5, 0.2))
    #properties elements
    propertiesNameLabel = Label(text='Properties', pos_hint={'x':0.5, 'y':0.9})
    props = PropertiesLayout()

    def __init__(self, **kwargs):
        super(MyBlock, self).__init__(**kwargs)
        #initiate some structure
        main = App.get_running_app()
        self.main = main
        #autosave callback
        Clock.schedule_interval(main.autoSaveFilesCallback, saveTimeInterval*60)
        self.buttons = (
            ('back', 'Back', partial(main.selectImgDict, direction=-1) ), 
            ('forward', 'Forward', partial(main.selectImgDict, direction=1) ),
            ('clear', 'Clear', main.clearFunc),
            ('clearAll', 'Clear All', main.clearAllFunc),
            ('scan', 'Scan', main.scanAllFunc),
            ('refresh', 'Refresh', partial(main.selectImgDict, direction=0) ),
            ('submit', 'Submit', main.submitPerson), 
            ('save', 'Save', main.saveFiles)
        )
        #add widgets
        self.add_widget(self.fileNameLabel)
        self.add_widget(self.nameIndicator)
        #text boxes
        self.add_widget(self.scanTextInput)
        self.add_widget(self.hintBox)
        #properties layout
        self.add_widget(self.propertiesNameLabel)
        self.add_widget(self.props)
        #bindings for widgets
        self.scanTextInput.bind(on_touch_up=lambda x, y: setattr(self.scanTextInput, 'selectedText', self.scanTextInput.selection_text))
        #buttons initiation and assignment
        bw, bh, bLn, bInter, yStart = 0.1, 0.05, 0.55, 0.01, 0.9
        for i, tup in enumerate(self.buttons):
            name, title, func = tup
            yStart -= bh if i==2 or i==4 else 0
            yPos = yStart - (bh + bInter)*i + bInter
            obj = Button(text=title, pos_hint={'x':bLn, 'top':yPos}, size_hint=(bw, bh))
            setattr(self, name, obj)
            self.add_widget(obj)
            obj.bind(on_release=func)
        else:
            yStart -= bh
            yPos = yStart - (bh + bInter)*i + bInter
            obj = EditLayout(pos_hint={'x':bLn, 'top':yPos})
            self.add_widget(obj)

class PostGradParseApp(App):
    activeImg = None
    defaultSettingsDict = {
        'selectedImageName':'0.jpg'
        }
    selectedImageName = defaultSettingsDict.get('selectedImageName')
    databaseDict = {}
    picturesDir = r"C:\Users\drsba\Desktop\report pictures COMPLETE"

    def __init__(self, **kwargs):
        super(PostGradParseApp, self).__init__(**kwargs)

    def build(self):
        self.gui = MyBlock()
        #load json
        self.loadPictureDatabase()
        self.loadSettings()
        #start gui
        return self.gui

    def wordLineList(self, dictionary):
        wordList = dictionary['text']
        pageNumList = dictionary['page_num']
        blockNumList = dictionary['block_num']
        paragraphNumList = dictionary['par_num']
        lineNumList = dictionary['line_num']
        assert len(wordList) == len(lineNumList)
        groups = list(zip(pageNumList, blockNumList, paragraphNumList, lineNumList))
        lineWords = []
        lineList = []
        saveTup = groups[0]
        for i, tup in enumerate(groups):
            word = wordList[i]
            if saveTup == tup:
                #if the word on the same line, append to the line
                lineWords.append(word)
            else:
                #reset line count
                saveTup = tup
                line = ' '.join(lineWords)
                anyMatterInside = re.findall(r"\S", line)
                if anyMatterInside:
                    #then append the line to list
                    lineList.append(line)
                lineWords = []
        return lineList
    def wordListString(self, wordList):
        strung = ' '.join(wordList)
        #filter the strung
        strung = re.sub(r' +', " ", strung)
        return strung
    def selectImgDict(self, instance, direction=0, assignValues= True):
        #select an image data (ditionary) based off of current and the direction of choice
        try:
            #use the oldKey > (oldIndex+direction) > newIndex > newKey > newDict
            nameKey = 'selectedImageName'
            defaultVal = self.defaultSettingsDict[nameKey]
            currentKey = getattr(self, nameKey, defaultVal)
            keys = self.keys
            #get indices
            currentIndex = keys.index(currentKey)
            newIndex = currentIndex + direction
            #clamping newIndex
            newIndex = max(0, min(newIndex, len(keys)-1))
            #newKey
            newKey = keys[newIndex]
            setattr(self, nameKey, newKey)
            picDict = self.dictionary[newKey]
            #now, assign values as new key selected
            if assignValues:
                toScanText = self.bodyText(picDict)
                #self.gui.scanTextInput.text = toScanText
                self.scanTextInputPrint(toScanText)
                #auto adjust text to top
                self.gui.scanTextInput.cursor = (0,0)
                #change displayed file name
                self.gui.fileNameLabel.text = newKey
            return picDict
        except KeyError as ke:
            print(ke)
            self.hintPrint(ke)
    def bodyText(self, picDict):
        strung = self.wordListString(picDict['text'])
        #optional
        lineList = self.wordLineList(picDict)
        strung = '\n'.join(lineList)
        return strung
    def hintPrint(self, text):
        hintInput = self.gui.hintBox
        hintInput.text = str(text)
    def scanTextInputPrint(self, text):
        scanTextInput = self.gui.scanTextInput
        scanTextInput.text = str(text)
    def submitPerson(self, instance=None):
        reportDict = self.scanAllFunc()
        self.databaseDict.update(reportDict)
        #when submit, clear screen
        if reportDict:
            print("report submitted")
            self.clearAllFunc()
            self.selectImgDict(None, direction=1)
        
    def clearAllFunc(self, instance=None):
        self.clearFunc()
        #now clear each property
        self.gui.props.propertiesClear()
    def clearFunc(self, instance=None):
        self.scanTextInputPrint("")
    def scanAllFunc(self, instance=None):
        prompt = ""
        #apply the scan of each property to the property text
        self.gui.props.scanAll()
        #take out dictionary of each property:value
        newDict = self.gui.props.propertiesValuesDict()
        ansDict = {}
        #now add the dictionary according to person name
        nameDictKey = 'Student Name'
        yearDictKey = 'Year'
        studentName = ''
        year = None
        try:
            studentName = newDict[nameDictKey]
            year = newDict[yearDictKey]
        except KeyError as err:
            if not studentName:
                studentName = tryKeyDict(newDict, 'tudent')
            if not year:
                year = tryKeyDict(newDict, 'ear')
            prompt = f"Wasn't able to find '{nameDictKey}' or '{yearDictKey}' in the dictionary. " + prompt
            print(err)
        if studentName and year:
            dictName = f"{year},{studentName}"
            ansDict = {dictName:newDict}
            self.hintPrint(prompt)
        return ansDict

    #load
    def loadJson(self, fileName):
        dictionary = {}
        try:
            with open(fileName, 'r') as jsonFile:
                strung = jsonFile.read()
                dictionary = json.loads(strung)
        except ValueError as err:
            print(err)
            self.hintPrint(err)
        except FileNotFoundError as err:
            #print error
            print(err)
            self.hintPrint(f"{err}. New dictionary created from json for file {fileName}")
        return dictionary
    def loadPictureDatabase(self, fileName='json postgrad text extras.txt'):
        dictionary = self.loadJson(fileName)
        self.dictionary = dictionary
        self.keys = list(dictionary)
    def loadDatabase(self):
        dictionary = self.loadJson(databaseFileName)
        return dictionary
    def loadSettings(self):
        fileName = settingsFileName
        try:
            dictionary = self.loadJson(fileName)
        except FileNotFoundError:
            #create the default dict and save it
            dictionary = self.defaultSettingsDict
            #jsonText = json.dumps(dictionary)
            with open(fileName, mode='w+') as file:
                json.dump(dictionary, file)
                #file.writelines(jsonText)
        #load dictionary
        for k,v in dictionary.items():
            setattr(self, k, v)
    #save
    def saveJson(self, fileName, dictionary, append=False):
        oldDict = {}
        appendEtc = append and os.path.isfile(fileName)
        if appendEtc:
            try:
                with open(fileName) as file:
                    #oldDict = json.loads(file.readlines)
                    oldDict = json.loads(file.read())
            except ValueError as err:
                #mostlikely json didnt convert good
                appendEtc = False
                #therefore rename previous file and continue with same file name
                sideFileName = f"random error code {randomString}: previous database {fileName}"
                self.hintPrint(err)
                os.rename(fileName, sideFileName)
        oldDict.update(dictionary)
        #oldDict is now new and now, save oldDict
        with open(fileName, 'w+') as file:
            #jsonText = json.dumps(oldDict)
            #file.writelines(jsonText)
            json.dump(oldDict, file)
        self.hintPrint(f"File '{fileName}', saved.")
    def saveDatabase(self, instance=None):
        saveDict = self.loadDatabase()
        saveDict.update(self.databaseDict)
        self.saveJson(databaseFileName, saveDict)
        print("File Saved.")
    def saveSettings(self, instance=None):
        keys = list(self.defaultSettingsDict)
        saveDict = {}
        for key in keys:
            val = getattr(self, key)
            saveDict.update({key:val})
        self.saveJson(settingsFileName, saveDict)
    def saveFiles(self, instance=None):
        self.saveSettings()
        self.saveDatabase()
        #just updating current professors list
        getSupervisorsFromFile(recalculate=True)
    def autoSaveFilesCallback(self, dt):
        self.saveFiles()
        print(f"Files saved. {dt}")
    def scan(self, imgPath=None):
        if imgPath:
            imz = cv2.imread(imgPath)
        elif self.activeImg:
            imz = self.activeImg
        text = pytesseract.image_to_string(imz, lang='eng')
        return text

def main1():
    obj = PostGradParseApp()
    st = time.monotonic()
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_141927.jpg"
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_142413.jpg"
    #imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "IMG_20191206_142413.jpg"
    imgDir = r'C:\\Users\\drsba\\Dropbox\\pictures test\\' + "pdf ocr try.png"
    obj.scan(imgDir)
    deltaTime = time.monotonic() - st
    print(f"The duration was {deltaTime}")
def main2():
    obj = PostGradParseApp()
    obj.run()

if __name__ == "__main__":
    #main1()
    main2()