#<python dir>\share\sdl2\bin
import kivy
from functools import partial
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock


kivy.require("1.11.1")

class StartPage(GridLayout):
    
    def __init__(self, **kwargs):
        super(StartPage, self).__init__(**kwargs)

        self.cols = 2
        #Handlers & Widgets
        self.username = TextInput(multiline=False)
        self.password = TextInput(password=True, multiline=False)
        self.nextButton = Button(text="NEXT")

        #addWidgets
        self.add_widget(Label(text='User Name', valign="middle", halign="center"))    #no need to handle widgets with this data. 
        self.add_widget(self.username)
        self.add_widget(Label(text='Password', font_size=30))
        self.add_widget(self.password)
        self.add_widget(Label())    #occupty an empty slot
        self.add_widget(self.nextButton)

        #Bindings
        #applied to usernameInput widget
        #self.username.bind(text=self.reactWithPrint)
        self.username.bind(focus=self.reactWithPrint)
        #ETC
        self.nextButton.bind(on_press=self.nextPage)

    def reactWithPrint(self, instance, value, former = None):
        print('The widget', instance, 'have:', value)
        print(former)
        former = value


    def nextPage(self, instance):
        mom.mainMenu.setData(f"{self.username.text}")
        #next page
        mom.screenManagerObj.current = "Mainz"

    def passWord2(self):
        pass

class MainMenu(GridLayout):
    '''THE SIZE ARGUMENTS ARE NOT WORKING    '''

    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

        self.cols = 1
        #Handles & Widgets
        self.data = Label()
        self.nextButton = Button(text="NEXT", width=50, height=20)
        self.settings = Button(text="Settings")
        self.texty = TextInput(multiline=False)#, width=Window.size[0]*0.8)
        bottomLine = GridLayout(cols=2, height=40)

        #add_widget
        self.add_widget(self.data)
        bottomLine.add_widget(self.settings)
        bottomLine.add_widget(self.texty)
        bottomLine.add_widget(self.nextButton)
        self.add_widget(bottomLine)

        #Bindings
        self.nextButton.bind(on_press=self.nextPage)
        self.settings.bind(on_press=self.runSettings)

    def runSettings(self, instance):
        mom.screenManagerObj.current = "Settings"
    def nextPage(self, instance):
        mom.screenManagerObj.current = "Info"

    def setData(self, str):
        self.data.text += str

class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super(InfoPage, self).__init__(**kwargs)

        self.rows = 1
        self.cols = 2
        #Handles & Widgets
        self.history = Label(height=Window.size[1] * 0.9, size_hint_y=None, text="Ent nunnin but a G thang")
        self.newMessage = TextInput(width=Window.size[0]*0.8)

        #add_widget
        self.add_widget(self.history)
        self.add_widget(self.newMessage)

        #Bindings


class Settings(GridLayout):

    #controller inputs here. eg. per element, True|1. 
    inputs = []
    resolution = Window.system_size
    right = Label()

    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)

        self.cols = 1
        self.rows = 2
        #Handles & Widgets
        top = GridLayout(cols=2, rows=1)
        self.conclude = GridLayout(rows = 1)    #self.buttom
        #right side settings
        self.game = Label(height=Window.size[1] * 0.9, size_hint_y=None, text="Ent nunnin but a G thang")
        self.display = Label(size_hint_y=None, text="Display Stuff Stuff")
        self.sound = Label(height=Window.size[1] * 0.9, size_hint_y=None, text="Sound Stuff")
        self.input = TextInput(width=Window.size[0]*0.8)
        #left Right Assign
        self.left = GridLayout(cols=1)
        #self.right = self.game
        #Settings buttons
        self.gameb = ToggleButton(text="Game Settings", group='set', background_color=[1,0,1,0.5])
        self.displayb = ToggleButton(text="Display Settings", group='set', background_color=[0,1,1,0.75])
        self.soundb = ToggleButton(text="Sound Settings", group='set', background_color=[1,1,1,1])
        self.inputb = ToggleButton(text="Key Bindings", group='set', background_color=[1,0,0,0.1])
        #buttom buttons
        self.default = Button(text="Default")
        self.cancel = Button(text="Cancel")
        self.apply = Button(text="Apply")
        self.return_ = Button(text="Return")

        #add_widget
        self.add_widget(top)
        self.add_widget(self.conclude)
        top.add_widget(self.left)
        top.add_widget(self.right)
        #leftSide Buttons
        self.left.add_widget(self.gameb)
        self.left.add_widget(self.displayb)
        self.left.add_widget(self.soundb)
        self.left.add_widget(self.inputb)
        #buttom buttons
        self.conclude.add_widget(self.default)
        self.conclude.add_widget(self.cancel)
        self.conclude.add_widget(self.apply)
        self.conclude.add_widget(self.return_)

        #Bindings
        #widget on right side based on button on left side pressed
        self.gameb.bind(on_press=partial(self.settingsButtonPress, key="game"))
        self.displayb.bind(on_press=partial(self.settingsButtonPress, key="display"))
        self.soundb.bind(on_press=partial(self.settingsButtonPress, key="sound"))
        self.inputb.bind(on_press=partial(self.settingsButtonPress, key="input"))
        #conclusions
        self.default.bind(on_press=partial(self.concludePress, key="default"))
        self.cancel.bind(on_press=partial(self.concludePress, key="cancel"))
        self.apply.bind(on_press=partial(self.concludePress, key="apply"))
        self.return_.bind(on_press=partial(self.concludePress, key="return"))

    def settingsButtonPress(self, instance, key):
        if key == "game":
            print("Bring up game options")
            self.right.clear_widgets()
            self.right.add_widget(self.game)
        elif key == "display":
            print("bring up display settings")
            self.right.clear_widgets()
            self.right.add_widget(self.display)
        elif key == "sound":
            print("bring up sound settings")
            self.right.clear_widgets()
            self.right.add_widget(self.sound)
        elif key == "input":
            print("Bring up key binding")   
            self.right.clear_widgets()
            self.right.add_widget(self.input)     

    def concludePress(self, instance, key):
        if key == "default":
            print("Default stuff here")
        elif key == "cancel":
            print("Cancel Stuff Here")
        elif key == "apply":
            print("Apply Stuff here")
        elif key == "return":
            print("return stuff here")
            mom.screenManagerObj.current = "Mainz"
        else:
            print("The key was ", key)
            raise "Wrong key input"


class TestApp(App):

    startData = ""

    def build(self):
        '''
        return a Widget
        '''
        #manager
        self.screenManagerObj = ScreenManager()

        #Handle objects
        self.startPageObj = StartPage()
        screen = Screen(name="Bobo")
        #add widgets
        screen.add_widget(self.startPageObj)
        self.screenManagerObj.add_widget(screen)

        #Handle objects
        self.mainMenu = MainMenu()
        screen = Screen(name="Mainz")
        #add widgets
        screen.add_widget(self.mainMenu)
        self.screenManagerObj.add_widget(screen)

        #Handle objects
        self.infoPage = InfoPage()
        screen = Screen(name="Info")
        #add widgets
        screen.add_widget(self.infoPage)
        self.screenManagerObj.add_widget(screen)

        #Handle objects
        self.settings = Settings()
        screen = Screen(name="Settings")
        #add widgets
        screen.add_widget(self.settings)
        self.screenManagerObj.add_widget(screen)

        return self.screenManagerObj


if __name__ == '__main__':
    mom = TestApp()
    mom.run()