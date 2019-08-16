from itertools import chain

import pygame
import collections

Dimensions = collections.namedtuple('Dimensions', ['width', 'height'])


class CrossHairs(pygame.sprite.Sprite):
    def __init__(self, pos, width, color):
        super().__init__()

        self.image = pygame.Surface([width, width])
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        # Draw crosshairs
        pygame.draw.line(self.image, (255, 255, 255), (0, width // 2), (width, width // 2), 5)
        pygame.draw.line(self.image, (255, 255, 255), (width // 2, 0), (width // 2, width), 5)

        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - width // 2
        self.rect.y = pos[1] - width // 2

    def update(self):
        pass


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
    def __init__(self, grid_spec, pos, width, height, font, vert_margin=0, horiz_margin=0, color=(0,0,0)):
        super().__init__()

        self.grid_spec = grid_spec
        self.width = width
        self.height = height
        self.font = font
        self.pos = pos
        self.color = color

        self._char_dims = Dimensions(*self.font.size('A'))  # Assumes fixed-width font
        self._grid_dims = Dimensions(width, height)
        self._margin_dims = Dimensions(horiz_margin, vert_margin)
        self._spacer_dims = self._get_spacer_dims()

        self.char_values = None

        # Pygame Surfaces and Sprites
        self.grid_surface = pygame.Surface([width, height])

        self.reset()

        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())

    def _get_spacer_dims(self):
        w_grid, h_grid = self._grid_dims
        w_char, h_char = self._char_dims

        n_rows, n_cols = self.grid_spec.n_rows, self.grid_spec.n_columns

        space_x = (w_grid - self._margin_dims.width - n_cols * w_char) // (n_cols - 1)
        space_y = (h_grid - self._margin_dims.height - n_rows * h_char) // (n_rows - 1)

        return Dimensions(space_x, space_y)

    def randomize(self):
        self.char_values = self.grid_spec.create_grid()

        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())

    def reset(self):
        self.char_values = [[' '] * self.grid_spec.n_columns] * self.grid_spec.n_rows

        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self._create_sprites())

    def _create_sprites(self):
        sprites = []
        for i, row in enumerate(self.char_values):
            for j, char in enumerate(row):
                char_pos = (
                    j * (self._char_dims.width + self._spacer_dims.width) + self._margin_dims.width // 2,
                    i * (self._char_dims.height + self._spacer_dims.height) + self._margin_dims.height // 2
                )
                sprite = Character(char, pos=char_pos, font=self.font, color=(255, 255, 255))
                sprites.append(sprite)

        return sprites

    def draw(self, surface):

        # Clear previously rendered letters from surface
        self.grid_surface.fill(self.color)

        # Draw all sprites onto grid surface
        self.sprite_group.draw(self.grid_surface)

        # Draw grid surface onto enclosing surface
        surface.blit(self.grid_surface, self.pos)

    def update(self):
        self.sprite_group.update()
