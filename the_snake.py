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


def draw_text(surface, text, position, size=24, color=TEXT_COLOR):
    """Отрисовывает текст на указанной поверхности."""
    font = pg.font.Font(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=position)
    surface.blit(rendered, rect)


class GameObject:
    """Базовый объект игрового поля."""

    def __init__(self, body_color=None):
        self.body_color = body_color
        self.position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

    def draw_cell(self, surface, position, color, border_color=BORDER_COLOR):
        """Рисует одну ячейку. Позиция передаётся целиком."""
        x, y = position
        rect = pg.Rect(
            x * GRID_SIZE,
            y * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE,
        )
        pg.draw.rect(surface, color, rect)
        pg.draw.rect(surface, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, которое должна съесть змейка."""

    def __init__(self, occupied_positions):
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Создаёт новую позицию, не совпадающую со змейкой."""
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in occupied_positions:
                self.position = pos
                break

    def draw(self, surface):
        """Отрисовывает яблоко."""
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Змейка игрока."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)

        # pylint fix: все атрибуты объявлены в __init__
        self.length = 1
        self.positions = [self.position]
        self.direction = UP
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
        """Меняет направление, запрещая разворот на 180."""
        if (new_direction[0] != -self.direction[0]
                or new_direction[1] != -self.direction[1]):
            self.direction = new_direction

    def move(self):
        """Передвигает змейку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_pos = (
            (head_x + dir_x) % GRID_WIDTH,
            (head_y + dir_y) % GRID_HEIGHT,
        )

        self.position = new_pos
        self.positions.insert(0, new_pos)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface):
        """Рисует всю змейку — полная перерисовка."""
        for segment in self.positions:
            self.draw_cell(surface, segment, self.body_color)


def handle_keys(snake, fps):
    """Обрабатывает нажатия клавиш."""
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


def main():
    """Точка входа в игру."""
    pg.init()
    screen = pg.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    clock = pg.time.Clock()

    pg.display.set_caption(
        'Змейка — Esc для выхода | +/- скорость'
    )

    snake = Snake()
    apple = Apple(snake.positions)
    fps = FPS_DEFAULT
    score = 0

    while True:
        clock.tick(fps)
        cont, fps = handle_keys(snake, fps)

        if not cont:
            break

        snake.move()

        # столкновение с собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            score = 0
            fps = FPS_DEFAULT
            continue

        # яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position(snake.positions)

            # победа
            if snake.length >= WIN_LENGTH:
                screen.fill(BOARD_BACKGROUND_COLOR)

                draw_text(
                    screen,
                    'Победа!',
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                    48,
                )
                draw_text(
                    screen,
                    'Нажмите ESC для выхода',
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40),
                    28,
                )
                pg.display.flip()

                while True:
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            pg.quit()
                            return

                        if (event.type == pg.KEYDOWN
                                and event.key == pg.K_ESCAPE):
                            pg.quit()
                            return

        # Полная перерисовка кадра
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        draw_text(screen, f'Счёт: {score}', (60, 20), 22)
        draw_text(screen, f'Скорость: {fps}', (560, 20), 22)

        pg.display.flip()

    pg.quit()


if __name__ == '__main__':
    main()
