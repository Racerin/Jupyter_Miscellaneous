import re, itertools, json

#METHODS
def relativeVector(vectorA, vectorB):
    #error checking
    if len(vectorA) != len(vectorB):
        raise f"The dimensions don't match. {vectorA} {vectorB}"
    
    #process
    long = len(vectorA)
    newVec = []
    for i in range(long):
        ele = vectorB[i] - vectorA[i]
        newVec.append(ele)
        return newVec

def magnitude(vector):
    return sqrMag(vector) ** 0.5

def sqrMag(vector):
    #error checking
    indicesCheck = [isinstance(i, (int, float)) for i in vector]
    assert (all(indicesCheck)), "There is not a number in the elements."
    #processing
    return sum([i**2 for i in vector])

def saveRecord(fName, inputVectors, bestSequence, minDist):
    myFileName = 'Best Sequence Records'
    records = {
        "FileName":fName,
        "Set of Vectors":inputVectors,
        "Best Sequence":bestSequence,
        "Minimum Distance":minDist
    }
    jsonStr = json.dumps(records, indent=4)
    #saves the records to name
    with open(f'{myFileName} {fName}.txt', encoding='utf-8', mode='w') as saveFile:
        saveFile.write(jsonStr + '\n')
    print("Complete")

def initiate():
    #USER INPUTS
    fileName = 'madeup vector space.txt'#input("Input the file name. \n")
    dimensionsQ = '2'#input("How many dimensions? \n")

    #a list of vectors of positions
    vectorList = []
    dimAns = int(dimensionsQ)
    searchVec = ''
    if dimAns == 2:
        searchVec = r'\d+,\d+'
    elif dimAns == 3:
        searchVec = r'\d+,\d+,\d+'
    else:
        raise "Something wrong with you."

    #access the file with correct name
    with open(fileName) as csvFile:
        for row in csvFile:
            #remove white spaces
            formatted = re.sub(r'\s', '', row)
            #get csv with commas in given line
            formatted = re.findall(searchVec, formatted)
            #get the elements of the vector in the row
            numberzStr = re.findall(r'\d+', formatted[0])
            #create vector of floats
            vector = [float(i) for i in numberzStr]
            #add each vector to the vector list
            vectorList.append(vector)

            #find the shortest route between all vectors
            minimumDist = float('inf')
    #create generator of all possible sequence of the vectors
    allOutcomes = itertools.permutations(vectorList)
    bestSeq = []
    travel = 0
    for vectorSeq in allOutcomes:
        startVec = vectorSeq[0]
        for vec in vectorSeq:
            if vec is startVec:
                continue
            relVec = relativeVector(startVec, vec)
            travel += magnitude(relVec)
            startVec = vec
        #now check if this sequence was better (in travel distance) to the previous
        if travel<=minimumDist:
            if travel < minimumDist:
                bestSeq = []
            bestSeq.append(vectorSeq)
            #print("This is a vector Sequence. ", vectorSeq)
            minimumDist = travel
        travel = 0

    #results
    saveRecord(fileName, vectorList, bestSeq, minimumDist)

if __name__ == "__main__":
    initiate()










