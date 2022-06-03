import math, re, kivy, os, sys, time, pathlib, json, copy, logging
import numpy as np
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

logging.basicConfig(level=logging.DEBUG,
#filename= 'output.txt',
format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Start of preliminary tractor program.")
#logging.disable(logging.CRITICAL)  #end all logging messages

def decoratorCheckTime(func):
    import time
    def wrapper(*arg, **kwargs):
        startTime = time.monotonic()
        func(*arg, **kwargs)
        logging.info(f"This is how long it took. {time.monotonic() - startTime}")
    return wrapper

class MathCalc:
    g = 9.81
    hp2w = 746
    rpm2omega = 2*math.pi/60

class Scenario:
    pass

class Soil:
    pass

class Wheel:
    def __init__(self):
        pass
    def create(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
        return self

class Hitch:
    def __init__(self):
        pass

class Tractor:
    __properties = {"manufacturer":"John Deere", "owner": "Darnell"}

    def __init__(self):
        pass
        #do what you have to do.
        
    def johnDeere(self):
        #create tractor obj 1st then call this method on the tractor
        #add stuff to tractor here
        #based off of a John Deere 6170R https://tractortestlab.unl.edu/John%20Deere%206170R.pdf
        #helpful paramters info. https://elibrary.asabe.org/data/pdf/6/ttp2003/Lecture27.pdf
        setattr(self, 'company', 'John Deere')
        setattr(self, 'pull', 77370)
        setattr(self, 'wheelbase', 2.8)
        setattr(self, 'threadWidthRear', (1.524+3.164)/2)
        setattr(self, 'threadWidthFront', (2.206+1.494)/2)
        setattr(self, 'drawbarHeight', 0.595)
        setattr(self, 'mass', 8280)
        setattr(self, 'massRear', 5568)
        setattr(self, 'massFront', 2712)
        setattr(self, 'ratedPower', 106.850)    #kW
        setattr(self, 'ratedEngineSpeed', 2100*MathCalc.rpm2omega)
        setattr(self, 'ratedEngineSpeed', 2712)
        whlFront = Wheel.create({
            'diameter':1,
            'powered':True
        })
        return self

class Simulate:
    def primeValues():
        #prints all the common values wanted from Wismer Luth Tractor simulation

class Finance:
    pass

class Commenter:
    '''
    Provides Prompts,hints for gui
    '''

class ErrorManager:
    '''
    Stores the shortcut functions for error checking
    '''

class StartPage(GridLayout):
    cols = 1
    clicks = 0
    def __init__(self, **kwargs):
        super(StartPage, self).__init__(**kwargs)
        #Handles & Widgets
        self.sign = Label(text="The beginning.")
        self.typeBox = TextInput()
        self.butt1 = Button(text="Click Me!")
        #add_widget
        self.add_widget(self.sign)
        self.add_widget(self.typeBox)
        self.add_widget(self.butt1)
        #Bindings
        self.butt1.bind(state=self.buttonState)
        self.butt1.bind(on_press=self.buttonDown)
    def buttonState(self, instance, value):
        string = f"There have been {self.clicks} clicks, the instance is {instance} and the value is {value}."
        self.typeBox.text = string
    def buttonDown(self, instance):
        self.clicks += 1


class Manager(App):
    '''
    works with kivy to showcase the code
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        #create and add layouts to screenmanager
        sm = ScreenManager()
        layoutz = {"start":StartPage()}
        for k, obj in layoutz.items():
            screen = Screen(name=k)
            screen.add_widget(obj)
            sm.add_widget(screen)
        sm.current = "start"
        self.sm = sm
        
        #return Label(text="To be continued.")
        return self.sm

def runIt():
    obj = Manager()
    obj.run()

if __name__ == '__main__':
    runIt()
    
