import numpy as np
import cv2, time, json, re, os, random, string, gta5Help
from functools import partial
from multiprocessing import Process


import kivy, logging
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.clock import Clock

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.CRITICAL)  #end all logging messages

class Space():
    boxPos = None
    gridPos = None
    index = None
    options = []
    value = None
    
    def __init__(self, numberAmount=9):
        self.options = list(range(1,numberAmount+1))

    def __repr__(self):
        strung = f"Space with Index:{self.index}, Box position:{self.boxPos}, Grid position:{self.gridPos}"
        return strung

    def update(self):
        #ensure values are valid
        if not self.value:
            options = []
            length = len(self.options)
            if length == 1:
                self.value = options[0]
    def removeFromOptions(self, val):
        try:
            self.options.remove(val)
        except ValueError:
            print(f"{val} was removed already from {self}.")
        self.update()

class Straight():
    spaces = []

    def check(self):
        #get all values
        values = [val for val in self.spaces if bool(val)]
        #TBD: veryfy length and unique elements
        #remove all found values from each in straight
        self.removeOptions(values)
    def removeOptions(self, options):
        options = options if isinstance(options, list) else [options]
        #remove all input options for all spaces from all spaces in this straight
        for option in options:
            for space in self.spaces:
                try:
                    space.removeFromOptions(option)
                except ValueError:
                    print(f"tried to remove a duplicate {option} from space {space} but not there.")

class Box(Straight):
    pos = None

class Table():
    boxPerSide = 3
    boxDimension = 3
    tableDimension = boxPerSide * boxDimension
    size = tableDimension ** 2
    spaces = []
    boxes = []
    rows = []
    columns = []
    #create table
    def __init__(self):
        #create boxes, rows and columns
        self.createRowsAndColumns()
        self.createBoxes()
        #create each space
        for i in range(self.size):
            #create each space
            space = Space(self.tableDimension)
            self.spaces.append(space)
            #get box, row and col positions
            space.index = i
            gridPos = self.indexToGridPosition(i)
            space.gridPos = gridPos
            boxPos = self.indexToBoxPosition(i)
            space.boxPos = boxPos
            #assign space to row and column
            rowInd, colInd = gridPos
            myRow = self.rows[rowInd]
            myRow.spaces.append(space)
            myCol = self.columns[colInd]
            myCol.spaces.append(space)
            #assign space to box
            for box in self.boxes:
                #go through each box and add space to box only if the box positions match
                if box.pos == boxPos:
                    box.spaces.append(space)
                    break
            else:
                #error checking
                print(f"Space number {i} didnt fit into a box.")

    #create function to check each row, column and box
    def scan(self):
        turns = 0
        turnsAim = self.size
        while turns < turnsAim:
            turns += 1
            #check rows, cols and boxes
            allThem = self.rows + self.columns + self.boxes
            for str8 in allThem:
                #check each row
                str8.check()
    def indexToGridPosition(self, index):
        gridPos = divmod(index, self.tableDimension)
        #print(f"gridPos, {gridPos}")
        return gridPos
    def indexToBoxPosition(self, index):
        div1, rem1 = divmod(index, self.tableDimension)
        col = rem1 // self.boxDimension
        row = div1 // self.boxDimension
        print(f"This is box position. {row, col} with index {index}.")
        return row, col
    #def indexToBoxPosition(self, index):
    #    boxRowSize = self.boxDimension * self.tableDimension
    #    row, rem = divmod(index, boxRowSize)
    #    rowSize = self.boxPerSide * self.tableDimension
    #    rem = rem % rowSize
    #    col = rem % self.boxDimension
    #    print(f"This is box position. {row, col} with index {index}.")
    #    #TO BE TESTED/CONFIRMED
    #    return row, col
    def createRowsAndColumns(self):
        #create each row
        tableDim = self.tableDimension
        for r in range(tableDim):
            row = Straight()
            #add the row to the table list
            self.rows.append(row)
        for c in range(tableDim):
            col = Straight()
            self.columns.append(col)
    def createBoxes(self):
        nBoxes = self.boxPerSide ** 2
        for b in range(nBoxes):
            box = Box()
            pos = divmod(b, self.boxDimension)
            box.pos = pos
            #add the box to table list
            self.boxes.append(box)

class BoxSquare(GridLayout):
    integerInputs = []
    size_hint = (0.2, 0.2)
    rgb = (0.5,0.5,0.5)

    def __init__(self, **kwargs):
        super(BoxSquare, self).__init__(**kwargs)
        #self.table = App.get_running_app().root.table
        self.table = App.get_running_app().table
        boxDim = self.table.boxDimension
        self.rows = boxDim
        self.cols = boxDim
    @classmethod
    def createBox(cls, box):
        self = cls()
        for logicBox in self.table.boxes:
            spaces = logicBox.spaces
            #sort the spaces in the box by position
            spaces.sort(key=lambda sp:sp.boxPos)
            #add each space to this widget as a text input
            print(f"THIS IS THE AMOUNT OF SPACES {len(spaces)}")
            for space in spaces:
                intInput = IntegerInput()
                intInput.space = space
                self.integerInputs.append(intInput)
                self.add_widget(intInput)
        return self

class IntegerInput(TextInput):
    size_hint = (0.05, 0.05)
    space = None
    numberRange = list(range(1,9+1))
    rgb = (0,.8,0)

    def __init__(self, **kwargs):
        super(IntegerInput, self).__init__(**kwargs)
        self.font_size = '20sp'
        #self.table = App.get_running_app().root.table
        self.table = App.get_running_app().table
        tableDim = self.table.tableDimension
        self.numberRange = list(range(1, tableDim+1))

    #filter for text input to only numbers
    def insert_text(self, subString, from_undo=False):
        strRange = [str(num) for num in self.numberRange]
        strung = self.text
        if subString in strRange:
            strung = ''.join([strung, subString])
        return super(IntegerInput, self).insert_text(strung, from_undo=from_undo)
    
    def updateGuiInt(self):
        #put space value into gui float input
        val = self.space.value
        self.text = str(val)
    def updateSpaceInt(self):
        #put value of space as gui float
        try:
            numVal = int(self.text)
        except:
            numVal = None
        self.space.value = numVal

class TableLayout(GridLayout):
    size_hint = (0.8, 0.8)
    integerInputs = []

    def __init__(self, **kwargs):
        super(TableLayout, self).__init__(**kwargs)
        #set up
        #self.table = App.get_running_app().root.table
        self.table = App.get_running_app().table
        self.rows = self.table.boxPerSide
        self.cols = self.table.boxPerSide
        #create my box layouts
        #print(f"The amount of boxes is  {len(self.table.boxes)}")
        for box in self.table.boxes:
            wid = BoxSquare.createBox(box)
            self.add_widget(wid)
        self.addIntegerInputsFromBox()

    def addIntegerInputsFromBox(self):
        boxWidgets = [wid for wid in self.children if isinstance(wid, BoxSquare)]
        for boxW in boxWidgets:
            self.integerInputs += boxW.integerInputs

class MyBlock(StackLayout):
    orientation = 'lr-tb'
    intInputs = []
    def __init__(self, **kwargs):
        super(MyBlock, self).__init__(**kwargs)
        #self.table = App.get_running_app().root.table
        self.table = App.get_running_app().table
        #create widgets
        self.title = Label(text="Sudoku Solver", font_size='40sp', size_hint=(1,0.1),)
        self.guiTable = TableLayout()
        self.scan = Button(text='scan', size_hint=(0.1, 0.1),)
        toAdd = [self.title, self.guiTable, self.scan]
        #add widgets
        [self.add_widget(w) for w in toAdd]
        #callbacks
        self.scan.bind(on_press=self.scanCallback)
        #create callback for scan button
    def scanCallback(self, instance):
        #apply intergers to each space
        self.updateSpaceValue()
        #initiate the scans
        self.table.scan()
        #finally, set each gui int input to see results
        self.updateIntInput()
    def updateIntInput(self):
        for intInput in self.intInputs:
            intInput.updateGuiInt()
    def updateSpaceValue(self):
        for intInput in self.intInputs:
            intInput.updateSpaceInt()

class SudokuSolverApp(App):
    def __init__(self, **kwargs):
        super(SudokuSolverApp, self).__init__(**kwargs)
        self.table = Table()
        self.gui = MyBlock()

    def build(self):
        #start gui
        return self.gui

if __name__ == "__main__":
    app = SudokuSolverApp()
    app.run()