import itertools, re

#create dominos and containers (NB, bank includes unplayed and other players dominos)
bank = createDominoList()
hand = []
board = []
#pick up dominos before main game
askHand()
#input all played dominos
probability()

def probability():
    #ask what players are playing
    played()
    #determine probabilities
    futureOutcomes()

def futureOutcomes():
    #returns information on all needed information to win the game
    response = ""
    #how many of value remain
    response += remaindersQ()
    #output
    print(response)

def remaindersQ(container = bank, highestValue = 6):
    #statisitcal info on values remaining
    ans = ""
    #think of a pill box with compartment for each value to put in quantity
    sorted = [0] * (highestValue + 1)

    for setty in container:
        valuz = list(setty)
        for num in valuz:
            sorted[num] += 1

    for index in range(len(sorted)):
        ans += f"{sorted[index]} {index}'s, "

    return ans + '\n'
        
def played():
    prompt = "What was played? \n[u - Undo, d - End, xx/x x - Domino value played]"
    ans = input(prompt)
    if 'd' in ans.lower():
        #end
        pass
    elif 'u' in ans.lower():
        #undo
        pass
    else:
        numbersStr = re.findall(r'\d', ans)
        testNumSet = {numbersStr[0], numbersStr[1]}

        if testNumSet in bank:
            #if the bank contains this number
            bank.remove(testNumSet)
            hand.append(testNumSet)
        else:
            #throw an error
            raise "This maths is not adding up."


def askHand(inHand = 7):
    #initiate the querying of dominos in hand
    for i in range(inHand):
        pickupDomino()

def pickupDomino():
    #input 2 numbers and their value 
    str = input("What are the hand pieces?\n")
    numbersStr = re.findall(r'\d', str)
    testNumSet = {numbersStr[0], numbersStr[1]}

    if testNumSet in bank:
        #if the bank contains this number
        bank.remove(testNumSet)
        hand.append(testNumSet)
    else:
        #throw an error
        raise "This maths is not adding up."

def createDominoList(highestValue = 6):
    #creates a list of sets with each set containing a pair of ints
    listOfTuplePairInts = itertools.combinations(range(highestValue + 1), 2)
    newBank = []
    #convert each pair into a set
    for pair in listOfTuplePairInts:
        setPair = {pair}
        newBank.append(setPair)
    return newBank
        




