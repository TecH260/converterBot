import telebot
from telebot import types
import re

import function
import keyboard
import config
import generateExcel

bot = telebot.TeleBot(config.TOKEN)

userDict = {}
userStatus = {}

@bot.message_handler(commands = ["start"])
def start(message):
    chat_id = message.chat.id
    bot.delete_message(chat_id, message.id)
    status = function.checkUser(message.from_user)
    Bid = function.Bid(chat_id)
    userDict[chat_id] = Bid
    if function.checkUser(message.from_user):
        markup = keyboard.GetTypeBidMarkup()
        bot.send_message(chat_id, "Клиент хочет", reply_markup = markup)
    else:
        bot.send_message(chat_id, "У вас нет прав доступа")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("btn"))
def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    code = callback_query.data[3:]
    regex = "^[a-zA-Zа-яА-ЯёЁ]+$"
    pattern = re.compile(regex)
    if code.isdigit():
        code = int(code)
        bot.delete_message(chat_id, callback_query.message.id)
        if code != 10 and code != 11:
            Bid = userDict[chat_id]
        if code <= 2:
            markupCrypto = keyboard.GetTypeCryptoMarkup()
            if code == 1:
                bot.send_message(chat_id, "Клиент хочет купить", reply_markup = markupCrypto)
                Bid.typeBid = "asks"
            elif code == 2:
                bot.send_message(chat_id, "Клиент хочет продать", reply_markup = markupCrypto)
                Bid.typeBid = "bids"
        elif code >= 3 and code <= 4:
            if code == 3:
                Bid.Crypto = "usdt"
            elif code == 4:
                Bid.Crypto = "btc"
            markupMoney = keyboard.GetTypeMoneyMarkup()
            if Bid.typeBid == "asks":
                bot.send_message(chat_id, f"Клиент хочет купить {Bid.Crypto.upper()} за", reply_markup=markupMoney)
            else:
                bot.send_message(chat_id, f"Клиент хочет продать {Bid.Crypto.upper()} за", reply_markup=markupMoney)
        elif code >= 5 and code <= 6:
            if code == 5:
                Bid.Money = "rub"
            elif code == 6:
                Bid.Money = "usd"
            markupMoney = keyboard.GetTypePercentMarkup()
            if Bid.typeBid == "asks":
                bot.send_message(chat_id, f"Клиент хочет купить {Bid.Crypto.upper()} за {Bid.Money.upper()}\nРасчет суммы сделки от", reply_markup=markupMoney)
            else:
                bot.send_message(chat_id, f"Клиент хочет продать {Bid.Crypto.upper()} за {Bid.Money.upper()}\nРасчет суммы сделки от", reply_markup=markupMoney)
        elif code >= 7 and code <= 8:
            if code == 7:
                Bid.PercentMoney = "crypto"
            elif code == 8:
                Bid.PercentMoney = "money"
            msg = bot.send_message(chat_id, "Сумма сделки")
            bot.register_next_step_handler(msg, GetSumm)
        elif code >= 20:
            Bid.Percent = code/10000
            print(Bid.Percent)
            msg = bot.send_message(chat_id, "Ваши данные получены")
            order = function.generateBid(Bid)
            if order == False:
                bot.send_message(chat_id, 'Не настроен API, обратитесь к администратору')
            else:
                print(order)
                if Bid.Money == 'rub':
                    money = '₽'
                else:
                    money = '$'

                text = f"🔴 <b>Заявка {order['idOrder']}:</b>\n"
                if Bid.typeBid == "asks":
                    text += "\nПокупка: "
                else:
                    text += "Продажа: "

                if Bid.PercentMoney == 'crypto':
                    if Bid.Crypto == "usdt":
                        summ = format(float(Bid.summ), '.2f')
                    else:
                        summ = format(float(Bid.summ), '.6f')
                    summ = '{:,}'.format(float(summ)).replace(',', ' ')
                    text += f"{summ} {Bid.Crypto.upper()} \n\n"
                    
                    text += "✅ Наличные в офисе:\n"
                    text += f"📍 Курс {Bid.Crypto.upper()}/{Bid.Money.upper()}: {order['price']} {money}\n"
                    text += f"📍 Клиент платит: {order['summ']} {money}\n" if Bid.typeBid == "asks" else f"📍 Клиент получает: {order['summ']} {money}\n"
                    text += f"🔒 Курс фиксируется на 1 час\n\n"
                    text += "🔘 Онлайн-платеж:\n"
                    text += f"📍 Клиент платит: {order['summCard']} {money}\n" if Bid.typeBid == "asks" else f"📍 Клиент получает: {order['summCard']} {money}\n"
                    text += f"📍 Курс {Bid.Crypto.upper()}/{Bid.Money.upper()}: {order['priceCard']} {money}\n\n"
                    
                else:
                    if Bid.Crypto == "usdt":
                        summ = format(float(Bid.summ), '.2f')
                    summ = '{:,}'.format(float(summ)).replace(',', ' ')
                    text += f"{Bid.Crypto.upper()} на сумму {summ} {money}\n\n"
                    text += "✅ Наличные в офисе:\n"
                    text += f"📍 Курс {Bid.Crypto.upper()}/{Bid.Money.upper()}: {order['price']} {money}\n"
                    text += f"📍 Клиент покупает: {order['summ']} {Bid.Crypto.upper()}\n" if Bid.typeBid == "asks" else f"📍 Клиент получает: {order['summ']} {money}\n"
                    text += f"🔒 Курс фиксируется на 1 час\n\n"
                    text += "🔘 Онлайн-платеж:\n"
                    text += f"📍 Клиент покупает: {order['summCard']} {Bid.Crypto.upper()}\n" if Bid.typeBid == "asks" else f"📍 Клиент получает: {order['summCard']} {money}\n"
                    text += f"📍 Курс {Bid.Crypto.upper()}/{Bid.Money.upper()}: {order['priceCard']} {money}\n\n"
                    

                

                markupStatus = keyboard.GetStatusBid(order['idOrder'])
                bot.delete_message(chat_id, msg.id)
                bot.send_message(chat_id, text, reply_markup=markupStatus, parse_mode="HTML")

                textProfit = f"🟡 <b>Комиссия по сделке {order['idOrder']}</b> \n"
                textProfit += f"📍 {format(order['profit'], '.2f')} {Bid.Money.upper()} \n"
                textProfit += f"📍 {format(order['profitCrypto'], '.2f')} {Bid.Crypto.upper()} \n"
                msg = bot.send_message(chat_id, textProfit, parse_mode="HTML")
                function.orderUpdateIdMessage(order['idOrder'], msg.id, textProfit)
        elif code == 10:
            msg = bot.send_message(chat_id, "Введите id Пользователя")
            bot.register_next_step_handler(msg, UserRightsStep1)
        elif code == 11:
            file = generateExcel.generateNewExcel()
            if file:
                bot.send_document(chat_id, open(r'orders.xlsx', 'rb'))
            
    else:
        print(code)
        type = code[4:]
        id = code[:4]
        print(type)
        print(id)
        if type == "s":
            status = 1
            bot.edit_message_text(chat_id = chat_id, message_id=callback_query.message.message_id, text=callback_query.message.text,reply_markup=None)
            msg = bot.send_message(chat_id, "Введите курс, по которому прошла сделка (указывайте биржевой курс)")
            bot.register_next_step_handler(msg, UserUpdateCourse, id)
        else:
            bot.delete_message(chat_id, callback_query.message.id)
            bot.delete_message(chat_id, callback_query.message.id+1)
            status = 0
        function.orderUpdate(id, status)
        

def UserUpdateCourse(message, orderId):
    chat_id = message.chat.id
    bot.delete_message(chat_id, message.message_id)
    bot.delete_message(chat_id, message.message_id-1)
    id_message = function.orderIdMessage(orderId, message.text)
    print(id_message)
    textMes = id_message[1] + f'\n <b>Спред:</b> {format(id_message[3], '.2f')}' 
    bot.edit_message_text(chat_id = chat_id, message_id=id_message[0], text= textMes, parse_mode="HTML")

def GetSumm(message):
    chat_id = message.chat.id
    bot.delete_message(chat_id, message.message_id)
    bot.delete_message(chat_id, message.message_id-1)

    Bid = userDict[chat_id]
    Bid.summ = message.text
    markupMoney = keyboard.GetFreeMarkup()
    bot.send_message(chat_id, "Выберите процент", reply_markup=markupMoney)
    

#ADMIN
@bot.message_handler(commands = ["admin"])
def admin(message):
    chat_id = message.chat.id
    if function.isAdmin(chat_id):
        markup = keyboard.GetAdminMarkup()
        bot.send_message(chat_id, "Выберите действие", reply_markup=markup)

@bot.message_handler(commands = ["stats"])
def statistics(message):
    chat_id = message.chat.id
    profit = function.getUserStatistics(chat_id)
    if profit:
        bot.send_message(chat_id, f"Ваш зарабток составил {profit} ₽ 👍")
    else:
        bot.send_message(chat_id, f"Вы пока ничего не заработали 😢")

def UserRightsStep1(message):
    chat_id = message.from_user.id
    user_id = message.text
    User = function.Bid(user_id)
    userStatus[chat_id] = User
    msg = bot.send_message(chat_id, "Укажите статус пользователя: \n0 - Клиент\n1 - Сотрудник\n2 - Администратор")
    bot.register_next_step_handler(msg, UserRightsStep2)

def UserRightsStep2(message):
    chat_id = message.from_user.id
    status = message.text
    User = userStatus[chat_id]
    User.status = status

    status = function.updateUser(User)
    if status:
        bot.send_message(chat_id, "Права пользователя обновлены")
    else:
        bot.send_message(chat_id, "Произошла ошибка")

    markup = keyboard.GetAdminMarkup()
    bot.send_message(chat_id, "Выберите действие", reply_markup=markup)

bot.polling(none_stop=True, interval=0)
