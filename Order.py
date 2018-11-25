from Dish import Dish

class Order:
    id = 0#ID заказа
    clientId = 0#ID клиента, которому принадлежит заказ
    currentDish = 0#Текущее блюдо
    dishes = []#Список блюд
    totalPayment = 0#Сколько всего за заказ
    def __init__(self, clientId, Id):#Конструктор класса
        self.clientId = clientId#Запоминаем клиентский ID
        self.dishes = []#Создаем список
        if Id is None:#Если нет ID
            Id = 0#То в ноль
        self.id = Id
        self.currentDish = 0
        self.totalPayment = 0
        return