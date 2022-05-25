import sqlite3
from sys import platform

if platform == 'win32':
    dbAddress = "rpg-tg-bot/db.sqlite" #for windows
elif platform == 'linux':
    dbAddress = "./db.sqlite" # for linux
else:
    print("THIS PLATFORM DON'T SUPPORTED (bd_manage.py")
# (personId,personUname,personName,personAge,personDes,100,0)
def insert_data_to_bd(id,uname,name,age,des,mon,loc):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(id,uname,name,age,des,mon,loc,'0','0','0','0','0','0','0')]
        sql = """INSERT INTO persons
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
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
def add_num_to_mon_by_id(id,val):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT mon FROM persons WHERE id=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchone()
    data = [(str(int(val)+int(fetch_data[0])), id)]
    sql = """UPDATE persons 
			SET mon = ?
			WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def get_friends_and_enemies_list(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE id=?"
    cursor.execute(sql, [(id)])
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
def add_friend(id,friend):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE id=?"
    cursor.execute(sql, [(id)])
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
        data = [(friends+' '+friend, id)]
        sql = """UPDATE relationship
                SET white = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        status = 200
    conn.commit()
    conn.close()
    return status
# 201 - удален из друзей 601 - не было в друзьях
def del_friend(id, friend):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE id=?"
    cursor.execute(sql, [(id)])
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
        data = [(friends, id)]
        sql = """UPDATE relationship
                SET white = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        status = 201
    conn.commit()
    conn.close()
    return status
# 200 - друг добавлен 300 - враг добавлен в чс 401 - друг уже есть 403 - друг в чс 501 - враг уже есть 503 - враг в друзьях
def add_enemy(id,enemy):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE id=?"
    cursor.execute(sql, [(id)])
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
        data = [(enemies+' '+enemy, id)]
        sql = """UPDATE relationship
                SET black = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        status = 300
    conn.commit()
    conn.close()
    return status
# 301 - враг удален 701 - не было во врагах
def del_enemy(id, enemy):
    status = 0
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM relationship WHERE id=?"
    cursor.execute(sql, [(id)])
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
        data = [(enemies, id)]
        sql = """UPDATE relationship
                SET black = ?
                WHERE id = ?"""
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
    data = [(id,date,0,date,businessStr,'0')]
    sql = """INSERT INTO management
                VALUES (?,?,?,?,?,?)"""
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

# GLOBAL VARS
def get_global_var_data_from_bd(var_name):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM global_vars WHERE var_name=?"
    cursor.execute(sql, [(var_name)])
    fetch_data = cursor.fetchall()
    conn.close()
    return fetch_data[0][1]
def set_global_var_data_from_bd(var_name,var_data):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(var_data, var_name)]
    sql = """UPDATE global_vars
			SET var_data = ?
			WHERE var_name = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
# /GLOBAL VARS
# STOCK

def get_stock_data():
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM stock"
    cursor.execute(sql)
    fetch_data = cursor.fetchall()
    conn.close()
    return fetch_data

def update_stock_data(company,prices,dates):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(prices, company)]
    sql = """UPDATE stock
			SET prices = ?
			WHERE company = ?"""
    cursor.executemany(sql, data)
    data = [(dates, company)]
    sql = """UPDATE stock
			SET dates = ?
			WHERE company = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def get_stock_by_id(id):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM stock WHERE id=?"
        cursor.execute(sql, [(id)])
        fetch_data = cursor.fetchall()
        conn.close()
        return fetch_data[0]
    except:
        return 0
def get_stock_by_uname(uname):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM stock WHERE username=?"
        cursor.execute(sql, [(uname)])
        fetch_data = cursor.fetchall()
        conn.close()
        return fetch_data[0]
    except:
        return 0
def add_one_in_company_budget(loc):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM stock WHERE id=?"
        cursor.execute(sql, [(str(loc)+'1')])
        fetch_data = cursor.fetchall()
        budget = int(fetch_data[0][5])+1
        data = [(budget, str(loc)+'1')]
        sql = """UPDATE stock
                SET budget = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
    except:
        return 0
def clean_company_budget(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(0, id)]
    sql = """UPDATE stock
            SET budget = ?
            WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_user_stocks(id, stock):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(stock, id)]
    sql = """UPDATE management
            SET stock = ?
            WHERE id = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
def update_stock_amount_by_suname(uname, amount):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(amount, uname)]
    sql = """UPDATE stock
            SET amount = ?
            WHERE username = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
# /STOCK

# ЖАЛОБЫ
def insert_data_to_reports(id1,id2,des,text):
    # try:
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(id1,id2,des,text,0,' ')]
    sql = """INSERT INTO reports
                VALUES (?,?,?,?,?)"""
    cursor.executemany(sql, data)
    sql = "SELECT rowid FROM reports WHERE text=?"
    cursor.execute(sql, [(text)])
    fetch_data = cursor.fetchall()
    data = fetch_data[-1]
    conn.commit()
    conn.close()
    return data[0]
    # except:
    #     return False
def get_reports_from_bd():
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT rowid,* FROM reports"
    cursor.execute(sql)
    fetch_data = cursor.fetchall()
    conn.close()
    
    return fetch_data
def get_report_from_by_report_id(id):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    sql = "SELECT * FROM reports WHERE rowid=?"
    cursor.execute(sql, [(id)])
    fetch_data = cursor.fetchone()
    conn.close()
    return fetch_data
def update_report_from_by_report_id(id, checked_by):
    conn = sqlite3.connect(dbAddress)
    cursor = conn.cursor()
    data = [(checked_by, id)]
    sql = """UPDATE reports
            SET checked_by = ?
            WHERE rowid = ?"""
    cursor.executemany(sql, data)
    conn.commit()
    conn.close()
# /ЖАЛОБЫ


# РОЗЫГРЫШ
def insert_raffle_in_bd(code,price,amount):
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(code,price,amount,'0')]
        sql = """INSERT INTO raffle
                    VALUES (?,?,?,?)"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        return True
    except:
        return False
def get_raffle_from_bd(code,uid):
    # 200 - успешно 404 - не найден 201 - использован 300 - исчерпан
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        sql = "SELECT * FROM raffle WHERE code=?"
        cursor.execute(sql, [(code)])
        fetch_data = cursor.fetchone()
        if str(uid) in fetch_data[3]:
            return 201
        else:
            amount = int(fetch_data[2])-1
            if amount < 0:
                return 300
            else:
                used_by = fetch_data[3] + str(uid) + ' '
                data = [(amount, code)]
                sql = """UPDATE raffle
                        SET amount = ?
                        WHERE code = ?"""
                cursor.executemany(sql, data)
                data = [(used_by,code)]
                sql = """UPDATE raffle
                        SET used_by = ?
                        WHERE code = ?"""
                cursor.executemany(sql, data)
                conn.commit()
                conn.close()
                add_num_to_mon_by_id(uid,fetch_data[1])
                return 200
    except:
        return 404
# /РОЗЫГРЫШ