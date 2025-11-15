# pylint: disable=missing-docstring, no-member
# flake8: noqa: D100, D101, D102, D103
# isort: skip_file

import random
import pygame as pg

# === Константы ===

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)

FPS_DEFAULT = 10
FPS_MIN, FPS_MAX = 5, 30
WIN_LENGTH = 20

KEY_DIR = {
    pg.K_UP: UP,
    pg.K_w: UP,
    pg.K_DOWN: DOWN,
    pg.K_s: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_a: LEFT,
    pg.K_RIGHT: RIGHT,
    pg.K_d: RIGHT,
}

# Инициализация pygame и создание глобальных переменных
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


def grid_to_pixels(position):
    """Преобразовывает координаты клетки в координаты пикселей."""
    x, y = position
    return x * GRID_SIZE, y * GRID_SIZE


def draw_text(text, position, size=24, color=TEXT_COLOR):
    """Отрисовка текста."""
    font = pg.font.Font(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=position)
    screen.blit(rendered, rect)


class GameObject:
    """Базовый объект игрового поля."""

    def __init__(self, color=SNAKE_COLOR):
        self.body_color = color
        self.position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

    def draw(self):
        """Отрисовывает объект на поверхности."""
        self.draw_cell(self.position, self.body_color)

    def draw_cell(self, position, color, border_color=BORDER_COLOR):
        """Рисует одну ячейку."""
        px, py = grid_to_pixels(position)
        rect = pg.Rect(px, py, GRID_SIZE, GRID_SIZE)
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, которое должна съесть змейка."""

    def __init__(self, occupied_positions=None):
        super().__init__(APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Создает новую позицию, не совпдадающую со змейкой."""
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if self.position not in occupied_positions:
                break


class Snake(GameObject):
    """Змейка игрока."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None
        self.reset()

    def reset(self):
        """Сбрасывает состояние змейки."""
        self.length = 1
        self.position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Меняет направление, запрещая разворот назад."""
        if new_direction != (-self.direction[0], -self.direction[1]):
            self.direction = new_direction

    def move(self):
        """Передвигает змейку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        self.position = (
            (head_x + dir_x) % GRID_WIDTH,
            (head_y + dir_y) % GRID_HEIGHT,
        )

        self.positions.insert(0, self.position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисует всю змейку."""
        for segment in self.positions:
            self.draw_cell(segment, self.body_color)


def erase_cell(pos):
    """Стирает клетку на экране."""
    px, py = grid_to_pixels(pos)
    rect = pg.Rect(px, py, GRID_SIZE, GRID_SIZE)
    pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


def handle_keys(snake, fps):
    """Обрабатывает нажатие клавиш."""
    new_fps = fps
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False, new_fps

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False, new_fps

            if event.key in KEY_DIR:
                snake.update_direction(KEY_DIR[event.key])
            elif event.key in (pg.K_PLUS, pg.K_EQUALS):
                new_fps = min(FPS_MAX, new_fps + 1)
            elif event.key in (pg.K_MINUS, pg.K_UNDERSCORE):
                new_fps = max(FPS_MIN, new_fps - 1)

    return True, new_fps


def handle_self_collision(snake, apple):
    """Обрабатывает столкновение змейки с самой собой."""
    if snake.get_head_position() in snake.positions[1:]:
        snake.reset()
        apple.randomize_position(snake.positions)
        return True
    return False


def show_victory_screen():
    """Показывает экран победы."""
    screen.fill(BOARD_BACKGROUND_COLOR)

    draw_text('Победа!', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 48)
    draw_text(
        'Нажмите ESC для выхода',
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40),
        28,
    )
    pg.display.flip()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return


def main():
    """Точка входа в игру."""
    pg.display.set_caption('Змейка — Esc | +/- скорость')

    snake = Snake()
    apple = Apple(snake.positions)

    fps = FPS_DEFAULT
    score = 0

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    draw_text('Счёт: 0', (60, 20), 22)
    draw_text(f'Скорость: {fps}', (560, 20), 22)
    pg.display.flip()

    while True:
        clock.tick(fps)
        cont, fps = handle_keys(snake, fps)

        if not cont:
            break

        snake.move()

        # Столкновение с собой
        if handle_self_collision(snake, apple):
            score = 0
            fps = FPS_DEFAULT
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.draw()
            apple.draw()
            draw_text(f'Счёт: {score}', (60, 20), 22)
            draw_text(f'Скорость: {fps}', (560, 20), 22)
            pg.display.flip()
            continue

        # Яблоко
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position(snake.positions)

            # Победа
            if snake.length >= WIN_LENGTH:
                show_victory_screen()
                return

        # Перерисовка
        if snake.last is not None:
            erase_cell(snake.last)

        snake.draw()
        apple.draw()

        draw_text(f'Счёт: {score}', (60, 20), 22)
        draw_text(f'Скорость: {fps}', (560, 20), 22)

        pg.display.flip()


if __name__ == '__main__':
    main()
    pg.quit()
