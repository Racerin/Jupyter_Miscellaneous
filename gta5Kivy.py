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

processes = {}
_timeDelay = 5
@property
def timeDelay(self):
    return _timeDelay   #for now
@timeDelay.setter
def timeDelay(self, val):
    if isinstance(val, str):
        try:
            val = float(str)
        except:
            logging.debug(f"{val} cannot be turned into a number")
    if isinstance(val, (int, float)):
        if _timeDelay >= 0:
            _timeDelay = val

def startProcess(func, label, *args):
    processes.update({label:None})
    part = lambda *args: func()
    Clock.schedule_once(part, _timeDelay)
'''def startProcess(func, label, *args):
    p = Process(target=func, daemon=False, args=args)
    processes.update({label:p})
    #time.sleep(_timeDelay)
    #p.start()
    part = lambda x: p.start()
    Clock.schedule_once(part, _timeDelay)'''
def closeProcesses():
    for nm, process in processes.items():
        p = processes.pop(nm)
        print(f"Process '{nm}' with id '{p.pid}' is terminated.")
        p.terminate()

class EachLine(BoxLayout):
    orientation = 'horizontal'
    #size_hint=(0.4,0.1)
    spacing = 5
    @classmethod
    def myBuild(cls, label, callback, args=[]):
        #properties
        obj = EachLine()
        fontSize = '20sp'
        #widgets
        obj.label = Label(text=label, font_size=fontSize)
        obj.button = Button(text=label, font_size=fontSize)
        toAdd = [obj.button,]
        #add widgets
        [obj.add_widget(w) for w in toAdd]
        #add bindings
        theCallback = partial(startProcess, callback, label)
        obj.button.bind(on_release=theCallback)
        return obj

class MyBlock(BoxLayout):
    #cols = 1
    orientation = 'vertical'
    def __init__(self, **kwargs):
        super(MyBlock, self).__init__(**kwargs)
        #create widgets
        self.title = Label(text="GTA 5 Hackerz", font_size='40sp')
        self.allFunctions = (
            ("Hand Wrestle", gta5Help.wrestle, []),
            ("Spin the Wheel", gta5Help.spinWheel, []),
            ("Modify Car", gta5Help.modifyCar, []),
            ("Random Movement", gta5Help.randomWalkAround, []),
            ("Close Processes", closeProcesses, []),
        )
        buttons = [EachLine.myBuild(label=lab, callback=call, args=args) for lab,call,args in self.allFunctions]
        toAdd = [self.title] + buttons
        #add widgets
        [self.add_widget(w) for w in toAdd]

class gta5HelpApp(App):
    
    def __init__(self, **kwargs):
        super(gta5HelpApp, self).__init__(**kwargs)

    def build(self):
        self.gui = MyBlock()
        #start gui
        return self.gui

if __name__ == "__main__":
    app = gta5HelpApp()
    app.run()