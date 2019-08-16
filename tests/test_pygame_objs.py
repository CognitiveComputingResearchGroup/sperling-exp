import unittest
import experiments
import experiments.pygame
import pygame

pygame.init()


class TestPygameGrid(unittest.TestCase):
    def test_init(self):
        grid_spec = experiments.GridSpec(n_rows=3, n_columns=4, charset_id=experiments.CHARSET_CONSONANTS)
        font = pygame.font.SysFont("courier", size=100)
        width, height = (800, 600)
        pos = (250, 250)

        try:
            grid = experiments.pygame.CharacterGrid(grid_spec=grid_spec, width=width, height=height, pos=pos, font=font)

            # Check internal state after initializer assignments
            self.assertIs(grid.grid_spec, grid_spec)
            self.assertEqual(grid.width, width)
            self.assertEqual(grid.height, height)
            self.assertEqual(grid.pos, pos)
            self.assertIs(grid.font, font)
            self.assertEqual(grid._char_dims, font.size('A'))

            # Verify one sprite per character in grid spec
            self.assertEqual(len(grid.sprite_group), grid_spec.n_rows * grid_spec.n_columns)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))
