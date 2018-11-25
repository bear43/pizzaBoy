class Dish:
    title = 'null'#Наименование блюда
    amount = 0#количество этого блюда
    cost = 0#Суммарная цена
    def __init__(self, title, amount, cost):
        self.title = title#Название
        self.amount = amount#Кол-во
        self.cost = cost#Цена