import pygame

import experiments.constants
from experiments.datatypes import Dimensions


def is_terminal_event(event):
    condition_1 = event.type == pygame.QUIT
    condition_2 = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    return condition_1 or condition_2


def terminate():
    pygame.quit()


class ArrowCue(pygame.sprite.Sprite):
    def __init__(self, screen, width, height, color, bg_color=experiments.constants.BLACK):
        super().__init__()

        self.screen = screen
        self.width = width
        self.height = height
        self.color = color
        self.bg_color = bg_color

        self.image = pygame.Surface([width, height])
        self.image.set_colorkey(experiments.constants.BLACK)

        self.rect = self.image.get_rect()

    def draw(self):
        self.image.fill(self.bg_color)

        pygame.draw.polygon(self.image, self.color,
                            [(0, self.height // 4), (self.width - 10, self.height // 4),
                             (self.width - 10, 0), (self.width, self.height // 2),
                             (self.width - 10, self.height), (self.width - 10, 3 * self.height // 4),
                             (0, 3 * self.height // 4)])


class CrossHairs(pygame.sprite.Sprite):
    def __init__(self, screen, pos, width, color):
        super().__init__()

        self.screen = screen
        self.pos = pos
        self.width = width
        self.color = color

        self.image = pygame.Surface([width, width])
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - width // 2
        self.rect.y = pos[1] - width // 2

    def update(self):
        self.screen.fill(experiments.constants.BLACK)
        self.image.fill((0, 0, 0))

        pygame.draw.line(self.image, self.color, (0, self.width // 2), (self.width, self.width // 2), 5)
        pygame.draw.line(self.image, self.color, (self.width // 2, 0), (self.width // 2, self.width), 5)


class Character(pygame.sprite.Sprite):
    def __init__(self, char, pos, font, color):
        super().__init__()

        self.char = char
        self.pos = pos
        self.font = font
        self.color = color

        self.update()

    def update(self):
        self.image = self.font.render(self.char, 1, self.color)
        self.rect = self.image.get_rect()

        width, height = self.font.size(self.char)
        self.rect.x, self.rect.y = self.pos


class CharacterGrid:
    def __init__(self, screen, grid, font, color_grid=None, bg_color=experiments.constants.BLACK):
        super().__init__()

        self.screen = screen
        self.grid = grid
        self.n_rows = len(grid)
        self.n_columns = len(grid[0])

        self.font = font
        self.color_grid = color_grid or [[experiments.constants.WHITE] * self.n_columns for _ in range(self.n_rows)]
        self.bg_color = bg_color

        self._x_margin, self._y_margin = (10, 10)
        self._x_char_spacer, self._y_char_spacer = (10, 10)
        self._char_dims = Dimensions(*self.font.size('A'))  # Assumes fixed-width font
        self._grid_dims = self._get_grid_dims()
        self._position = self._get_position()

        # Pygame Surfaces and Sprites
        self.grid_surface = pygame.Surface(self._grid_dims)

        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())

    def _get_position(self):
        screen_width, screen_height = self.screen.get_size()

        x = (screen_width - self._grid_dims.width) // 2
        y = (screen_height - self._grid_dims.height) // 2

        return x, y

    def _get_grid_dims(self):
        width = 2 * self._x_margin + (self.n_columns - 1) * self._x_char_spacer + self.n_columns * self._char_dims.width
        height = 2 * self._y_margin + (self.n_rows - 1) * self._y_char_spacer + self.n_rows * self._char_dims.height

        return Dimensions(width, height)

    def _create_sprites(self):
        sprites = []
        for i, row in enumerate(self.grid):
            for j, char in enumerate(row):
                char_pos = (
                    j * (self._char_dims.width + self._x_char_spacer) + self._x_margin,
                    i * (self._char_dims.height + self._y_char_spacer) + self._y_margin
                )
                sprite = Character(char, pos=char_pos, font=self.font, color=self.color_grid[i][j])
                sprites.append(sprite)

        return sprites

    def draw(self, *args):
        # Clear previously rendered letters from surface
        self.grid_surface.fill(self.bg_color)

        # Draw all sprites onto grid surface
        self.sprite_group.draw(self.grid_surface)

        # Draw grid surface onto enclosing surface
        self.screen.blit(self.grid_surface, self._position)

    def update(self):
        self.sprite_group.update()

    def refresh(self):
        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())


class GridRenderer:
    def __init__(self, screen, grid, font, padding, color_grid=None):
        self.screen = screen
        self.grid = grid
        self.font = font
        self.padding = padding
        self.color_grid = color_grid

        self.char_grid = CharacterGrid(screen=screen, grid=grid, font=font, color_grid=color_grid)

    def __call__(self, *args, **kwargs):
        self.char_grid.update()
        self.char_grid.draw(self.screen)

    def refresh(self):
        self.char_grid.refresh()


class FeedbackGridRenderer:
    def __init__(self, screen, correct_response, actual_response, font, padding):
        self.screen = screen
        self.correct_response = correct_response
        self.actual_response = actual_response
        self.font = font
        self.padding = padding

        self.color_grid = [[experiments.constants.BLACK] * len(correct_response[0]) for _ in
                           range(len(correct_response))]
        self.char_grid = CharacterGrid(screen=screen, grid=actual_response, font=font, color_grid=self.color_grid)

    def __call__(self, *args, **kwargs):
        n_rows = len(self.correct_response)
        n_cols = len(self.correct_response[0])

        for i in range(n_rows):
            for j in range(n_cols):
                self.color_grid[i][j] = self._color(self.correct_response[i][j], self.actual_response[i][j])

        self.char_grid.update()
        self.char_grid.draw(self.screen)

        self.char_grid.refresh()

    def _color(self, correct, actual):
        correct_color = experiments.constants.GREEN
        incorrect_color = experiments.constants.RED

        return correct_color if actual == correct else incorrect_color


class SpriteRenderer(object):
    def __init__(self, screen, sprite):
        self.screen = screen
        self.sprite = sprite

    def __call__(self, *args, **kwargs):
        self.sprite.update()
        self.screen.blit(self.sprite.image, self.sprite.rect)


class MaskRenderer(object):
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color

    def __call__(self, *args, **kwargs):
        self.screen.fill(self.color)


class WaitUntilKeyHandler(object):
    def __init__(self, terminal_event):
        self.terminal_event = terminal_event

    def __call__(self, event):
        if event.type == pygame.KEYDOWN and event.key == self.terminal_event:
            return True

        return False


key_dict = {eval('pygame.K_{}'.format(char.lower())): char.upper() for char in experiments.constants.CONSONANTS}


class GridEventHandler(WaitUntilKeyHandler):
    def __init__(self, grid, view, terminal_event):
        super().__init__(terminal_event)

        self.grid = grid
        self.view = view
        self.n_rows, self.n_cols = len(self.grid), len(self.grid[0])
        self.pos = [0, 0]

    def __call__(self, event):
        if event.type == pygame.KEYDOWN:

            # process characters in charset
            if event.key in key_dict:
                self.grid[self.pos[0]][self.pos[1]] = key_dict[event.key]
                self.view.refresh()

            # question mark
            elif event.key == pygame.K_SLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.grid[self.pos[0]][self.pos[1]] = '?'
                self.view.refresh()

            # move grid position
            elif event.key == pygame.K_UP:
                self.pos[0] = (self.pos[0] - 1) % self.n_rows
            elif event.key == pygame.K_DOWN:
                self.pos[0] = (self.pos[0] + 1) % self.n_rows
            elif event.key == pygame.K_LEFT:
                self.pos[1] = (self.pos[1] - 1) % self.n_cols
            elif event.key == pygame.K_RIGHT:
                self.pos[1] = (self.pos[1] + 1) % self.n_cols

        return super().__call__(event)
