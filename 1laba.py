# food_delivery.py
import json
from datetime import datetime
from typing import List, Optional

# Исключения
class FoodError(Exception):
    pass

class NoMoneyError(FoodError):
    pass

class RestaurantClosedError(FoodError):
    pass

# Классы
class User:
    def __init__(self, user_id: int, name: str, phone: str, balance: float = 0):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.balance = balance
        self.orders = []
    
    def add_money(self, amount: float):
        self.balance += amount
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'balance': self.balance
        }

class Restaurant:
    def __init__(self, rest_id: int, name: str, address: str):
        self.rest_id = rest_id
        self.name = name
        self.address = address
        self.menu = {}  # название -> цена
        self.is_open = True
    
    def add_dish(self, name: str, price: float):
        self.menu[name] = price
    
    def to_dict(self):
        return {
            'rest_id': self.rest_id,
            'name': self.name,
            'address': self.address,
            'menu': self.menu,
            'is_open': self.is_open
        }

class Order:
    def __init__(self, order_id: int, user: User, restaurant: Restaurant, items: dict):
        self.order_id = order_id
        self.user = user
        self.restaurant = restaurant
        self.items = items  # название -> количество
        
        # Правильно считаем сумму
        self.total = 0
        for item_name, quantity in items.items():
            price = restaurant.menu.get(item_name, 0)
            self.total += price * quantity
            
        self.status = "created"
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user.user_id,
            'rest_id': self.restaurant.rest_id,
            'items': self.items,
            'total': self.total,
            'status': self.status
        }

# Основная система
class FoodDelivery:
    def __init__(self):
        self.users = []
        self.restaurants = []
        self.orders = []
        self.next_user_id = 1
        self.next_rest_id = 1
        self.next_order_id = 1
    
    # CRUD операции
    def add_user(self, name: str, phone: str) -> User:
        user = User(self.next_user_id, name, phone)
        self.users.append(user)
        self.next_user_id += 1
        return user
    
    def add_restaurant(self, name: str, address: str) -> Restaurant:
        rest = Restaurant(self.next_rest_id, name, address)
        self.restaurants.append(rest)
        self.next_rest_id += 1
        return rest
    
    def create_order(self, user_id: int, rest_id: int, items: dict) -> Order:
        user = self.find_user(user_id)
        rest = self.find_restaurant(rest_id)
        
        if not user:
            raise FoodError("Пользователь не найден")
        if not rest:
            raise FoodError("Ресторан не найден")
        if not rest.is_open:
            raise RestaurantClosedError("Ресторан закрыт")
        
        # Считаем сумму заказа
        total_cost = 0
        for item_name, quantity in items.items():
            if item_name not in rest.menu:
                raise FoodError(f"Блюдо {item_name} не найдено в меню")
            total_cost += rest.menu[item_name] * quantity
        
        if user.balance < total_cost:
            raise NoMoneyError(f"Не хватает денег. Нужно: {total_cost}, есть: {user.balance}")
        
        # Создаем заказ
        order = Order(self.next_order_id, user, rest, items)
        self.orders.append(order)
        self.next_order_id += 1
        
        # Списываем деньги
        user.balance -= total_cost
        user.orders.append(order)
        
        return order
    
    def find_user(self, user_id: int) -> Optional[User]:
        for u in self.users:
            if u.user_id == user_id:
                return u
        return None
    
    def find_restaurant(self, rest_id: int) -> Optional[Restaurant]:
        for r in self.restaurants:
            if r.rest_id == rest_id:
                return r
        return None
    
    # Работа с файлами
    def save_to_json(self, filename: str):
        data = {
            'users': [u.to_dict() for u in self.users],
            'restaurants': [r.to_dict() for r in self.restaurants],
            'orders': [o.to_dict() for o in self.orders],
            'next_ids': {
                'user': self.next_user_id,
                'rest': self.next_rest_id,
                'order': self.next_order_id
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Очищаем текущие данные
        self.users = []
        self.restaurants = []
        self.orders = []
        
        # Восстанавливаем пользователей
        for u_data in data['users']:
            user = User(u_data['user_id'], u_data['name'], u_data['phone'], u_data['balance'])
            self.users.append(user)
        
        # Восстанавливаем рестораны
        for r_data in data['restaurants']:
            rest = Restaurant(r_data['rest_id'], r_data['name'], r_data['address'])
            rest.menu = r_data['menu']
            rest.is_open = r_data['is_open']
            self.restaurants.append(rest)
        
        # Восстанавливаем заказы
        for o_data in data['orders']:
            user = self.find_user(o_data['user_id'])
            rest = self.find_restaurant(o_data['rest_id'])
            if user and rest:
                order = Order(o_data['order_id'], user, rest, o_data['items'])
                order.status = o_data['status']
                self.orders.append(order)
                if order not in user.orders:  # избегаем дублирования
                    user.orders.append(order)
        
        # Восстанавливаем счетчики ID
        self.next_user_id = data['next_ids']['user']
        self.next_rest_id = data['next_ids']['rest']
        self.next_order_id = data['next_ids']['order']

# Демо работа
def main():
    system = FoodDelivery()
    
    # Создаем тестовые данные
    user1 = system.add_user("Вася", "+79991112233")
    user1.add_money(1000)
    
    rest1 = system.add_restaurant("ПиццаШоп", "ул. Ленина 1")
    rest1.add_dish("Пепперони", 450)
    rest1.add_dish("Маргарита", 380)
    
    print("Доступные рестораны:")
    for rest in system.restaurants:
        print(f"{rest.rest_id}. {rest.name} - {rest.menu}")
    
    print(f"\nБаланс Васи: {user1.balance}")
    
    # Пытаемся сделать заказ
    try:
        order = system.create_order(1, 1, {"Пепперони": 2})
        print(f"Заказ создан! Сумма: {order.total}")
        print(f"Остаток денег: {user1.balance}")
    except FoodError as e:
        print(f"Ошибка: {e}")
    
    # Сохраняем в JSON
    system.save_to_json("food_data.json")
    print("Данные сохранены в food_data.json")

if __name__ == "__main__":
    main()