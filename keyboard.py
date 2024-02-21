from telebot import types

def GetTypeBidMarkup():
    markup = types.InlineKeyboardMarkup()
    inline_btn_buy = types.InlineKeyboardButton('Купить', callback_data='btn1')
    inline_btn_sell = types.InlineKeyboardButton('Продать', callback_data='btn2')
    markup.add(inline_btn_buy, inline_btn_sell)
    return markup

def GetTypeCryptoMarkup():
    markup = types.InlineKeyboardMarkup()
    inline_btn_usdt = types.InlineKeyboardButton('USDT', callback_data='btn3')
    inline_btn_crypto = types.InlineKeyboardButton('BTC', callback_data='btn4')
    markup.add(inline_btn_usdt, inline_btn_crypto)
    return markup

def GetTypeMoneyMarkup():
    markup = types.InlineKeyboardMarkup()
    inline_btn_usdt = types.InlineKeyboardButton('Рубли (₽)', callback_data='btn5')
    inline_btn_crypto = types.InlineKeyboardButton('Доллары ($)', callback_data='btn6')
    markup.add(inline_btn_usdt, inline_btn_crypto)
    return markup

def GetTypePercentMarkup():
    markup = types.InlineKeyboardMarkup()
    inline_btn_crypto = types.InlineKeyboardButton('От крипты', callback_data='btn7')
    inline_btn_fiat = types.InlineKeyboardButton('От Фиата', callback_data='btn8')
    markup.add(inline_btn_crypto, inline_btn_fiat)
    return markup

def GetStatusBid(id):
    markup = types.InlineKeyboardMarkup()
    inline_btn_crypto = types.InlineKeyboardButton('✅ Успешно', callback_data=f'btn{id}s')
    inline_btn_fiat = types.InlineKeyboardButton('❌ Отказано', callback_data=f'btn{id}b')
    markup.add(inline_btn_crypto, inline_btn_fiat)
    return markup

def GetAdminMarkup():
    markup = types.InlineKeyboardMarkup()
    inline_btn_1 = types.InlineKeyboardButton('Выдать права', callback_data=f'btn10')
    inline_btn_2 = types.InlineKeyboardButton('Получить отчет', callback_data=f'btn11')
    markup.add(inline_btn_1, inline_btn_2)
    return markup

def GetFreeMarkup():
    free_markup = types.InlineKeyboardMarkup()
    btn20 = types.InlineKeyboardButton('0.2%', callback_data='btn20')
    btn25 = types.InlineKeyboardButton('0.25%', callback_data='btn25')
    btn30 = types.InlineKeyboardButton('0.3%', callback_data='btn30')
    btn35 = types.InlineKeyboardButton('0.35%', callback_data='btn35')
    btn40 = types.InlineKeyboardButton('0.4%', callback_data='btn40')
    btn45 = types.InlineKeyboardButton('0.45%', callback_data='btn45')
    btn50 = types.InlineKeyboardButton('0.5%', callback_data='btn50')
    btn55 = types.InlineKeyboardButton('0.55%', callback_data='btn55')
    btn60 = types.InlineKeyboardButton('0.6%', callback_data='btn60')
    btn65 = types.InlineKeyboardButton('0.65%', callback_data='btn65')
    btn70 = types.InlineKeyboardButton('0.7%', callback_data='btn70')
    btn75 = types.InlineKeyboardButton('0.75%', callback_data='btn75')
    btn80 = types.InlineKeyboardButton('0.8%', callback_data='btn80')
    btn90 = types.InlineKeyboardButton('0.9%', callback_data='btn90')
    btn100 = types.InlineKeyboardButton('1.0%', callback_data='btn100')
    btn120 = types.InlineKeyboardButton('1.2%', callback_data='btn120')
    btn130 = types.InlineKeyboardButton('1.3%', callback_data='btn130')
    btn150 = types.InlineKeyboardButton('1.5%', callback_data='btn150')
    btn175 = types.InlineKeyboardButton('1.75%', callback_data='btn175')
    btn200 = types.InlineKeyboardButton('2.0%', callback_data='btn200')
    btn250 = types.InlineKeyboardButton('2.5%', callback_data='btn250')

    free_markup.add(btn20, btn25, btn30, btn35, btn40, btn45, btn50, btn55, btn60, btn65, btn70, btn75, btn80, btn90, btn100, btn120, btn130, btn150, btn175, btn200, btn250)

    return free_markup