#!/usr/bin/env python3
import re, sys, copy, logging
import numpy as np

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)  #end all logging messages

class Player():
    cpu = False
    icon = None
    name = ""
    wins = 0
    losses = 0
    squashes = 0

    def __repr__(self):
        strung = f"{self.name}, CPU: {self.cpu}"
        return strung
    def __str__(self):
        strung = self.name
        return strung
    @staticmethod
    def create(**kwargs):
        p = Player()
        for kw, v in kwargs:
            setattr(p, kw, v)
        p.confirm('name', str)
        #p.confirm('icon', int)
        return p
    #Auxiliary functions
    def confirm(self, kw, typeOf):
        while True:
            prompt = input(f"What is the player's {kw}?\n")
            ticTacToeTable.programStringCheck(prompt)
            try:
                typeOf(prompt)
            except ValueError:
                print(f"That is an invalid {kw}. Please try again.")
            print("OK.")
            setattr(self, kw, typeOf(prompt))
            break
    @classmethod
    def bot1(self):
        bot = Player()
        bot.name, bot.cpu = "Bot 1", True
        return bot
    @classmethod
    def bot2(self):
        bot = Player()
        bot.name, bot.cpu = "Bot 2", True
        return bot
    def setScore(self, score):
        '''if score is '-'ve, add to losses. if score is '+'ve, add to wins, if '0', add 1 to squashes
        '''
        if score > 0:
            self.wins += score
        elif score < 0:
            self.losses += abs(score)
        else:
            self.squashes += 1

class ticTacToeTable():

    #properties
    table =  np.zeros((3,3))
    rules = """These are the rules:
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
    players = []
    currentStr = ""
    outcomes = {}

    #game conditions
    diagonalQ = True
    tableSize = 3

    #game statistics
    turn = 0
    coinToss = 0
    instance = 0

    #instantiation functions
    def createTable(self, size = 3):
        #creates a 3*3 list of zeros by default
        self.table = np.zeros((3,3))
    def createPlayers(self):
        #ask for players
        while len(self.players) < 2:
            #Asks for more players
            playR = Player.create()
            playR.icon = 1 + len(self.players)
            self.players.append(playR)
        #Now, remove excess players (if there are). (This step is not needed but is used for cleaner code)
        while len(self.players) > 2:
            del self.players[2]

    #game Processes
    def playPosition(self):
    #uses input arguments to place icon on table
        table = self.table
        assert 0 in table, "There are no free spots to play."
        while True:
            row, col = self.queryPlayPosition()
            row, col = row-1, col-1
            try:
                point = table[row, col]
                if point == 0:
                    self.table[row,col] = self.getTurnPlayer().icon
                    break
                else:
                    print("That spot was played already.")
            except IndexError:
                print(f"The values {row} {col} are out of bounds.")
    def queryPlayPosition(self):
        #returns row, col
        playerName = self.getTurnPlayer().name
        while True:
            try:
                prompt = input(f"{playerName}, Choose a spot to play.\n")
                ticTacToeTable.programStringCheck(prompt)
                found = re.findall(r'\d', prompt)
                if len(found) == 2:
                    row, col = [int(x) for x in found]
                    return row, col
                else:
                    print("Not exact amount of coordinates recognized.")
            except ValueError:
                print(f"There is a number error. (Probably on coder end). Values: {found}")
    def loopedGame(self):
        tableElements = np.unique(self.table)
        while 0 in tableElements:
            #display table
            print(self.table)
            #play turn
            self.playPosition()
            #determine turn result
            winningIcon = self.determineRoundOutcome()
            #determine winner or not
            if winningIcon != 0:
                self.congratulate(winningIcon)
                break
            self.turn += 1
        else:
            #game squashed
            print("The game was squashed!!!")
            for player in self.players:
                player.score(0)
        self.roundEnd()
        if self.playAgain():
            self.roundReset()
        else:
            return

    def playAgain(self):
        ans = input("Do you want to play again? [Y/N] \n")
        if 'n' not in ans.lower():
            self.createTable(self.tableSize)
            return True
        else:
            return False
    def roundEnd(self):
        self.turn = 0
        self.instance += 1
    def roundReset(self):
        self.createTable(self.tableSize)
    def congratulate(self, icon):
        winner = self.getPlayerFromIcon(icon)
        print(f"The winner is {winner}.")

    def getPlayerFromIcon(self, icon):
        assert icon != 0, "The game is flawed as a 0 was obtained"
        rightPlayer = None
        for player in self.players:
            if player.icon == icon:
                rightPlayer = player
                break
        return rightPlayer
    def getTurnPlayer(self):
        side = (self.turn + self.coinToss) % 2
        return self.players[side]

    def saveScore(self, name = "Tic Tac Toe Scores."):
        prompt = input("Do you want to save the score? [Y/N] \n")

        fileName = f"{name}.txt"
        string = "\n"

        #game conditions
        string += f"Instance: {self.instance}"

        length = len(self.players)
        for i in range(length):
            plyR = self.players[i]
            pName = plyR.name
            pWins = plyR.wins
            pLosses = plyR.losses

            string += f"{pName}: Wins: {pWins}. Losses: {pLosses} \n"
        
        if 'n' not in prompt.lower():
            with open(fileName, mode="w", encoding="utf-8") as textFile:
                textFile.write(string)
        else:
            sys.exit()
    @classmethod
    def programStringCheck(self, strung):
        if 'x' in strung:
            raise SystemExit
    def introGame(self): #no need to be a class method but w/e
        print("Welcome to the game of Tic Tac Toe.")
        print(self.rules)
    def ruleSet(self, **kwargs):
        for kw, v in kwargs:
            setattr(self, kw, v)
        self.yesORnoT3('diagonal', 'diagonalQ')
    def yesORnoT3(self, kw, name=''):
        if not name:
            name = kw
        while True:
            prompt = input(f"{name}? [Y/N]\n")
            ticTacToeTable.programStringCheck(prompt)
            if prompt:
                if 'y' in prompt.lower():
                    setattr(self, kw, True)
                    break
                elif 'n' in prompt.lower():
                    setattr(self, kw, False)
                    break
            print(f"That is an invalid answer for {kw}. Please try again.")


    def play(self):
        while True:
            if self.instance == 0:
                #initiate the game of ticTacToe
                self.introGame()
                #TBD: Load saved data from text file

                #Select Players
                self.createPlayers()       
                #select game rules and conditions [tablesize, diagonalplay, coin toss?, switch when win?]
                self.ruleSet()
            #Start game
            print("GAME START \n")
            #loop game
            self.loopedGame()
            #save score?
            #self.saveScore()

    def cpuCreatePlayers(self):
        self.players = []
        self.players.append(Player.bot1())
        self.players.append(Player.bot2())

    def determineRoundOutcome(self):
        #INITIALIZATION
        table = self.table
        diagonal = self.diagonalQ
        tSize = self.tableSize
        answer = 0
        fullOfSomething = lambda line: np.unique(line).size == 1 and 0 not in line
            
        #PROCESSING
        #check through each row,col,diag and return the icon if true
        rowCheck, colCheck, tl2brCheck, tr2blCheck = [],[],[],[]
        for i in range(tSize):
            tl2brCheck.append(table[i,i])
            tr2blCheck.append(table[i,tSize-i-1])
            #check per row and column
            rowCheck = table[:,i]
            colCheck = table[i,:]
            if fullOfSomething(rowCheck):
                answer = rowCheck[0]
            if fullOfSomething(colCheck):
                answer = colCheck[0]
        #diagoanl check
        if diagonal:
            if fullOfSomething(tl2brCheck):
                answer = tl2brCheck[0]
            if fullOfSomething(tr2blCheck):
                answer = tr2blCheck[0]
        return answer
        
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
        table = self.table
        size = self.table.shape
        x = num//size
        y = num%size
        point = table[x,y]

        assert point == 0, f"That spot was played already. x = {x}, y = {y}"
        #self.bale()
        self.table[x, y] = self.getTurnPlayer().icon

    def cpuSetTable(self, listy = ""):
        listy = self.currentStr
        #listy is a (list of ints)/string which holds the data to create a table
        #initiation
        size = len(self.table)
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
        name += f"size{self.table.size}"
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
        myNameTest += f"size{self.table.size}"
        myFileName = myNameTest + ".txt"
        
        #Return file to load or create new file
        try:
            with open(myFileName, mode='r', encoding = "utf-8") as myFile:
                #load the file content
                import re

        except FileNotFoundError:
            print("The database file for these settings was not found, a new file will be generated now.")
            #self.cpuSelfPlay()






if __name__ == '__main__':
    game = ticTacToeTable()
    game.play()
    #game.cpuSelfPlay()



