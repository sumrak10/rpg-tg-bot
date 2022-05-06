import sqlite3

# dbAddress = "./db.sqlite" # for linux
dbAddress = "C:/vscode/rpg-tg-bot/db.sqlite" #for windows
# (personId,personUname,personName,personAge,personDes,100,0)
def insert_data_to_bd(id,uname,name,age,des,mon,loc):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(id,uname,name,age,des,mon,loc)]
        sql = """INSERT INTO persons
                    VALUES (?,?,?,?,?,?,?)"""
        cursor.executemany(sql, data)
        data = [(id,uname,'','')]
        sql = """INSERT INTO relationship
                    VALUES (?,?,?,?)"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        return True
    except:
        return False
def get_persons_in_loc_bd(loc):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE loc=?"
    cursor.execute(sql, [(loc)])
    fetch_data = cursor.fetchall()
    conn.close()
    return fetch_data
def get_data_from_bd_by_id(id):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM persons WHERE id=?"
        cursor.execute(sql, [(id)])
        fetch_data = cursor.fetchall()
        fetch_data_reg = fetch_data[0]
        conn.close()
        return fetch_data_reg
    except:
        return 0
def get_data_from_bd_by_uname(uname):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM persons WHERE uname=?"
        cursor.execute(sql, [(uname)])
        fetch_data = cursor.fetchall()
        fetch_data_reg = fetch_data[0]
        conn.close()
        return fetch_data_reg
    except:
        return 0
def get_id_by_uname(uname):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    fetch_data_reg = fetch_data[0]
    conn.close()
    return fetch_data_reg[0]
def get_uname_by_id(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM persons WHERE id=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchall()
    fetch_data_reg = fetch_data[0]
    conn.close()
    return fetch_data_reg[1]
def update_loc_bd(id, val):
	conn = sqlite3.connect(dbAddress)
	cursor = conn.cursor()
	data = [(val, id)]
	sql = """UPDATE persons 
			SET loc = ?
			WHERE id = ?"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()
def update_mon_bd(uname, val):
	conn = sqlite3.connect(dbAddress)
	cursor = conn.cursor()
	data = [(val, uname)]
	sql = """UPDATE persons 
			SET mon = ?
			WHERE uname = ?"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()
def update_mon_bd_by_id(id, val):
	conn = sqlite3.connect(dbAddress)
	cursor = conn.cursor()
	data = [(val, id)]
	sql = """UPDATE persons 
			SET mon = ?
			WHERE id = ?"""
	cursor.executemany(sql, data)
	conn.commit()
	conn.close()

def get_friends_and_enemies_list(uname):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    try:
        fetch_data = fetch_data[0]
        friends = fetch_data[2]
        enemies = fetch_data[3]
    except:
        friends = ''
        enemies = ''
    conn.commit()
    conn.close()
    return friends, enemies
# 200 - друг добавлен 300 - враг добавлен в чс 401 - друг уже есть 403 - друг в чс 501 - враг уже есть 503 - враг в друзьях
def add_friend(uname,friend):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    fetch_data = fetch_data[0]
    friends = fetch_data[2]
    enemies = fetch_data[3]
    for i in friends.split():
        if i == friend:
            status = 401
            break
    for i in enemies.split():
        if i == friend:
            status = 403
            break
    if status == 0:
        data = [(friends+' '+friend, uname)]
        sql = """UPDATE relationship
                SET white = ?
                WHERE uname = ?"""
        cursor.executemany(sql, data)
        status = 200
    conn.commit()
    conn.close()
    return status
# 201 - удален из друзей 601 - не было в друзьях
def del_friend(uname, friend):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    fetch_data = fetch_data[0]
    friends = fetch_data[2]
    enemies = fetch_data[3]
    friends1 = ''
    if friend in friends.split():
        for i in friends.split():
            if i == friend:
                continue
            else:
                friends1 += i+' '
    else:
        status = 601
    friends = friends1
    if status == 0:
        data = [(friends, uname)]
        sql = """UPDATE relationship
                SET white = ?
                WHERE uname = ?"""
        cursor.executemany(sql, data)
        status = 201
    conn.commit()
    conn.close()
    return status
# 200 - друг добавлен 300 - враг добавлен в чс 401 - друг уже есть 403 - друг в чс 501 - враг уже есть 503 - враг в друзьях
def add_enemy(uname,enemy):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    fetch_data = fetch_data[0]
    friends = fetch_data[2]
    enemies = fetch_data[3]
    for i in friends.split():
        if i == enemy:
            status = 503
            break
    for i in enemies.split():
        if i == enemy:
            status = 501
            break
    if status == 0:
        data = [(enemies+' '+enemy, uname)]
        sql = """UPDATE relationship
                SET black = ?
                WHERE uname = ?"""
        cursor.executemany(sql, data)
        status = 300
    conn.commit()
    conn.close()
    return status
# 301 - враг удален 701 - не было во врагах
def del_enemy(uname, enemy):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE uname=?"
    cursor.execute(sql, [(uname)])
    fetch_data = cursor.fetchall()
    fetch_data = fetch_data[0]
    friends = fetch_data[2]
    enemies = fetch_data[3]
    enemies1 = ''
    if enemy in enemies.split():
        for i in enemies.split():
            if i == enemy:
                continue
            else:
                enemies += i+' '
    else:
        status = 701
    enemies = enemies1
    if status == 0:
        data = [(enemies, uname)]
        sql = """UPDATE relationship
                SET black = ?
                WHERE uname = ?"""
        cursor.executemany(sql, data)
        status = 301
    conn.commit()
    conn.close()
    return status
def get_data_from_management(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM management WHERE id=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchall()
    fetch_data_reg = fetch_data[0]
    conn.close()
    return fetch_data_reg
def insert_new_person_in_management(id,date,businessStr):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(id,date,0,date,businessStr)]
    sql = """INSERT INTO management
                VALUES (?,?,?,?,?)"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_income(id,val):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(val, id)]
    sql = """UPDATE management
			SET income = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_prize_date(id,date):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(date, id)]
    sql = """UPDATE management
			SET prize_date = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_business_date(id,date):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(date, id)]
    sql = """UPDATE management
			SET business_date = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_business(id,date):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(date, id)]
    sql = """UPDATE management
			SET business = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()

# GARDEN

def get_data_from_gardening(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM gardening WHERE id=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchall()
    fetch_data_reg = fetch_data[0]
    conn.close()
    return fetch_data_reg
def insert_new_person_in_gardening(id,garden,date):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(id,garden,date)]
    sql = """INSERT INTO gardening
                VALUES (?,?,?)"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_garden(id,garden):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(garden, id)]
    sql = """UPDATE gardening
			SET garden = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_last_watering_date(id,date):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(date, id)]
    sql = """UPDATE gardening
			SET last_watering = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()

# /GARDEN