from msilib.schema import Class
from posixpath import split
from re import A
import requests, random, datetime, sys, time, argparse, os
from colorama import Fore, Back, Style
import telebot
from telebot import apihelper
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import datetime
import random

from bd_manage import *
import config

bot = telebot.TeleBot(config.token)

# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
personId = ""
personUname = ""
personName = ""
personAge = ""
personDes = ""
personMon = ""
personLoc = ""
personsId = []

# локации
clubopen = datetime.time(18, 0)
clubclose = datetime.time(6, 0)
schoolopen = datetime.time(8, 0)
schoolclose = datetime.time(20,0)

# казино
kosti_sides = []
kosti_bet = 0
# чаты
productsList = [[],[],[['Вода',3],['Кола',5],['Кофе',5],['Шаурма',8]],[['Вода',3],['Кола',5],['Кофе',5],['Хот-дог',10],['Бургер',10],['Чизбургер',12],['Лаваш',15],['Суп мясной',15],['Суп овощной',13]],[['Вода',3],['Кола',5],['Кофе',5],['Водка',10],['Пиво',8],['Текила',12],['Джин',13],['Вино',12]]]
# /ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ


# ГЛОБАЛЬНЫЕ ФУНКЦИИ
def getProductsList(productsList):
    products = ''
    for product,price in productsList:
        products += product+' - '+str(price)+'\n'
    return products
def getProductsPrice(productsList,product):
    price = 0
    for i in productsList:
        if product.lower() == i[0].lower():
            price = i[1]
    return price
def timedelta(stop,time_now):
    stop = datetime.datetime(int(datetime.datetime.today().strftime('%Y')),int(datetime.datetime.today().strftime('%m')), int(datetime.datetime.today().strftime('%d')), int(stop.strftime('%H')), int(stop.strftime('%M')),0 )
    diff = stop - time_now
    diffins = diff.total_seconds()
    return str(int(divmod(diffins, 3600)[0]))+':'+str(int(divmod(diffins, 60)[0]-(divmod(diffins, 3600)[0]*60)))
# /ГЛОБАЛЬНЫЕ ФУНКЦИИ

# РЕГИСТРАЦИЯ
@bot.message_handler(commands=['start'])
def start(message):
    global personId, personUname,personName,personAge,personDes,personMon,personLoc,personsId
    personId = ""
    personUname = ""
    personName = ""
    personAge = ""
    personDes = ""
    personMon = ""
    personLoc = ""
    personsId = []
    personId = message.from_user.id
    if len(message.text.split()) > 1:
        viewPerson(message)
    else:
        try:
            personData = get_data_from_bd_by_id(personId)
            # bot.reply_to(message, "Привет я кажется тебя помню. \nНапиши /game чтобы начать играть!")
            mainMenu(message)
        except:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Привет! Я хочу создать персонажа!')
            msg = bot.send_message(message.from_user.id, "Привет! \nЯ вижу ты новенький, бегом создавать персонажа :)", reply_markup=markup)	
            bot.register_next_step_handler(msg, createPerson)
def createPerson(message):
    msg = bot.send_message(message.from_user.id, 'Как тебя будут звать? :)')
    bot.register_next_step_handler(msg, setPersonName)
def setPersonName(message):
    global personName
    personName = message.text
    msg = bot.send_message(message.from_user.id, 'Придумай уникальный идентификатор, он должен содержать только буквы английского алфавита и цифры \n(можно использовать такой же username как и у твоего телеграм аккаунта)')
    bot.register_next_step_handler(msg, setPersonUname)
def setPersonUname(message):
    global personUname
    personUname = message.text
    try:
        get_data_from_bd_by_uname(personUname)
        msg = bot.send_message(message.from_user.id, 'Увы, такой username занят, попробуй еще раз :(')
        bot.register_next_step_handler(msg, setPersonUname)
    except:
        msg = bot.send_message(message.from_user.id, 'А теперь придумаем возраст, '+personName+' :)')
        bot.register_next_step_handler(msg, setPersonAge)
def setPersonAge(message):
    global personAge
    try:
        personAge = int(message.text)
        msg = bot.send_message(message.from_user.id, "Придумай описание своего персонажа\n (Текст должен быть не более 255 символов. Учти это!)")
        bot.register_next_step_handler(msg, initPerson)
    except:
        msg = bot.send_message(message.from_user.id, "Мне нужны только цифры (без лишних слов и букв) :(")
        bot.register_next_step_handler(msg, setPersonAge)
def initPerson(message):
    global personDes
    personDes = message.text
    if (insert_data_to_bd(personId,personUname,personName,personAge,personDes,100,0)):
        print('-----------new person----------- 120')
        print(personId,personUname,personName,personAge,personDes)
        bot.reply_to(message, "Отлично, персонаж создан! Напишите /game чтобы начать играть!")
    else:
        bot.reply_to(message, "Возникла ошибка! Напишите /start чтобы попробовать еще раз!")
# /РЕГИСТРАЦИЯ


# КЛАВИАТУРЫ
def mainMenu_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add('Профиль','Локации', 'Панель заработок')
	return markup
def chat_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('!меню', '!помощь')
    return markup
def relationShip_kb(uname,user):
    friends, enemies = get_friends_and_enemies_list(uname)
    markup = telebot.types.InlineKeyboardMarkup()
    if user in friends:
        markup.add(telebot.types.InlineKeyboardButton(text = 'Удалить из друзей', callback_data ='relationship delfriend '+user))
    elif not(user in enemies):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Добавить в друзья', callback_data ='relationship addfriend '+user))
    if (user in enemies):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Убрать из ЧС', callback_data ='relationship delenemy '+user))
    elif not(user in friends):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Отправить в ЧС', callback_data ='relationship addenemy '+user))
    return markup
def casinoMonetkaBet_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = '50', callback_data ='casino monetka bet 50'))
    markup.add(telebot.types.InlineKeyboardButton(text = '100', callback_data ='casino monetka bet 100'))
    markup.add(telebot.types.InlineKeyboardButton(text = '500', callback_data ='casino monetka bet 500'))
    markup.add(telebot.types.InlineKeyboardButton(text = '1000', callback_data ='casino monetka bet 1000'))
    return markup
def casinoMonetkaSide_kb(bet):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Орёл', callback_data ='casino monetka '+str(bet)+' orel'))
    markup.add(telebot.types.InlineKeyboardButton(text = 'Решка', callback_data ='casino monetka '+str(bet)+' reshka'))
    return markup
def casinoKostiBet_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = '50', callback_data ='casino kosti bet 50'))
    markup.add(telebot.types.InlineKeyboardButton(text = '100', callback_data ='casino kosti bet 100'))
    markup.add(telebot.types.InlineKeyboardButton(text = '500', callback_data ='casino kosti bet 500'))
    markup.add(telebot.types.InlineKeyboardButton(text = '1000', callback_data ='casino kosti bet 1000'))
    return markup
def casinoKostiSide_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = '1', callback_data ='casino kosti side 1'),telebot.types.InlineKeyboardButton(text = '2', callback_data ='casino kosti side 2'),telebot.types.InlineKeyboardButton(text = '3', callback_data ='casino kosti side 3'))
    markup.add(telebot.types.InlineKeyboardButton(text = '4', callback_data ='casino kosti side 4'),telebot.types.InlineKeyboardButton(text = '5', callback_data ='casino kosti side 5'),telebot.types.InlineKeyboardButton(text = '6', callback_data ='casino kosti side 6'))
    markup.add(telebot.types.InlineKeyboardButton(text = 'Готово', callback_data ='casino kosti ok'))
    return markup
# /КЛАВИАТУРЫ


# КОЛБЕКИ
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    if call.data.split()[0] == 'relationship':
        func = call.data.split()[1]
        user = call.data.split()[2]
        me = get_data_from_bd_by_id(call.message.chat.id)
        me = me[1]
        if func == 'addfriend':
            status = add_friend(me,user)
            if status == 200:
                bot.answer_callback_query(callback_query_id=call.id, text="Друг добавлен", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,user))
        elif func == 'addenemy':
            status = add_enemy(me,user)
            if status == 300:
                bot.answer_callback_query(callback_query_id=call.id, text="Отправлен в ЧС", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,user))
        elif func == 'delfriend':
            status = del_friend(me,user)
            if status == 201:
                bot.answer_callback_query(callback_query_id=call.id, text="Друг удален", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,user))
        elif func == 'delenemy':
            status = del_enemy(me,user)
            if status == 301:
                bot.answer_callback_query(callback_query_id=call.id, text="Убран из ЧС", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,user))
    if call.data.split()[0] == 'casino':
        uid = call.message.chat.id
        data = get_data_from_bd_by_id(uid)
        gametype = call.data.split()[1]
        if gametype == 'monetka':
            if call.data.split()[2] == 'bet':
                bet = int(call.data.split()[3])
                if bet > data[5]:
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Не достаточно средств, проверьте баланс')
                else:
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text="А теперь сторону...", reply_markup=casinoMonetkaSide_kb(bet))
            else:
                bet = int(call.data.split()[2])
                side = call.data.split()[3]
                rnd = random.randint(0,1)
                sides = ['orel','reshka']
                if sides[rnd] == side:
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Поздравляю, Вы выиграли '+str(bet)+' RPCoin\nВаш баланс: '+str(data[5]+bet))
                    update_mon_bd(get_uname_by_id(uid),data[5]+bet)
                else:
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Увы и ах. Вы потеряли '+str(bet)+' RPCoin\nВаш баланс: '+str(data[5]-bet))
                    update_mon_bd(get_uname_by_id(uid),data[5]-bet)

        # print(call.data.split(),kosti_bet,kosti_sides)
        if gametype == 'kosti':
            if call.data.split()[2] == 'bet':
                global kosti_sides, kosti_bet
                kosti_sides = []
                kosti_bet = 0
                if int(call.data.split()[3]) > data[5]:
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Не достаточно средств, проверьте баланс')
                else:
                    kosti_bet = int(call.data.split()[3])
                    bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Ваша ставка: '+str(kosti_bet), reply_markup=casinoKostiSide_kb())
            if call.data.split()[2] == 'side':
                if call.data.split()[3] in kosti_sides:
                    kosti_sides.remove(call.data.split()[3])
                else:
                    kosti_sides.append(call.data.split()[3])
                kst = ''
                for i in kosti_sides:
                    kst += str(i)+' '
                bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Ваша ставка: '+str(kosti_bet)+'\nВаши позиции: '+kst, reply_markup=casinoKostiSide_kb())
            if call.data.split()[2] == 'ok':
                if len(kosti_sides) == 0:
                    bot.answer_callback_query(callback_query_id=call.id, text="Выберите хотя бы одну позицию", show_alert=True)
                else:
                    rnd = str(random.randint(1,6))
                    if rnd in kosti_sides:
                        mn = 6 / len(kosti_sides)
                        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Вы выиграли: '+str(round(int(kosti_bet)*mn))+' RPCoin\nВаш баланс: '+str(data[5]+(round(int(kosti_bet)*mn)-kosti_bet)))
                        update_mon_bd(get_uname_by_id(uid),data[5]+(round(int(kosti_bet)*mn)-kosti_bet))
                    else:
                        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text='Вы потеряли: '+str(kosti_bet)+' RPCoin\nВаш баланс: '+str(data[5]-kosti_bet))
                        update_mon_bd(get_uname_by_id(uid),data[5]-kosti_bet)
# /КОЛБЕКИ  




# ИГРА
@bot.message_handler(commands=['game'])
def mainMenu(message):
    error = 0
    try:
        data = get_data_from_bd_by_id(message.from_user.id)
    except:
        bot.send_message(message.from_user.id,'У тебя кажется нет персонажа.\nВведи /start')
        error = 1
    if error == 0:
        global personId,personUname,personName,personAge,personDes,personMon,personLoc
        personId = data[0]
        personUname = data[1]
        personName = data[2]
        personAge = data[3]
        personDes = data[4]
        personMon = data[5]
        personLoc = data[6]

        personsId = get_persons_in_loc_bd(personLoc)
        if personLoc != 0:
            for i in range(len(personsId)):
                if personsId[i][0] == personId:
                    continue
                try:
                    bot.send_message(personsId[i][0],'<u>'+personName+" покинул локацию</u>", parse_mode="HTML")
                except:
                    print(str(personsId[i][0])+"bot was blocked by that user 182")
            update_loc_bd(message.from_user.id, "0")

        msg = bot.send_message(message.from_user.id, "Главное меню:", reply_markup=mainMenu_kb())
        bot.register_next_step_handler(msg, mainMenuHandler)
def mainMenuHandler(message):
    global personId,personUname,personName,personAge,personDes,personMon,personLoc
    if message.text == 'Профиль':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Редактировать профиль','Друзья и ЧС', 'Назад')
        msg = bot.send_message(message.from_user.id, "Имя: "+personName+"\nUsername: "+personUname+"\nВозраст: "+str(personAge)+"\nОписание: "+personDes+"\nБаланс: "+str(personMon), reply_markup=markup)
        bot.register_next_step_handler(msg, profileHandler)
    elif message.text == 'Локации':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        time_now = datetime.datetime.now().time()
        locationlist = ['Дом', 'В гости', 'Улица', 'Парк', 'Кафе']
        if (6 < personAge <= 18) or ((schoolopen<=time_now) or (schoolclose>time_now)):
            locationlist.append('Школа')
        if (18 <= personAge) or((clubopen<=time_now) or (clubclose>time_now)):
            locationlist.append('Клуб')
        if 18 <= personAge:
            locationlist.append('Казино')
        locationlist.append('Назад')
        for i in locationlist:
            markup.add(i)
        msg = bot.send_message(message.from_user.id, "Выберите локацию", reply_markup=markup)
        bot.register_next_step_handler(msg, locationHandler)
    else:
        bot.send_message(message.from_user.id, "Нет такого пункта меню")
        mainMenu(message)
# /ИГРА



# ПРОФИЛЬ
def profileHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Редактировать профиль':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Имя и Фамилию', 'Username', 'Возраст', 'Описание', 'Назад')
        msg = bot.send_message(message.from_user.id, "Что хотите редактировать?", reply_markup=markup)
        bot.register_next_step_handler(msg, profileRegHandler)
    elif message.text == 'Друзья и ЧС':
        friends, enemies = get_friends_and_enemies_list(personUname)
        friendslist = ''
        enemieslist = ''
        for i in friends.split():
            data = get_data_from_bd_by_uname(i)
            friendslist += '<a href="t.me/SmrkRP_bot?start='+data[1]+'">['+data[1]+'] '+data[2]+'</a>\n'
        for i in enemies.split():
            data = get_data_from_bd_by_uname(i)
            enemieslist += '<a href="t.me/SmrkRP_bot?start='+data[1]+'">['+data[1]+'] '+data[2]+'</a>'
        bot.send_message(message.from_user.id, "Друзья:\n"+friendslist, parse_mode="HTML",disable_web_page_preview = True)
        bot.send_message(message.from_user.id, "В черном списке:\n"+enemieslist, parse_mode="HTML",disable_web_page_preview = True, reply_markup=chat_kb())
def viewPerson(message, user_id=0):
    try:
        data = get_data_from_bd_by_uname(message.text.split()[1])
        user_id = message.from_user.id
    except:
        data = get_data_from_bd_by_uname(message)
    if data == 0:
        bot.send_message(user_id, 'Такого персонажа нет в базе данных')
    else:
        if data[0] == user_id:
            bot.send_message(user_id, 'Вы можете посмотреть свой профиль с помощью пункта меню "Профиль" в главном меню')
        else:
            try:
                bot.send_message(user_id, 'Username: ' + data[1] + '\nИмя: '+data[2] + '\nВозраст: '+str(data[3]) + '\nОписание: '+data[4],reply_markup = relationShip_kb(get_uname_by_id(user_id), data[1]))
            except:
                bot.send_message(user_id, 'Такого персонажа нет в базе данных')
def profileRegHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Имя и Фамилию':
        msg = bot.send_message(message.from_user.id, "Введите новое имя: ")
        bot.register_next_step_handler(msg, changeName)
    elif message.text == 'Username':
        msg = bot.send_message(message.from_user.id, "Введите новый username: ")
        bot.register_next_step_handler(msg, changeUname)
    elif message.text == 'Возраст':
        msg = bot.send_message(message.from_user.id, "Введите новый возраст: ")
        bot.register_next_step_handler(msg, changeAge)
    elif message.text == 'Описание':
        msg = bot.send_message(message.from_user.id, "Введите новое описание: ")
        bot.register_next_step_handler(msg, changeDes)
def changeName(message):
    val = message.text
    usid = message.from_user.id
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(val, usid)]
        sql = """UPDATE persons 
                SET fio = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, "Имя успешно изменено")
    except:
        bot.send_message(message.from_user.id, "Произошла ошибка! Попробуйте позже!")
    mainMenu(message)
def changeUname(message):
    val = message.text
    usid = message.from_user.id
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(val, usid)]
        sql = """UPDATE persons 
                SET uname = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        sql = """UPDATE relationship
                SET uname = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, "Username успешно изменен")
        mainMenu(message)
    except:
        bot.send_message(message.from_user.id, "Такой username уже занят!")
        bot.register_next_step_handler(message, changeUname)
def changeAge(message):
    val = message.text
    usid = message.from_user.id
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(val, usid)]
        sql = """UPDATE persons 
                SET age = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, "Возраст успешно изменен")
    except:
        bot.send_message(message.from_user.id, "Произошла ошибка! Попробуйте позже!")
    mainMenu(message)
def changeDes(message):
    val = message.text
    usid = message.from_user.id
    try:
        conn = sqlite3.connect(dbAddress)
        cursor = conn.cursor()
        data = [(val, usid)]
        sql = """UPDATE persons 
                SET des = ?
                WHERE id = ?"""
        cursor.executemany(sql, data)
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, "Описание успешно изменено")
    except:
        bot.send_message(message.from_user.id, "Произошла ошибка! Попробуйте позже!")
    mainMenu(message)
# /ПРОФИЛЬ




# ЛОКАЦИИ
def locationHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Дом':
        bot.send_message(message.from_user.id, "Локация: Ваш дом"+"\n", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, message.from_user.id)
        personsId = get_persons_in_loc_bd(message.from_user.id)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" пришел домой</u>", parse_mode="HTML")
    elif message.text == 'В гости':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Назад')
        msg = bot.send_message(message.from_user.id, "Впишите username персонажа к которому вы хотите пойти в гости", reply_markup=markup)
        bot.register_next_step_handler(msg, visitsHandler)
    elif message.text == 'Улица': 
        bot.send_message(message.from_user.id, "Локация: Улица\nБольшая широкая улица кишащая толпами людей которые вечно куда-то спешат", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "2")
        personsId = get_persons_in_loc_bd(2)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Улица'</u>", parse_mode="HTML")
    elif message.text == 'Парк':
        bot.send_message(message.from_user.id, "Локация: Парк\nДовольно спокойное место, в самый раз чтобы отдохнуть от городской суеты", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "3")
        personsId = get_persons_in_loc_bd(3)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],personName+" вошел в локацию 'Парк'")
    elif message.text == 'Кафе':
        bot.send_message(message.from_user.id, "Локация: Кафе\nНебольшое кафе находящееся недалеко от вашего дома. Ни чем не приметная, но такая уютная", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "4")
        personsId = get_persons_in_loc_bd(4)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Кафе'</u>", parse_mode="HTML")
    elif message.text == 'Клуб':
        bot.send_message(message.from_user.id, "Локация: Клуб\nС самого входа слышно музыку которая так и тянет танцевать!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "5")
        personsId = get_persons_in_loc_bd(5)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Клуб'</u>", parse_mode="HTML")
    elif message.text == 'Школа':
        bot.send_message(message.from_user.id, "Локация: Школа\nЗнания - сила!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "6")
        personsId = get_persons_in_loc_bd(6)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Школа'</u>", parse_mode="HTML")
    elif message.text == 'Казино':
        bot.send_message(message.from_user.id, "Локация: Казино\nУмей во время остановиться!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "7")
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('!монетка','!кости')
        markup.add('!меню','!помощь')
        bot.send_message(message.from_user.id, "!монетка - обычная игра с шансом 50%\n!кости - шанс выиграть 1 к 6, но и приз будет с коэффициентом 6х", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Нажми на пункт меню!")
        mainMenu(message)
def visitsHandler(message):
    if personUname == message.text:
        bot.send_message(message.from_user.id, 'Домой вы можете попасть с помощью пункта меню "Дом" в меню локаций')
        mainMenu(message)
    else:
        try:
            data = get_data_from_bd_by_uname(message.text)
            friends, enemies = get_friends_and_enemies_list(message.text)
        except:
            bot.send_message(message.from_user.id, "Такого персонажа нет в нашей базе данных, проверьте корректность введеного username")
            mainMenu(message)
        
        if not(personUname in enemies):
            if personUname in friends:
                update_loc_bd(message.from_user.id, data[0])
                bot.send_message(message.from_user.id, "Локация: Дом пользователя "+data[2],reply_markup=chat_kb())
                bot.send_message(data[0], 'Персонаж ['+personUname+'] '+personName+' пришел к вам домой',reply_markup=chat_kb())
            else:
                bot.send_message(message.from_user.id, "Вас нет в друзьях у данного персонажа")
                mainMenu(message)
        else:
            bot.send_message(message.from_user.id, "Вы в ЧС у данного персонажа")
            mainMenu(message)
# /ЛОКАЦИИ




# ЧАТЫ
@bot.message_handler(content_types=['text'])
def messagesHandler(message):
    error = 0
    try:
        data = get_data_from_bd_by_id(message.from_user.id)
    except:
        bot.send_message(message.from_user.id,'У тебя кажется нет персонажа.\nВведи /start')
        error = 1
    if error == 0:
        personId = data[0]
        personUname = data[1]
        personName = data[2]
        personAge = data[3]
        personDes = data[4]
        personMon = data[5]
        personLoc = data[6]
        if message.text[0] == '!':
            splitMessage = message.text.split()
            if message.text.lower() == '!меню':
                mainMenu(message)
            elif splitMessage[0].lower() == '!передать':
                i = True
                try:
                    int(splitMessage[2])
                except:
                    i = False
                if (len(splitMessage) <= 2) or (i == False):
                    bot.send_message(personId,'Формат ввода команды: !Передать [username адресата] [сумма перевода]')
                else:
                    if int(splitMessage[2]) <= 0:
                        bot.send_message(personId,'Введите корректную сумму')
                    else:
                        if splitMessage[1] == personUname:
                            bot.send_message(personId,'Самому себе деньги переводить нет смысла!')
                        else:
                            clientdata = get_data_from_bd_by_uname(splitMessage[1])
                            if int(personMon)-int(splitMessage[2])>0:
                                update_mon_bd(splitMessage[1], int(clientdata[5])+int(splitMessage[2]))
                                update_mon_bd(personUname, int(personMon)-int(splitMessage[2]))
                                bot.send_message(personId,'Вы перевели деньги персонажу '+clientdata[1]+' на сумму '+splitMessage[2])
                                bot.send_message(get_id_by_uname(splitMessage[1]),'Персонаж '+personName+' перевел вам '+splitMessage[2]+" RPCoin")
                            else:
                                bot.send_message(personId,'Не хватает денег')
            elif message.text.lower() == '!баланс':
                bot.send_message(personId,'Ваш баланс: '+str(personMon)+' RPCoin')
            elif message.text.lower() == '!ктоздесь':
                personsId = get_persons_in_loc_bd(personLoc)
                personlist = ''
                for i in personsId:
                    personlist += '<a href="t.me/SmrkRP_bot?start='+i[1]+'">'+i[2]+'</a>\n'
                bot.send_message(personId,'В локации находятся: \n'+personlist, parse_mode="HTML",disable_web_page_preview = True)
            elif message.text.lower() == '!время':
                time_now = datetime.datetime.now().time()
                bot.send_message(personId,'Время: '+time_now.strftime('%H:%M'))
            elif splitMessage[0].lower() == '!купить':
                if personLoc in [2,3,4]:
                    if (len(splitMessage) == 1):
                        bot.send_message(personId,'Формат ввода команды: !Купить [вид товара]')
                        bot.send_message(personId,'Виды товара доступные для покупки в данной локации')
                        bot.send_message(personId,getProductsList(productsList[personLoc]))
                    else:
                        product = splitMessage[1]
                        price = getProductsPrice(productsList[personLoc],product)
                        if price == 0:
                            bot.send_message(personId,'Такого товара нет(Проверьте правильно написания наименования товара)')
                        else:
                            if int(personMon)-int(price)>0:
                                update_mon_bd(personId, int(personMon)-int(price))
                                bot.send_message(personId,'Вы купили '+product+' на сумму '+str(price))
                            else:
                                bot.send_message(splitMessage[1],'Не хватает денег')
                else:
                    bot.send_message(personId,'В данной локации эта команда не доступна!')
            elif splitMessage[0].lower() == '!профиль':
                if len(splitMessage) < 2:
                    bot.send_message(personId,'Формат ввода команды: \n!Профиль [username]')
                else:
                    viewPerson(splitMessage[1],personId)
            elif message.text.lower() == '!помощь':
                bot.send_message(personId,"""
<code>!меню</code> - возвращает вас в главное меню\n
<code>!передать</code> [username] [сумма] - передает деньги другому персонажу\n
<code>!баланс</code> - показывает ваш баланс\n
<code>!ктоздесь</code> - показывает всех персонажей которые находятся в одной локации что и вы\n
<code>!время</code> - показывает текущее время\n
<code>!профиль</code> [username] - показывает профиль персонажа.\n
<code>!помощь</code> - <tg-spoiler>выводит данный текст</tg-spoiler>""",parse_mode="HTML")
            elif message.text.lower() == '!монетка':
                if personLoc == 7:
                    bot.send_message(message.from_user.id, "Выбери ставку", reply_markup=casinoMonetkaBet_kb())
            elif message.text.lower() == '!кости':
                if personLoc == 7:
                    bot.send_message(message.from_user.id, "Выбери ставку", reply_markup=casinoKostiBet_kb())
        else:
            if personLoc == 0:
                bot.send_message(personId,'Что-то поломалось! Вы перенаправлены в главное меню!')
                mainMenu(message)
            else:
                personsId = get_persons_in_loc_bd(personLoc)
                myfriends, myenemies = get_friends_and_enemies_list(personUname)
                for i in personsId:
                    urfriends, urenemies = get_friends_and_enemies_list(i[1])
                    if i[0] == personId:
                        continue
                    if  personUname in urenemies:
                        bot.send_message(i[0],'<a href="t.me/SmrkRP_bot?start='+personUname+'">'+personName+'(ЧС)</a>: <tg-spoiler>'+message.text+'</tg-spoiler>', parse_mode="HTML",disable_web_page_preview = True)
                    else:
                        if not(i[1] in myenemies):
                        #     bot.send_message(i[0],'<a href="t.me/SmrkRP_bot?start='+personUname+'"> Вы не видите данное сообщение потому что '+personName+' добавил вас в ЧС</a>', parse_mode="HTML",disable_web_page_preview = True)
                        # else:
                            try:
                                bot.send_message(i[0],'<b>'+'<a href="t.me/SmrkRP_bot?start='+personUname+'">'+personName+'</a></b>: '+message.text, parse_mode="HTML",disable_web_page_preview = True)
                            except:
                                print(i[0],'не получается отправить сообщение этому пользователю')
        
# /ЧАТЫ
