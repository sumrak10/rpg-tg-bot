import sqlite3

dbAddress = "./db.sqlite"

def get_persons_in_loc_bd(loc):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE loc=?"
    cursor.execute(sql, [(loc)])
    fetch_data = cursor.fetchall()
    conn.close()
    return fetch_data
def get_data_from_bd(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE id=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchall()
    fetch_data_reg = fetch_data[0]
    conn.close()
    return fetch_data_reg
def insert_data_to_bd(id,data1,data2,data3,data4,data5):
    # try:
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(id, data1, data2, data3, 100, 0)]
    sql = """INSERT INTO persons
                VALUES (?,?,?,?,?,?)"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
    return True
def update_loc_bd(usid, val):
	conn = sqlite3.connect(dbAddress)
	cursor = conn.cursor()
	data = [(val, usid)]
	sql = """UPDATE persons 
			SET loc = ?
			WHERE id = ?"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()
def update_mon_bd(usid, val):
	conn = sqlite3.connect(dbAddress)
	cursor = conn.cursor()
	data = [(val, usid)]
	sql = """UPDATE persons 
			SET mon = ?
			WHERE id = ?"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()