# food_delivery.py
# система доставки еды для лабораторной работы
# сделал: студент группы ИВТ-202

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

# перечисление для статусов заказа
class OrderStatus:
    created = "created"
    processing = "processing"
    delivering = "delivering"
    completed = "completed"
    cancelled = "cancelled"

# свои ошибки для системы
class DeliveryError(Exception):
    pass

class UserNotFoundError(DeliveryError):
    pass

class RestaurantNotFoundError(DeliveryError):
    pass

class DishNotFoundError(DeliveryError):
    pass

class NotEnoughMoneyError(DeliveryError):
    pass

class RestaurantClosedError(DeliveryError):
    pass

# класс блюда
class Dish:
    """блюдо в меню ресторана"""
    
    def __init__(self, name: str, price: float, desc: str = "", category: str = "основное"):
        self.name = name
        self.price = price
        self.desc = desc
        self.category = category
    
    # в словарь для json
    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'desc': self.desc,
            'category': self.category
        }
    
    # в xml элемент
    def to_xml(self):
        dish_elem = ET.Element('dish')
        ET.SubElement(dish_elem, 'name').text = self.name
        ET.SubElement(dish_elem, 'price').text = str(self.price)
        ET.SubElement(dish_elem, 'desc').text = self.desc
        ET.SubElement(dish_elem, 'category').text = self.category
        return dish_elem
    
    def __str__(self):
        return f"{self.name} - {self.price} руб."

# класс пользователя
class User:
    """пользователь системы"""
    
    def __init__(self, uid: int, name: str, email: str, phone: str, money: float = 0.0):
        self.id = uid
        self.name = name
        self.email = email
        self.phone = phone
        self.money = money
        self.my_orders = []  # история заказов
    
    # пополнить баланс
    def add_money(self, amount: float):
        if amount > 0:
            self.money += amount
    
    # списать деньги
    def take_money(self, amount: float):
        if amount > self.money:
            raise NotEnoughMoneyError(f"мало денег: надо {amount}, есть {self.money}")
        self.money -= amount
    
    # для сохранения в файл
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'money': self.money
        }
    
    def to_xml(self):
        user_elem = ET.Element('user')
        ET.SubElement(user_elem, 'id').text = str(self.id)
        ET.SubElement(user_elem, 'name').text = self.name
        ET.SubElement(user_elem, 'email').text = self.email
        ET.SubElement(user_elem, 'phone').text = self.phone
        ET.SubElement(user_elem, 'money').text = str(self.money)
        return user_elem

# класс ресторана
class Restaurant:
    """ресторан с меню"""
    
    def __init__(self, rid: int, name: str, address: str, phone: str = ""):
        self.id = rid
        self.name = name
        self.address = address
        self.phone = phone
        self.menu = {}  # название -> объект Dish
        self.open = True
        self.rating = 0.0
    
    # добавить блюдо
    def add_dish(self, dish: Dish):
        self.menu[dish.name] = dish
    
    # найти блюдо
    def find_dish(self, dish_name: str):
        return self.menu.get(dish_name)
    
    # открыть/закрыть
    def switch_open(self):
        self.open = not self.open
    
    # для файлов
    def to_dict(self):
        menu_dict = {name: dish.to_dict() for name, dish in self.menu.items()}
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'open': self.open,
            'rating': self.rating,
            'menu': menu_dict
        }
    
    def to_xml(self):
        rest_elem = ET.Element('restaurant')
        ET.SubElement(rest_elem, 'id').text = str(self.id)
        ET.SubElement(rest_elem, 'name').text = self.name
        ET.SubElement(rest_elem, 'address').text = self.address
        ET.SubElement(rest_elem, 'phone').text = self.phone
        ET.SubElement(rest_elem, 'open').text = str(self.open).lower()
        ET.SubElement(rest_elem, 'rating').text = str(self.rating)
        
        menu_elem = ET.SubElement(rest_elem, 'menu')
        for dish in self.menu.values():
            menu_elem.append(dish.to_xml())
        
        return rest_elem

# класс заказа
class Order:
    """заказ пользователя"""
    
    def __init__(self, oid: int, user: User, rest: Restaurant):
        self.id = oid
        self.user = user
        self.rest = rest
        self.items = {}  # что заказано: название -> количество
        self.sum = 0.0
        self.status = OrderStatus.created
        self.time = datetime.now()
        self.end_time = None
    
    # добавить блюдо в заказ
    def add_dish(self, dish_name: str, count: int = 1):
        dish = self.rest.find_dish(dish_name)
        if not dish:
            raise DishNotFoundError(f"нет блюда '{dish_name}'")
        
        if dish_name in self.items:
            self.items[dish_name] += count
        else:
            self.items[dish_name] = count
        
        self.sum += dish.price * count
    
    # поменять статус
    def change_status(self, new_status: str):
        self.status = new_status
        if new_status == OrderStatus.completed:
            self.end_time = datetime.now()
    
    # для сохранения
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user.id,
            'rest_id': self.rest.id,
            'items': self.items,
            'sum': self.sum,
            'status': self.status,
            'time': self.time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def to_xml(self):
        order_elem = ET.Element('order')
        ET.SubElement(order_elem, 'id').text = str(self.id)
        ET.SubElement(order_elem, 'user_id').text = str(self.user.id)
        ET.SubElement(order_elem, 'rest_id').text = str(self.rest.id)
        ET.SubElement(order_elem, 'sum').text = str(self.sum)
        ET.SubElement(order_elem, 'status').text = self.status
        ET.SubElement(order_elem, 'time').text = self.time.isoformat()
        
        if self.end_time:
            ET.SubElement(order_elem, 'end_time').text = self.end_time.isoformat()
        
        items_elem = ET.SubElement(order_elem, 'items')
        for dish_name, count in self.items.items():
            item_elem = ET.SubElement(items_elem, 'item')
            ET.SubElement(item_elem, 'dish').text = dish_name
            ET.SubElement(item_elem, 'count').text = str(count)
        
        return order_elem

# главный класс системы
class FoodDelivery:
    """основная система доставки"""
    
    def __init__(self):
        self.users = []
        self.restaurants = []
        self.orders = []
        self.next_uid = 1
        self.next_rid = 1
        self.next_oid = 1
    
    # добавить пользователя
    def add_user(self, name: str, email: str, phone: str) -> User:
        user = User(self.next_uid, name, email, phone)
        self.users.append(user)
        self.next_uid += 1
        return user
    
    # найти пользователя
    def find_user(self, uid: int):
        for u in self.users:
            if u.id == uid:
                return u
        return None
    
    # добавить ресторан
    def add_restaurant(self, name: str, address: str, phone: str = "") -> Restaurant:
        rest = Restaurant(self.next_rid, name, address, phone)
        self.restaurants.append(rest)
        self.next_rid += 1
        return rest
    
    # найти ресторан
    def find_rest(self, rid: int):
        for r in self.restaurants:
            if r.id == rid:
                return r
        return None
    
    # создать заказ
    def make_order(self, uid: int, rid: int) -> Order:
        user = self.find_user(uid)
        rest = self.find_rest(rid)
        
        if not user:
            raise UserNotFoundError(f"нет пользователя {uid}")
        if not rest:
            raise RestaurantNotFoundError(f"нет ресторана {rid}")
        if not rest.open:
            raise RestaurantClosedError(f"ресторан {rest.name} закрыт")
        
        order = Order(self.next_oid, user, rest)
        self.orders.append(order)
        self.next_oid += 1
        
        return order
    
    # обработать заказ (списать деньги)
    def process_order(self, oid: int) -> bool:
        order = self.find_order(oid)
        if not order:
            return False
        
        try:
            # проверяем что в заказе что-то есть
            if not order.items:
                raise DeliveryError("пустой заказ")
            
            # хватает ли денег
            if order.user.money < order.sum:
                raise NotEnoughMoneyError(
                    f"мало денег у {order.user.name}: надо {order.sum}, есть {order.user.money}"
                )
            
            # списываем
            order.user.take_money(order.sum)
            
            # меняем статус
            order.change_status(OrderStatus.processing)
            
            # добавляем в историю
            order.user.my_orders.append(order)
            
            return True
            
        except DeliveryError as e:
            print(f"ошибка: {e}")
            order.change_status(OrderStatus.cancelled)
            return False
    
    # найти заказ
    def find_order(self, oid: int):
        for o in self.orders:
            if o.id == oid:
                return o
        return None
    
    # завершить заказ
    def finish_order(self, oid: int) -> bool:
        order = self.find_order(oid)
        if order and order.status in [OrderStatus.processing, OrderStatus.delivering]:
            order.change_status(OrderStatus.completed)
            return True
        return False
    
    # отменить заказ
    def cancel_order(self, oid: int) -> bool:
        order = self.find_order(oid)
        if order and order.status != OrderStatus.completed:
            order.change_status(OrderStatus.cancelled)
            # возвращаем деньги если уже списали
            if order.status == OrderStatus.processing:
                order.user.add_money(order.sum)
            return True
        return False
    
    # --- работа с файлами ---
    
    # сохранить в json
    def save_json(self, filename: str):
        data = {
            'users': [u.to_dict() for u in self.users],
            'restaurants': [r.to_dict() for r in self.restaurants],
            'orders': [o.to_dict() for o in self.orders],
            'next_ids': {
                'user': self.next_uid,
                'rest': self.next_rid,
                'order': self.next_oid
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"сохранено в {filename}")
        except Exception as e:
            print(f"ошибка сохранения json: {e}")
    
    # загрузить из json
    def load_json(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"ошибка загрузки json: {e}")
            return
        
        # очищаем
        self.users.clear()
        self.restaurants.clear()
        self.orders.clear()
        
        # пользователи
        for u_data in data.get('users', []):
            user = User(
                u_data['id'],
                u_data['name'],
                u_data['email'],
                u_data['phone'],
                u_data['money']
            )
            self.users.append(user)
        
        # рестораны
        for r_data in data.get('restaurants', []):
            rest = Restaurant(
                r_data['id'],
                r_data['name'],
                r_data['address'],
                r_data.get('phone', '')
            )
            rest.open = r_data['open']
            rest.rating = r_data.get('rating', 0.0)
            
            # меню
            for dish_name, dish_data in r_data.get('menu', {}).items():
                dish = Dish(
                    dish_data['name'],
                    dish_data['price'],
                    dish_data.get('desc', ''),
                    dish_data.get('category', 'основное')
                )
                rest.menu[dish_name] = dish
            
            self.restaurants.append(rest)
        
        # заказы
        for o_data in data.get('orders', []):
            user = self.find_user(o_data['user_id'])
            rest = self.find_rest(o_data['rest_id'])
            
            if user and rest:
                order = Order(o_data['id'], user, rest)
                order.items = o_data['items']
                order.sum = o_data['sum']
                order.status = o_data['status']
                order.time = datetime.fromisoformat(o_data['time'])
                
                if o_data.get('end_time'):
                    order.end_time = datetime.fromisoformat(o_data['end_time'])
                
                self.orders.append(order)
        
        # id для следующих
        next_ids = data.get('next_ids', {})
        self.next_uid = next_ids.get('user', 1)
        self.next_rid = next_ids.get('rest', 1)
        self.next_oid = next_ids.get('order', 1)
        
        print(f"загружено из {filename}")
    
    # сохранить в xml
    def save_xml(self, filename: str):
        root = ET.Element('delivery_system')
        
        # пользователи
        users_elem = ET.SubElement(root, 'users')
        for user in self.users:
            users_elem.append(user.to_xml())
        
        # рестораны
        rests_elem = ET.SubElement(root, 'restaurants')
        for rest in self.restaurants:
            rests_elem.append(rest.to_xml())
        
        # заказы
        orders_elem = ET.SubElement(root, 'orders')
        for order in self.orders:
            orders_elem.append(order.to_xml())
        
        # id
        ids_elem = ET.SubElement(root, 'ids')
        ET.SubElement(ids_elem, 'user').text = str(self.next_uid)
        ET.SubElement(ids_elem, 'rest').text = str(self.next_rid)
        ET.SubElement(ids_elem, 'order').text = str(self.next_oid)
        
        # сохраняем
        tree = ET.ElementTree(root)
        try:
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            print(f"сохранено в {filename}")
        except Exception as e:
            print(f"ошибка сохранения xml: {e}")
    
    # загрузить из xml
    def load_xml(self, filename: str):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except Exception as e:
            print(f"ошибка загрузки xml: {e}")
            return
        
        # очищаем
        self.users.clear()
        self.restaurants.clear()
        self.orders.clear()
        
        # пользователи
        users_elem = root.find('users')
        if users_elem:
            for user_elem in users_elem.findall('user'):
                user = User(
                    int(user_elem.find('id').text),
                    user_elem.find('name').text,
                    user_elem.find('email').text,
                    user_elem.find('phone').text,
                    float(user_elem.find('money').text)
                )
                self.users.append(user)
        
        # рестораны
        rests_elem = root.find('restaurants')
        if rests_elem:
            for rest_elem in rests_elem.findall('restaurant'):
                rest = Restaurant(
                    int(rest_elem.find('id').text),
                    rest_elem.find('name').text,
                    rest_elem.find('address').text,
                    rest_elem.find('phone').text if rest_elem.find('phone') is not None else ""
                )
                rest.open = rest_elem.find('open').text.lower() == 'true'
                rest.rating = float(rest_elem.find('rating').text)
                
                # меню
                menu_elem = rest_elem.find('menu')
                if menu_elem:
                    for dish_elem in menu_elem.findall('dish'):
                        dish = Dish(
                            dish_elem.find('name').text,
                            float(dish_elem.find('price').text),
                            dish_elem.find('desc').text,
                            dish_elem.find('category').text
                        )
                        rest.menu[dish.name] = dish
                
                self.restaurants.append(rest)
        
        # заказы
        orders_elem = root.find('orders')
        if orders_elem:
            for order_elem in orders_elem.findall('order'):
                user_id = int(order_elem.find('user_id').text)
                rest_id = int(order_elem.find('rest_id').text)
                
                user = self.find_user(user_id)
                rest = self.find_rest(rest_id)
                
                if user and rest:
                    order = Order(int(order_elem.find('id').text), user, rest)
                    order.sum = float(order_elem.find('sum').text)
                    order.status = order_elem.find('status').text
                    order.time = datetime.fromisoformat(order_elem.find('time').text)
                    
                    end_elem = order_elem.find('end_time')
                    if end_elem is not None and end_elem.text:
                        order.end_time = datetime.fromisoformat(end_elem.text)
                    
                    # блюда в заказе
                    items_elem = order_elem.find('items')
                    if items_elem:
                        for item_elem in items_elem.findall('item'):
                            dish_name = item_elem.find('dish').text
                            count = int(item_elem.find('count').text)
                            order.items[dish_name] = count
                    
                    self.orders.append(order)
        
        # id
        ids_elem = root.find('ids')
        if ids_elem:
            self.next_uid = int(ids_elem.find('user').text)
            self.next_rid = int(ids_elem.find('rest').text)
            self.next_oid = int(ids_elem.find('order').text)
        
        print(f"загружено из {filename}")
    
    # показать статистику
    def show_stats(self):
        print("\n" + "="*40)
        print("статистика системы:")
        print(f"пользователей: {len(self.users)}")
        print(f"ресторанов: {len(self.restaurants)}")
        print(f"заказов: {len(self.orders)}")
        
        if self.orders:
            completed = [o for o in self.orders if o.status == OrderStatus.completed]
            if completed:
                total = sum(o.sum for o in completed)
                avg = total / len(completed)
                print(f"выручка: {total:.2f} руб.")
                print(f"средний заказ: {avg:.2f} руб.")
        
        print("="*40)

# демонстрация работы
def demo():
    """показать как работает система"""
    
    print("="*50)
    print("демонстрация системы доставки еды")
    print("="*50)
    
    # создаем систему
    system = FoodDelivery()
    
    # 1. пользователи
    print("\n1. создаем пользователей")
    user1 = system.add_user("иван иванов", "ivan@mail.ru", "+79161112233")
    user1.add_money(2000)
    print(f"создан: {user1.name}, деньги: {user1.money}")
    
    user2 = system.add_user("мария", "maria@mail.ru", "+79163334455")
    user2.add_money(1000)
    print(f"создан: {user2.name}, деньги: {user2.money}")
    
    # 2. рестораны
    print("\n2. создаем рестораны")
    rest1 = system.add_restaurant("пицца шоп", "ул. ленина 10", "88005553535")
    
    # блюда
    rest1.add_dish(Dish("пепперони", 550, "острая пицца", "пицца"))
    rest1.add_dish(Dish("маргарита", 450, "классическая", "пицца"))
    rest1.add_dish(Dish("салат цезарь", 350, "с курицей", "салаты"))
    print(f"создан: {rest1.name}, блюд: {len(rest1.menu)}")
    
    rest2 = system.add_restaurant("суши бар", "ул. пушкина 5")
    rest2.add_dish(Dish("филадельфия", 720, "роллы", "суши"))
    rest2.add_dish(Dish("рис", 280, "с овощами", "гарниры"))
    
    # 3. заказы
    print("\n3. делаем заказы")
    
    # нормальный заказ
    try:
        order1 = system.make_order(user1.id, rest1.id)
        order1.add_dish("пепперони", 2)
        order1.add_dish("салат цезарь", 1)
        
        print(f"заказ #{order1.id} создан, сумма: {order1.sum}")
        
        # обрабатываем
        if system.process_order(order1.id):
            print(f"заказ обработан, у {user1.name} осталось: {user1.money}")
            
            # завершаем
            system.finish_order(order1.id)
            print(f"заказ завершен")
        
    except DeliveryError as e:
        print(f"ошибка: {e}")
    
    # заказ с ошибкой (мало денег)
    print("\nпробуем заказ без денег:")
    try:
        user3 = system.add_user("бедный студент", "student@mail.ru", "+79169998877")
        user3.add_money(100)  # мало денег
        
        order2 = system.make_order(user3.id, rest2.id)
        order2.add_dish("филадельфия", 2)  # 2 * 720 = 1440
        
        print(f"заказ #{order2.id}, сумма: {order2.sum}")
        
        if system.process_order(order2.id):
            print("успех")
        else:
            print("заказ не прошел")
            
    except DeliveryError as e:
        print(f"поймали ошибку: {e}")
    
    # заказ в закрытый ресторан
    print("\nпробуем в закрытый ресторан:")
    try:
        rest2.switch_open()  # закрываем
        
        order3 = system.make_order(user2.id, rest2.id)
        order3.add_dish("рис", 1)
        
    except RestaurantClosedError as e:
        print(f"не вышло: {e}")
        rest2.switch_open()  # открываем обратно
    
    # 4. работа с файлами
    print("\n4. сохраняем в файлы")
    system.save_json("delivery_data.json")
    system.save_xml("delivery_data.xml")
    
    # 5. загружаем в новую систему
    print("\n5. загружаем данные в новую систему")
    new_system = FoodDelivery()
    new_system.load_json("delivery_data.json")
    
    # статистика
    new_system.show_stats()
    
    # 6. дополнительные операции
    print("\n6. что еще умеем:")
    
    # все заказы пользователя
    user_orders = [o for o in new_system.orders if o.user.id == user1.id]
    print(f"у {user1.name} заказов: {len(user_orders)}")
    
    # отмена заказа
    if user_orders:
        order_id = user_orders[0].id
        if new_system.cancel_order(order_id):
            print(f"заказ #{order_id} отменен")
    
    print("\n" + "="*50)
    print("демо закончено")
    print("="*50)

# запуск
if __name__ == "__main__":
    demo()
