"""Классическая игра "Змейка" на Pygame"""
from random import choice, randint

import pygame

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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                 body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовка объектов. Переопределяется в дочерних классах."""


class Apple(GameObject):
    """Класс объекта яблоко."""

    def __init__(self, position=None, body_color=APPLE_COLOR):
        super().__init__(position, body_color)
        if position is None:
            self.randomize_position()

    def randomize_position(self):
        """Генерирует координаты местоположения яблока."""
        col = randint(0, GRID_WIDTH - 1)
        row = randint(0, GRID_HEIGHT - 1)
        self.position = (col * GRID_SIZE, row * GRID_SIZE)

    def draw(self):
        """Отрисовка объекта яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс объекта змейка."""

    def __init__(self, position=None, body_color=SNAKE_COLOR,
                 direction=RIGHT):
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position, body_color)
        self.positions = [position]
        self.direction = direction
        self.next_direction = None
        self.length = len(self.positions)
        self.last = None

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
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self):
        """Отрисовка змейки и очистка клетки, с которой она уползла."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        # Очищаем клетку удалённого хвоста цветом поля:
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш и сохраняет next_direction"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            # Запрет разворота на 180 градусов:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Основная функция игры: игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    # Настройка шрифта для счёта очков:
    FONT = pygame.font.SysFont(None, 30)
    apple = Apple()
    snake = Snake()
    # Переменные для хранения счёта.
    score = 0
    best_score = 0
    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        # Змейка съела яблоко:
        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position()
            # Исключаем появление яблока на теле змейки.
            while apple.position in snake.positions:
                apple.randomize_position()
        # Змейка столкнулась с собой:
        if snake.get_head_position() in snake.positions[1:]:
            best_score = max(best_score, score)
            score = 0
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        # Отрисовка счёта очков:
        score_text = FONT.render(f'Счёт: {score}', True, (255, 255, 255))
        best_score_text = FONT.render(f'Рекорд: {best_score}', True,
                                      (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (10, 30))
        pygame.display.update()


if __name__ == '__main__':
    main()
