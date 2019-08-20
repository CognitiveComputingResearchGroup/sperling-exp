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
    def __init__(self, dims, color):
        super().__init__()

        self.color = color

        self.image = pygame.Surface(dims)
        self.rect = self.image.get_rect()

    def update(self):
        width, height = self.image.get_size()
        pygame.draw.polygon(self.image, self.color,
                            [(0, height // 4), (width - 10, height // 4), (width - 10, 0), (width, height // 2),
                             (width - 10, height), (width - 10, 3 * height // 4), (0, 3 * height // 4)])


class CrossHairs(pygame.sprite.Sprite):
    def __init__(self, size, color):
        """A sprite for crosshairs

        :param size (int): width and height (in pixels) of crosshairs
        :param color (3-tuple): foreground color of crosshairs
        """
        super().__init__()

        self.size = size
        self.color = color

        self.image = pygame.Surface([size, size])
        self.image.set_colorkey(experiments.constants.BLACK)

        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill(experiments.constants.BLACK)

        pygame.draw.line(self.image, self.color, (0, self.size // 2), (self.size, self.size // 2), 5)
        pygame.draw.line(self.image, self.color, (self.size // 2, 0), (self.size // 2, self.size), 5)


class Character(pygame.sprite.Sprite):
    def __init__(self, char, pos, font, color):
        super().__init__()

        self.char = char
        self.pos = pos
        self.font = font
        self.color = color

        self.image = self.font.render(self.char, 1, self.color)
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.font.render(self.char, 1, self.color)
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = self.pos


class CharacterGridWithArrowCues(pygame.sprite.Sprite):
    def __init__(self, screen, char_grid, bg_color):
        super().__init__()

        self.screen = screen
        self.char_grid = char_grid
        self.bg_color = bg_color

        self._arrow_dims = Dimensions(50, 20)
        self._grid_dims = Dimensions(width=self.char_grid.image.get_width() + self._arrow_dims.width,
                                     height=self.char_grid.image.get_height())

        self.image = pygame.Surface(self._grid_dims)
        # self.image.set_colorkey(self.bg_color)

        self.rect = self.image.get_rect()

        self._x_margin, self._y_margin = (10, 10)
        self._x_arrow_spacer, self._y_arrow_spacer = (15, 15)

        self._sprite_group = pygame.sprite.Group()
        self._sprite_group.add(self._create_sprites())

    def _create_sprites(self):
        sprites = []

        for i in range(self.char_grid.n_rows):
            arrow_pos = (
                self._x_margin,
                i * (self._arrow_dims.height + self._y_arrow_spacer) + self._y_margin
            )
            arrow_sprite = ArrowCue(self.screen,
                                    Dimensions(width=self._arrow_dims.width, height=self._arrow_dims.height),
                                    color=experiments.constants.GRAY)
            arrow_sprite.rect.topleft = arrow_pos
            sprites.append(arrow_sprite)

        return sprites

    def _get_position(self):
        screen_width, screen_height = self.screen.get_size()

        x = (screen_width - self._grid_dims.width) // 2
        y = (screen_height - self._grid_dims.height) // 2

        return x, y

    def draw(self, *args):
        # Clear previously rendered letters from surface
        self.image.fill(experiments.constants.RED)

        for sprite in self._sprite_group:
            self.image.blit(sprite.image, sprite.pos)

        self.char_grid.draw()

        # Draw all sprites onto grid surface
        self._sprite_group.draw(self.image)

        # Draw grid surface onto enclosing surface
        self.screen.blit(self.image, self._get_position())

    def update(self):
        self._sprite_group.update()
        # self.char_grid.update()

    def refresh(self):
        self._sprite_group = pygame.sprite.Group()
        self._sprite_group.add(self._create_sprites())


class CharacterGrid(pygame.sprite.Sprite):
    def __init__(self, grid, font, color_grid=None):
        super().__init__()

        self.grid = grid
        self.n_rows = len(grid)
        self.n_columns = len(grid[0])

        self.font = font
        self.color_grid = color_grid or [[experiments.constants.WHITE] * self.n_columns for _ in range(self.n_rows)]

        self._x_margin, self._y_margin = (10, 10)
        self._x_char_spacer, self._y_char_spacer = (10, 10)
        self._char_dims = Dimensions(*self.font.size('A'))  # Assumes fixed-size font
        self._grid_dims = self._get_grid_dims()

        # Pygame Surfaces and Sprites
        self.image = pygame.Surface(self._grid_dims)
        self.image.set_colorkey(experiments.constants.BLACK)

        self.rect = self.image.get_rect()

        self._sprite_group = pygame.sprite.Group()
        self._sprite_group.add(self._create_sprites())

    def _get_grid_dims(self):
        width = 2 * self._x_margin + (self.n_columns - 1) * self._x_char_spacer + self.n_columns * self._char_dims.width
        height = 2 * self._y_margin + (self.n_rows - 1) * self._y_char_spacer + self.n_rows * self._char_dims.height

        return Dimensions(width, height)

    def _create_sprites(self):
        sprites = []

        for i, row in enumerate(self.grid):
            # add characters
            for j, char in enumerate(row):
                char_pos = (
                    j * (self._char_dims.width + self._x_char_spacer) + self._x_margin,
                    i * (self._char_dims.height + self._y_char_spacer) + self._y_margin
                )
                char_sprite = Character(char, pos=char_pos, font=self.font, color=self.color_grid[i][j])
                sprites.append(char_sprite)

        return sprites

    def update(self):
        self.image.fill(experiments.constants.BLACK)
        self._sprite_group.update()
        self._sprite_group.draw(self.image)

    def refresh(self):
        self._sprite_group = pygame.sprite.Group()
        self._sprite_group.add(self._create_sprites())


class GridRenderer:
    def __init__(self, surface, pos, grid):
        self.surface = surface
        self.pos = pos
        self.grid = grid

    def __call__(self, *args, **kwargs):
        # clear previously rendered letters
        self.surface.fill(experiments.constants.BLACK)

        self.grid.rect.topleft = self.pos
        self.grid.update()

        self.surface.blit(self.grid.image, self.grid.rect)

    def refresh(self):
        self.grid.refresh()


class FeedbackGridRenderer:
    def __init__(self, surface, grid, correct_response, actual_response):
        self.surface = surface
        self.grid = grid
        self.correct_response = correct_response
        self.actual_response = actual_response

    def __call__(self, *args, **kwargs):
        n_rows = len(self.correct_response)
        n_cols = len(self.correct_response[0])

        for i in range(n_rows):
            for j in range(n_cols):
                self.grid.color_grid[i][j] = self._color(self.correct_response[i][j], self.actual_response[i][j])

        self.grid.image.fill(experiments.constants.BLACK)
        self.grid.update()

        self.surface.blit(self.grid.image, self.grid.rect)

        self.grid.refresh()

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
