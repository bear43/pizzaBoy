from enum import Enum


class State(Enum):#Возможные состояния клиента
    NONE = 0#В меню
    ENTERING_ORDER = 1#Вводит номера блюд(формирует заказ)
    ENTERING_AMOUNT = 2#Вводит количество блюд
    WAITING_FOR_TOTAL_PAYMENT = 3#Ждет итогового чека
    CONFIRM_ORDER = 4#Подтверждает заказ
    CHOOSED_CREATE_ORDER = 5#Выбрал создание заказа
    CHOOSED_EDIT_MODE = 6#Выбрал редактирование заказа
    CHOOSED_REMOVE_MODE = 7#Выбрал удаление заказа
    CHOOSING_EDIT_ID = 8#Отправляет ID для редактирования
    CHOOSING_EDIT_DISH = 9#Отправляет блюдо для редактирования
    EDITING_AMOUNT = 10#Вводит количество
    ENTERING_ID = 11#Вводит ID
    SENDING_NUMBER = 12#Отправляет номер
    SENDING_ADDRESS = 13#Отправляет адрес
    ASKING_CHANGING_CONTACTS = 14#Ожидает ответа на переопределение контактных данных

class Client:
    name = 'null'#Имя клиента
    id = -1#ID клиента
    orders = []#Список заказов
    totalPayment = 0#Суммарная стоимость
    state = State(0)#Состояние клиента
    address = ''#Адрес клиента
    phone = 0#Телефон клиента
    editingOrder = -1#ID заказа для редактирования
    def __init__(self, id):#Конструктор экземпляра класса
        self.id = id#Устанавливаем ID
        self.editingOrder = -1#Устанавливаем ID редактируемого заказа