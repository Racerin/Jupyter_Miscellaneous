import sqlite3
import sqliteConvertData as scd

#pass a file for storing data or create m memory
conn = sqlite3.connect(scd.dbFileName)
#conn = sqlite3.connect("employee.db")

#to execute sql commands
cursor = conn.cursor()

"""
(0, 'Supervisor', 'TEXT', 0, None, 0)
(1, 'Keywords', 'TEXT', 0, None, 0)
(2, 'Project_Title', 'TEXT', 0, None, 0)
(3, 'Metadata', 'TEXT', 0, None, 0)
(4, 'Student_Name', 'TEXT', 0, None, 0)
(5, 'Knowledge_Areas', 'TEXT', 0, None, 0)
(6, 'Keywords', 'TEXT', 0, None, 0)
(7, 'ID', 'INTEGER', 0, None, 0)
(8, 'Year', 'INTEGER', 0, None, 0)
#cursor.execute('PRAGMA table_info(postGraduateReports)')
#cursor.execute('PRAGMA table_info(postGraduateReports);')
"""

#cursor.execute('SELECT * FROM postGraduateReports')
cursor.execute("SELECT Project_Title FROM postGraduateReports WHERE Supervisor LIKE '%lalla%'")
items = cursor.fetchall()
[print(x) for x in items]

#get the results of line of text
#cursor.fetchone(); cursor.fetchmany(); cursor.fetchall()

#sqlite3.OperationalError:
#apply changes
conn.commit()

cursor.close()
conn.close()