import pygame
import sys

from experiments.datatypes import Dimensions


def is_terminal_event(event):
    return event.type == pygame.QUIT \
           or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)


def terminate():
    pygame.quit()


class CrossHairs(pygame.sprite.Sprite):
    def __init__(self, pos, width, color):
        super().__init__()

        self.pos = pos
        self.width = width
        self.color = color

        self.image = pygame.Surface([width, width])
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - width // 2
        self.rect.y = pos[1] - width // 2

    def update(self):
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
    def __init__(self, screen, grid, pos, width, height, font, vert_margin=0, horiz_margin=0, color=(0, 0, 0)):
        super().__init__()

        self.screen = screen
        self.grid = grid
        self.n_rows = len(grid)
        self.n_columns = len(grid[0])

        self.width = width
        self.height = height
        self.font = font
        self.pos = pos
        self.color = color

        self._char_dims = Dimensions(*self.font.size('A'))  # Assumes fixed-width font
        self._grid_dims = Dimensions(width, height)
        self._margin_dims = Dimensions(horiz_margin, vert_margin)
        self._spacer_dims = self._get_spacer_dims()

        # Pygame Surfaces and Sprites
        self.grid_surface = pygame.Surface([width, height])

        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())

    def _get_spacer_dims(self):
        w_grid, h_grid = self._grid_dims
        w_char, h_char = self._char_dims

        n_rows, n_cols = self.n_rows, self.n_columns

        space_x = (w_grid - self._margin_dims.width - n_cols * w_char) // (n_cols - 1)
        space_y = (h_grid - self._margin_dims.height - n_rows * h_char) // (n_rows - 1)

        return Dimensions(space_x, space_y)

    def _create_sprites(self):
        sprites = []
        for i, row in enumerate(self.grid):
            for j, char in enumerate(row):
                char_pos = (
                    j * (self._char_dims.width + self._spacer_dims.width) + self._margin_dims.width // 2,
                    i * (self._char_dims.height + self._spacer_dims.height) + self._margin_dims.height // 2
                )
                sprite = Character(char, pos=char_pos, font=self.font, color=(255, 255, 255))
                sprites.append(sprite)

        return sprites

    def draw(self, *args):
        # Clear previously rendered letters from surface
        self.grid_surface.fill(self.color)

        # Draw all sprites onto grid surface
        self.sprite_group.draw(self.grid_surface)

        # Draw grid surface onto enclosing surface
        self.screen.blit(self.grid_surface, self.pos)

    def update(self):
        self.sprite_group.update()


class GridRenderer:
    def __init__(self, screen, grid, font, padding):
        self.screen = screen
        self.grid = grid
        self.font = font
        self.padding = padding

        screen_dims = Dimensions(*screen.get_size())

        grid_dims = Dimensions(screen_dims.width - 2 * self.padding.width,
                               screen_dims.height - 2 * self.padding.height)

        grid_pos = (
            (screen_dims.width - grid_dims.width) / 2,
            (screen_dims.height - grid_dims.height) / 2
        )

        self.char_grid = CharacterGrid(screen=screen,
                                       grid=grid,
                                       pos=grid_pos,
                                       font=font,
                                       width=grid_dims.width,
                                       height=grid_dims.height,
                                       horiz_margin=100,
                                       vert_margin=100
                                       )

    def __call__(self, *args, **kwargs):
        self.char_grid.update()
        self.char_grid.draw(self.screen)


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
