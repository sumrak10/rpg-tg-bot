import sqlite3

from numpy import number
from bd_manage import *
# dbAddress = "./db.sqlite"
dbAddress = "C:/vscode/rpg-tg-bot/db.sqlite"

# conn = sqlite3.connect(dbAddress)
# cursor = conn.cursor()
# # (personId,personUname,personName,personAge,personDes,100,0)
# data = [(2,'sm','asd',12,'asdasdasd',100,0)]
# sql = """INSERT INTO persons
#             VALUES (?,?,?,?,?,?,?)"""
# cursor.executemany(sql, data)
# conn.commit()
# conn.close()

# conn = sqlite3.connect(dbAddress)
# cursor = conn.cursor()
# # (personId,personUname,personName,personAge,personDes,100,0)
# sql = """SELECT * FROM persons WHERE uname=?"""
# cursor.execute(sql, [('sm')])
# fetch_data = cursor.fetchall()
# fetch_data_reg = fetch_data[0]
# conn.commit()
# conn.close()
# print(fetch_data_reg[0])

# conn = sqlite3.connect(dbAddress)
# cursor = conn.cursor()
# sql = """
# CREATE TABLE [persons](
#   [id] INTEGER PRIMARY KEY ON CONFLICT ABORT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT DEFAULT 0, 
#   [uname] NVARCHAR(100) NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT, 
#   [fio] VARCHAR(255), 
#   [age] INT(255) NOT NULL ON CONFLICT ABORT, 
#   [des] VARCHAR(255), 
#   [mon] INT NOT NULL ON CONFLICT ABORT DEFAULT 0, 
#   [loc] INT NOT NULL ON CONFLICT ABORT DEFAULT 0) WITHOUT ROWID;
# """
# cursor.execute(sql)
# conn.commit()
# conn.close()


# from datetime import datetime

# start_time = datetime.now()
# a= 0 
# #Тут выполняются действия
# for i in range(100000000):
#     a = a + i

# print(datetime.now() - start_time)


from sys import platform
print(platform)