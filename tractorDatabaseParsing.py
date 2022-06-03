import requests, re, json, io, multiprocessing, functools, string, random, time, logging, os, urllib, types, PyPDF2, concurrent, threading
import tractorConstructLib as tcl
from tractorOnlineExtraction import *
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout, ConnectionError
#https://realpython.com/python-requests/
#tabula-py  #try tabula #https://github.com/chezou/tabula-py

logging.basicConfig(level=logging.DEBUG,
#filename= 'tractorDataDownloadLog.txt',
format='%(asctime)s - %(levelname)s - %(message)s')

def motherPageSubURLs(motherURL='https://tractortestlab.unl.edu/'):
    #obtain all url links from a webpage
    sauce = urllib.request.urlopen(motherURL).read()
    mainSoup = BeautifulSoup(sauce, 'html.parser')
    refTags = mainSoup.find_all('a')
    hrefs = [refTag.get('href') for refTag in refTags]
    urls = [urllib.parse.urljoin(motherURL, href) for href in hrefs]
    return urls
def url_pdf_filter(urlList, motherURL='https://tractortestlab.unl.edu/'):
    #now, browse each webpage in urlList and search for '.pdf' urls and return them
    pdfURLs = []
    for url in urlList:
        try:
            subSauce = urllib.request.urlopen(url).read()
            subSoup = BeautifulSoup(subSauce, 'html.parser')
            subRefTags = subSoup.find_all('a')
            subURLs = [urllib.parse.urljoin(motherURL, path.get('href')) for path in subRefTags]
            subPdfURLs = [subURL for subURL in subURLs if subURL.endswith('.pdf')]
            pdfURLs += subPdfURLs
        except urllib.error.HTTPError as err:
            print(err)
    return pdfURLs
def tractors_pdf_dict(pdfURLs):
    def checkForTractor(url, i):
        pdfName = f"{randomString(20)}.pdf"
        try:
            #save pdf from online pdf
            onlinePDF2File(url, pdfName)
            #extract text from pdf
            dict = pdf2Dict(pdfName)
            #do metadata check to see if is a tractor
            ansDict = keysCheck(dict)
            if ansDict:
                dicts[i] = ansDict
        except:
            logging.debug(f"Error occured with url {url}.")
        finally:
            try:
                #delete file
                os.remove(pdfName)
            except FileNotFoundError as err:
                strungE = f"{err}, maybe didnt find file to delete."
                logging.error(strungE)

    def keysCheck(dict):
        keys = list(dict)
        tractorBrand = ''
        #look for tractor company name in 'title' or 'subject' value
        for key in keys:
            val = dict[key]
            if 'title' in key.lower():
                for company in tcl.tractorCompanies:
                    if company in val:
                        tractorBrand = company
            elif 'subject' in key.lower():
                for company in tcl.tractorCompanies:
                    if company in val:
                        tractorBrand = company
        if tractorBrand:
            #return tractor dictionary
            return dict
        else:
            return None
    def threadsActiveCheck():
        now = time.monotonic
        st = now()
        ct = now()
        timeout = 10
        deltaTime = 1
        while ct-st < timeout:
            for i, thr in enumerate(activeThreads):
                if not thr.isAlive():
                    activeThreads.pop(i)
            if len(activeThreads) < maxThreads:
                break
            time.sleep(deltaTime)
            ct = now()
    #look at each pdf url, look at its metadata and determine whether it is tractor file by tractorCompanies list
    threads = []
    activeThreads = []
    dicts = [None] * len(pdfURLs)
    maxThreads = 4
    for i, pdfURL in enumerate(pdfURLs):
        threadsActiveCheck()
        x = threading.Thread(target=checkForTractor, args=(pdfURL,i))
        threads.append(x)
        activeThreads.append(x)
        x.start()
    #for thread in threads:
    for thread in activeThreads:
        thread.join()
    finalDicts = [x for x in dicts if bool(x)]
    return finalDicts
        
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def onlinePDF2File(url, pdfFileName, maxAttempts=5):
    try:
        response = None
        #while we didnt get it
        for _ in range(maxAttempts):
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                break
        response.raise_for_status()     #raise, error checking
        #write data to pdf in bit format
        with open(pdfFileName, 'wb') as my_data:
            my_data.write(response.content)
    #error testing
    except HTTPError as http_err:
        strungE = f"{http_err}, idk httperror."
        logging.exception(http_err)
    except Timeout:
        strungE = f"{Timeout}, timeout error in retrieving pdf"
        logging.exception(strungE)
    except ConnectionError:
        strungE = f"{ConnectionError}, did not make connection to retrieve pdf"
        logging.exception(ConnectionError)
    except OSError:
        strungE = f"{OSError}, the pdf file did not save."
        logging.exception(OSError)
def pdf2Dict(pdfName):
    dict = {}
    with open(pdfName, 'rb') as pdfFile:
        try:
            #pdf text data
            strung = ""
            read_pdf = PyPDF2.PdfFileReader(pdfFile)
            pages = read_pdf.numPages
            for num in range(pages):
                pageObj = read_pdf.getPage(num)
                strung += pageObj.extractText()
            #pdf meta data
            #reader = PyPDF2.PdfFileReader(pdfFile)
            metadata = read_pdf.getDocumentInfo()
            #add all info to dictionary
            dict.update(metadata)
            dict.update({'text':strung})
        except OSError:
            logging.error(f"pdf {pdfName} was not converted to text.")
        except Exception as err:
            strungE = f"{err}, maybe metadata"
            logging.error(strungE)
    return dict
def onlinePDF2Dict(url, maxAttempts=5):
    pdfName = f"{randomString(20)}.pdf"
    try:
        for _ in range(maxAttempts):
            response = requests.get(url, timeout=5)
            if response.status_code in [200,204,203]:   #https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
                break
        #raise, error checking
        response.raise_for_status()
        #now, save pdf to path to then extract pdf info
        with open(pdfName, 'wb+') as my_data:
            my_data.write(response.content)
            #pdf text data
            dict = {}
            holdText = []
            read_pdf = PyPDF2.PdfFileReader(my_data)
            pages = read_pdf.numPages
            for i in range(pages):
                pageObj = read_pdf.getPage(i)
                pageText = pageObj.extractText()
                holdText.append(pageText)
            text = "".join(holdText)
            #pdf meta data
            metadata = read_pdf.getDocumentInfo()
            #add all info to dictionary
            dict.update(metadata)
            dict.update({'text':text})
        return dict

    #error testing
    except HTTPError as http_err:
        strungE = f"{http_err}, idk httperror."
        logging.exception(http_err)
    except Timeout:
        strungE = f"{Timeout}, timeout error in retrieving pdf"
        logging.exception(strungE)
    except ConnectionError:
        strungE = f"{ConnectionError}, did not make connection to retrieve pdf"
        logging.exception(ConnectionError)
    except Exception as err:
        strungE = f"{err}, maybe metadata"
        logging.error(strungE)
    finally:
        #delete pdf file
        if os.path.exists(pdfName):
            os.remove(pdfName)

def getTractorNameFromDict(dict, defaultTractorName=""):
    #searching for name of tractor in sequence
    tractorName = defaultTractorName
    try:
        searchKeys = ['subject', 'title']
        for k, val in dict.items():
            for searchKey in searchKeys:
                if searchKey in k.lower():
                    tractorName = val
    except: 
        print("did not get the tractor's name")
        #print(dict)
    return tractorName
def string2BracketNums(strang="", thresholdPercent=0.4):
    #gets all brackets in string and calculate if brackets are legit
    #if legit(calculated power == power), store it
    nums = tcl.extractBracketNumberFromText(strang)
    checkLength = 5
    allNums = []
    numsPiece = nums[:-checkLength]
    for i, brac in enumerate(numsPiece):
        subNums = nums[i:i+checkLength]
        checkTup = subNums[:checkLength]
        #power, pull, speed = checkTup[:3]
        power, pull, speed, fc1, fc2 = checkTup
        calcPower = pull * speed/3.6
        diff = abs(calcPower - power)
        try:
            ratio = diff/min(power, calcPower)
        except:
            continue
        if ratio < (thresholdPercent/100):
            allNums.append(checkTup)
            #print(f"This is power {power}, pull {pull}, speed {speed}, and ratio {ratio * 100}%.")
            print(f"This is power {power}, pull {pull}, speed {speed}, fc1 {fc1}, fc2 {fc2},  and ratio { str(ratio*100)[:4] }%.")
    print(f"Total count is {len(allNums)}.")
    return allNums

def stringToDBPerformance(strung):
    pass
def stringToTractor(strung):
    pass