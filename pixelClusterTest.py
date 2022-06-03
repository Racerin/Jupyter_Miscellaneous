import pynput, threading
from pynput.mouse import Button, Controller as mouseController, Listener as mouseListener
from pynput.keyboard import Key, Controller as keyboardController, Listener as keyboardListener

#DONT THINK ELLIPSE, THINK CIRCLE
class cluster():
    dots = []
    axes = (1,1)
    centroid = None
    thresholdRange = 50
    one = 1
    lastClick = None
    def __init__(self):
        self.runON = True
        self.clickAccess = False

    def __repr__(self):
        pass

    def oneQ(self):
        #whether a pixel fits in the axis or not
        #https://en.wikipedia.org/wiki/Ellipse
        if self.centroid:
            x,y = self.lastClick
            xCentre, yCentre = self.centroid
            xAxis, yAxis = self.axes
            xAxis += self.thresholdRange
            yAxis += self.thresholdRange
            left = ((x - xCentre)**2)/((xAxis)**2)
            right = ((y - yCentre)**2)/((yAxis)**2)
            juan = left + right
            print("This number suppose to be '1'.", juan)
            if juan < self.one:
                #inside the range
                print("Inside the range of the ellipse.")
                self.dots.append(self.lastClick)
                self.calculate()
                print(self)
            else:
                #outside the range
                print("Outside the range.")
        else:
            self.centroid = self.lastClick
        self.lastClick = None
    def calculate(self):
        pass

    #keyboard events
    def on_press(self, key):
        print('{0} pressed'.format(key))
    def on_release(self, key):
        print('{0} release'.format(key))
        if key == Key.esc:
            self.runON = False
            return False
    def keyboardControl(self):
        # Collect events until released
        with keyboardListener(
        on_press=self.on_press,
        on_release=self.on_release) as listener:
            listener.join()
    
    #mouse events
    def on_move(self, x, y):
        pass
        #print('Pointer moved to {0}'.format((x, y)))
        if self.runON == False:
            return False
    def on_click(self, x, y, button, pressed):
        print('{0} at {1}'.format('Pressed' if pressed else 'Released',(x, y)))
        self.lastClick = (x,y)
    def on_scroll(self, x, y, dx, dy):
        print('Scrolled {0}'.format((x, y)))
    def mouseControl(self):
        with mouseListener(
        on_move=self.on_move,
        on_click=self.on_click,
        on_scroll=self.on_scroll) as listener:
            listener.join()

    def run(self):
        mouseThread = threading.Thread(target=self.mouseControl)
        keyboardThread = threading.Thread(target=self.keyboardControl)
        logicThread = threading.Thread(target=self.mane)
        mouseThread.start()
        keyboardThread.start()
        logicThread.start()
        mouseThread.join()
        keyboardThread.join()
        logicThread.join()
        print("Finished")

    def mane(self):
        while self.runON:
            if self.lastClick:
                self.oneQ()

if __name__ == "__main__":
    obj = cluster()
    obj.run()

