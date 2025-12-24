"""
Игра "Уклоняйся от падающих объектов"
Лабораторная работа по программированию
"""
import tkinter as tk
import random
import json
import os
import time
from typing import List, Tuple, Optional, Dict

class Config:
    """Класс для хранения конфигурации игры"""
    def __init__(self):
        self.WIDTH = 600
        self.HEIGHT = 600
        self.PLAYER_WIDTH = 50
        self.PLAYER_HEIGHT = 30
        self.PLAYER_SPEED = 10
        self.OBSTACLE_MIN_SIZE = 20
        self.OBSTACLE_MAX_SIZE = 50
        self.OBSTACLE_SPEED_MIN = 3
        self.OBSTACLE_SPEED_MAX = 8
        self.OBSTACLE_SPAWN_RATE = 0.02
        self.SCORE_PER_SECOND = 20
        self.GAME_SPEED = 90  # FPS
        
        self.COLORS = {
            'background': '#1a1a2e',
            'player': '#2a9df4',
            'obstacle': '#ff6b6b',
            'fast_obstacle': '#ffd93d',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'button': '#4a6fa5',
            'button_hover': '#5a8fcc',
            'game_over': '#ff3333',
            'score': '#ffff99'
        }

class Player:
    """Класс игрока"""
    def __init__(self, canvas: tk.Canvas, config: Config):
        self.canvas = canvas
        self.config = config
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.x = config.WIDTH // 2
        self.y = config.HEIGHT - self.height - 20
        self.speed = config.PLAYER_SPEED
        self.id = None
        
    def create(self):
        """Создание игрока на холсте"""
        self.id = self.canvas.create_rectangle(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2,
            fill=self.config.COLORS['player'],
            outline='#1e6faf',
            width=2
        )
        
    def move(self, dx: int):
        """Движение игрока"""
        new_x = self.x + dx * self.speed
        new_x = max(self.width // 2, min(new_x, self.config.WIDTH - self.width // 2))
        self.x = new_x
        
        if self.id:
            self.canvas.coords(
                self.id,
                self.x - self.width // 2,
                self.y - self.height // 2,
                self.x + self.width // 2,
                self.y + self.height // 2
            )
            
    def get_bbox(self) -> Tuple[int, int, int, int]:
        """Получить границы игрока"""
        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2
        )

class Obstacle:
    """Класс препятствия"""
    def __init__(self, canvas: tk.Canvas, config: Config, is_fast: bool = False):
        self.canvas = canvas
        self.config = config
        self.is_fast = is_fast
        
        # Размер препятствия
        if is_fast:
            size = random.randint(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE // 2)
            self.speed = random.randint(config.OBSTACLE_SPEED_MIN + 2, config.OBSTACLE_SPEED_MAX + 3)
            self.color = config.COLORS['fast_obstacle']
        else:
            size = random.randint(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
            self.speed = random.randint(config.OBSTACLE_SPEED_MIN, config.OBSTACLE_SPEED_MAX)
            self.color = config.COLORS['obstacle']
            
        self.width = size
        self.height = size
        
        # Начальная позиция
        self.x = random.randint(size, config.WIDTH - size)
        self.y = -size
        
        self.id = None
        
    def create(self):
        """Создание препятствия на холсте"""
        outline_color = '#ff9f43' if self.is_fast else '#ff3838'
        self.id = self.canvas.create_rectangle(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2,
            fill=self.color,
            outline=outline_color,
            width=2
        )
        
    def update(self) -> bool:
        """Обновление позиции препятствия"""
        self.y += self.speed
        
        if self.id:
            self.canvas.coords(
                self.id,
                self.x - self.width // 2,
                self.y - self.height // 2,
                self.x + self.width // 2,
                self.y + self.height // 2
            )
            
        # Возвращает True если препятствие ушло за экран
        return self.y > self.config.HEIGHT + self.height
        
    def get_bbox(self) -> Tuple[int, int, int, int]:
        """Получить границы препятствия"""
        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2
        )

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.config = Config()
        
        # Создание главного окна
        self.root = tk.Tk()
        self.root.title("Уклоняйся от падающих объектов")
        self.root.geometry(f"{self.config.WIDTH}x{self.config.HEIGHT}")
        self.root.resizable(True, True)
        
        # Создание холста
        self.canvas = tk.Canvas(
            self.root,
            bg=self.config.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Привязка событий изменения размера
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Игровые переменные
        self.player = None
        self.obstacles: List[Obstacle] = []
        self.score = 0
        self.high_score = 0
        self.game_time = 0
        self.game_active = False
        self.start_time = 0
        
        # Элементы интерфейса
        self.score_text = None
        self.time_text = None
        self.high_score_text = None
        self.game_over_text = None
        self.menu_frame = None
        
        # Загрузка рекорда
        self.load_high_score()
        
        # Инициализация игры
        self.init_menu()
        
        # Привязка клавиш
        self.setup_key_bindings()
        
    def setup_key_bindings(self):
        """Настройка привязки клавиш"""
        self.root.bind('<Left>', lambda e: self.on_key_press('left'))
        self.root.bind('<Right>', lambda e: self.on_key_press('right'))
        self.root.bind('<a>', lambda e: self.on_key_press('left'))
        self.root.bind('<d>', lambda e: self.on_key_press('right'))
        self.root.bind('<Return>', lambda e: self.on_key_press('enter'))
        self.root.bind('<Escape>', lambda e: self.on_key_press('escape'))
        self.root.bind('<r>', lambda e: self.on_key_press('restart'))
        
    def on_key_press(self, key: str):
        """Обработка нажатия клавиш"""
        try:
            if key == 'left' and self.game_active:
                self.player.move(-1)
            elif key == 'right' and self.game_active:
                self.player.move(1)
            elif key == 'enter':
                if not self.game_active:
                    self.start_game()
            elif key == 'escape':
                if self.game_active:
                    self.show_menu()
                else:
                    self.root.quit()
            elif key == 'restart' and not self.game_active:
                self.start_game()
        except Exception as e:
            print(f"Ошибка обработки клавиши: {e}")
            
    def on_resize(self, event):
        """Обработка изменения размера окна"""
        try:
            self.config.WIDTH = event.width
            self.config.HEIGHT = event.height
            
            # Обновление позиции игрока
            if self.player:
                self.player.x = min(self.player.x, self.config.WIDTH - self.player.width // 2)
                self.player.x = max(self.player.width // 2, self.player.x)
                self.player.y = self.config.HEIGHT - self.player.height - 20
                
                if self.player.id:
                    self.canvas.coords(
                        self.player.id,
                        self.player.x - self.player.width // 2,
                        self.player.y - self.player.height // 2,
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2
                    )
        except Exception as e:
            print(f"Ошибка при изменении размера: {e}")
            
    def load_high_score(self):
        """Загрузка рекорда из файла"""
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            else:
                self.high_score = 0
        except Exception as e:
            print(f"Ошибка загрузки рекорда: {e}")
            self.high_score = 0
            
    def save_high_score(self):
        """Сохранение рекорда в файл"""
        try:
            with open("highscore.json", "w", encoding='utf-8') as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception as e:
            print(f"Ошибка сохранения рекорда: {e}")
            
    def init_menu(self):
        """Инициализация меню"""
        self.clear_canvas()
        
        # Создание фрейма для меню
        self.menu_frame = tk.Frame(self.canvas, bg=self.config.COLORS['background'])
        self.canvas.create_window(
            self.config.WIDTH // 2,
            self.config.HEIGHT // 2,
            window=self.menu_frame
        )
        
        # Заголовок
        title_label = tk.Label(
            self.menu_frame,
            text="УКЛОНЯЙСЯ!",
            font=("Arial", 36, "bold"),
            fg=self.config.COLORS['text'],
            bg=self.config.COLORS['background']
        )
        title_label.pack(pady=20)
        
        # Подзаголовок
        subtitle_label = tk.Label(
            self.menu_frame,
            text="Избегайте падающих объектов",
            font=("Arial", 16),
            fg=self.config.COLORS['text_secondary'],
            bg=self.config.COLORS['background']
        )
        subtitle_label.pack(pady=10)
        
        # Инструкции
        instructions = [
            "Управление:",
            "← → - движение",
            "ENTER - начать игру",
            "ESC - меню/выход",
            "R - перезапуск после проигрыша"
        ]
        
        for instruction in instructions:
            label = tk.Label(
                self.menu_frame,
                text=instruction,
                font=("Arial", 14),
                fg=self.config.COLORS['text'],
                bg=self.config.COLORS['background']
            )
            label.pack(pady=5)
            
        # Кнопка начала игры
        start_button = tk.Button(
            self.menu_frame,
            text="НАЧАТЬ ИГРУ",
            font=("Arial", 18, "bold"),
            bg=self.config.COLORS['button'],
            fg="white",
            activebackground=self.config.COLORS['button_hover'],
            activeforeground="white",
            relief=tk.RAISED,
            borderwidth=3,
            command=self.start_game
        )
        start_button.pack(pady=30)
        
        # Отображение рекорда
        high_score_label = tk.Label(
            self.menu_frame,
            text=f"Рекорд: {int(self.high_score)}",
            font=("Arial", 16, "bold"),
            fg=self.config.COLORS['score'],
            bg=self.config.COLORS['background']
        )
        high_score_label.pack(pady=10)
        
    def clear_canvas(self):
        """Очистка холста"""
        try:
            self.canvas.delete("all")
            self.menu_frame = None
        except Exception as e:
            print(f"Ошибка очистки холста: {e}")
            
    def start_game(self):
        """Начало игры"""
        try:
            self.clear_canvas()
            self.game_active = True
            self.score = 0
            self.game_time = 0
            self.start_time = time.time()
            self.obstacles.clear()
            
            # Создание игрока
            self.player = Player(self.canvas, self.config)
            self.player.create()
            
            # Создание текстовых элементов
            self.score_text = self.canvas.create_text(
                20, 20,
                text=f"Счет: {int(self.score)}",
                font=("Arial", 16, "bold"),
                fill=self.config.COLORS['text'],
                anchor=tk.W
            )
            
            self.time_text = self.canvas.create_text(
                20, 50,
                text="Время: 0с",
                font=("Arial", 16),
                fill=self.config.COLORS['text'],
                anchor=tk.W
            )
            
            self.high_score_text = self.canvas.create_text(
                20, 80,
                text=f"Рекорд: {int(self.high_score)}",
                font=("Arial", 16),
                fill=self.config.COLORS['score'],
                anchor=tk.W
            )
            
            # Запуск игрового цикла
            self.game_loop()
        except Exception as e:
            print(f"Ошибка при запуске игры: {e}")
            self.show_menu()
            
    def game_loop(self):
        """Основной игровой цикл"""
        try:
            if not self.game_active:
                return
                
            # Обновление времени
            self.game_time = time.time() - self.start_time
            self.score = self.game_time * self.config.SCORE_PER_SECOND
            
            # Спавн препятствий
            if random.random() < self.config.OBSTACLE_SPAWN_RATE:
                is_fast = random.random() < 0.15
                obstacle = Obstacle(self.canvas, self.config, is_fast)
                obstacle.create()
                self.obstacles.append(obstacle)
                
            # Обновление препятствий
            for obstacle in self.obstacles[:]:
                if obstacle.update():  # Препятствие ушло за экран
                    self.canvas.delete(obstacle.id)
                    self.obstacles.remove(obstacle)
                    self.score += 3
                else:
                    # Проверка столкновения
                    player_bbox = self.player.get_bbox()
                    obstacle_bbox = obstacle.get_bbox()
                    
                    # Простая проверка пересечения прямоугольников
                    if (player_bbox[0] < obstacle_bbox[2] and
                        player_bbox[2] > obstacle_bbox[0] and
                        player_bbox[1] < obstacle_bbox[3] and
                        player_bbox[3] > obstacle_bbox[1]):
                        self.game_over()
                        return
                        
            # Обновление текста
            self.canvas.itemconfig(self.score_text, text=f"Счет: {int(self.score)}")
            self.canvas.itemconfig(self.time_text, text=f"Время: {int(self.game_time)}с")
            
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
                self.canvas.delete(obstacle.id)
            self.obstacles.clear()
            
            # Сообщение о завершении игры
            self.canvas.create_rectangle(
                0, 0,
                self.config.WIDTH, self.config.HEIGHT,
                fill="black",
                stipple="gray50"
            )
            
            game_over_text = self.canvas.create_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 - 50,
                text="ИГРА ОКОНЧЕНА",
                font=("Arial", 40, "bold"),
                fill=self.config.COLORS['game_over']
            )
            
            score_text = self.canvas.create_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 + 10,
                text=f"Ваш счет: {int(self.score)}",
                font=("Arial", 24),
                fill=self.config.COLORS['text']
            )
            
            high_score_text = self.canvas.create_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 + 50,
                text=f"Рекорд: {int(self.high_score)}",
                font=("Arial", 24, "bold"),
                fill=self.config.COLORS['score']
            )
            
            restart_text = self.canvas.create_text(
                self.config.WIDTH // 2,
                self.config.HEIGHT // 2 + 120,
                text="Нажмите R для перезапуска или ESC для меню",
                font=("Arial", 16),
                fill=self.config.COLORS['text_secondary']
            )
            
        except Exception as e:
            print(f"Ошибка при завершении игры: {e}")
            self.show_menu()
            
    def show_menu(self):
        """Показать меню"""
        try:
            self.game_active = False
            self.init_menu()
        except Exception as e:
            print(f"Ошибка при показе меню: {e}")
            self.root.quit()
            
    def run(self):
        """Запуск приложения"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            input("Нажмите Enter для выхода...")

def main():
    """Точка входа в программу"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()