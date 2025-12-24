"""
Игра "Уклоняйся от падающих объектов"
Улучшенная версия с красивым интерфейсом - ИСПРАВЛЕННЫЕ ЦВЕТА
"""
import tkinter as tk
import random
import json
import os
import time
import math
from typing import List, Tuple

class Config:
    """Класс для хранения конфигурации игры"""
    def __init__(self):
        self.WIDTH = 900
        self.HEIGHT = 700
        self.PLAYER_WIDTH = 60
        self.PLAYER_HEIGHT = 40
        self.PLAYER_SPEED = 12
        self.OBSTACLE_MIN_SIZE = 25
        self.OBSTACLE_MAX_SIZE = 55
        self.OBSTACLE_SPEED_MIN = 4
        self.OBSTACLE_SPEED_MAX = 10
        self.OBSTACLE_SPAWN_RATE = 0.025
        self.SCORE_PER_SECOND = 15
        self.GAME_SPEED = 35  # FPS
        
        # Цветовая палитра (только 6-значные HEX коды)
        self.COLORS = {
            'background': '#0a0a1a',
            'background2': '#1a1a3a',
            'background3': '#2a2a5a',
            'player': '#4a9fff',
            'player_glow': '#6abfff',
            'rock': '#8b7765',
            'rock_highlight': '#a38b75',
            'branch': '#8b5a2b',
            'branch_highlight': '#a67c52',
            'fast_obstacle': '#ffaa33',
            'fast_glow': '#ffcc66',
            'text': '#ffffff',
            'text_glow': '#aaccff',
            'button': '#3a5a8a',
            'button_hover': '#4a7abb',
            'button_text': '#ffffff',
            'score': '#ffff77',
            'score_glow': '#ffffaa',
            'game_over': '#ff5555',
            'game_over_glow': '#ff8888',
            'health': '#55ff55',
            'time': '#aaaaff',
            'cockpit': '#aaccff',
            'engine': '#ff6633',
            'engine_glow': '#ffaa33',
            'gun': '#666666',
            'leaf': '#6b8e23',
            'leaf_outline': '#8fbc8f'
        }

class Particle:
    """Класс частиц для эффектов"""
    def __init__(self, x, y, color, speed=2, size=3, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = size
        self.life = life
        self.max_life = life
        angle = random.uniform(0, math.pi * 2)
        self.vx = math.cos(angle) * random.uniform(0.5, 1.5) * speed
        self.vy = math.sin(angle) * random.uniform(0.5, 1.5) * speed
        self.id = None
        
    def update(self):
        """Обновление частицы"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # гравитация
        self.life -= 1
        self.size = max(1, self.size * (self.life / self.max_life))
        return self.life > 0

class Player:
    """Класс игрока - космический корабль"""
    def __init__(self, canvas: tk.Canvas, config: Config):
        self.canvas = canvas
        self.config = config
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.x = config.WIDTH // 2
        self.y = config.HEIGHT - self.height - 40
        self.speed = config.PLAYER_SPEED
        self.ids = []  # Все элементы корабля
        self.particles = []
        self.engine_particle_timer = 0
        self.original_coords = {}  # Сохраняем оригинальные координаты
        
    def create_ship(self):
        """Создание космического корабля"""
        # Основной корпус (треугольник)
        hull_points = [
            self.x, self.y - self.height//2,  # верх
            self.x - self.width//2, self.y + self.height//2,  # левый низ
            self.x + self.width//4, self.y + self.height//3,  # правый средний
            self.x + self.width//2, self.y + self.height//2,  # правый низ
            self.x, self.y - self.height//2  # закрываем полигон
        ]
        
        hull = self.canvas.create_polygon(
            hull_points,
            fill=self.config.COLORS['player'],
            outline=self.config.COLORS['player_glow'],
            width=2,
            smooth=True
        )
        self.ids.append(hull)
        self.original_coords[hull] = hull_points
        
        # Кабина (овал)
        cockpit = self.canvas.create_oval(
            self.x - self.width//6, self.y - self.height//3,
            self.x + self.width//6, self.y,
            fill=self.config.COLORS['cockpit'],
            outline='#ffffff',
            width=1
        )
        self.ids.append(cockpit)
        self.original_coords[cockpit] = [self.x - self.width//6, self.y - self.height//3,
                                        self.x + self.width//6, self.y]
        
        # Двигатели (треугольники)
        engine_left_points = [
            self.x - self.width//3, self.y + self.height//2,
            self.x - self.width//3 - 10, self.y + self.height//2 + 15,
            self.x - self.width//3 + 10, self.y + self.height//2 + 15
        ]
        
        engine_left = self.canvas.create_polygon(
            engine_left_points,
            fill=self.config.COLORS['engine'],
            outline=self.config.COLORS['engine_glow'],
            width=1
        )
        self.ids.append(engine_left)
        self.original_coords[engine_left] = engine_left_points
        
        engine_right_points = [
            self.x + self.width//3, self.y + self.height//2,
            self.x + self.width//3 - 10, self.y + self.height//2 + 15,
            self.x + self.width//3 + 10, self.y + self.height//2 + 15
        ]
        
        engine_right = self.canvas.create_polygon(
            engine_right_points,
            fill=self.config.COLORS['engine'],
            outline=self.config.COLORS['engine_glow'],
            width=1
        )
        self.ids.append(engine_right)
        self.original_coords[engine_right] = engine_right_points
        
        # Орудия (прямоугольники)
        gun_left = self.canvas.create_rectangle(
            self.x - self.width//2 + 5, self.y - self.height//4,
            self.x - self.width//2 + 15, self.y + self.height//4,
            fill=self.config.COLORS['gun'],
            outline='#888888',
            width=1
        )
        self.ids.append(gun_left)
        self.original_coords[gun_left] = [self.x - self.width//2 + 5, self.y - self.height//4,
                                         self.x - self.width//2 + 15, self.y + self.height//4]
        
        gun_right = self.canvas.create_rectangle(
            self.x + self.width//2 - 15, self.y - self.height//4,
            self.x + self.width//2 - 5, self.y + self.height//4,
            fill=self.config.COLORS['gun'],
            outline='#888888',
            width=1
        )
        self.ids.append(gun_right)
        self.original_coords[gun_right] = [self.x + self.width//2 - 15, self.y - self.height//4,
                                          self.x + self.width//2 - 5, self.y + self.height//4]
        
    def create_particles(self):
        """Создание частиц выхлопа"""
        if self.engine_particle_timer <= 0:
            # Цвета для частиц
            particle_colors = ['#ff6633', '#ffaa33', '#ffcc33']
            
            # Левый двигатель
            for _ in range(2):
                p = Particle(
                    self.x - self.width//3 + random.uniform(-5, 5),
                    self.y + self.height//2 + 15,
                    random.choice(particle_colors),
                    speed=random.uniform(2, 4),
                    size=random.uniform(2, 4),
                    life=random.randint(15, 25)
                )
                p.id = self.canvas.create_oval(
                    p.x - p.size, p.y - p.size,
                    p.x + p.size, p.y + p.size,
                    fill=p.color,
                    outline=''
                )
                self.particles.append(p)
            
            # Правый двигатель
            for _ in range(2):
                p = Particle(
                    self.x + self.width//3 + random.uniform(-5, 5),
                    self.y + self.height//2 + 15,
                    random.choice(particle_colors),
                    speed=random.uniform(2, 4),
                    size=random.uniform(2, 4),
                    life=random.randint(15, 25)
                )
                p.id = self.canvas.create_oval(
                    p.x - p.size, p.y - p.size,
                    p.x + p.size, p.y + p.size,
                    fill=p.color,
                    outline=''
                )
                self.particles.append(p)
            
            self.engine_particle_timer = 3
        
        self.engine_particle_timer -= 1
        
    def update_particles(self):
        """Обновление частиц"""
        for particle in self.particles[:]:
            if particle.update():
                self.canvas.coords(
                    particle.id,
                    particle.x - particle.size, particle.y - particle.size,
                    particle.x + particle.size, particle.y + particle.size
                )
            else:
                self.canvas.delete(particle.id)
                self.particles.remove(particle)
        
    def move(self, dx: int):
        """Движение игрока"""
        new_x = self.x + dx * self.speed
        new_x = max(self.width // 2, min(new_x, self.config.WIDTH - self.width // 2))
        
        # Вычисляем смещение
        dx_move = new_x - self.x
        self.x = new_x
        
        # Обновляем все элементы корабля
        for item_id in self.ids:
            if item_id in self.original_coords:
                orig_coords = self.original_coords[item_id]
                new_coords = []
                
                # Для каждого элемента применяем смещение по X
                if len(orig_coords) == 4:  # Прямоугольники/овалы
                    new_coords = [
                        orig_coords[0] + dx_move, orig_coords[1],
                        orig_coords[2] + dx_move, orig_coords[3]
                    ]
                else:  # Полигоны
                    for i in range(0, len(orig_coords), 2):
                        new_coords.append(orig_coords[i] + dx_move)
                        new_coords.append(orig_coords[i+1])
                
                self.canvas.coords(item_id, *new_coords)
        
        # Обновляем частицы
        self.create_particles()
            
    def get_bbox(self) -> Tuple[int, int, int, int]:
        """Получить границы игрока (упрощенный прямоугольник для коллизий)"""
        return (
            self.x - self.width//2 + 5,
            self.y - self.height//2 + 5,
            self.x + self.width//2 - 5,
            self.y + self.height//2 + 10
        )
        
    def destroy(self):
        """Удаление корабля"""
        for item_id in self.ids:
            self.canvas.delete(item_id)
        for particle in self.particles:
            self.canvas.delete(particle.id)
        self.particles.clear()
        self.ids.clear()
        self.original_coords.clear()

class Obstacle:
    """Класс препятствий с разными формами"""
    def __init__(self, canvas: tk.Canvas, config: Config):
        self.canvas = canvas
        self.config = config
        self.type = random.choice(['rock', 'branch', 'fast_rock', 'fast_branch'])
        self.is_fast = 'fast' in self.type
        
        # Размеры
        base_size = random.randint(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
        if self.is_fast:
            self.size = int(base_size * 0.8)
            self.speed = random.randint(config.OBSTACLE_SPEED_MIN + 3, config.OBSTACLE_SPEED_MAX + 4)
        else:
            self.size = base_size
            self.speed = random.randint(config.OBSTACLE_SPEED_MIN, config.OBSTACLE_SPEED_MAX)
        
        # Начальная позиция
        self.x = random.randint(self.size, config.WIDTH - self.size)
        self.y = -self.size
        
        self.ids = []  # Все элементы препятствия
        self.particles = []
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.original_coords = {}  # Сохраняем оригинальные координаты
        
    def create_rock(self):
        """Создание камня (многоугольник)"""
        points = []
        num_points = random.randint(6, 10)
        center_x, center_y = 0, 0
        
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            radius = self.size // 2 * random.uniform(0.7, 1.3)
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            points.extend([center_x + x, center_y + y])
        
        # Создаем камень
        rock = self.canvas.create_polygon(
            points,
            fill=self.config.COLORS['rock'],
            outline=self.config.COLORS['rock_highlight'],
            width=2,
            smooth=True
        )
        self.ids.append(rock)
        self.original_coords[rock] = points
        
        # Текстура камня (кружочки)
        for _ in range(random.randint(2, 4)):
            rx = random.uniform(-self.size//3, self.size//3)
            ry = random.uniform(-self.size//3, self.size//3)
            rsize = random.randint(2, self.size//6)
            texture = self.canvas.create_oval(
                center_x + rx - rsize, center_y + ry - rsize,
                center_x + rx + rsize, center_y + ry + rsize,
                fill=self.config.COLORS['rock_highlight'],
                outline=''
            )
            self.ids.append(texture)
            self.original_coords[texture] = [center_x + rx - rsize, center_y + ry - rsize,
                                            center_x + rx + rsize, center_y + ry + rsize]
        
    def create_branch(self):
        """Создание ветки (древовидная структура)"""
        # Основная ветка (толстая линия)
        main_length = self.size * random.uniform(1.5, 2.5)
        branch = self.canvas.create_line(
            0, -main_length//2,
            0, main_length//2,
            width=self.size//4,
            fill=self.config.COLORS['branch'],
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )
        self.ids.append(branch)
        self.original_coords[branch] = [0, -main_length//2, 0, main_length//2]
        
        # Боковые веточки
        num_branches = random.randint(2, 4)
        for _ in range(num_branches):
            bx = random.uniform(-self.size//2, self.size//2)
            by = random.uniform(-main_length//3, main_length//3)
            blength = random.uniform(self.size//2, self.size)
            angle = random.uniform(math.pi/4, 3*math.pi/4)
            
            bx2 = bx + math.cos(angle) * blength
            by2 = by + math.sin(angle) * blength
            
            side_branch = self.canvas.create_line(
                bx, by,
                bx2, by2,
                width=max(2, self.size//8),
                fill=self.config.COLORS['branch_highlight'],
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )
            self.ids.append(side_branch)
            self.original_coords[side_branch] = [bx, by, bx2, by2]
        
        # Листья (овалы)
        for _ in range(random.randint(3, 6)):
            lx = random.uniform(-self.size//2, self.size//2)
            ly = random.uniform(-main_length//2, main_length//2)
            lsize = random.randint(2, self.size//8)
            leaf = self.canvas.create_oval(
                lx - lsize, ly - lsize,
                lx + lsize, ly + lsize,
                fill=self.config.COLORS['leaf'],
                outline=self.config.COLORS['leaf_outline'],
                width=1
            )
            self.ids.append(leaf)
            self.original_coords[leaf] = [lx - lsize, ly - lsize, lx + lsize, ly + lsize]
        
    def create(self):
        """Создание препятствия"""
        if 'rock' in self.type:
            self.create_rock()
        else:
            self.create_branch()
            
        # Добавляем свечение для быстрых объектов (контурный круг)
        if self.is_fast:
            glow_size = self.size + 10
            glow = self.canvas.create_oval(
                -glow_size//2, -glow_size//2,
                glow_size//2, glow_size//2,
                fill='',
                outline=self.config.COLORS['fast_glow'],
                width=2
            )
            self.ids.append(glow)
            self.original_coords[glow] = [-glow_size//2, -glow_size//2, glow_size//2, glow_size//2]
            
    def update(self) -> bool:
        """Обновление позиции препятствия"""
        self.y += self.speed
        self.rotation += self.rotation_speed
        
        # Обновляем все элементы препятствия
        for item_id in self.ids:
            if item_id in self.original_coords:
                orig_coords = self.original_coords[item_id]
                new_coords = []
                
                if len(orig_coords) == 4:  # Для овалов/прямоугольников/линий
                    # Для линий
                    if self.canvas.type(item_id) == 'line':
                        for i in range(0, len(orig_coords), 2):
                            # Поворот
                            angle = math.radians(self.rotation)
                            x_rot = orig_coords[i] * math.cos(angle) - orig_coords[i+1] * math.sin(angle)
                            y_rot = orig_coords[i] * math.sin(angle) + orig_coords[i+1] * math.cos(angle)
                            
                            # Смещение
                            new_coords.append(x_rot + self.x)
                            new_coords.append(y_rot + self.y)
                    else:  # Для овалов/прямоугольников
                        dx = self.x - (orig_coords[0] + orig_coords[2]) / 2
                        dy = self.y - (orig_coords[1] + orig_coords[3]) / 2
                        new_coords = [
                            orig_coords[0] + dx, orig_coords[1] + dy,
                            orig_coords[2] + dx, orig_coords[3] + dy
                        ]
                else:  # Для полигонов
                    for i in range(0, len(orig_coords), 2):
                        # Поворот
                        angle = math.radians(self.rotation)
                        x_rot = orig_coords[i] * math.cos(angle) - orig_coords[i+1] * math.sin(angle)
                        y_rot = orig_coords[i] * math.sin(angle) + orig_coords[i+1] * math.cos(angle)
                        
                        # Смещение
                        new_coords.append(x_rot + self.x)
                        new_coords.append(y_rot + self.y)
                
                self.canvas.coords(item_id, *new_coords)
            
        # Возвращает True если препятствие ушло за экран
        return self.y > self.config.HEIGHT + self.size * 2
        
    def get_bbox(self) -> Tuple[int, int, int, int]:
        """Получить границы препятствия"""
        return (
            self.x - self.size//2,
            self.y - self.size//2,
            self.x + self.size//2,
            self.y + self.size//2
        )
        
    def destroy(self):
        """Удаление препятствия"""
        for item_id in self.ids:
            self.canvas.delete(item_id)
        self.ids.clear()
        self.original_coords.clear()

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.config = Config()
        
        # Создание главного окна
        self.root = tk.Tk()
        self.root.title("🚀 Космический уклонятель v2.0")
        self.root.geometry(f"{self.config.WIDTH}x{self.config.HEIGHT}")
        self.root.configure(bg=self.config.COLORS['background'])
        self.root.resizable(True, True)
        
        # Создание холста
        self.canvas = tk.Canvas(
            self.root,
            bg=self.config.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Привязка событий
        self.canvas.bind('<Configure>', self.on_resize)
        self.root.bind('<Key>', self.on_key_press)
        
        # Игровые переменные
        self.player = None
        self.obstacles: List[Obstacle] = []
        self.score = 0
        self.high_score = 0
        self.game_time = 0
        self.game_active = False
        self.start_time = 0
        self.stars = []  # Фоновые звезды
        self.explosion_particles = []
        
        # Элементы интерфейса
        self.score_text = None
        self.time_text = None
        self.high_score_text = None
        self.health_text = None
        self.game_over_texts = []
        self.menu_animation_items = []
        
        # Загрузка рекорда
        self.load_high_score()
        
        # Инициализация меню
        self.init_menu()
        
    def create_background(self):
        """Создание фона со звездами"""
        # Сплошной фон
        self.canvas.create_rectangle(
            0, 0,
            self.config.WIDTH, self.config.HEIGHT,
            fill=self.config.COLORS['background'],
            outline=''
        )
        
        # Создание звезд
        for _ in range(80):
            x = random.randint(0, self.config.WIDTH)
            y = random.randint(0, self.config.HEIGHT)
            size = random.uniform(0.5, 2)
            brightness = random.randint(150, 255)
            color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
            
            star = self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color,
                outline=''
            )
            self.stars.append(star)
            
        # Несколько больших звезд
        for _ in range(10):
            x = random.randint(0, self.config.WIDTH)
            y = random.randint(0, self.config.HEIGHT)
            size = random.uniform(1.5, 3)
            color = f'#{random.randint(200, 255):02x}{random.randint(200, 255):02x}ff'
            
            star = self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color,
                outline='#ffffff',
                width=1
            )
            self.stars.append(star)
            
    def update_background(self):
        """Анимация фоновых звезд"""
        for star in self.stars:
            # Медленное мерцание
            if random.random() < 0.01:
                brightness = random.randint(150, 255)
                color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
                self.canvas.itemconfig(star, fill=color)
                
    def load_high_score(self):
        """Загрузка рекорда"""
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            else:
                self.high_score = 0
        except:
            self.high_score = 0
            
    def save_high_score(self):
        """Сохранение рекорда"""
        try:
            with open("highscore.json", "w", encoding='utf-8') as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
            
    def on_resize(self, event):
        """Обработка изменения размера окна"""
        try:
            if event.width > 100 and event.height > 100:
                self.config.WIDTH = event.width
                self.config.HEIGHT = event.height
        except Exception as e:
            print(f"Ошибка изменения размера: {e}")
            
    def on_key_press(self, event):
        """Обработка нажатия клавиш"""
        try:
            key = event.keysym.lower()
            
            if key in ['left', 'a'] and self.game_active:
                self.player.move(-1)
            elif key in ['right', 'd'] and self.game_active:
                self.player.move(1)
            elif key == 'return' or key == 'enter':
                if not self.game_active:
                    self.start_game()
            elif key == 'escape':
                if self.game_active:
                    self.show_menu()
                else:
                    self.root.quit()
            elif key == 'r':  # Работает всегда!
                if not self.game_active:
                    self.start_game()
        except Exception as e:
            print(f"Ошибка обработки клавиши: {e}")
            
    def create_glow_text(self, x, y, text, font_size, color1, color2):
        """Создание текста с эффектом свечения (исправленная версия)"""
        texts = []
        
        # Создаем три слоя для свечения (разные смещения и цвета)
        glow_colors = [color2, self.lighten_color(color2, 0.3), self.lighten_color(color2, 0.6)]
        offsets = [(3, 3), (2, 2), (1, 1)]
        
        for offset, glow_color in zip(offsets, glow_colors):
            text_id = self.canvas.create_text(
                x + offset[0], y + offset[1],
                text=text,
                font=("Arial", font_size, "bold"),
                fill=glow_color,
                anchor=tk.CENTER
            )
            texts.append(text_id)
            
        # Основной текст
        main_text = self.canvas.create_text(
            x, y,
            text=text,
            font=("Arial", font_size, "bold"),
            fill=color1,
            anchor=tk.CENTER
        )
        texts.append(main_text)
        
        return texts
        
    def lighten_color(self, color_hex, factor=0.3):
        """Осветлить цвет"""
        # Удаляем # если есть
        color_hex = color_hex.lstrip('#')
        
        # Конвертируем в RGB
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        
        # Осветляем
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        # Возвращаем в HEX формате
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def init_menu(self):
        """Инициализация красивого меню"""
        self.clear_canvas()
        self.create_background()
        self.menu_animation_items = []
        
        # Заголовок с градиентом
        title_texts = self.create_glow_text(
            self.config.WIDTH // 2,
            self.config.HEIGHT // 4,
            "КОСМИЧЕСКИЙ УКЛОНЯТЕЛЬ",
            42,
            self.config.COLORS['text'],
            self.config.COLORS['text_glow']
        )
        self.menu_animation_items.extend(title_texts)
        
        # Анимированный корабль в меню
        menu_ship_points = [
            self.config.WIDTH // 2, 100,
            self.config.WIDTH // 2 - 40, 160,
            self.config.WIDTH // 2 + 20, 140,
            self.config.WIDTH // 2 + 40, 160
        ]
        
        menu_ship = self.canvas.create_polygon(
            menu_ship_points,
            fill=self.config.COLORS['player'],
            outline=self.config.COLORS['player_glow'],
            width=2,
            smooth=True
        )
        
        # Планеты в меню
        planet1 = self.canvas.create_oval(
            self.config.WIDTH // 4 - 50, self.config.HEIGHT // 3 - 50,
            self.config.WIDTH // 4 + 50, self.config.HEIGHT // 3 + 50,
            fill='#ff9966',
            outline='#ffcc99',
            width=3
        )
        
        planet2 = self.canvas.create_oval(
            self.config.WIDTH * 3 // 4 - 40, self.config.HEIGHT // 2 - 40,
            self.config.WIDTH * 3 // 4 + 40, self.config.HEIGHT // 2 + 40,
            fill='#6699ff',
            outline='#99ccff',
            width=3
        )
        
        self.menu_animation_items.extend([menu_ship, planet1, planet2])
        
        # Информация об управлении
        controls = [
            "🎮 УПРАВЛЕНИЕ 🎮",
            "← → или A D - Движение корабля",
            "ENTER - Начать игру",
            "R - Перезапуск (работает всегда!)",
            "ESC - Меню/Выход"
        ]
        
        for i, control in enumerate(controls):
            y_pos = self.config.HEIGHT // 2 + i * 35
            if i == 0:
                # Заголовок управления
                control_texts = self.create_glow_text(
                    self.config.WIDTH // 2,
                    y_pos,
                    control,
                    20,
                    self.config.COLORS['player'],
                    self.config.COLORS['player_glow']
                )
                self.menu_animation_items.extend(control_texts)
            else:
                text_id = self.canvas.create_text(
                    self.config.WIDTH // 2,
                    y_pos,
                    text=control,
                    font=("Arial", 14),
                    fill=self.config.COLORS['text'],
                    anchor=tk.CENTER
                )
                self.menu_animation_items.append(text_id)
        
        # Рекорд
        record_texts = self.create_glow_text(
            self.config.WIDTH // 2,
            self.config.HEIGHT - 100,
            f"🏆 РЕКОРД: {int(self.high_score)}",
            24,
            self.config.COLORS['score'],
            self.config.COLORS['score_glow']
        )
        self.menu_animation_items.extend(record_texts)
        
        # Кнопка начала игры (скругленная через многоугольник)
        button_width, button_height = 240, 60
        button_x = self.config.WIDTH // 2
        button_y = self.config.HEIGHT - 150
        
        # Создаем многоугольник, имитирующий скругленный прямоугольник
        button_points = [
            button_x - button_width//2 + 15, button_y - button_height//2,
            button_x + button_width//2 - 15, button_y - button_height//2,
            button_x + button_width//2, button_y - button_height//2 + 15,
            button_x + button_width//2, button_y + button_height//2 - 15,
            button_x + button_width//2 - 15, button_y + button_height//2,
            button_x - button_width//2 + 15, button_y + button_height//2,
            button_x - button_width//2, button_y + button_height//2 - 15,
            button_x - button_width//2, button_y - button_height//2 + 15
        ]
        
        button_bg = self.canvas.create_polygon(
            button_points,
            fill=self.config.COLORS['button'],
            outline=self.config.COLORS['button_hover'],
            width=3,
            smooth=True
        )
        
        button_text = self.canvas.create_text(
            button_x, button_y,
            text="🚀 НАЧАТЬ ПОЛЕТ 🚀",
            font=("Arial", 22, "bold"),
            fill=self.config.COLORS['button_text'],
            anchor=tk.CENTER
        )
        
        self.menu_animation_items.extend([button_bg, button_text])
        
        # Делаем кнопку кликабельной
        self.canvas.tag_bind(button_bg, '<Button-1>', lambda e: self.start_game())
        self.canvas.tag_bind(button_text, '<Button-1>', lambda e: self.start_game())
        self.canvas.tag_bind(button_bg, '<Enter>', 
                           lambda e: self.canvas.itemconfig(button_bg, 
                                                          fill=self.config.COLORS['button_hover']))
        self.canvas.tag_bind(button_bg, '<Leave>', 
                           lambda e: self.canvas.itemconfig(button_bg, 
                                                          fill=self.config.COLORS['button']))
        
        # Анимация меню
        self.animate_menu()
        
    def animate_menu(self):
        """Анимация элементов меню"""
        if not self.game_active:
            # Анимация корабля в меню (если есть элементы)
            if len(self.menu_animation_items) > 3:
                ship_id = self.menu_animation_items[4] if len(self.menu_animation_items) > 4 else None
                if ship_id:
                    # Плавное перемещение влево-вправо
                    dx = math.sin(time.time() * 1.5) * 2
                    self.canvas.move(ship_id, dx, 0)
            
            # Продолжаем анимацию
            self.root.after(50, self.animate_menu)
            
    def clear_canvas(self):
        """Очистка холста"""
        try:
            self.canvas.delete("all")
            self.stars.clear()
            self.menu_animation_items.clear()
            if hasattr(self, 'explosion_particles'):
                for particle in self.explosion_particles:
                    if particle.id:
                        self.canvas.delete(particle.id)
                self.explosion_particles.clear()
        except:
            pass
            
    def start_game(self):
        """Начало игры"""
        try:
            self.clear_canvas()
            self.create_background()
            self.game_active = True
            self.score = 0
            self.game_time = 0
            self.start_time = time.time()
            self.obstacles.clear()
            self.explosion_particles.clear()
            
            # Создание игрока
            self.player = Player(self.canvas, self.config)
            self.player.create_ship()
            
            # Создание элементов интерфейса
            self.score_text = self.canvas.create_text(
                20, 20,
                text="🔰 ОЧКИ: 0",
                font=("Arial", 18, "bold"),
                fill=self.config.COLORS['score'],
                anchor=tk.W
            )
            
            self.time_text = self.canvas.create_text(
                20, 50,
                text="⏱ ВРЕМЯ: 0с",
                font=("Arial", 16),
                fill=self.config.COLORS['time'],
                anchor=tk.W
            )
            
            self.high_score_text = self.canvas.create_text(
                20, 80,
                text=f"🏆 РЕКОРД: {int(self.high_score)}",
                font=("Arial", 16),
                fill=self.config.COLORS['score'],
                anchor=tk.W
            )
            
            self.health_text = self.canvas.create_text(
                self.config.WIDTH - 20, 20,
                text="❤ СТАТУС: В ПОЛЕТЕ",
                font=("Arial", 16),
                fill=self.config.COLORS['health'],
                anchor=tk.E
            )
            
            # Запуск игрового цикла
            self.game_loop()
        except Exception as e:
            print(f"Ошибка при запуске игры: {e}")
            self.show_menu()
            
    def create_explosion(self, x, y):
        """Создание взрыва"""
        colors = ['#ff3333', '#ff6633', '#ff9933', '#ffcc33']
        for _ in range(30):
            p = Particle(
                x, y,
                random.choice(colors),
                speed=random.uniform(2, 8),
                size=random.uniform(3, 8),
                life=random.randint(20, 40)
            )
            p.id = self.canvas.create_oval(
                p.x - p.size, p.y - p.size,
                p.x + p.size, p.y + p.size,
                fill=p.color,
                outline=''
            )
            self.explosion_particles.append(p)
            
    def update_particles(self):
        """Обновление частиц взрыва"""
        for particle in self.explosion_particles[:]:
            if particle.update():
                self.canvas.coords(
                    particle.id,
                    particle.x - particle.size, particle.y - particle.size,
                    particle.x + particle.size, particle.y + particle.size
                )
            else:
                self.canvas.delete(particle.id)
                self.explosion_particles.remove(particle)
                
    def game_loop(self):
        """Основной игровой цикл"""
        try:
            if not self.game_active:
                return
                
            # Обновление времени
            self.game_time = time.time() - self.start_time
            self.score = self.game_time * self.config.SCORE_PER_SECOND
            
            # Обновление фона
            self.update_background()
            
            # Обновление частиц игрока
            if self.player:
                self.player.update_particles()
                
            # Обновление частиц взрыва
            self.update_particles()
            
            # Спавн препятствий
            if random.random() < self.config.OBSTACLE_SPAWN_RATE:
                obstacle = Obstacle(self.canvas, self.config)
                obstacle.create()
                self.obstacles.append(obstacle)
                
            # Обновление препятствий
            for obstacle in self.obstacles[:]:
                if obstacle.update():  # Препятствие ушло за экран
                    obstacle.destroy()
                    self.obstacles.remove(obstacle)
                    self.score += 5
                else:
                    # Проверка столкновения
                    if self.player:
                        player_bbox = self.player.get_bbox()
                        obstacle_bbox = obstacle.get_bbox()
                        
                        # Проверка пересечения
                        if (player_bbox[0] < obstacle_bbox[2] and
                            player_bbox[2] > obstacle_bbox[0] and
                            player_bbox[1] < obstacle_bbox[3] and
                            player_bbox[3] > obstacle_bbox[1]):
                            self.create_explosion(self.player.x, self.player.y)
                            self.game_over()
                            return
                            
            # Обновление интерфейса
            self.canvas.itemconfig(self.score_text, text=f"🔰 ОЧКИ: {int(self.score)}")
            self.canvas.itemconfig(self.time_text, text=f"⏱ ВРЕМЯ: {int(self.game_time)}с")
            self.canvas.itemconfig(self.health_text, text="❤ СТАТУС: В ПОЛЕТЕ")
            
            # Плавное увеличение сложности
            self.config.OBSTACLE_SPAWN_RATE = min(0.05, 0.02 + self.game_time / 1000)
            
            # Продолжение игрового цикла
            self.root.after(1000 // self.config.GAME_SPEED, self.game_loop)
            
        except Exception as e:
            print(f"Ошибка в игровом цикле: {e}")
            self.game_over()
            
    def game_over(self):
        """Завершение игры"""
        try:
            self.game_active = False
            
            # Обновление рекорда
            final_score = int(self.score)
            if final_score > self.high_score:
                self.high_score = final_score
                self.save_high_score()
                
            # Удаление препятствий
            for obstacle in self.obstacles:
                obstacle.destroy()
            self.obstacles.clear()
            
            # Удаление игрока
            if self.player:
                self.player.destroy()
                self.player = None
                
            # Затемнение экрана
            overlay = self.canvas.create_rectangle(
                0, 0,
                self.config.WIDTH, self.config.HEIGHT,
                fill="#000000",
                width=0
            )
            
            # Сообщение о завершении игры
            game_over_texts = self.create_glow_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 - 60,
                "💥 КОРАБЛЬ УНИЧТОЖЕН 💥",
                36,
                self.config.COLORS['game_over'],
                self.config.COLORS['game_over_glow']
            )
            
            score_texts = self.create_glow_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2,
                f"🎯 ВАШ РЕЗУЛЬТАТ: {int(self.score)}",
                28,
                self.config.COLORS['text'],
                self.config.COLORS['text_glow']
            )
            
            high_score_texts = self.create_glow_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 + 40,
                f"🏆 РЕКОРД: {int(self.high_score)}",
                24,
                self.config.COLORS['score'],
                self.config.COLORS['score_glow']
            )
            
            restart_text = self.canvas.create_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 + 100,
                text="Нажмите R для нового полета или ESC для меню",
                font=("Arial", 16),
                fill=self.config.COLORS['text'],
                anchor=tk.CENTER
            )
            
            # Сохраняем ссылки на тексты для удаления
            self.game_over_texts = [
                overlay,
                *game_over_texts,
                *score_texts,
                *high_score_texts,
                restart_text
            ]
            
        except Exception as e:
            print(f"Ошибка при завершении игры: {e}")
            self.show_menu()
            
    def show_menu(self):
        """Показать меню"""
        try:
            self.game_active = False
            if hasattr(self, 'game_over_texts'):
                for item in self.game_over_texts:
                    self.canvas.delete(item)
                self.game_over_texts.clear()
            self.init_menu()
        except Exception as e:
            print(f"Ошибка при показе меню: {e}")
            
    def run(self):
        """Запуск приложения"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Критическая ошибка: {e}")

def main():
    """Точка входа в программу"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Ошибка запуска: {e}")

if __name__ == "__main__":
    main()