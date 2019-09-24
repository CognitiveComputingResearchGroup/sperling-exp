import collections
import pygame

import sperling.constants


def find_font(acceptable_fonts, size):
    available_fonts = list(set(acceptable_fonts).intersection(set(pygame.font.get_fonts())))
    if not available_fonts:
        raise EnvironmentError('No acceptable fonts found! acceptable fonts = ({})]'.format(','.join(acceptable_fonts)))

    return pygame.font.SysFont(available_fonts[0], size=size)


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
        head_width = width // 5
        pygame.draw.polygon(self.image, self.color,
                            [(0, height // 4), (width - head_width, height // 4), (width - head_width, 0),
                             (width, height // 2), (width - head_width, height),
                             (width - head_width, 3 * height // 4), (0, 3 * height // 4)])


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
        self.image.set_colorkey(sperling.constants.BLACK)

        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill(sperling.constants.BLACK)

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
    def __init__(self, grid, arrow_dims, cue_row, grid_visible=False):
        """

        :param grid (CharacterGrid): a 2d character grid
        :param cue_row (int): the row that is currently being cued (0-offset)
        """
        super().__init__()

        self.grid = grid
        self.arrow_dims = arrow_dims
        self.cue_row = cue_row
        self.grid_visible = grid_visible

        self._x_arrow_spacer, self._y_arrow_spacer = (10, 10)

        self._grid_dims = Dimensions(*self._get_grid_dims())

        self.image = pygame.Surface(self._grid_dims)
        self.rect = self.image.get_rect()

        self.sprites_group = pygame.sprite.RenderPlain()
        self.sprites_group.add(self._create_sprites())

    def _get_grid_dims(self):
        width = self._x_arrow_spacer + self.arrow_dims.width + self.grid._grid_dims.width

        # column arrow cues not supported yet, so this is just the grid height
        height = self.grid._grid_dims.height

        return width, height

    def update(self):
        self.image.fill(sperling.constants.BLACK)

        self.grid.update()
        self.grid.rect.topleft = (self.arrow_dims.width, 0)

        if self.grid_visible:
            self.image.blit(self.grid.image, self.grid.rect)

        self.sprites_group.update()
        self.sprites_group.draw(self.image)

    def _create_sprites(self):
        sprites = []

        spacer_height = (self.grid._char_dims.height - self.arrow_dims.height) // 2

        for i in range(self.grid.n_rows):
            arrow_pos = (
                0,
                spacer_height + i * (self.grid._char_dims.height + self.grid._y_char_spacer) + self.grid._y_margin
            )

            sprite = ArrowCue(self.arrow_dims,
                              color=sperling.constants.GREEN if i == self.cue_row else sperling.constants.GRAY)
            sprite.rect.topleft = arrow_pos

            sprites.append(sprite)

        return sprites


class CharacterGrid(pygame.sprite.Sprite):
    def __init__(self, grid, font, color_grid=None):
        super().__init__()

        self.grid = grid
        self.n_rows = len(grid)
        self.n_columns = len(grid[0])

        self.font = font
        self.color_grid = color_grid or [[sperling.constants.WHITE] * self.n_columns for _ in range(self.n_rows)]

        self._x_margin, self._y_margin = (0, 0)
        self._x_char_spacer, self._y_char_spacer = (5, 0)
        self._char_dims = Dimensions(*self.font.size('A'))  # Assumes fixed-size font
        self._grid_dims = self._get_grid_dims()

        # Pygame Surfaces and Sprites
        self.image = pygame.Surface(self._grid_dims)
        self.image.set_colorkey(sperling.constants.BLACK)

        self.rect = self.image.get_rect()

        self._sprite_group = pygame.sprite.Group()
        self._sprite_group.add(self._create_sprites())

    def _get_grid_dims(self):
        width = 2 * self._x_margin + (
                self.n_columns - 1) * self._x_char_spacer + self.n_columns * self._char_dims.width
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
        self.image.fill(sperling.constants.BLACK)
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
        self.surface.fill(sperling.constants.BLACK)

        self.grid.rect.topleft = self.pos
        self.grid.update()

        self.surface.blit(self.grid.image, self.grid.rect)
        pygame.display.flip()

    def refresh(self):
        self.grid.refresh()


class FeedbackGridRenderer:
    def __init__(self, surface, grid, correct, actual):
        self.surface = surface
        self.grid = grid
        self.correct = correct
        self.actual_response = actual

    def __call__(self, *args, **kwargs):
        n_rows = len(self.correct)
        n_cols = len(self.correct[0])

        for i in range(n_rows):
            for j in range(n_cols):
                self.grid.color_grid[i][j] = self._color(self.correct[i][j], self.actual_response[i][j])

        self.grid.image.fill(sperling.constants.BLACK)
        self.grid.update()

        self.surface.blit(self.grid.image, self.grid.rect)

        self.grid.refresh()
        pygame.display.flip()

    def _color(self, correct, actual):
        correct_color = sperling.constants.GREEN
        incorrect_color = sperling.constants.RED

        return correct_color if actual == correct else incorrect_color


class SpriteRenderer(object):
    def __init__(self, screen, sprite):
        self.screen = screen
        self.sprite = sprite

    def __call__(self, *args, **kwargs):
        self.sprite.update()
        self.screen.blit(self.sprite.image, self.sprite.rect)
        pygame.display.flip()


class MaskRenderer(object):
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color

    def __call__(self, *args, **kwargs):
        self.screen.fill(self.color)
        pygame.display.flip()


class WaitUntilKeyHandler(object):
    def __init__(self, terminal_event):
        self.terminal_event = terminal_event

    def __call__(self, event):
        if event.type == pygame.KEYDOWN and event.key == self.terminal_event:
            return True

        return False


key_dict = {eval('pygame.K_{}'.format(char.lower())): char.upper() for char in sperling.constants.CONSONANTS}


class GridEventHandler(WaitUntilKeyHandler):
    def __init__(self, grid, view, terminal_event):
        super().__init__(terminal_event)

        self.grid = grid
        self.view = view
        self.n_rows, self.n_cols = len(self.grid.grid), len(self.grid.grid[0])
        self.pos = [0, 0]

        # Highlight character in current position
        self.grid.color_grid[self.pos[0]][self.pos[1]] = sperling.constants.YELLOW
        self.view.refresh()

    def __call__(self, event):
        if event.type == pygame.KEYDOWN:

            prev_pos = self.pos[0], self.pos[1]
            # process characters in charset
            if event.key in key_dict:
                self.grid.grid[self.pos[0]][self.pos[1]] = key_dict[event.key]
                self.pos[1] = (self.pos[1] + 1) % self.n_cols

            # question mark
            elif event.key == pygame.K_SLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.grid.grid[self.pos[0]][self.pos[1]] = '?'
                self.pos[1] = (self.pos[1] + 1) % self.n_cols

            elif event.key == pygame.K_BACKSPACE:
                self.grid.grid[self.pos[0]][self.pos[1] - 1] = '?'
                self.pos[1] = (self.pos[1] - 1) % self.n_cols

            # move grid position
            elif event.key == pygame.K_UP:
                self.pos[0] = (self.pos[0] - 1) % self.n_rows
            elif event.key == pygame.K_DOWN:
                self.pos[0] = (self.pos[0] + 1) % self.n_rows
            elif event.key == pygame.K_LEFT:
                self.pos[1] = (self.pos[1] - 1) % self.n_cols
            elif event.key == pygame.K_RIGHT:
                self.pos[1] = (self.pos[1] + 1) % self.n_cols

            self.grid.color_grid[prev_pos[0]][prev_pos[1]] = sperling.constants.WHITE
            self.grid.color_grid[self.pos[0]][self.pos[1]] = sperling.constants.YELLOW

            self.view.refresh()
        return super().__call__(event)


Dimensions = collections.namedtuple('Dimensions', ['width', 'height'])
