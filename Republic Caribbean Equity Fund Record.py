#keeping up to date on republic bank mutual fund

import time, configparser, re, requests, sqlite3, os, sys
from bs4 import BeautifulSoup


#Republic Caribbean Equity Fund
def republic_caribbean_equity_fund():
    #GET NUMBERS OFF OF WEBSITE
    #get web info
    url = 'https://republictt.com/corporate/republic-mutual-funds'
    html = requests.get(url).text
    soup = BeautifulSoup(html)
    
    #parse web info
    #hierarchy: tbody > tr > td > (all the numbers)
    match_strings = []
    escape_bool = False
    for tbody in soup.find_all('tbody'):
        #print(tbody, '\n')
        for tr in tbody.find_all('tr'):
            elements = [td.string for td in tr.find_all('td')]
            match_strings = [re.search(r'[-+]?[0-9]*\.?[0-9]*', ele).group(0) for ele in elements if isinstance(ele,str)]
            if all(match_strings):
                escape_bool = True
                #print(match_strings)
            if escape_bool: break        
        if escape_bool: break
            
    #SAVE NUMBERS
    #using sqlite
    cwd = os.path.dirname(os.path.realpath(__file__))
    db_name = 'financial info.db'
    db_path = os.path.join(cwd, db_name)
    conn = sqlite3.connect(db_path)
    #conn = sqlite3.connect(':memory:')
    sql_values = [time.time(),] + [str(match_strings[i]) for i in [0,1,2,-1]]
    with conn:
        #create table if it doesnt exist
        conn.execute('''CREATE TABLE IF NOT EXISTS Caribbean_Equity_Fund_Trends
        (date REAL , offer_price real, bid_price real, ytd_return real, cummulative_from_inception real);''')
        
        prompt = input(f"Do you accept these numbers? [Y/N]\n{sql_values}\n")
        if 'y' in prompt.lower():
            #add values to table
            print('You accept these values.')
            conn.execute('''INSERT INTO Caribbean_Equity_Fund_Trends 
            VALUES (?,?,?,?,?);''', sql_values)
        else:
            print('You do not accept these values.')
        
        #delete all database values
        #conn.execute('DELETE FROM Caribbean_Equity_Fund_Trends;')
        
        #print values of table
        maco = True
        if maco:
            print("This is the current stores values.")
            maco = conn.execute('SELECT * FROM Caribbean_Equity_Fund_Trends;')
            for r in maco:
                print(r)
    conn.close()
    input("That's all folks.")
republic_caribbean_equity_fund()
#print(os.getcwd())
print(os.path.dirname(os.path.realpath(__file__)))
#print(os.path.dirname(os.path.realpath(sys.argv[0])))