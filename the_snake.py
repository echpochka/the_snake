# pylint: disable=missing-docstring, no-member
# flake8: noqa: D100, D101, D102, D103

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


# === Вспомогательные функции ===
def draw_text(surface, text, position, size=24, color=TEXT_COLOR):
    """Отрисовывает текст на экране."""
    font = pg.font.Font(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=position)
    surface.blit(rendered, rect)


# === Базовый класс ===
class GameObject:
    """Базовый игровой объект."""

    def __init__(self, body_color):
        self.body_color = body_color

    @staticmethod
    def to_pixels(grid_pos):
        """Конвертирует координаты сетки в пиксели."""
        gx, gy = grid_pos
        return gx * GRID_SIZE, gy * GRID_SIZE

    @staticmethod
    def draw_cell(surface, grid_pos, color, border_color=BORDER_COLOR):
        """Рисует одну ячейку."""
        px, py = GameObject.to_pixels(grid_pos)
        rect = pg.Rect(px, py, GRID_SIZE, GRID_SIZE)
        pg.draw.rect(surface, color, rect)
        pg.draw.rect(surface, border_color, rect, 1)


# === Яблоко ===
class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions):
        super().__init__(APPLE_COLOR)
        self.position = (0, 0)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию яблока."""
        occupied_positions = occupied_positions or []
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if pos not in occupied_positions:
                self.position = pos
                break

    def draw(self, surface):
        """Отрисовывает яблоко."""
        GameObject.draw_cell(surface, self.position, self.body_color)


# === Змейка ===
class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = []
        self.direction = None
        self.last_removed = None
        self.reset()

    def reset(self):
        """Сбрасывает состояние змейки."""
        self.length = 1
        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.positions = [center]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last_removed = None

    def get_head_position(self):
        """Возвращает позицию головы."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Меняет направление движения."""
        if not (new_direction[0] == -self.direction[0]
                and new_direction[1] == -self.direction[1]):
            self.direction = new_direction

    def move(self):
        """Двигает змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x) % GRID_WIDTH,
            (head_y + dir_y) % GRID_HEIGHT
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last_removed = self.positions.pop()
        else:
            self.last_removed = None

    def check_self_collision(self):
        """Проверяет столкновение с собой."""
        return self.get_head_position() in self.positions[1:]

    def draw_full(self, surface):
        """Отрисовывает всю змейку."""
        for pos in self.positions:
            GameObject.draw_cell(surface, pos, self.body_color)

    def draw_incremental(self, surface):
        """Инкрементальная отрисовка змейки."""
        GameObject.draw_cell(surface, self.get_head_position(),
                             self.body_color)
        if self.last_removed:
            GameObject.draw_cell(
                surface,
                self.last_removed,
                BOARD_BACKGROUND_COLOR,
                border_color=BOARD_BACKGROUND_COLOR
            )


# === Обработка клавиш ===
def handle_keys(snake, current_fps):
    """Обрабатывает ввод с клавиатуры."""
    key_dir = {
        pg.K_UP: UP,
        pg.K_w: UP,
        pg.K_DOWN: DOWN,
        pg.K_s: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_a: LEFT,
        pg.K_RIGHT: RIGHT,
        pg.K_d: RIGHT,
    }

    new_fps = current_fps

    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False, new_fps
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False, new_fps
            if event.key in key_dir:
                snake.update_direction(key_dir[event.key])
            elif event.key in (pg.K_PLUS, pg.K_EQUALS):
                new_fps = min(FPS_MAX, new_fps + 1)
            elif event.key in (pg.K_MINUS, pg.K_UNDERSCORE):
                new_fps = max(FPS_MIN, new_fps - 1)

    return True, new_fps


# === Экран победы ===
def show_victory_screen(screen):
    """Показывает экран победы."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_text(screen, 'Победа!',
              (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20), 48)
    draw_text(screen, 'Нажмите ESC для выхода',
              (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30), 28)
    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                waiting = False


# === Основная функция ===
def main():
    """Главная функция игры."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption('Змейка — Esc для выхода | +/- скорость')
    clock = pg.time.Clock()

    snake = Snake()
    apple = Apple(snake.positions)
    fps = FPS_DEFAULT
    score = 0

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw_full(screen)
    apple.draw(screen)
    pg.display.flip()

    while True:
        clock.tick(fps)
        cont, fps = handle_keys(snake, fps)
        if not cont:
            break

        snake.move()

        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position(snake.positions)
            score = 0
            fps = FPS_DEFAULT
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.draw_full(screen)
            apple.draw(screen)
            pg.display.flip()
            continue

        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position(snake.positions)
            apple.draw(screen)

        if snake.length >= WIN_LENGTH:
            show_victory_screen(screen)
            break

        snake.draw_incremental(screen)
        apple.draw(screen)

        draw_text(screen, f'Счёт: {score}', (60, 20), 22)
        draw_text(screen, f'Скорость: {fps}', (560, 20), 22)

        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    main()
