import sqlite3, json, time

dbFileName = "Post Graduate Reports.db"
tableName = "postGraduateReports"
dbJsonFileName = "postGradReportDatabaseRefined.json"

def loadJsonData():
    with open(dbJsonFileName, "r") as jsonFile:
        try:
            dictionary = json.load(jsonFile)
            return dictionary
        #except json.decoder.JSONDecodeError as err:
        except ValueError as err:
            print(err)

def dressStr(strung):
    ans = strung.strip()
    ans = ans.replace(" ", "_")
    return ans

#INITIATE
conn = sqlite3.connect(dbFileName)
cursor = conn.cursor()
jsonDict = loadJsonData()
jsonKeys = []
for diction in jsonDict.values():
    for key in diction.keys():
        jsonKeys.append(key)
jsonKeys = list(set(jsonKeys))
dbKeys = [dressStr(jKey) for jKey in jsonKeys]

#variable type for key
dbTypeTest = (
    ("Year","INTEGER"),
    ("id","INTEGER")
)
def keyDBType(key):
    #returns db type for key passed in
    for test, returnType in dbTypeTest:
        if test.lower() in key.lower():
            return returnType
    else:
        return "TEXT"

def submitDictionary():
    st = time.monotonic()
    #condition string of keys for creating database
    insideList = [f"{strang} {keyDBType(strang)}" for strang in dbKeys]
    inside = ", ".join(insideList)
    dbCreateStr = f"CREATE TABLE IF NOT EXISTS {tableName} ({inside})"
    #create database
    cursor.execute(dbCreateStr)
    #build database
    for v in jsonDict.values():
        insertReport(v, commit=False)
    conn.commit()
    nd = time.monotonic()
    print(f"Finished in {nd-st} seconds.")

def insertReport(diction, commit=True):
    #Func: Insert dictionary into database
    #get the value of dictionary in correct sequence for database
    #insideList = [adaptVarToSqlite(diction[key]) for key in jsonKeys]
    insideList = [str(diction[key]) for key in jsonKeys]
    #put sufficient space holder for dbString format 
    quesFiller = ["?"] * len(dbKeys)
    inside = ", ".join(quesFiller)
    print("This is insideList.", insideList)
    dbInsertStr = f"INSERT INTO {tableName} VALUES ({inside})"
    cursor.execute(dbInsertStr, insideList)
    if commit:
        conn.commit()

def readReport():
    pass
    #cursor.execute("SELECT * FROM employees WHERE lastName='Baird'")
def adaptVarToSqlite(variable):
    if isinstance(variable, (int, float)):
        return variable
    elif isinstance(variable, list):
        return str(variable)
    else:
        str(variable)

if __name__ == "__main__":
    submitDictionary()