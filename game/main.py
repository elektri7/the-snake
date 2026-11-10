"""Классическая игра "Змейка" на Pygame."""
import asyncio
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь соответствий: (нажатая клавиша, текущее направление) ->
# новое направление:
KEY_TO_DIRECTION = {
    (pg.K_UP, UP): UP,
    (pg.K_UP, RIGHT): UP,
    (pg.K_UP, LEFT): UP,

    (pg.K_DOWN, DOWN): DOWN,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_DOWN, LEFT): DOWN,

    (pg.K_LEFT, LEFT): LEFT,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,

    (pg.K_RIGHT, RIGHT): RIGHT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Начальная скорость движения змейки:
SPEED = 7

# Цвет текста счёта:
TEXT_COLOR = (255, 255, 255)

# Размер шрифта для счёта:
FONT_SIZE = 30

# Позиции отрисовки текста счёта и рекорда:
SCORE_POSITION = (10, 10)
BEST_SCORE_POSITION = (10, 30)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def _draw_cell(self, position=None, color=None):
        """Рисует одну ячейку на игровом поле."""
        cell_position = position or self.position
        cell_color = color or self.body_color
        rect = pg.Rect(cell_position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, cell_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовка объектов. Переопределяется в дочерних классах."""


class Apple(GameObject):
    """Класс объекта яблока."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Устанавливает случайную позицию яблока вне занятых клеток."""
        while True:
            col = randint(0, GRID_WIDTH - 1)
            row = randint(0, GRID_HEIGHT - 1)
            self.position = (col * GRID_SIZE, row * GRID_SIZE)
            if self.position not in occupied_positions:
                return

    def draw(self):
        """Отрисовка объекта яблоко."""
        self._draw_cell()


class Snake(GameObject):
    """Класс объекта змейка."""

    def __init__(self, body_color=SNAKE_COLOR, direction=RIGHT):
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Реализует движение змейки на одну клетку."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))
        self.last = (self.positions.pop()
                     if len(self.positions) > self.length
                     else None)

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def draw(self):
        """Отрисовка змейки и очистка клетки, с которой она уползла."""
        # Очищаем клетку удалённого хвоста цветом поля:
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        # Рисуем только голову:
        self._draw_cell(self.get_head_position())


running = True


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и сохраняет next_direction."""
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            running = False
            return
        if event.type == pg.KEYDOWN:
            snake.next_direction = KEY_TO_DIRECTION.get(
                (event.key, snake.direction), snake.direction)
        # Обработка касаний-свайпов при игре на телефоне:
        if event.type == pg.FINGERDOWN:
            x, y = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
            head_x, head_y = snake.get_head_position()
            if abs(x - head_x) > abs(y - head_y):
                # Горизонтальный свайп — лево или право:
                snake.next_direction = (
                    RIGHT if x > head_x else LEFT)
            else:
                # Вертикальный свайп — вверх или вниз:
                snake.next_direction = (
                    DOWN if y > head_y else UP)


async def main():
    """Основная функция игры: игровой цикл."""
    # Инициализация PyGame:
    pg.init()
    # Настройка шрифта для счёта очков:
    font = pg.font.SysFont(None, FONT_SIZE)
    snake = Snake()
    apple = Apple(snake.positions)
    # Переменные для хранения счёта.
    score = 0
    best_score = 0
    # Первичная отрисовка поля — только один раз, до цикла:
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(SPEED)
        await asyncio.sleep(0)
        handle_keys(snake)
        if not running:
            return
        snake.update_direction()
        snake.move()
        # Змейка съела яблоко:
        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            # Передаём занятые клетки — тела змейки:
            apple.randomize_position(snake.positions)
        # Змейка столкнулась с собой:
        if snake.get_head_position() in snake.positions[1:]:
            best_score = max(best_score, score)
            score = 0
            snake.reset()
            # После сброса змейки переносим яблоко на свободную клетку:
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        # Отрисовка счёта очков:
        score_text = font.render(f'Счёт: {score}', True, TEXT_COLOR,
                                 BOARD_BACKGROUND_COLOR)
        best_score_text = font.render(f'Рекорд: {best_score}', True,
                                      TEXT_COLOR, BOARD_BACKGROUND_COLOR)
        screen.blit(score_text, SCORE_POSITION)
        screen.blit(best_score_text, BEST_SCORE_POSITION)
        pg.display.update()


if __name__ == '__main__':
    asyncio.run(main())
