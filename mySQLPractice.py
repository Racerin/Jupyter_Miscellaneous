import mysql.connector

#global variables
hostName = "localhost"
#hostName = "first"
userName = "Darnell"
password = "password1"
databaseName = "firstTry"

myDB = mysql.connector.connect(
    host=hostName,
    user=userName,
    #database=databaseName,
    #passwd=password
)

cursor = myDB.cursor()
cursor.execute(f"CREATE DATABASE {databaseName}")
#to be tried: create table if it does exist already
#cursor.execute(f"CREATE DATABASE IF NOT EXISTS {databaseName}")
#create a database with incremented int and other fields
cursor.execute(f"CREATE TABLE {databaseName} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))")
#change database
cursor. execute(f"ALTER TABLE {databaseName} ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")

#insert row
sql = f"INSERT INTO {databaseName} (name, address) VALUES (%s, %s)"
val = ("Darnell", "La Canoa")
cursor.execute(sql, val)

myDB.commit()


'''cursor.execute("SHOW TABLES")
[print(x) for x in cursor]'''