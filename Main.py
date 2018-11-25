from telebot import TeleBot
from Client import State
from Client import Client
from DishTitles import pizzaTitles
from Order import Order
from Dish import Dish
from DishTitles import pizzaCost

#Telegram service
botToken = '507799483:AAGUMgEQqb05Jsvs86jVBD9ilSGG4BhOPFk'#Токен на бота
bot = TeleBot(botToken)#Экземпляр объекта, через который мы производим манипуляции с пользователями

#Program variables
client = {}#Словарь пользователей, вид [Пользовательский ID : Экземпляр пользователя, в котором хранятся все сведения о нём]
orders = []#Словарь заказов.


def findOrderInOrders(OrderID):#Метод для поиска заказа в списке заказов по ID
    for o in range(0, len(orders)):#Перебираем все заказы в списке заказов
        if orders[o].id == OrderID:#Видим одинаковый ID, который мы запрашиваем
            return o#Возвращаем позицию в списке с данным ID
    return None#Если ничего не нашли, то возвращаем ничего

def recountOrder(orderId):#Расчет итоговой стоимости
    ord = findOrderInOrders(orderId)#Ищем в списке заказов заказ с таким ID
    if ord is not None:#Если такой заказ существует, то
        orders[ord].totalPayment = 0#Сбрасываем текущую оплату в ноль, дабы не было суммы(и неверного ответа)
        for d in orders[ord].dishes:#Перебираем все блюда в заказе и суммируем их цены
            orders[ord].totalPayment += d.amount * d.cost#Суммируем и записываем в поле экземпляра Order(Order.py содержит опередение класса)

def getOrder(orderId):#Вывод итогового заказа по ID
    ord = findOrderInOrders(orderId)#Ищем в списке заказов заказ с таким ID
    if ord is not None:#Если такой заказ существует
        result = ''#Формируем переменную, в которую будем записывать все данные о заказе
        result += 'Заказ ID: ' + str(orderId) + '\n'#Помещаем ID заказа
        counter = 1#Счетчик для вывода номера блюда в заказе
        for d in orders[ord].dishes:#Перебираем все блюда в заказе
            result += str(counter) + '. ' + d.title + '. Количество: ' + str(d.amount) + '\n'#Выводим блюда + количество
            counter += 1#Увеличиваем счетчик на единицу
        return result#Возвращаем переменную, в которой хранится текстовое представление всего заказа в форме [№ блюа. Название блюда. Количество:]

def getClientOrder(clientId, orderId):#Поиск клиентского заказа в списке заказов самого клиента по ID заказа и ID клиента!
    for o in range(0, len(client[clientId].orders)):#Перебираем клиентские заказы, которые хранятся в поле класса Client(определение класса в Client.py)
        if client[clientId].orders[o].id == orderId:#Если мы нашли заказ с таким ID
            return o#То возращаем индекс в списке заказов клиента
    return None#Иначе ничего не возвращаем

def getClientOrders(clientID):#Получение заказов клиента по ID клиента
    if clientID not in client:#Если такого клиента нет в "Базе"
        return None#То ничего не возвращаем
    else:#Но если он есть
        result = ''#То создаем переменную, в которой будем хранить информацию в виде [ID заказа. Итог: Цена за заказ]
        for o in client[clientID].orders:#Проходимся по клиентскому списку заказов
            result += 'ID заказа: ' + str(o.id) + '. Итог: ' + str(o.totalPayment) + '\n'#Записываем данные в перменную
        return result#Возвращаем текстовое представление данных


@bot.message_handler(commands=['start'])
def onStart(message):#Вывод меню по команде /start
    if message.chat.id not in client:#Если клиента нет в "Базе"
        client[message.chat.id] = Client(message.chat.id)#То создаем экземпляр класса Client
        client[message.chat.id].name = message.from_user.first_name#Сохраняем его имя
    result = 'Привет, ' + client[message.chat.id].name + '!\n'#Переменная для формирования меню
    result += 'Меню:\n1. Создать заказ\n2. Редактировать заказ\n3. Удалить заказ'#Добавляем пункты
    bot.send_message(message.chat.id, result)#Отправялем наше сообщение клиенту
    client[message.chat.id].state = State.NONE#Устанавливаем состояние клиента в NONE(Что значит, что мы ожидаем ответа, в котором будет цифра выбора в меню)


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.NONE)#Обработчик сообщений от клиента, если его состояние NONE(Выбирает пункт меню)
def onChoosing(message):#Обработка пункта меню, который выбрал пользователь
    result = ''#Переменная для резудьтата
    try:#Конструкция try .. except - Исключения и их обработка. В случае, если что-то идет не так, как надо, выбрасываем исключение командой raise BaseException
        mode = int(message.text)#Переменная mode содержит ответ, который прислал client(в данном случае, пункт меню, которое он хочет открыть)
        if mode > 3 or mode < 1:#Если номер пункта не соответствует ожиданиям(ввел 4 или 5, а может быть 0 или вообще отрицательный), то выбрасываем исключение
            result += 'Нет такого варианта\n'#Переменная для хранения ответа
            raise BaseException()#Выбрасываем исключение
        elif mode == 1:  # Созданеи заказа
            client[message.chat.id].state = State.CHOOSED_CREATE_ORDER#Меняем состояние клиента, теперь бот ждет ответа на создание заказа
            onCreateOrder(message)#Вызываем функцию, которая займется созданием заказа
        elif mode == 2:  # Редактирование заказа
            client[message.chat.id].state = State.CHOOSED_EDIT_MODE#Меняем состояние клиента, он хочет редактировать, так пусть редактирует
            onEditOrder(message)#Вызываем функцию, которая отвечает за работу с редактированием
        elif mode == 3:  # Удаление заказа
            client[message.chat.id].state = State.CHOOSED_REMOVE_MODE#Клиент имеет статус, который говорит программе, что он хочет удалять
            onDelete(message)#Вызываем функцию, которая будет работать с удалением заказа
        else:
            onStart(message)#Ну а коли пользователь ввел чушь, то выводим меню заного
    except BaseException:#Если на ввод пользователь вместо цифр ввел буквы, то мы попадем сюда и не будем исполнять другой код
        client[message.chat.id].state = State.NONE#Поменяем его состояние на то, когда программа ждет ответа от него в виде пункта главного меню
        result += 'Ошибка! /start для открытия меню'#Дополняем переменную ответа
        bot.send_message(message.chat.id, result)#Выводим все клиенту


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CHOOSED_REMOVE_MODE)#Сюда придет ответ клиента, в случае, если его состояние говорит о том, что он хочет удалять
def onDelete(message):#Если пользователь выбрал удаление заказа
    if len(client[message.chat.id].orders) == 0:#Если количество его заказов равно нулю(он ещё не заказывал)
        bot.send_message(message.chat.id, 'Вы ещё не делали заказов! /start для вызова меню')#Выводим клиенту соответсвующее сообщение
    else:
        result = 'Выберите ID заказа:\n'#Иначе формируем его список заказов
        result += getClientOrders(message.chat.id)#Вызовом этой функции
        bot.send_message(message.chat.id, result)#Отправляем все это клиенту
        client[message.chat.id].state = State.ENTERING_ID#И меняем его состояние на то, которое говорит программе, что пользователь введет желаемый ID заказа для удаления


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.ENTERING_ID)
def onEnterIdDel(message):#Пользователь ввел ID для удаления заказа, проверяем его
    try:
        ID = int(message.text)#Берем ID который ввел пользователь
        id = findOrderInOrders(ID)#Берем индекс этого ID заказа, который ввел пользователь
        if id is None:#Если такого индекса нет в списке(заказ отсутствует)
            raise BaseException()#Выбрасываем исключение
        isBelongToClient = False#Булева переменная, которая показывает на то, принадлежит ли заказ клиенту
        for o in range(0, len(client[message.chat.id].orders)):#Пречисляем все заказы в списке клиентских заказов
            if client[message.chat.id].orders[o].id == ID:#Если нашли заказ с нужным на ID
                del client[message.chat.id].orders[o]#То удаляем его
                isBelongToClient = True#И говорим, что этот ID принадлежит клиенту
                break#Выходим преждевременно из цикла
        if isBelongToClient == True:#Да, заказ принадлежит клиенту
            del orders[id]#Тогда удаляем его из глобального списка заказов
            bot.send_message(message.chat.id, 'Заказ удален! /start для меню')#выводим соответственное сообщение
            client[message.chat.id].state = State.NONE#Меняем клинентское состояние, якобы он в меню и выбирает его пункт
        else:#Нет, заказ не принадлежит клиенту
            bot.send_message(message.chat.id, 'Этот заказ Вам не принадлежит! /start для вызова меню')#Скажем об этом
    except BaseException:#Обработка исключения, если в коде есть raise, то после строчки с ним, код пойдет сюда
        bot.send_message(message.chat.id, 'Неверный ID, попробуйте ещё раз, или /start дял меню')#Сообщаем об исключегнии и чаго делать

@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CHOOSED_CREATE_ORDER)#Клиент сюда попадет, только если он выбрал создание заказа
def onCreateOrder(message):#Пользователь выбрал в меню создание заказа, обрабатываем
    counter = 1#Счетчик номера заказа
    result = ''#Переменная для хранения вывода результата
    for title in pizzaTitles:#Перечисляем имена пицц и их номера и их стоимость и их их их...
        result += str(counter) + '. ' + title + '. Стоимость порции: ' + str(pizzaCost[counter-1]) + '\n'#Добавляем в переменную инфу
        counter += 1#Увеличиваем счетчик
    result += 'Введите номера пицц через пробел'#Добавляем ещё и эту строку
    bot.send_message(message.chat.id, result)#Выводим все что навводили
    client[message.chat.id].state = State.ENTERING_ORDER#Меняем состояние заказа. Программа ждет ввода заказа, числа через пробел

@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CHOOSED_EDIT_MODE)#Клиент выбрал редактирование
def onEditOrder(message):#Пользователь выбрал в меню редактирование заказа
    if len(client[message.chat.id].orders) == 0:#Если нет заказов
        bot.send_message(message.chat.id, 'Вы ещё не делали заказов! /start для вызова меню')
    else:
        result = ''#Формируем его заказы
        result += 'Заказы сделанные Вами:\n'
        result += getClientOrders(message.chat.id)#Получаем заказы клиента
        bot.send_message(message.chat.id, result+'Введите желаемый ID для редактирования')#Выводим список заказов
        client[message.chat.id].state = State.CHOOSING_EDIT_ID#Отправляем все клиенту

@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CHOOSING_EDIT_ID)#Сюда попадет ID, который ввел пользователь для редактирования
def onEnterId(message):#Пользователь ввел ID редактирования заказа
    try:#Обработка исключений, если ID некорректен, то идем на except
        Id = int(message.text)#Берем ID
        id = findOrderInOrders(Id)#Ищем индекс в списке заказов по ID
        if id is None:#Если не нашли такой индекс
            raise BaseException()#Выбрасываем исключение, идем на except
        result = ''#Переменная для сохранения вывода
        result += getOrder(Id)#Получаем заказ, вернее его блюда
        result += 'Введите номер блюда для редактирования, либо введите 0 для добавления блюд'
        bot.send_message(message.chat.id, result)#Отправляем клиенту
        client[message.chat.id].state = State.CHOOSING_EDIT_DISH#Меняем состояние клиенту, выбирает блюдо
        client[message.chat.id].editingOrder = Id#Сохраняем ID редактируемого заказа
        ide = getClientOrder(message.chat.id, Id)#Получаем индекс в клиентских заказах
        if ide is not None:#Если такой индекс есть
            client[message.chat.id].orders[ide].currentDish = len(
            client[message.chat.id].orders[ide].dishes)#Текущее блюдо для редактирование устанавливаем равным количеству блюд в заказе
        else: raise BaseException()#Иначе выбрасываем исключение
    except BaseException:
        bot.send_message(message.chat.id, 'Неккоректный ID! Введите ещё раз или /start для вызова меню')#Выводим сообщение


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CHOOSING_EDIT_DISH)#Клиент ввел номер блюда
def onEnterDish(message):#Пользователь вводит ID блюда для редактирования
    try:
        Val = int(message.text)#Сохраняем значение, которое ввел клиент
        if Val < 0 or Val > len(orders[findOrderInOrders(client[message.chat.id].editingOrder)].dishes):
            raise BaseException()#Если значение меньше нуля или превышает кол-во блюд, то исключение
        if Val == 0:#Если значение равно нулю
            onCreateOrder(message)#То идем создавать заказ(добавлять блюда)
        else:
            bot.send_message(message.chat.id,
                             'Введите новое значение для ' + orders[findOrderInOrders(client[message.chat.id].editingOrder)].dishes[
                                 Val - 1].title)#Выводим сообщение
            orders[findOrderInOrders(client[message.chat.id].editingOrder)].currentDish = Val - 1#Уменьшаем текущее блюдо на единицу. Инлекс в массиве блюд
            client[message.chat.id].state = State.EDITING_AMOUNT#Состояние клиента ввода кол-ва блюда
    except BaseException:
        bot.send_message(message.chat.id, 'Некорректное значение! Введите ещё раз либо /start для меню')


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.EDITING_AMOUNT)
def onEditAmount(message):#Пользователь вводит новое количество для блюда
    try:
        Val = int(message.text)#Сохраняем значение
        if Val < 0 or Val > 50:#Если меньше нуля или превышает 50, то исключение выкидываем
            raise BaseException()#на except
        if Val == 0:
            del orders[findOrderInOrders(client[message.chat.id].editingOrder)].dishes[
                orders[findOrderInOrders(client[message.chat.id].editingOrder)].currentDish]#Удаляем текущее блюдо
        else:#Иначе
            orders[findOrderInOrders(client[message.chat.id].editingOrder)].dishes[#Редактируем кол-во
                orders[findOrderInOrders(client[message.chat.id].editingOrder)].currentDish].amount = Val
        recountOrder(client[message.chat.id].editingOrder)#Перерасчитываем цену заказа
        index = -1#Сбрасываем индекс
        for i in range(0, len(client[message.chat.id].orders)):
            if client[message.chat.id].orders[i].id == orders[findOrderInOrders(client[message.chat.id].editingOrder)].id:
                index = i
                if len(client[message.chat.id].orders[i].dishes) == 0:
                    del client[message.chat.id].orders[i]
                else:
                    client[message.chat.id].orders[i] = orders[findOrderInOrders(client[message.chat.id].editingOrder)]
                break
        bot.send_message(message.chat.id, 'Изменения приняты!\n' + getOrder(orders[findOrderInOrders(client[message.chat.id].editingOrder)].id) + '\nХотите ли вы изменить контактные данные?(Да/нет)')
        client[message.chat.id].editingOrder = -1
        client[message.chat.id].orders[index].currentDish = 0
        client[message.chat.id].state = State.ASKING_CHANGING_CONTACTS
    except BaseException:
        bot.send_message(message.chat.id, 'Некорректное значение, попробуйте ещё раз или /start для меню')


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.ASKING_CHANGING_CONTACTS)
def onAnsweringQuestion(message):#Пользователь отвечает на вопрос о смене контактных данных
    if message.text == 'Да':
        client[message.chat.id].state = State.SENDING_NUMBER
        bot.send_message(message.chat.id, 'Введите номер телефона:')
    else:
        client[message.chat.id].state = State.NONE
        bot.send_message(message.chat.id, '/start для вызова меню')


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.ENTERING_ORDER)
def onEnteringOrder(message):#Пользователь вводит заказ(номера блюд)
    try:
        numbers = str.split(message.text, ' ')
        for number in numbers:
            if int(number) > len(pizzaTitles) or int(number) < 1:
                bot.send_message(message.chat.id, 'В меню нет блюда под номером ' + number)
                raise BaseException()
        if client[message.chat.id].editingOrder == -1:
            client[message.chat.id].orders.append(Order(message.chat.id, 0))
        orderID = getClientOrder(message.chat.id, client[message.chat.id].editingOrder)
        if orderID is None: orderID = -1
        for number in numbers:
            client[message.chat.id].orders[orderID].dishes.append(
                Dish(pizzaTitles[int(number) - 1], 0, pizzaCost[int(number) - 1]))
        bot.send_message(message.chat.id,
                         'Введите количество для пиццы ' + client[message.chat.id].orders[orderID].dishes[
                             client[message.chat.id].orders[orderID].currentDish].title)
        client[message.chat.id].state = State.ENTERING_AMOUNT
    except BaseException:
        bot.send_message(message.chat.id, 'Неверный ввод! Повторите ещё раз. Для вызова меню /start')


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.ENTERING_AMOUNT)
def onEnteringAmount(message):#Пользователь вводит количество для блюд(сколько и какой пиццы)
    orderID = getClientOrder(message.chat.id, client[message.chat.id].editingOrder)
    if orderID is None: orderID = -1
    d = client[message.chat.id].orders[orderID].currentDish
    if d < len(client[message.chat.id].orders[orderID].dishes):
        try:
            pizzaAmount = int(message.text)
            if pizzaAmount > 30:
                raise BaseException()
            client[message.chat.id].orders[orderID].dishes[d].amount = pizzaAmount
            if d < len(client[message.chat.id].orders[orderID].dishes) - 1:
                bot.send_message(message.chat.id,
                                 'Введите количество для пиццы ' + client[message.chat.id].orders[orderID].dishes[
                                     d + 1].title)
                client[message.chat.id].orders[orderID].currentDish = d + 1
            else:
                client[message.chat.id].state = State.WAITING_FOR_TOTAL_PAYMENT
                onWaitingPayment(message)
        except BaseException:
            bot.send_message(message.chat.id, 'Вы ввели неверное значение, попробуйте ещё раз')
            bot.send_message(message.chat.id, 'Введите количество для пиццы ' + client[message.chat.id].orders[orderID].dishes[d].title)
    elif d == 0:
        bot.send_message(message.chat.id, ' ')
        client[message.chat.id] = State.NONE
    else:
        client[message.chat.id] = State.WAITING_FOR_TOTAL_PAYMENT


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.WAITING_FOR_TOTAL_PAYMENT)
def onWaitingPayment(message):#Пользователь ожидает вывода чека с расчетными данными
    bot.send_message(message.chat.id, 'Ваш заказ:')
    orderID = getClientOrder(message.chat.id, client[message.chat.id].editingOrder)#Получаем индекс с клиентским заказом
    if orderID is None: orderID = -1#Если его нет
    client[message.chat.id].orders[orderID].totalPayment = 0#Обнуляем итоговую цену
    for dish in client[message.chat.id].orders[orderID].dishes:#Перечисляем все блюда
        bot.send_message(message.chat.id, dish.title +#Выводим
                         ' в количестве ' + str(dish.amount))
        client[message.chat.id].orders[orderID].totalPayment += dish.amount * dish.cost#Увеличиваем итоговую цену
    bot.send_message(message.chat.id, 'Итого с Вас: ' + str(client[message.chat.id].orders[orderID].totalPayment))#Отправляем клиенту
    if orderID != -1:#Если это было изменение заказа
        client[message.chat.id].state = State.NONE
        bot.send_message(message.chat.id, 'Изменения приняты!\n/start для вызова меню')
        client[message.chat.id].editingOrder = -1#Идем в меню и обнуляем инфу о заказе
    else:#Иначе выводим вообщение о подтверждении
        bot.send_message(message.chat.id, 'Введите 1 для подтверждения\n2 для отмены')
        client[message.chat.id].state = State.CONFIRM_ORDER#Ждем подтверждения заказа
    client[message.chat.id].orders[orderID].currentDish = 0


@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.CONFIRM_ORDER)
def onConfirmOrder(message):#Пользователь подтверждает заказ, обработка его ответа
    if message.text == '1':
        counter = 0
        for d in client[message.chat.id].orders[-1].dishes:
            counter += d.amount
        if counter == 0:
            del client[message.chat.id].orders[-1]
            bot.send_message(message.chat.id, 'Мы не можем обслужить Вас пустым заказом)\n/start')
            client[message.chat.id].state = State.NONE
        else:
            orders.append(client[message.chat.id].orders[-1])
            for i in range(1, 500):#Ищем индекс заказа
                if findOrderInOrders(i) is None:
                    client[message.chat.id].orders[-1].id = i
                    break
            bot.send_message(message.chat.id, 'Ваш номер заказа: ' +
                         str(client[message.chat.id].orders[-1].id) + '\nУкажите номер телефона')
            client[message.chat.id].state = State.SENDING_NUMBER
            return
    else:
        bot.send_message(message.chat.id, 'Ваш заказ обнулен! Для повтора введите /start')
        del client[message.chat.id].orders[-1]
    client[message.chat.id].state = State.NONE

@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.SENDING_NUMBER)
def onSendNumber(message):#Обработка номера, который ввел пользователь
    try:
        client[message.chat.id].phone = int(message.text)
        client[message.chat.id].state = State.SENDING_ADDRESS
        bot.send_message(message.chat.id, 'Введите адрес доставки')
    except BaseException:
        bot.send_message(message.chat.id, 'Ошибка! Введите номер заного')

@bot.message_handler(func=lambda message: message.chat.id in client and client[message.chat.id].state == State.SENDING_ADDRESS)
def onSendAddress(message):#Обработка адреса, который ввел пользователь
    client[message.chat.id].address = message.text
    bot.send_message(message.chat.id, 'Заказ принят. /start для вызова меню')
    client[message.chat.id].state = State.NONE
    return

bot.polling(none_stop=True)#Запуск бота в ожидании сообщений