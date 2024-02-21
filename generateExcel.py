import openpyxl
import function

def generateNewExcel():
    wb = openpyxl.Workbook()
    list = wb.active
    orders = function.getOrders()
    list.append(('#', 'Тип сделки', 'Сумма', 'Клиент получит', 'Курс', 'Комиссия', 'Доход в рублях', 'Доход в крипте', 'id сотрудника', 'Дата', 'Статус'))
    for order in orders:
        list.append(order)
    wb.save('orders.xlsx')
    return True

