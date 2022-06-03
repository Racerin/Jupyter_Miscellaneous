import sqlite3

#pass a file for storing data or create m memory
conn = sqlite3.connect(':memory:')
#conn = sqlite3.connect("employee.db")

#to execute sql commands
cursor = conn.cursor()

#cursor.execute("""CREATE TABLE employees (
cursor.execute("""CREATE TABLE IF NOT EXISTS employees (
            First_Name TEXT,
            lastName TEXT,
            pay integer
    )""")

cursor.execute("INSERT INTO employees (lastName, pay, First_Name) VALUES ('Baird', 0, 'Darnell')")
cursor.execute("INSERT INTO employees VALUES ('Darnell', 'Baird', 0)")
#probably use 'cursor.commit()' after an insert before reading
#cursor.execute("SELECT * FROM employees WHERE lastName='Baird'")
#cursor.execute("SELECT * FROM employees")
#cursor.execute("PRAGMA table_info(employees)")
cursor.execute("schema employees")
cursor.execute("UPDATE employees SET pay = 50 WHERE lastName = Baird AND firstName = Darnell")
cursor.execute("DELETE FROM employees  WHERE lastName = Baird AND firstName = Darnell")
print(cursor.fetchall())

#get the results of line of text
#cursor.fetchone(); cursor.fetchmany(); cursor.fetchall()

#sqlite3.OperationalError:
#apply changes
conn.commit()

cursor.close()
conn.close()