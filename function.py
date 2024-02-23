from telebot import types
import json
import sqlite3
import base64
import time
import datetime
import random
import requests
import jwt
import re
import locale

import config

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

class Bid:
    def __init__(self, id):
        self.id = id #id чата
        self.typeBid = None #Тип заявки Купить/Продавть
        self.Money = None #Тип денег
        self.Crypto = None #Тип Крипты
        self.PercentMoney = None #От чего считать комиссию
        self.Percent = None #Размер комисси
        self.summ = None #сумма

class User:
    def __init__(self, id):
        self.id = id
        self.status = None

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def generateBid(userBid):
    depth = getCourse(f"{userBid.Crypto}{userBid.Money}")
    param = {}
    if depth == False:
        return False
    else:
        rate = depth[userBid.typeBid][0]["price"]
        rateCom = float(rate) + 0.002 * float(rate)
        rateComCard = rateCom + 0.02 * float(rate)

        rateComUser = rateCom + userBid.Percent * float(rate)
        rateComUserCard = rateComCard + userBid.Percent * float(rate)

        if userBid.PercentMoney == "money":
            summ = float(userBid.summ) / rateComUser
            summCard = float(userBid.summ) / rateComUserCard
            percent = float(userBid.summ) / rateCom - summ
            if userBid.Crypto == "usdt":
                summ = format(summ, '.2f')
                summCard = format(summCard, '.2f')
            else:
                summ = format(summ, '.6f')
                summCard = format(summCard, '.6f')
            profit = percent * rateCom
            profitCrypto = profit / float(rate)
        elif userBid.PercentMoney == "crypto":
            if userBid.Crypto == "usdt":
                summ = float(userBid.summ) * rateComUser
                summCard = float(userBid.summ) * rateComUserCard
                profit = summ - (float(userBid.summ) * float(rateCom))
                summ = format(summ, '.2f')
                summCard = format(summCard, '.2f')
            elif userBid.Crypto == "btc":
                summ = float(userBid.summ) * rateComUser
                summCard = float(userBid.summ) * rateComUserCard
                profit = summ - (float(userBid.summ) * float(rateCom))
                summ = format(summ, '.6f')
                summCard = format(summCard, '.6f')
            profitCrypto = profit / float(rateCom)

        param["summ"] = '{:,}'.format(float(summ)).replace(',', ' ')
        param["summCard"] = '{:,}'.format(float(summCard)).replace(',', ' ')
        param["price"] = format(rateComUser, '.2f') if userBid.Crypto == "usdt" else (format(rateComUser, '.7f'))
        param["priceCard"] = format(rateComUserCard, '.2f') if userBid.Crypto == "usdt" else (format(rateComUserCard, '.7f'))
        param["profit"] = profit
        param["profitCrypto"] = profitCrypto

        order = {}
        order["type"] = f"{userBid.Crypto}{userBid.Money}"
        order["summ"] = float(userBid.summ)
        order["ressumm"] = summ
        order["price"] = rate
        order["percent"] = userBid.Percent
        order["user_id"] = userBid.id
        order["date"] = time.time()
        order["profit"] = profit
        order["profitCrypto"] = profitCrypto
        idOrder = writeOrderBase(order)

        param["idOrder"] = idOrder
        return param

def getCourse(market):
    url = "https://garantex.org/api/v2/depth?market="+market
    headers = {
    'Authorization': 'Bearer ' + getApiToken()
    }
    response = requests.request("GET", url, headers=headers, data={})
    res = json.loads(response.text)
    keys = res.keys()
    if 'code' in keys:
        if int(res["code"]) == 2001:
            return False
    else: 
        return res

def getApiToken():
    key = base64.b64decode(config.PRIVATE_KEY)
    iat = int(time.mktime(datetime.datetime.now().timetuple()))
    claims = {
        "exp": iat + 1*60*60,
        "jti": hex(random.getrandbits(12)).upper()
    }

    jwt_token = jwt.encode(claims, key, algorithm="RS256")
    ret = requests.post('https://dauth.' + config.HOST + '/api/v1/sessions/generate_jwt',json={'kid': config.UID, 'jwt_token': jwt_token})
    token = ret.json().get('token')
    return token

def checkUser(user):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM users WHERE id ={user.id}')
    users = cursor.fetchall()

    if len(users) == 1:
        for user in users:
            if user[3] == 0:
                return False
            else:
                return True
    else:
        cursor.execute("INSERT INTO users (id, name, username, status) VALUES (?, ?, ?, ?)", (user.id, user.first_name, user.username, 0))
        connection.commit()
        return False
    connection.close()

def updateUser(user):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE users SET status = {user.status} WHERE id = {user.id}')
    connection.commit()
    connection.close()
    return True

def isAdmin(id):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT status FROM users WHERE id = {id} LIMIT 1')
    users = cursor.fetchall()
    if len(users) == 1:
        for user in users:
            if user[0] == 2:
                return True
            else:
                return False

def writeOrderBase(order):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    print(order)
    cursor.execute("INSERT INTO orders (type, summ, orderSumm, price, percent, user_id, date, status, profit, profitCrypto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (order["type"], order["summ"], order["ressumm"], order["price"], order["percent"], order["user_id"], order["date"], 2, order["profit"], order["profitCrypto"]))
    connection.commit()
    cursor.execute(f'SELECT id FROM orders WHERE date = {order["date"]} LIMIT 1')
    orders = cursor.fetchall()
    connection.close()
    for res in orders:
        return res[0]
    
def orderUpdate(id, status):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE orders SET status = {status} WHERE id = {id}')
    connection.commit()
    connection.close()
    return True

def orderUpdateIdMessage(id, id_message, textProfit):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE orders SET id_message = "{id_message}", textProfit = "{textProfit}" WHERE id = {id}')
    connection.commit()
    connection.close()
    return True

def orderIdMessage(orderId, priceTo):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT id_message, textProfit, price FROM orders WHERE id = {orderId}')
    message = cursor.fetchall()
    for mes in message:
        res = list()
        res.append(mes[0])
        res.append(mes[1])
        res.append(mes[2])
        spred = float(mes[2]) - float(priceTo)
        res.append(spred)
        cursor.execute(f'UPDATE orders SET priceSend = "{priceTo}", spred = "{spred}" WHERE id = {orderId}')
        connection.commit()
        connection.close()
        return res

def getUserStatistics(id):
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT SUM(profit) as profit FROM orders WHERE user_id = {id} AND status = 1')
    statistics = cursor.fetchall()
    for stat in statistics:
        if stat[0] != None:
            return stat[0]
        else:
            return 0
        
def getOrders():
    connection = sqlite3.connect('base.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM orders')
    orders = cursor.fetchall()
    return orders
