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

personId = ""
personName = ""
personAge = ""
personDes = ""
personMon = ""
personLoc = ""
personsId = []

def sayHello_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add('Привет! Я хочу создать персонажа!')
	return markup
def choice_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add('Да!','Нет!')
	return markup
def down_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add('Назад')
	return markup

# РЕГИСТРАЦИЯ
@bot.message_handler(commands=['start'])
def start(message):
    global personId
    personId = message.from_user.id
    try:
        personData = get_data_from_bd(personId)
        bot.reply_to(message, "Привет я кажется тебя помню. Напиши /game чтобы начать играть!")
    except:
        msg = bot.send_message(message.from_user.id, "Привет! \n Тебя нет в моей базе данных, бегом создавать персонажа :)", reply_markup=sayHello_kb())	
        bot.register_next_step_handler(msg, createPerson)
def createPerson(message):
	if message.text == 'Назад':
		start(message)
	elif message.text == 'Привет! Я хочу создать персонажа!':
		msg = bot.send_message(message.from_user.id, 'Введи Имя и Фамилию персонажа :)')
		bot.register_next_step_handler(msg, setPersonName)
	else:
		msg = bot.send_message(message.from_user.id, "Давай придумаем имя персонажу!")
		bot.register_next_step_handler(msg, setPersonName)
def setPersonName(message):
    global personName
    if message.text:
        personName = message.text
        msg = bot.send_message(message.from_user.id, 'Ты уверен что твоего персонажа будут так звать? :)', reply_markup=choice_kb())
        bot.register_next_step_handler(msg, setPersonName2)
    else:
        msg = bot.send_message(message.from_user.id, "Разве трудно просто придумать имя? :(")
        bot.register_next_step_handler(msg, setPersonName)
def setPersonName2(message):
    if message.text == 'Нет!':
        createPerson(message)
        bot.send_message(message.from_user.id, 'Введи Имя и Фамилию персонажа :)')
    elif message.text == 'Да!':
        msg = bot.send_message(message.from_user.id, 'А теперь придумаем возраст! '+message.text+'? :)', reply_markup=down_kb())
        bot.register_next_step_handler(msg, setPersonAge)
    else:
        msg = bot.send_message(message.from_user.id, "Какой возраст будет у твоего персонажа?")
        bot.register_next_step_handler(msg, setPersonAge)
def setPersonAge(message):
    global personAge
    if message.text == 'Назад':
        setPersonName2(message)
    elif message.text:
        try:
            personAge = int(message.text)
            msg = bot.send_message(message.from_user.id, "Перейдем к последнему пункту! Придумай описание своего персонажа (Прошлое персонажа,особенности характера, описание внешности", reply_markup=down_kb())
            bot.register_next_step_handler(msg, setPersonDes)
        except:
            msg = bot.send_message(message.from_user.id, "Мне нужны только цифры (без лишних слов и букв) :(")
            bot.register_next_step_handler(msg, setPersonAge)
def setPersonDes(message):
    global personDes
    if message.text == 'Назад':
        setPersonAge(message)
    elif message.text:
        personDes = message.text
        msg = bot.send_message(message.from_user.id, "Доволен описанием? Можем заканчивать?", reply_markup=choice_kb())
        bot.register_next_step_handler(msg, setPersonDes2)
def setPersonDes2(message):
    if message.text == 'Нет!':
        setPersonDes(message)
    elif message.text == 'Да!':
        house = 0
        mon_coming = 0
        if personAge < 18:
            mon_coming = random.randint(2,7)*10
            rndm = 0
            rndm = random.random()
            if rndm > 0.5:
                house = 50
            else:
                house = 100
        if (insert_data_to_bd(personId,personName,personAge,personDes,house,mon_coming)):
            print(personId,personName,personAge,personDes,house,mon_coming)
            update_date_bd(message.from_user.id, datetime.date.today().strftime('%d %m %Y'))
            bot.reply_to(message, "Отлично, персонаж создан! Напишите /game чтобы начать играть!")
        else:
            bot.reply_to(message, "Возникла ошибка! Напишите /start чтобы попробовать еще раз!")
# /РЕГИСТРАЦИЯ

def mainMenu_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add('Профиль','Локации', 'Панель заработок')
	return markup
def chat_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('!Меню')
    return markup

def timedelta(stop,time_now):
    stop = datetime.datetime(int(datetime.datetime.today().strftime('%Y')),int(datetime.datetime.today().strftime('%m')), int(datetime.datetime.today().strftime('%d')), int(stop.strftime('%H')), int(stop.strftime('%M')),0 )
    diff = stop - time_now
    diffins = diff.total_seconds()
    return str(int(divmod(diffins, 3600)[0]))+':'+str(int(divmod(diffins, 60)[0]-(divmod(diffins, 3600)[0]*60)))
    
clubopen = datetime.time(18, 0)
clubclose = datetime.time(7, 0)
# ИГРА
@bot.message_handler(commands=['game'])
def mainMenu(message):
    error = 0
    try:
        data = get_data_from_bd(message.from_user.id)
    except:
        bot.send_message(message.from_user.id,'У тебя кажется нет персонажа.\nВведи /start')
        error = 1
    if error == 0:
        global personId,personName,personAge,personDes,personMon,personLoc
        personId = data[0]
        personName = data[1]
        personAge = data[2]
        personDes = data[3]
        personMon = data[4]
        personLoc = data[5]

        personsId = get_persons_in_loc_bd(personLoc)
        if personLoc != 0:
            for i in range(len(personsId)):
                if personsId[i][0] == personId:
                    continue
                try:
                    bot.send_message(personsId[i][0],'<u>'+personName+" покинул локацию</u>", parse_mode="HTML")
                except:
                    print(str(personsId[i][0])+"bot was blocke by th user")
            update_loc_bd(message.from_user.id, "0")

        msg = bot.send_message(message.from_user.id, "Главное меню:", reply_markup=mainMenu_kb())
        bot.register_next_step_handler(msg, mainMenuHandler)
def mainMenuHandler(message):
    global personId,personName,personAge,personDes,personMon,personLoc
    
    if message.text == 'Профиль':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Редактировать профиль', 'Назад')
        msg = bot.send_message(message.from_user.id, "Имя и Фамилия: "+personName+"\nВозраст: "+str(personAge)+"\nОписание: "+personDes+"\nБаланс: "+str(personMon), reply_markup=markup)
        bot.register_next_step_handler(msg, profileHandler)
    elif message.text == 'Локации':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Дом', 'Пойти в гости', 'Улица', 'Парк', 'Кафе', 'Клуб', 'Назад')
        msg = bot.send_message(message.from_user.id, "Выберите локацию", reply_markup=markup)
        bot.register_next_step_handler(msg, locationHandler)
    else:
        bot.send_message(message.from_user.id, "Нажми на пункт меню!")
        mainMenu(message)]

def locationHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Дом':
        propdata = get_prop_data_from_bd(message.from_user.id)
        if propdata[3] > 0:
            if propdata[3] == 50:
                hellotext = 'Войдя в помещение которое трудно назвать домом вы почуствовали противный запах сырости. Хотелось побыстрей унести ноги из этого богом забытого места'
            elif propdata[3] == 100:
                hellotext = 'Войдя в помещение вы увидели большие панорамные окна с видом на город. Было заметно что человек проживающий тут любит себя.'
            bot.send_message(message.from_user.id, "Локация: Дом №"+str(message.from_user.id)+"\n"+hellotext, reply_markup=chat_kb())
            update_loc_bd(message.from_user.id, message.from_user.id)
            personsId = get_persons_in_loc_bd(message.from_user.id)
            for i in range(len(personsId)):
                if personsId[i][0] == personId:
                    continue
                bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Дом'</u>", parse_mode="HTML")
        else:
            bot.send_message(message.from_user.id,"У вас нет дома! Приобретите его во вкладке 'Панель заработок'")
            mainMenu(message)
    elif message.text == 'Пойти в гости':
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Назад')
        msg = bot.send_message(message.from_user.id, "Впишите id персонажа к кому вы хотите пойти в гости", reply_markup=markup)
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
        bot.send_message(message.from_user.id, "Локация: Кафе\nНебольшое кафе находящееся недалеко от вашего дома. Ни чем не приметная но такая уютная", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "4")
        personsId = get_persons_in_loc_bd(4)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Кафе'</u>", parse_mode="HTML")
    elif message.text == 'Клуб':
        time_now = datetime.datetime.now().time()
        if ((clubopen<=time_now) or (clubclose>time_now)):
            data = get_data_from_bd(message.from_user.id)
            if data[2] >= 18:
                bot.send_message(message.from_user.id, "Локация: Клуб\nС самого входа слышно музыку которая так и тянет танцевать!", reply_markup=chat_kb())
                update_loc_bd(message.from_user.id, "5")
                personsId = get_persons_in_loc_bd(5)
                for i in range(len(personsId)):
                    if personsId[i][0] == personId:
                        continue
                    bot.send_message(personsId[i][0],'<u>'+personName+" вошел в локацию 'Клуб'</u>", parse_mode="HTML")
            else:
                bot.send_message(message.from_user.id,"Вам нет 18 лет чтобы посещать клуб!")
                mainMenu(message)
        else:
            bot.send_message(message.from_user.id,"Клуб работает с 18:00 до 7:00 \nА время сейчас: "+time_now.strftime('%H:%M'))
            mainMenu(message)
    else:
        bot.send_message(message.from_user.id, "Нажми на пункт меню!")
        mainMenu(message)
def visitsHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    else:
        isint = 0
        try:
            visidID = int(message.text)
            isint = 1
        except:
            bot.send_message(message.from_user.id, "Мне нужен только ID цифрами и ничего лишнего")
            mainMenu(message)
        if isint:
            visidID = int(message.text)
            propdata = get_prop_data_from_bd(visidID)
            if propdata[3] > 0:
                if propdata[3] == 50:
                    hellotext = 'Войдя в помещение которое трудно назвать домом вы почуствовали противный запах сырости. Хотелось побыстрей унести ноги из этого богом забытого места'
                elif propdata[3] == 100:
                    hellotext = 'Войдя в помещение вы увидели большие панорамные окна с видом на город. Было заметно что человек проживающий тут любит себя.'
                bot.send_message(message.from_user.id, "Локация: Дом №"+str(message.from_user.id)+"\n"+hellotext, reply_markup=chat_kb())
                update_loc_bd(message.from_user.id, visidID)
                personsId = get_persons_in_loc_bd(visidID)
                for i in range(len(personsId)):
                    if personsId[i][0] == personId:
                        continue
                    bot.send_message(personsId[i][0],personName+" вошел в локацию 'Дом'")
            else:
                bot.send_message(message.from_user.id,"У персонажа нет дома!")
                mainMenu(message)
def profileHandler(message):
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Редактировать профиль':
        bot.send_message(message.from_user.id, "Имейте ввиду что изменения имеют определенную цену!\nИмя и фамилия - 1000\nВозраст - 1000000\nОписание - 100")
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Имя и Фамилию', 'Возраст', 'Описание', 'Назад')
        msg = bot.send_message(message.from_user.id, "Что хотите редактировать?", reply_markup=markup)
        bot.register_next_step_handler(msg, progileRedHandler)
def progileRedHandler(message):
    personData = get_data_from_bd(message.from_user.id)
    if message.text == 'Назад':
        mainMenu(message)
    elif message.text == 'Имя и Фамилию':
        if personData[4] >= 1000:
            msg = bot.send_message(message.from_user.id, "Введите новое имя: ")
            bot.register_next_step_handler(msg, changeName)
        else:
            bot.send_message(message.from_user.id, "У вас не достаточно денег на балансе")
            mainMenu(message)
    elif message.text == 'Возраст':
        if personData[4] >= 1000000:
            msg = bot.send_message(message.from_user.id, "Введите новый возраст: ")
            bot.register_next_step_handler(msg, changeAge)
        else:
            bot.send_message(message.from_user.id, "У вас не достаточно денег на балансе")
            mainMenu(message)
    elif message.text == 'Описание':
        if personData[4] >= 100:
            msg = bot.send_message(message.from_user.id, "Введите новое описание: ")
            bot.register_next_step_handler(msg, changeDes)
        else:
            bot.send_message(message.from_user.id, "У вас не достаточно денег на балансе")
            mainMenu(message)
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
        bot.send_message(message.from_user.id, "Имя и Фамилия успешно изменены")
    except:
        bot.send_message(message.from_user.id, "Произошла ошибка! Попробуйте позже!")
    mainMenu(message)
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
# /ИГРА
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
productsList = [[],[],[['Вода',3],['Кола',5],['Кофе',5],['Шаурма',8]],[['Вода',3],['Кола',5],['Кофе',5],['Хот-дог',10],['Бургер',10],['Чизбургер',12],['Лаваш',15],['Суп мясной',15],['Суп овощной',13]],[['Вода',3],['Кола',5],['Кофе',5],['Водка',10],['Пиво',8],['Текила',12],['Джин',13],['Вино',12]]]
# ЧАТЫ
@bot.message_handler(content_types=['text'])
def messagesHandler(message):
    error = 0
    try:
        data = get_data_from_bd(message.from_user.id)
    except:
        bot.send_message(message.from_user.id,'У тебя кажется нет персонажа.\nВведи /start')
        error = 1
    if error == 0:
        personId = data[0]
        personName = data[1]
        personAge = data[2]
        personDes = data[3]
        personMon = data[4]
        personLoc = data[5]
        prop_data = get_prop_data_from_bd(message.from_user.id)
        if not(prop_data[5] == ''):
            time_work = prop_data[5].split('-')
            start_work = datetime.datetime.strptime(time_work[0], '%H:%M').time()
            stop_work = datetime.datetime.strptime(time_work[1], '%H:%M').time()
            time_now = datetime.datetime.now().time()
            if (start_work<=time_now<stop_work):
                bot.send_message(message.from_user.id,'Вы сейчас на работе и не можете находиться в локациях')
                mainMenu(message)
        if message.text[0] == '!':
            slpitMessage = message.text.split()
            if message.text.lower() == '!меню':
                mainMenu(message)
            elif slpitMessage[0].lower() == '!передать':
                if (len(slpitMessage) == 2):
                    bot.send_message(personId,'Формат ввода команды: !Передать (id адресата) (сумма перевода)')
                else:
                    try:
                        if int(slpitMessage[1]) == int(personId):
                            bot.send_message(personId,'Самому себе деньги переводить нет смысла!')
                        else:
                            clientdata = get_data_from_bd(int(slpitMessage[1]))
                            if int(personMon)-int(slpitMessage[2])>0:
                                update_mon_bd(slpitMessage[1], int(clientdata[4])+int(slpitMessage[2]))
                                update_mon_bd(personId, int(personMon)-int(slpitMessage[2]))
                                bot.send_message(personId,'Вы перевели деньги персонажу '+clientdata[1]+' на сумму '+slpitMessage[2])
                                bot.send_message(slpitMessage[1],'Персонаж '+personName+' перевел вам деньги на сумму'+slpitMessage[2])
                            else:
                                bot.send_message(slpitMessage[1],'Не хватает денег')
                    except:
                        bot.send_message(personId,'Произошла ошибка! Повторите запрос.')
            elif message.text.lower() == '!баланс':
                bot.send_message(personId,'Ваш баланс: '+str(personMon))
            elif message.text.lower() == '!ктоздесь':
                personsId = get_persons_in_loc_bd(personLoc)
                personlist = ''
                for i in range(len(personsId)):
                    personlist += personsId[i][1]+', '
                personlist = personlist[0:-2]
                bot.send_message(personId,'В локации находятся: \n'+personlist)
            elif message.text.lower() == '!мойid':
                bot.send_message(personId,'Твой ID: '+str(personId))
            elif message.text.lower() == '!время':
                time_now = datetime.datetime.now().time()
                bot.send_message(personId,'Время: '+time_now.strftime('%H:%M'))
            elif slpitMessage[0].lower() == '!купить':
                if personLoc in [2,3,4]:
                    if (len(slpitMessage) == 1):
                        bot.send_message(personId,'Формат ввода команды: !Купить (вид товара)')
                        bot.send_message(personId,'Виды товара доступные для покупки в данной локации')
                        bot.send_message(personId,getProductsList(productsList[personLoc]))
                    else:
                        product = slpitMessage[1]
                        price = getProductsPrice(productsList[personLoc],product)
                        if price == 0:
                            bot.send_message(personId,'Такого товара нет(Проверьте правильно написания наименования товара)')
                        else:
                            if int(personMon)-int(price)>0:
                                update_mon_bd(personId, int(personMon)-int(price))
                                bot.send_message(personId,'Вы купили '+product+' на сумму '+str(price))
                            else:
                                bot.send_message(slpitMessage[1],'Не хватает денег')
                else:
                    bot.send_message(personId,'В данной локации эта команда не доступна!')
            elif message.text.lower() == '!помощь':
                bot.send_message(personId,"""
!Меню - возвращает вас в главное меню\n
!Передать - передает деньги другому персонажу. Формат ввода команды: !Передать (id адресата) (сумма перевода)\n
!Баланс - показывает ваш баланс\n
!Ктоздесь - показывает всех персонажей которые находятся в одной локации что и вы\n
!Мойid - показывает ваш id\n
!Время - показывает текущее время\n
!Помощь - выводит данный текст""")
        else:
            if personLoc == 0:
                bot.send_message(personId,'Введи /game чтобы оказаться в главном меню!')
            else:
                personsId = get_persons_in_loc_bd(personLoc)
                for i in range(len(personsId)):
                    if personsId[i][0] == personId:
                        continue
                    try:
                        bot.send_message(personsId[i][0],'<b>'+personName+'</b>: '+message.text, parse_mode="HTML")
                    except telebot.apihelper.ApiException:
                        print(personsId[i][0],'error')
        
# /ЧАТЫ
