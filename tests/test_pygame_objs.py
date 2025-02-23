import unittest
import sperling
import pygame

import sperling.constants

pygame.init()
screen = pygame.display.set_mode((32, 24))


class TestPygameGrid(unittest.TestCase):
    def test_init(self):
        grid_spec = sperling.GridGenerator(n_rows=3, n_columns=4, charset=sperling.constants.CONSONANTS)
        font = pygame.font.SysFont("courier", size=100)
        grid_values = grid_spec()

        try:
            char_grid = sperling.view.CharacterGrid(grid=grid_values, font=font)

            # Check internal state after initializer assignments
            self.assertIs(char_grid.grid, grid_values)
            self.assertIs(char_grid.font, font)
            self.assertEqual(char_grid._char_dims, font.size('A'))

            # Verify one sprite per character in grid spec
            self.assertEqual(len(char_grid._sprite_group), grid_spec.n_rows * grid_spec.n_columns)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))
