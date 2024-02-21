from telebot import types
import json
import sqlite3
import base64
import time
import datetime
import random
import requests
import jwt

import config

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
        if userBid.PercentMoney == "money":
            summ = float(userBid.summ) / float(rate)
            percent = userBid.Percent * summ
            if userBid.Money == "usd":
                percentEx = 0.002 * summ 
            else: 
                percentEx = 0.0025 * summ
            if userBid.Crypto == "usdt":
                summ = summ - percent - percentEx - 2.5 
            else: 
                summ = summ - percent - percentEx - 0.00015
            profit = percent * float(rate)
            profitCrypto = profit / float(rate)
        elif userBid.PercentMoney == "crypto":
            if userBid.Crypto == "usdt" and userBid.Money == "rub":
                summ = (userBid.Percent * float(userBid.summ) + float(userBid.summ) + 2.5 + 0.0025 * float(userBid.summ)) * float(rate)
                profit = summ - ((float(userBid.summ) + 2.5 + 0.0025 * float(userBid.summ)) * float(rate))
                summ = format(summ, '.2f')
            elif userBid.Crypto == "usdt" and userBid.Money == "usd":
                summ = (userBid.Percent * float(userBid.summ) + float(userBid.summ) + 2.5 + 0.002* float(userBid.summ)) * float(rate)
                profit = summ - ((float(userBid.summ) + 2.5 + 0.002 * float(userBid.summ)) * float(rate))
                summ = format(summ, '.2f')
            elif userBid.Crypto == "btc" and userBid.Money == "rub":
                summ = (userBid.Percent * float(userBid.summ) + float(userBid.summ) + 0.00015 + 0.0025* float(userBid.summ)) * float(rate)
                profit = summ - ((float(userBid.summ) + 0.00015 + 0.0025 * float(userBid.summ)) * float(rate))
                summ = format(summ, '.6f')
            elif userBid.Crypto == "btc" and userBid.Money == "usd":
                summ = (userBid.Percent * float(userBid.summ) + float(userBid.summ) + 0.00015 + 0.0025* float(userBid.summ)) * float(rate)
                profit = summ - ((float(userBid.summ) + 0.00015 + 0.002 * float(userBid.summ)) * float(rate))
                summ = format(summ, '.6f')
            profitCrypto = profit / float(rate)

        param["summ"] = summ
        param["price"] = rate
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


    
