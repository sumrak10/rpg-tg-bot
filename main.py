from posixpath import split
import requests, random, datetime, sys, time, argparse, os
from colorama import Fore, Back, Style
import telebot
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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
trueSimInUname = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_'
minUnameLen = 3

# локации
not_available_emoji = '❌'
locationlist = []
clubopen = datetime.time(18, 0)
clubclose = datetime.time(6, 0)
schoolopen = datetime.time(8, 0)
schoolclose = datetime.time(20,0)

# казино
kosti_sides = []
kosti_bet = 0
# чаты
productsList = [[],[],[['Вода',3],['Кола',5],['Кофе',5],['Шаурма',8]],[['Вода',3],['Кола',5],['Кофе',5],['Хот-дог',10],['Бургер',10],['Чизбургер',12],['Лаваш',15],['Суп мясной',15],['Суп овощной',13]],[['Вода',3],['Кола',5],['Кофе',5],['Водка',10],['Пиво',8],['Текила',12],['Джин',13],['Вино',12]]]
businessList = [['Лавка с мороженным',25],['Мойка машин',50],['Кафе',500],['Ресторан',1000],['Сеть магазинов',10000],['Завод машин',100000],['Своя компания',500000],['Монополия компаний',1000000]]
business_cost_factor = 75 # во сколько раз будет соотноситься ( ежедневный доход от бизнеса : цена покупки бизнеса )
gardenList = [["🍅",1,2,4],["🧅",1,5,10],["🥒",1,10,20],["🥬",3,15,25],["🥕",5,20,30],["🍆",5,30,50],["🌽",10,45,70],["🧄",10,50,80],["🍓",10,60,90],["🥔",10,70,95],["🍉",20,90,160],["🍇",20,100,180],["🍎",30,150,280],["🍐",30,200,380],["🍑",30,500,950]]
decay_factor = -3 # через сколько дней созревший урожай сгниет
min_koef_sell_harvest = 0.75 # на сколько будет множиться рыночная стоимость товара (минимальный порог)
max_koef_sell_harvest = 1.25 # (максимальный порог - соответсвенно)
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
def updateGlobalVars(uid):
    global personId,personUname,personName,personAge,personDes,personMon,personLoc
    data = get_data_from_bd_by_id(uid)
    if data == 0:
        bot.send_message(uid, 'Введи /start')
        return 0
    personId = data[0]
    personUname = data[1]
    personName = data[2]
    personAge = data[3]
    personDes = data[4]
    personMon = data[5]
    personLoc = data[6]
def date_to_string(date):
    return str(date.strftime('%d/%m/%Y'))
def string_to_date(str):
    d,m,y = str.split('/')
    return datetime.date(int(y),int(m),int(d))
def remake_garden(garden,cell,planttype=0, harvest=False):
    garden = garden.split()
    newgarden = ''
    if harvest == False:
        for i in range(len(garden)):
            if int(i) == int(cell): 
                newplant = str(planttype) +'-'+ date_to_string(datetime.datetime.now().date())
                newgarden += newplant + ' '
            else:
                newgarden += garden[i] + ' '
    else:
        for i in range(len(garden)):
            if int(i) == int(cell): 
                newplant = '0-0'
                newgarden += newplant + ' '
            else:
                newgarden += garden[i] + ' '
    return newgarden
# /ГЛОБАЛЬНЫЕ ФУНКЦИИ

# РЕГИСТРАЦИЯ
@bot.message_handler(commands=['start'])
def start(message):
    global personId
    personId = message.from_user.id
    startdata = message.text[7:]
    if startdata.split('-')[0] == 'viewPerson':
        bot.delete_message(personId, message.message_id)
        viewPerson(startdata.split('-')[1], personId)
    else:
        personData = get_data_from_bd_by_id(message.from_user.id)
        # bot.reply_to(message, "Привет я кажется тебя помню. \nНапиши /game чтобы начать играть!")
        # mainMenu(message)
        if personData == 0:
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
    msg = bot.send_message(message.from_user.id, 'Придумай уникальный идентификатор\nОн должен содержать только буквы английского алфавита a-z и цифры 0-9 так же нижние подчеркивания\nДолжен содержать более '+str(minUnameLen)+'х символов и не должен начинаться с цифры\n(можно использовать такой же username как и у твоего телеграм аккаунта)')
    bot.register_next_step_handler(msg, setPersonUname)
def setPersonUname(message):
    global personUname
    unameStatus = True
    personUname = message.text
    for sim in personUname:
        if not(sim in trueSimInUname):
            unameStatus = False
    if sim[0] in '1234567890':
        unameStatus = False
    data = get_data_from_bd_by_uname(personUname)
    if ( data != 0 ) or ( unameStatus ):
        msg = bot.send_message(message.from_user.id, 'Увы, такой username занят, попробуй еще раз :(')
        bot.register_next_step_handler(msg, setPersonUname)
    if ( data == 0 ) or ( unameStatus ):
        msg = bot.send_message(message.from_user.id, 'А теперь придумаем возраст, '+personName+' :)')
        bot.register_next_step_handler(msg, setPersonAge)
def setPersonAge(message):
    global personAge
    try:
        personAge = int(message.text)
        if 0 <= personAge <= 120:
            msg = bot.send_message(message.from_user.id, "А если серьезно? :(")
            bot.register_next_step_handler(msg, setPersonAge)
        msg = bot.send_message(message.from_user.id, "Придумай описание своего персонажа\n (Текст должен быть не более 255 символов. Учти это!)")
        bot.register_next_step_handler(msg, initPerson)
    except:
        msg = bot.send_message(message.from_user.id, "Мне нужны только цифры (без лишних слов и букв) :(")
        bot.register_next_step_handler(msg, setPersonAge)
def initPerson(message):
    global personDes
    personDes = message.text
    if (insert_data_to_bd(personId,personUname,personName,personAge,personDes,100,0)):\
        bot.reply_to(message, "Отлично, персонаж создан! Напишите /game чтобы начать играть!")
    else:
        bot.reply_to(message, "Возникла ошибка! Напишите /start чтобы попробовать еще раз!")
# /РЕГИСТРАЦИЯ


# КЛАВИАТУРЫ
def mainMenu_kb():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add('Профиль👤','Локации📍', 'Панель заработка🧮')
	return markup
def chat_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('!помощь', '!локации','!меню')
    return markup
def relationShip_kb(id,uid):
    friends, enemies = get_friends_and_enemies_list(id)
    markup = telebot.types.InlineKeyboardMarkup()
    if uid in friends:
        markup.add(telebot.types.InlineKeyboardButton(text = 'Удалить из друзей', callback_data ='relationship delfriend '+uid))
    elif not(uid in enemies):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Добавить в друзья', callback_data ='relationship addfriend '+uid))
    if (uid in enemies):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Убрать из ЧС', callback_data ='relationship delenemy '+uid))
    elif not(uid in friends):
        markup.add(telebot.types.InlineKeyboardButton(text = 'Отправить в ЧС', callback_data ='relationship addenemy '+uid))
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
def everydayPrize_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Забрать ежедневный приз!', callback_data ='management prize'))
    return markup
def management_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Купить бизнес', callback_data ='management get business'))
    markup.add(telebot.types.InlineKeyboardButton(text = 'Забрать заработок', callback_data ='management get income'))
    return markup
def management_buy_kb():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Вернуться в меню', callback_data ='management buy back'))
    for i in businessList:
        markup.add(telebot.types.InlineKeyboardButton(text = i[0]+' Цена: '+str(int(i[1])*business_cost_factor)+' Доход: '+str(i[1]), callback_data ='management buy '+str(i[1])))
    return markup
def garden_kb(garden):
    markup = telebot.types.InlineKeyboardMarkup()
    garden = garden.split()
    garray = []
    garray3 = []
    k = 0
    for i in range(5):
        for j in range(3):
            if str(garden[k].split('-')[0]) == '0':
                txt = 'Посадить'
                clbdata = 'plant ' + str(k)
            else:
                ddelta = datetime.datetime.now().date() - string_to_date(garden[k].split('-')[1])
                days = int(gardenList[int(garden[k].split('-')[0])-1][1]) - int(ddelta.days)
                if decay_factor <= days <= 0:
                    txt = gardenList[int(garden[k].split('-')[0])-1][0] + ' Собрать'
                    clbdata = 'harvest ' + str(k) + ' ' + str(garden[k].split('-')[0])
                elif days < decay_factor:
                    txt = gardenList[int(garden[k].split('-')[0])-1][0] + ' Убрать'
                    clbdata = 'clean ' + str(k)
                else:
                    txt = gardenList[int(garden[k].split('-')[0])-1][0] + ' '+str(days) + ' дней'
                    clbdata = 'manage ' + str(k)+ ' ' +str(garden[k].split('-')[0])
            garray3.append([txt, clbdata])
            k += 1
        garray.append(garray3)
        garray3 = []
    markup.add(telebot.types.InlineKeyboardButton(text = 'Полить', callback_data ='garden water 0'))
    for i in range(5):
        markup.add(telebot.types.InlineKeyboardButton(text = garray[i][0][0], callback_data ='garden '+garray[i][0][1]),telebot.types.InlineKeyboardButton(text = garray[i][1][0], callback_data ='garden '+garray[i][1][1]),telebot.types.InlineKeyboardButton(text = garray[i][2][0], callback_data ='garden '+garray[i][2][1]))
    return markup
def garden_plant_kb(cell):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Отменить', callback_data ='garden buy back'))
    for i in range(len(gardenList)):
        markup.add(telebot.types.InlineKeyboardButton(text = '[ '+gardenList[i][0]+' ] Цена семян: '+str(gardenList[i][2])+' Время роста: '+str(gardenList[i][1])+'\n', callback_data ='garden buy '+str(cell)+' '+str(int(i)+1)))
    return markup
def garden_manage_kb(cell):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = 'Назад', callback_data ='garden buy back'))
    markup.add(telebot.types.InlineKeyboardButton(text = 'Убрать растение', callback_data ='garden clean '+str(cell)))
    return markup
# /КЛАВИАТУРЫ




# КОЛБЕКИ
@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    if call.data.split()[0] == 'garden':
        func = call.data.split()[1]
        cell = call.data.split()[2]
        data = get_data_from_bd_by_id(call.message.chat.id)
        gdata = get_data_from_gardening(call.message.chat.id)
        if func == 'plant':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_plant_kb(cell))
        if func == 'buy':
            if cell == 'back':
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_kb(gdata[1]))
            else:
                plantprice = gardenList[int(call.data.split()[3])-1][2]
                if data[5] >= plantprice:
                    planttype = call.data.split()[3]
                    newg =  remake_garden(gdata[1],cell,planttype)
                    update_garden(call.message.chat.id, newg)
                    update_mon_bd_by_id(call.message.chat.id,str(int(data[5])-plantprice))
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_kb(newg))
                else:
                    bot.answer_callback_query(callback_query_id=call.id, text="Недостаточно средств для покупки данных семян! Ваш баланс: "+str(data[5]), show_alert=True)
        if func == 'harvest':
            plantnum = int(call.data.split()[3])
            plantprice = int(gardenList[plantnum-1][3])
            sellprice = random.randint(round(min_koef_sell_harvest*plantprice), round(max_koef_sell_harvest*plantprice))
            update_mon_bd_by_id(call.message.chat.id, str(int(data[5])+int(sellprice)))
            newg = remake_garden(gdata[1],cell,harvest=True)
            update_garden(call.message.chat.id, newg)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_kb(newg))
            bot.answer_callback_query(callback_query_id=call.id, text="Урожай собран и продан за: "+str(sellprice)+' RPCoin', show_alert=False)
        if func == 'clean':
            newg = remake_garden(gdata[1],cell,harvest=True)
            update_garden(call.message.chat.id, newg)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_kb(newg))
            bot.answer_callback_query(callback_query_id=call.id, text="Растение убрано!", show_alert=False)
        if func == 'water':
            if str(gdata[2]) == date_to_string(datetime.datetime.now().date()):
                bot.answer_callback_query(callback_query_id=call.id, text="Вы уже поливали урожай сегодня!", show_alert=True)
            else:
                update_last_watering_date(call.message.chat.id, date_to_string(datetime.datetime.now().date()))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Последний полив: '+date_to_string(datetime.datetime.now().date()),reply_markup=garden_kb(gdata[1]))
        if func == 'manage':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=garden_manage_kb(cell))


    if call.data.split()[0] == 'relationship':
        func = call.data.split()[1]
        uid = call.data.split()[2]
        me = call.message.chat.id
        if func == 'addfriend':
            status = add_friend(me,uid)
            if status == 200:
                bot.answer_callback_query(callback_query_id=call.id, text="Друг добавлен", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,uid))
        elif func == 'addenemy':
            status = add_enemy(me,uid)
            if status == 300:
                bot.answer_callback_query(callback_query_id=call.id, text="Отправлен в ЧС", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,uid))
        elif func == 'delfriend':
            status = del_friend(me,uid)
            if status == 201:
                bot.answer_callback_query(callback_query_id=call.id, text="Друг удален", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,uid))
        elif func == 'delenemy':
            status = del_enemy(me,uid)
            if status == 301:
                bot.answer_callback_query(callback_query_id=call.id, text="Убран из ЧС", show_alert=False)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=relationShip_kb(me,uid))


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
    if call.data.split()[0] == 'management':
        mdata = get_data_from_management(call.message.chat.id)
        data = get_data_from_bd_by_id(call.message.chat.id)
        date_now = datetime.datetime.now().date()
        datedelta = date_now - string_to_date(mdata[3])
        income_money = int(datedelta.days) * int(mdata[2])
        func = call.data.split()[1]
        if len(call.data.split()) > 2:
            func2 = call.data.split()[2]
        if func == 'prize':
            update_prize_date(call.message.chat.id,date_to_string(date_now))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Приз получен!')
            update_mon_bd(data[1],int(data[5])+25)
        else:
            if func == 'get':
                if func2 == 'income':
                    if mdata[2] != '0':
                        update_mon_bd_by_id(call.message.chat.id,str(int(data[5])+income_money))
                        update_business_date(call.message.chat.id,date_to_string(date_now))
                        if int(datedelta.days) == 0:
                            bot.answer_callback_query(callback_query_id=call.id, text="Вы уже собирали сегодня доход", show_alert=True)
                        else:
                            bot.answer_callback_query(callback_query_id=call.id, text="Доход: "+str(income_money)+' RPCoin за '+str(datedelta.days)+' дней', show_alert=True)
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Баланс: '+str(int(data[5])+int(income_money))+' RPC\nДенег нокопилось: '+str('0')+' RPC\nПассивный ежедневный доход: '+str(mdata[2])+' RPC',reply_markup=management_kb())
                    else: 
                        bot.answer_callback_query(callback_query_id=call.id, text="Нет пассивного дохода", show_alert=True)
                elif func2 == 'business':
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=management_buy_kb())
            if func == 'buy':
                if not(func2 == 'back'):
                    cost = int(func2)
                    if data[5] >= cost*business_cost_factor:
                        busiList = mdata[4]
                        busiList_new = ''
                        for i in busiList.split():
                            j = i.split('-')
                            if int(j[0]) == int(cost):
                                j[1] = str(int(j[1]) + 1)
                            busiList_new += str(j[0])+'-'+str(j[1])+' '
                        update_business(call.message.chat.id, busiList_new)
                        income_new = int(mdata[2])+int(cost)
                        update_income(call.message.chat.id, str(income_new))
                        update_mon_bd_by_id(call.message.chat.id, str(int(data[5])-int(cost)*business_cost_factor))
                        bot.answer_callback_query(callback_query_id=call.id, text="Вы успешно купили бизнес", show_alert=False)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Баланс: '+str(data[5])+'\nДенег нокопилось: '+str(income_money)+'\nПассивный ежедневный доход: '+str(income_new),reply_markup=management_buy_kb())
                    else:
                        bot.answer_callback_query(callback_query_id=call.id, text="Не достаточно средств! Ваш баланс: "+str(data[5]), show_alert=True)
                else:
                    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,reply_markup=management_kb())
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
        updateGlobalVars(message.from_user.id)

        if personLoc != 0:
            personsId = get_persons_in_loc_bd(personLoc)
            for i in range(len(personsId)):
                if int(personsId[i][0]) == int(personId):
                    continue
                try:
                    bot.send_message(personsId[i][0],'<i>'+personName+" покинул локацию</i>", parse_mode="HTML")
                except:
                    print(str(personsId[i][0])+"bot was blocked by that user 182")
            update_loc_bd(message.from_user.id, "0")
            personLoc = 0
        bot.send_message(message.from_user.id, "Главное меню:", reply_markup=mainMenu_kb())

# @bot.message_handler(content_types=['text'])
# def mainMenuHandler(message):
    
        # mainMenu(message)
# /ИГРА



# ПРОФИЛЬ
def viewPerson(message, user_id=0):
    data = get_data_from_bd_by_uname(message)
    if data == 0:
        bot.send_message(user_id, 'Такого персонажа нет в базе данных')
    else:
        if data[0] == user_id:
            bot.send_message(user_id, 'Вы можете посмотреть свой профиль с помощью пункта меню "Профиль" в главном меню')
        else:
            bot.send_message(user_id, 'Username: <code>' + data[1] + '</code>\nИмя: '+data[2] + '\nВозраст: '+str(data[3]) + '\nОписание: '+data[4],parse_mode="HTML",reply_markup = relationShip_kb(user_id, str(data[0])))

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
    else:
        msg = bot.send_message(message.from_user.id, "Выберите пункт меню!")
        bot.register_next_step_handler(msg, profileRegHandler)
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
    if len(val) <= minUnameLen:
        bot.send_message(message.from_user.id, "Твой username должен быть не менее "+str(minUnameLen)+"х символов. Придумай другой соответсвующий правилам")
        bot.register_next_step_handler(message, changeUname)
    else:
        unameStatus = True
        for sim in val:
            if not(sim in trueSimInUname):
                unameStatus = False
        if val[0] in '1234567890':
            unameStatus = False
        try:
            if unameStatus:
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
            else:
                bot.send_message(message.from_user.id, "В username присутсвуют недопустимые символы или он начинается с цифры. Придумай другой соответсвующий правилам")
                bot.register_next_step_handler(message, changeUname)
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
    if message.text == locationlist[0][2]:
        mainMenu(message)
    elif message.text[len(message.text)-1:] == not_available_emoji:
        bot.send_message(message.from_user.id, 'Локация '+message.text[0:len(message.text)-1]+' не доступна вам в данный момент')
        mainMenu(message)
    elif message.text == locationlist[0][0]:
        bot.send_message(message.from_user.id, "Локация: "+locationlist[0][0]+"\n", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, message.from_user.id)
        personsId = get_persons_in_loc_bd(message.from_user.id)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<u>'+personName+" пришел домой</u>", parse_mode="HTML")
    elif message.text == locationlist[0][1]:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Назад')
        msg = bot.send_message(message.from_user.id, "Впишите username персонажа к которому вы хотите пойти в гости", reply_markup=markup)
        bot.register_next_step_handler(msg, visitsHandler)
    elif message.text == locationlist[1][0]: 
        bot.send_message(message.from_user.id, "Локация: Улица\nБольшая широкая улица кишащая толпами людей которые вечно куда-то спешат", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "2")
        personsId = get_persons_in_loc_bd(2)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<i>'+personName+' вошел в локацию "Улица"</i>', parse_mode="HTML")
    elif message.text == locationlist[1][1]:
        bot.send_message(message.from_user.id, "Локация: Парк\nДовольно спокойное место, в самый раз чтобы отдохнуть от городской суеты", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "3")
        personsId = get_persons_in_loc_bd(3)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<i>'+personName+' вошел в локацию "Парк" </i>',parse_mode="HTML")
    elif message.text == locationlist[1][2]:
        bot.send_message(message.from_user.id, "Локация: Кафе\nНебольшое кафе находящееся недалеко от вашего дома. Ни чем не приметная, но такая уютная", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "4")
        personsId = get_persons_in_loc_bd(4)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<i>'+personName+' вошел в локацию "Кафе"</i>', parse_mode="HTML")
    elif message.text == locationlist[2][1]:
        bot.send_message(message.from_user.id, "Локация: Клуб\nС самого входа слышно музыку которая так и тянет танцевать!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "5")
        personsId = get_persons_in_loc_bd(5)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<i>'+personName+' вошел в локацию "Клуб"</i>', parse_mode="HTML")
    elif message.text == locationlist[2][0]:
        bot.send_message(message.from_user.id, "Локация: Школа\nЗнания - сила!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "6")
        personsId = get_persons_in_loc_bd(6)
        for i in range(len(personsId)):
            if personsId[i][0] == personId:
                continue
            bot.send_message(personsId[i][0],'<i>'+personName+' вошел в локацию "Школа"</i>', parse_mode="HTML")
    elif message.text == locationlist[2][2]:
        bot.send_message(message.from_user.id, "Локация: Казино\nУмей во время остановиться!", reply_markup=chat_kb())
        update_loc_bd(message.from_user.id, "7")
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('!помощь','!локации','!меню')
        markup.add('!монетка','!кости')
        bot.send_message(message.from_user.id, "!монетка - обычная игра с шансом 50%\n!кости - шанс выиграть 1 к 6, но и приз будет с коэффициентом 6х", reply_markup=markup)
    else:
        msg = bot.send_message(message.from_user.id, "Нажми на пункт меню!")
        bot.register_next_step_handler(msg, locationHandler)
def visitsHandler(message):
    if personUname == message.text:
        bot.send_message(message.from_user.id, 'Домой вы можете попасть с помощью пункта меню "Дом" в меню локаций')
        mainMenu(message)
    elif message.text == 'Назад':
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





@bot.message_handler(content_types=['text'])
def messagesHandler(message):
    error = 0
    try:
        data = get_data_from_bd_by_id(message.from_user.id)
    except:
        bot.send_message(message.from_user.id,'У тебя кажется нет персонажа.\nВведи /start')
        error = 1
    if error == 0:
        global personId,personUname,personName,personAge,personDes,personMon,personLoc, locationlist
        updateGlobalVars(message.from_user.id)
        
        if message.text == 'Назад↩️':
            mainMenu(message)
        elif message.text == 'Редактировать профиль⚙️':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Имя и Фамилию', 'Username', 'Возраст', 'Описание', 'Назад')
            msg = bot.send_message(message.from_user.id, "Что хотите редактировать?", reply_markup=markup)
            bot.register_next_step_handler(msg, profileRegHandler)
        elif message.text == 'Друзья и ЧС👥':
            friends, enemies = get_friends_and_enemies_list(personUname)
            friendslist = ''
            enemieslist = ''
            for i in friends.split():
                data = get_data_from_bd_by_uname(i)
                friendslist += '<a href="t.me/SmrkRP_bot?start=viewPerson-'+data[1]+'">['+data[1]+'] '+data[2]+'</a>\n'
            for i in enemies.split():
                data = get_data_from_bd_by_uname(i)
                enemieslist += '<a href="t.me/SmrkRP_bot?start=viewPerson-'+data[1]+'">['+data[1]+'] '+data[2]+'</a>'
            bot.send_message(message.from_user.id, "Друзья:\n"+friendslist, parse_mode="HTML",disable_web_page_preview = True)
            bot.send_message(message.from_user.id, "В черном списке:\n"+enemieslist, parse_mode="HTML",disable_web_page_preview = True, reply_markup=chat_kb())


        elif message.text == 'Профиль👤':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Друзья и ЧС👥', 'Назад↩️')
            markup.add('Редактировать профиль⚙️')
            bot.send_message(message.from_user.id, "\nUsername: <code>"+personUname+"</code>\nИмя: "+personName+"\nВозраст: "+str(personAge)+"\nБаланс: "+str(personMon)+"\nОписание: "+personDes, parse_mode="HTML",reply_markup=markup)
            # bot.register_next_step_handler(msg, profileHandler)
        elif message.text == 'Локации📍' or message.text.lower() == '!локации':
            if personLoc != 0:
                personsId = get_persons_in_loc_bd(personLoc)
                for i in range(len(personsId)):
                    if int(personsId[i][0]) == int(personId):
                        continue
                    try:
                        bot.send_message(personsId[i][0],'<i>'+personName+" покинул локацию</i>", parse_mode="HTML")
                    except:
                        print(str(personsId[i][0])+"bot was blocked by that user 313")
                update_loc_bd(message.from_user.id, "0")
                personLoc = 0
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            time_now = datetime.datetime.now().time()
            locationlist = [['Дом🏠', 'В гости🏘','Назад↩️'],['Улица🚙', 'Парк🏞', 'Кафе☕️'],['Школа✍️','Клуб🌃','Казино💸']]
            if not((6 < int(personAge) <= 18) and ((schoolopen<=time_now) and (schoolclose>time_now))):
                locationlist[2][0] = locationlist[2][0][0:len(locationlist[2][0])-2] + not_available_emoji
            if not((18 <= int(personAge)) and ((clubopen<=time_now) and (clubclose>time_now))):
                locationlist[2][1] = locationlist[2][1][0:len(locationlist[2][1])-1] + not_available_emoji
            if not(18 <= int(personAge)):
                locationlist[2][2] = locationlist[2][2][0:len(locationlist[2][2])-1] + not_available_emoji
            for i in range(len(locationlist)):
                if len(locationlist[i]) == 3:
                    markup.add(locationlist[i][0],locationlist[i][1],locationlist[i][2])
                if len(locationlist[i]) == 2:
                    markup.add(locationlist[i][0],locationlist[i][1])
                if len(locationlist[i]) == 1:
                    markup.add(locationlist[i][0])
            msg = bot.send_message(message.from_user.id, "Выберите локацию", reply_markup=markup)
            bot.register_next_step_handler(msg, locationHandler)
        elif message.text == 'Панель заработка🧮':
            date_now = datetime.datetime.now().date()
            date = date_now - datetime.timedelta(1)
            try:
                mdata = get_data_from_management(personId)
            except:
                businessStr = ''
                for i in businessList:
                    businessStr += str(i[1])+'-0 '
                insert_new_person_in_management(personId,date_to_string(date), businessStr)
            mdata = get_data_from_management(personId)
            data = get_data_from_bd_by_id(personId)
            datedelta = date_now - string_to_date(mdata[1])
            datedeltafinc = date_now - string_to_date(mdata[3])
            income_money = int(datedeltafinc.days) * int(mdata[2])
            if datedelta.days >= 1:
                bot.send_message(personId,'Вам доступен ежедневный приз размером в 25 RPCoin!', reply_markup=everydayPrize_kb())
            bot.send_message(personId,'Баланс: '+str(data[5])+'\nДенег нокопилось: '+str(income_money)+'\nПассивный ежедневный доход: '+str(mdata[2]),reply_markup=management_kb())
        
        # ЧАТЫ
        elif message.text[0] == '!':
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
                                bot.send_message(personId,'<i>Вы перевели деньги персонажу '+clientdata[1]+' на сумму '+splitMessage[2]+'</i>',parse_mode="HTML")
                                bot.send_message(get_id_by_uname(splitMessage[1]),'<i>Персонаж '+personName+' перевел вам '+splitMessage[2]+' RPCoin</i>',parse_mode="HTML")
                            else:
                                bot.send_message(personId,'Не хватает денег')
            elif message.text.lower() == '!баланс':
                bot.send_message(personId,'Ваш баланс: '+str(personMon)+' RPCoin')
            elif message.text.lower() == '!ктоздесь':
                personsId = get_persons_in_loc_bd(personLoc)
                personlist = ''
                for i in personsId:
                    personlist += '<a href="t.me/SmrkRP_bot?start=viewPerson-'+i[1]+'">'+i[2]+'</a>\n'
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

            elif (splitMessage[0].lower() == '!сад') and (personLoc == personId):
                try: 
                    gdata = get_data_from_gardening(personId)
                except:
                    insert_new_person_in_gardening(personId,'0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 ', date_to_string(datetime.datetime.now().date()))
                    gdata = get_data_from_gardening(personId)
                last_watering =  datetime.datetime.now().date() - string_to_date(gdata[2])
                print(last_watering.days)
                if int(last_watering.days) > 1:
                    update_garden(personId,'0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 ')
                    gdata = get_data_from_gardening(personId)
                    bot.send_message(personId,'Вы не поливали сад более 1 дня поэтому весь урожай высох!',reply_markup=garden_kb(gdata[1]))
                else:
                    bot.send_message(personId,'Последний полив: '+gdata[2],reply_markup=garden_kb(gdata[1]))

            elif message.text.lower() == '!помощь':
                bot.send_message(personId,"""
<code>!меню</code> - возвращает вас в главное меню\n
<code>!передать</code> [username] [сумма] - передает деньги другому персонажу\n
<code>!баланс</code> - показывает ваш баланс\n
<code>!ктоздесь</code> - показывает всех персонажей которые находятся в одной локации что и вы\n
<code>!время</code> - показывает текущее время\n
<code>!профиль</code> [username] - показывает профиль персонажа.\n
<code>!помощь</code> - <tg-spoiler>выводит данный текст</tg-spoiler>""",parse_mode="HTML")
# казино
            elif message.text.lower() == '!монетка':
                if personLoc == 7:
                    bot.send_message(message.from_user.id, "Выбери ставку", reply_markup=casinoMonetkaBet_kb())
            elif message.text.lower() == '!кости':
                if personLoc == 7:
                    bot.send_message(message.from_user.id, "Выбери ставку", reply_markup=casinoKostiBet_kb())
        elif int(personLoc) != 0:
            personsId = get_persons_in_loc_bd(personLoc)
            myfriends, myenemies = get_friends_and_enemies_list(personUname)
            for i in personsId:
                urfriends, urenemies = get_friends_and_enemies_list(i[1])
                if i[0] == personId:
                    continue
                if  personUname in urenemies:
                    bot.send_message(i[0],'<a href="t.me/SmrkRP_bot?start=viewPerson-'+personUname+'">'+personName+'(ЧС)</a>: <tg-spoiler>'+message.text+'</tg-spoiler>', parse_mode="HTML",disable_web_page_preview = True)
                else:
                    if not(i[1] in myenemies):
                    #     bot.send_message(i[0],'<a href="t.me/SmrkRP_bot?start='+personUname+'"> Вы не видите данное сообщение потому что '+personName+' добавил вас в ЧС</a>', parse_mode="HTML",disable_web_page_preview = True)
                    # else:
                        try:
                            bot.send_message(i[0],'<b>'+'<a href="t.me/SmrkRP_bot?start=viewPerson-'+personUname+'">'+personName+'</a></b>: '+message.text, parse_mode="HTML",disable_web_page_preview = True)
                        except:
                            print(i[0],'не получается отправить сообщение этому пользователю')
        
# /ЧАТЫ
