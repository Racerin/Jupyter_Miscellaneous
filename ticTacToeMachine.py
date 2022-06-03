#!/usr/bin/env python3
import re, sys, copy
import kivy
from functools import partial
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

class StartPage(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(StartPage, self).__init__(**kwargs)

class OptionPage(RelativeLayout):
    def __init__(self, **kwargs):
        super(OptionPage, self).__init__(**kwargs)

class GamePage(RelativeLayout):
    def __init__(self, **kwargs):
        super(GamePage, self).__init__(**kwargs)

        #Handles & Widgets
        self.p1Indicate = PlayerGameCanvas()
        self.p2Indicate = PlayerGameCanvas()
        self.gGrid = GameGrid()

        #Widget Parameters
        #self.gGrid.    #Insert Parameters for the grid

        #add_widget
        self.add_widget(self.p1Indicate)
        self.add_widget(self.p2Indicate)
        self.add_widget(self.gGrid)

        #Bindings
        self.gGrid.bind()   #create binding for each square in the grid

class PlayerStartCanvas(GridLayout):
    name = "Player"
    playerNumber = None

    def __init__(self, number = '', **kwargs):
        super(PlayerStartCanvas, self).__init__(**kwargs)
        self.name += f" {number}"

        #widgets
        self.nameW = TextInput(text=self.name, multiline=False)    #position, Size of font
        #add widget
        self.add_widget(self.nameW)
        #bindings
        self.nameW.bind()

    def setName(self, instance, name):
        super(TestApp, self).
    

class PlayerGameCanvas(GridLayout):
    name = "Player"

    def __init__(self, **kwargs):
        super(PlayerGameCanvas, self).__init__(**kwargs)

        #widgets
        self.nameW = Label(text=self.name, multiline=False)    #position, Size of font
        #add widget
        self.add_widget(self.nameW)

    def nameIt(self, newName):
        self.name = newName
        self.nameW.text = self.name

class GameGrid(GridLayout):
    def __init__(self, **kwargs):
        super(GameGrid, self).__init__(**kwargs)

class ticTacToeTable():

    #properties
    __table =  [[] * 3 for i in range(3)]
    __rules = """These are the rules:
1). To choose the correct spot on the table, input a pair of numbers as follows.
    [Row, Column]

2). The following is the coordinates for the table.
    [(1,1), (1,2), (1,3)]
    [(2,1), (2,2), (2,3)]
    [(3,1), (3,2), (3,3)]

3). There are a few rules that can be decided.
    a). You could select whether diagonal straights are allowed for score.
    b). You could decide the size of the table.
    """

    __noteWell = '''Things to take note of.
    table[y][x] 
    or table[row][column] from top left
    '''

    #things to look for and obtain values in the title of the results file name
    resultTags = {
        #'noDiagonal':
    }

    __codes = ""

    players = []
    currentStr = ""
    outcomes = {}
    draw = False

    diagonalQ = True

    turn = 0
    coinToss = 0
    instance = 0

    #inner classes
    class uniqueError(Exception): pass

    class player():
        __cpu = False
        __icon = 'X'
        __name = 'Player'
        __wins = 0
        __losses = 0

        def __init__(self, name = __name, icon = __icon, prompt = False, playerNumber = None, iscpu = __cpu):

            if prompt:
                name = ""
                icon = ""
                isStr = lambda x: True if type("") == type(playerNumber) else False
                if isStr(playerNumber):
                    name = input(f"Enter the name of player {playerNumber}." + "\n")
                    icon = input(f"Enter the symbol for player {playerNumber}." + "\n")
                else:
                    name = input("Enter the name of the player.\n")
                    icon = input("Enter the symbol for the player. \n")
            
                if len(icon) > 1:
                    icon = icon[0]
                    print("The icon is too long so the first character would be used.")
            else:
                #typical initialization
                self.__name = name
                self.__icon = icon

        def nameSet(self, nm):
            self.__name = nm

        def iconSet(self, ico):
            self.__icon = ico

        def getIcon(self):
            return self.__icon

        def getName(self):
            return self.__name

        def getScore(self):
            return (self.__losses, self.__wins)

        def setScore(self, score):
            '''if score is '-'ve, add to losses. if score is '+'ve, add to wins
            '''
            if score > 0:
                self.__wins += score
            elif score < 0:
                self.__losses += abs(score)


        #these are the list of shortcuts for creating a player. Engaged after entering cheats in game start-up
        @classmethod
        def darnell(cls):
            return cls("Darnell Baird", "X")
        @classmethod
        def chinelo(cls):
            return cls("Chinelo Gilbert", "O")
        @classmethod
        def robert(cls):
            return cls("Robert Birch", "0")
        @classmethod
        def bot1(cls):
            return cls("bot1", "a")
        @classmethod
        def bot2(cls):
            return cls("bot2", "b")

    #ticTacToeTable methods
    #initiation
    def __init__(self):

        #create a dictionary of shortcut players accessible by player names
        self.__class__.playerCheats = {
        "darnell" : self.player.darnell(), 
        "chinelo" : self.player.chinelo(),
        'robert'  : self.player.robert()
        }

    #cheat codes are saved for cheats later in the program
    def setCheatCodes(self, string = ""):
        if not any(string): #if there is nothing in 'string' although it's of type 'char'
            string = input("Press ENTER to continue. \n")
        self.__codes = string

    def getCheatCodes(self, string = ""):
        return self.__codes

    def appendCheatCodes(self, string):
        oldString = self.getCheatCodes(" ")
        self.setCheatCodes(oldString + " " + string)

    def createTable(self, size = 3):
        #creates a 3*3 list of zeros by default
        self.__table = [[0] * size for i in range(size)]

    def createNumberedTable(self, size = 3):
        self.__table = [[(i + 1) + (size*abb) for i in range(size)] for abb in range(size)]

    def getTableSize(self):
        table = self.__table
        return len(table)
        
    def getTurnPlayer(self):
        side = (self.turn + self.coinToss) % 2
        return self.players[side]

    #uses input arguments to place icon on table
    def playPosition(self, x, y):
        #return None, sets values in table

        table = self.__table
        point = table[x][y]

        assert point == 0, "That spot was played already. "
        self.__table[x][y] = self.getTurnPlayer().getIcon()

    def queryPlayPosition(self, turnPlayer):
        #prompts user, error capture, analyse input, passes coordinates to table scanner "playPosition"
        while True:
            try:
                promtpStr = f"{turnPlayer.getName()}, Choose your position. [X Y]" + "\n"
                playPosQ = input(promtpStr)
                strPiece = re.findall(r"\d+", playPosQ)
                #obtain the intergers from the string 
                iterated = map(int, strPiece)
                #[coordi]nates
                nates = list(iterated)
                pieces = len(nates)
                max = self.getTableSize()
                
                if pieces == 2:
                    #validate the numbers can fit in the table
                    #meepo = list(map(lambda x: True if x <= max else False, nates))
                    meepo = [i <= max for i in nates]
                    if not all(meepo):
                        print("The values entered are too big.")
                        continue
                    #now, play the spot. The 'minus 1's are to convert player numbers to array index numbers
                    self.playPosition(nates[0] - 1, nates[1] - 1)
                    break
                if pieces == 1:
                    num = nates[0]
                    if num > max**2:
                        print("The values entered are too big.")
                        continue
                    row = (num-1)//max
                    col = num%max - 1
                    #now, play the spot. The 'minus 1's are to convert player numbers to array index numbers
                    self.playPosition(row, col)
                    break
                else:
                    print("You've entered the wrong amount of values, try again.")

            except ValueError:
                print("something is wrong with me")
            except AssertionError as err:
                print(err)

    def displayTable(self):
        tab = self.__table
        for row in range(len(tab)):
            #turns row to string to make it look nicer when displayed
            mappy = map(lambda x: str(x), tab[row])
            print(list(mappy))
            #print(tab[row])

    def createPlayers(self):
        '''
        adds player names from the cheat code as players to the game
        Output - None
        '''

        #obtain the name position and names of cheat players as pairs and place in dictionary 
        filt = [i for i in self.playerCheats.keys() if i in self.getCheatCodes()]
        self.players += [self.playerCheats[igg] for igg in sorted(filt, key = self.getCheatCodes().index)]

        #Now, ask for players (if needed)
        plyRz = len(self.players)
        while plyRz < 2:
            #Asks for more players
            self.players.append(self.player(prompt = True, playerNumber = plyRz))
            plyRz = len(self.players)

        #Now, remove excess players (if there are). (This step is not needed but is used for cleaner code)
        while len(self.players) > 2:
            del self.players[2]

    def resultAction(self):
        return True

    #returns player of input symbol (if any)
    def detPlayer(self, symbol):
        if symbol == None:
            return None
        else:
            return self.getTurnPlayer()

    def ruleSet(self):
        #here is where the rules of the game is set
        #Output - None

        #ruleskip - else leaves default values and skips decisions
        if not self.getCheatCodes("ruleskip"):
            #diagonal win
            dq = input("Is diagonal win allowed? [Y/N]\n")
            self.diagonalQ = False if "n" in dq.lower() else True

            #coin toss (TBD)


            #switch sides of who plays 1st for a round (when a round win or just alternating)

            #table size
            tabSize = self.inputMust("What is the size of the Tic Tac Toe Table?\n", int)
            self.createTable(tabSize)
            self.appendCheatCodes("ruleskip")
        else:
            #any other input conditions
            self.diagonalQ = True if self.getCheatCodes("noDiagonal") else False
            
            #create table
            self.createTable()

    def loopedGame(self):
        #The main game is looped here
        #Output - player<class>

        countdown = self.getTableSize() ** 2
        while countdown > 0:
            playR = self.getTurnPlayer()
            #display table
            self.displayTable()
            #wait for input
            self.queryPlayPosition(playR)
            #determine if win or normal
            roundResult = self.determineCondition(self.resultAction)
            print(roundResult)
            winner = self.detPlayer(roundResult)
            if type(winner) == type(playR):
                return playR
            self.turn += 1
            countdown -+ 1
        else:
            #game squashed
            return None

    def winFunc(self, playr):
        #the winner/squash is delt with here
        self.displayTable()
        if playr == None:
            print("The game was squashed!!!\n")
        else:
            print(f"The winner is {playr.getName()}")

    def playAgain(self):
        self.instance += 1
        ans = input("Do you want to play again? [Y/N] \n")
        if 'n' not in ans.lower():
            self.createTable(self.getTableSize())
            self.playTicTacToe()

    def saveScore(self, name = "Tic Tac Toe Scores."):
        inputt = input("Do you want to save the score? [Y/N] \n")

        fileName = f"{name}.txt"
        string = "\n"

        #game conditions
        string += f"Instance: {self.instance}"

        length = len(self.players)
        for i in range(length):
            plyR = self.players[i]
            pName = plyR.getName()
            pWins = plyR.getScore()[1]
            pLosses = plyR.getScore()[0]

            string += f"{pName}: Wins: {pWins}. Losses: {pLosses} \n"
        
        if 'n' not in inputt.lower():
            with open(fileName, mode="w", encoding="utf-8") as textFile:
                textFile.write(string)
        else:
            sys.exit()

    @staticmethod
    #def inputMust(question, func = int, errorMessage = "Incorrect value. Please try again."):
    def inputMust(question, func = lambda x: 0 if not x else int, errorMessage = "Incorrect value. Please try again."):
        
        #TBD: Error correction of inputs

        while(True):
            try:
                ans = input(question)
                final = func(ans)
                return final
            except:
                print(errorMessage)
        
    @staticmethod
    def intInput(question, errorMessage = "Incorrect value. Please try again.", emptyAllowed = False):
        #if empty is allowed, the return value is 0
        
        while(True):
            try:
                ans = input(question)
                if not ans and emptyAllowed: #empty is falsy
                    return 0

                return int(ans)
            except:
                print(errorMessage)

    @classmethod
    def introGame(cls): #no need to be a class method but w/e
        print("Welcome to the game of Tic Tac Toe.")
        print(cls.__rules)


    def playTicTacToe(self):
        
        if self.instance == 0:
            #initiate the game of ticTacToe
            self.introGame()

            #TBD: Load saved data from text file

            #press enter to exit rules and insert characters for secret codes
            self.setCheatCodes()

            #Select Players
            self.createPlayers()       

            #select game rules and conditions [tablesize, diagonalplay, coin toss?, switch when win?]
            self.ruleSet()

        #Start game
        print("GAME START \n")

        #loop game
        winR = self.loopedGame()

        #display winner/losser
        self.winFunc(winR)

        #play again?
        self.playAgain()

        #save score?
        self.saveScore()

    def playTicTacToeKivy(App):
        def build(self):
            '''
            return a Widget
            '''
            #manager
            self.screenManager = ScreenManager()

            self.kvCandy(
                option=OptionPage(),
                game=GamePage()
            )

        def kvCandy(self, **kwargs):
            for k,v in kwargs:
                self.widgetScreenAdd(k, v)

        def widgetScreenAdd(self, fieldName, classObject):
            #object handle
            setattr(self, fieldName, classObject)
            screen = Screen(name = fieldName)
            #add widget
            #screen.add_widget(getattr(self, fieldName))
            screen.add_widget(classObject)
            self.screenManager.add_widget(screen)
        
        #START OF LOGIC CODE
        if self.instance == 0:
            #initiate the game of ticTacToe
            self.introGame()
            #TBD: Load saved data from text file

            #press enter to exit rules and insert characters for secret codes
            self.setCheatCodes()
            #Select Players
            self.createPlayers()       
            #select game rules and conditions [tablesize, diagonalplay, coin toss?, switch when win?]
            self.ruleSet()

        #Start game
        print("GAME START \n")
        #loop game
        winR = self.loopedGame()
        #display winner/losser
        self.winFunc(winR)
        #play again?
        self.playAgain()
        #save score?
        self.saveScore()

    def cpuCreatePlayers(self):
        self.players = []
        self.players.append(self.player.bot1())
        self.players.append(self.player.bot2())

    @staticmethod
    def sTest(array):
        '''
        function for checking that the 'array' arguement is of type string 
        and if each element of array is the same
        '''
        #return all(x == array[0] for x in array) and isinstance(array[0], str)
        return len(set(array)) == 1 and isinstance(array[0], str)

    @staticmethod
    def countStr(line):
        #function for counting the number of non-zero elements
        return [isinstance(x, str) for x in line].count(True)


    def determineCondition(self, func, mySelf = None):
        '''
        returns game round outcomes. 1 - P1 wins, 3 - squash
        '''

        #INITIALIZATION
        table = self.__table
        diagonal = self.diagonalQ
        tSize = len(table)
        answer = False
            
        #PROCESSING
        #check through each row,col,diag and return the icon if true

        #iterate through each row and column
        for rou in range(tSize):
            #check per row
            if self.sTest(table[rou]):
            #1* if all of the row is the same character and if sample element of row is a char, return char
                #A WIN OCCURED
                answer = True

            #Checking per column
            lat = [table[i][rou] for i in range(tSize)]     #lat[eral] is holder for column elements. 
            if self.sTest(lat):
                #A WIN OCCURED. 1*
                answer = True         

        #checking diagonals
        tl2br = [table[i][i] for i in range(tSize)]         #top left to buttom right
        tr2bl = [table[i][-(1+i)] for i in range(tSize)]    #top right 2 buttom left
        if diagonal and (self.sTest(tl2br) or self.sTest(tr2bl)):
            #A WIN OCCURED. 1*
            answer = True

        if answer:
            if mySelf == None:
                return func()
            else:
                return func(mySelf)

        
    def processCondition(self, id = None):
        '''
        when id is used, the dictionary being developed contains a string with all its reductions. 
        This is to buildup a database where each possible occurence can be used to determine the next best statistical play.
        '''

        if isinstance(id, int):
            strCode = self.strCodeSort(self.currentStr)
            endIt = True    #for one more iteration when strCode is empty
            while bool(strCode) or endIt:    #while strCode is not an empty string
                endIt = bool(strCode)
                value = self.outcomes.get(strCode, [0, 0, 0])      #[outcomes, wins, draws]
                value[0] += 1   #a win occured
                value[1] += 1   #an outcome reached
                self.outcomes.update({strCode:value})
                strCode = strCode[:-1]

        else:
            #DEFAULT WIN
            self.draw = False

    def cpuPlayPosition(self, num):
        table = self.__table
        size = self.getTableSize()
        x = num//size
        y = num%size
        point = table[x][y]

        assert point == 0, f"That spot was played already. x = {x}, y = {y}"
        #self.bale()
        self.__table[x][y] = self.getTurnPlayer().getIcon()

    def cpuSetTable(self, listy = ""):
        listy = self.currentStr
        #listy is a (list of ints)/string which holds the data to create a table
        #initiation
        size = len(self.__table)
        self.createTable(size)
        
        #if listy is a dna string of code
        if type(listy) == type(""):
            string = listy
            length = len(string)
            for i in range(length):
                cha = string[i]
                print("Number Here.", ord(cha))
                self.cpuPlayPosition(ord(cha))
                #recreating table using each cha of dna string code
        #if listy is an array of indices
        elif type(listy) == type([]) and type(listy[0]) == type(10):
            length = len(listy)
            for i in range(length):
                digit = listy[i]
                self.cpuPlayPosition(digit)

    def string2numString(self, dna):
        holder = ""
        length = len(dna)
        for i in range(length):
            letter = dna[i]
            num = ord(letter)
            numCha = str(num)
            holder += numCha

        #print(holder)
        return holder

    def bale(self):
        import csv
        csv_columns = ['String','Result']
        dict_data = self.outcomes
        csv_file = "Names.csv"
        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in dict_data:
                    writer.writerow(data)
        except IOError:
            print("I/O error") 

    def cpuSelfPlay(self):
        '''A function used to obtain all the instances of a tictactoe game.
        Used to determine whether an outcome is a win/draw/loss
        '''
        #initiated
        print("program initiated")
        import itertools, datetime
        startTime = datetime.datetime.now()
        self.setCheatCodes("ruleskip")
        self.cpuCreatePlayers()
        self.ruleSet()
        numPositions = self.getTableSize() ** 2
        rg = range(numPositions)
        permutGen = itertools.permutations(rg)

        #for each array sequence generated of the positions of the table
        for array in permutGen:
            self.createTable(self.getTableSize())
            self.draw = True
            for position in array:
                self.currentStr += chr(position)
                self.cpuPlayPosition(position)
                self.determineCondition(self.processCondition, mySelf=99)
                if not self.draw: break
                self.turn += 1

            if self.draw:
                #self.outcomes.update({self.currentStr:3})
                value = self.outcomes.get(self.currentStr, [0, 0, 0])
                value[0] += 1
                value[2] += 1
                self.outcomes.update({self.currentStr:value})
            else:
                #self.outcomes.update({self.currentStr:1})
                pass

            self.currentStr = ''
            self.turn = 0

        #what to do with dictionary output
        self.saveDict2Text()
        endTime = datetime.datetime.now()
        print("The simulation finished in ", (endTime - startTime))

    def strCodeSort(self, str):
        try:
            index = []
            length = len(str)
            for i in range(length):
                index.append(ord(str[i]))
            temp = sorted(str, key = ord)
            answer = ""
            for ele in temp:
                answer += ele
            return ele
        except TypeError:
            print(TypeError, len(str), "HERE")
            raise TypeError


    def saveDict2Text(self):
        import os

        #initiation
        name = ""
        keys = self.outcomes.keys()

        #Processing
        #name defining
        name += "" if self.diagonalQ else "noDiagonal"
        name += f"size{self.getTableSize()}"
        fileName = name + ".txt"

        if os.path.exists(fileName):
            os.remove(fileName)
        with open(fileName, mode="a+", encoding ="utf-8") as myFile:
            for key in keys:
                status = self.outcomes[key]
                if status == 1:
                    str = "Player "
                    if len(key) % 2 == 0:
                        str += "2 Won"
                    else:
                        str += "1 Won"
                else:
                    str = "Draw"
                #string = f"{key},{status}\n"
                #string = f"{self.string2numString(key)},{str}\n"
                string = f"{self.string2numString(key)},{status}\n"
                myFile.write(string)

    def loadDict2Text(self):
        #initiation
        myNameTest = ""     #refer to saveDict2Text > name
        textList = []
        myFile = None

        #Processing
        #setup myNameTest
        myNameTest += "" if self.diagonalQ else "noDiagonal"
        myNameTest += f"size{self.getTableSize()}"
        myFileName = myNameTest + ".txt"
        
        #Return file to load or create new file
        try:
            with open(myFileName, mode='r', encoding = "utf-8") as myFile:
                #load the file content
                import re

        except FileNotFoundError:
            print("The database file for these settings was not found, a new file will be generated now.")
            self.cpuSelfPlay()






if __name__ == '__main__':
    game = ticTacToeTable()
    game.playTicTacToe()
    #game.cpuSelfPlay()



