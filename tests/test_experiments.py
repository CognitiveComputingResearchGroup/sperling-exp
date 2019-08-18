from unittest import TestCase
from unittest.mock import patch, MagicMock

import experiments
import pygame

pygame.init()
screen = pygame.display.set_mode((32, 24))


class TestSerialTrialRunner(TestCase):

    def setUp(self):
        self._items = [
            experiments.TrialItem(
                renderer=MagicMock(), event_processor=MagicMock(), pre=MagicMock(), post=MagicMock(), duration=50)
            for i in range(10)]

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]))
    def test_run_terminates_on_escape(self):
        self._execute_basic_runner()

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.QUIT, {})]))
    def test_run_terminates_on_quit(self):
        self._execute_basic_runner()

    def test_run_terminates_after_duration(self):
        self._execute_basic_runner()

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_0)]))
    def test_run_calls_all_item_methods(self):
        runner, _ = self._execute_basic_runner()

        try:
            for item in runner.trial:
                item.pre.assert_called()
                item.renderer.assert_called()
                item.event_processor.assert_called()
                item.post.assert_called()

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))

    def _execute_basic_runner(self):
        runner = experiments.SerialTrialRunner(trial=self._items,
                                               clock=pygame.time.Clock(),
                                               surface=screen,
                                               fps=100)

        try:
            total_elapsed_time = runner.run()
            return runner, total_elapsed_time
        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))


class TestTrialItem(TestCase):
    def test_init(self):

        # A renderer callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            experiments.TrialItem(renderer=1)
        self.assertEqual(str(context.exception), 'renderer must be a callable')

        # A event_processor callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            experiments.TrialItem(renderer=experiments.functions.no_op, event_processor=1)
        self.assertEqual(str(context.exception), 'event_processor, if defined, must be a callable')

        # A pre callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            experiments.TrialItem(renderer=experiments.functions.no_op, pre='invalid')
        self.assertEqual(str(context.exception), 'pre, if defined, must be a callable')

        # A post callback, if provided, must be a callable
        with self.assertRaises(ValueError) as context:
            experiments.TrialItem(renderer=experiments.functions.no_op, post='invalid')
        self.assertEqual(str(context.exception), 'post, if defined, must be a callable')

        with self.assertRaises(ValueError) as context:
            experiments.TrialItem(renderer=experiments.functions.no_op, duration=-1)
        self.assertEqual(str(context.exception), 'duration, if defined, must be non-negative')

        # Valid input
        try:
            pre = lambda x: 1
            render = lambda x: 2
            event_p = lambda x: 3
            post = lambda x: 4
            duration = 100

            item = experiments.TrialItem(renderer=render, event_processor=event_p, pre=pre, post=post, duration=duration)

            self.assertEqual(item.renderer, render)
            self.assertEqual(item.event_processor, event_p)
            self.assertEqual(item.pre, pre)
            self.assertEqual(item.post, post)
            self.assertEqual(item.duration, duration)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))


class TestGridSpec(TestCase):

    def test_valid_grid_specs(self):
        try:
            # Test row and column bounds
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='consonants')
            experiments.GridSpec(n_rows=1, n_columns=experiments.MAX_GRID_COLUMNS, charset_id='consonants')
            experiments.GridSpec(n_rows=experiments.MAX_GRID_ROWS, n_columns=1, charset_id='consonants')
            experiments.GridSpec(n_rows=experiments.MAX_GRID_ROWS, n_columns=experiments.MAX_GRID_COLUMNS,
                                 charset_id='consonants')

            # Test all valid charsets
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='consonants')
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='alpha')
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='alphanum')

        except Exception as exc:
            self.fail('Raised unexpected exception: {}'.format(exc))

    def test_invalid_grid_spec_raises_value_error(self):
        # Check row bounds
        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=0, n_columns=1, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of CharacterGrid Rows: Must be > 0 and < {}.'.format(experiments.MAX_GRID_ROWS),
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=experiments.MAX_GRID_ROWS + 1, n_columns=1, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of CharacterGrid Rows: Must be > 0 and < {}.'.format(experiments.MAX_GRID_ROWS),
            str(context.exception))

        # Check Column Bounds
        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=0, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of CharacterGrid Columns: Must be > 0 and < {}.'.format(experiments.MAX_GRID_COLUMNS),
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=experiments.MAX_GRID_COLUMNS + 1, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of CharacterGrid Columns: Must be > 0 and < {}.'.format(experiments.MAX_GRID_COLUMNS),
            str(context.exception))

        # Check Invalid Charset
        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='invalid')

        self.assertEqual(
            'Invalid CharacterGrid Character Set: Must be one of {}'.format(','.join(
                sorted(experiments.charsets_dict.keys()))),
            str(context.exception))

    def test_create_grid(self):

        n_rows = 5
        n_columns = 4
        charset_id = 'consonants'

        try:
            spec = experiments.GridSpec(n_rows, n_columns, charset_id)
            grid = spec.create_grid()

            self.assertIsInstance(grid, list)
            self.assertEqual(len(grid), n_rows)

            for row in grid:
                self.assertEqual(len(row), n_columns)

                for char in row:
                    self.assertIn(char, spec.charset)

            # Verify characters are unique
            self.assertEqual(len(set([l for row in grid for l in row])), n_rows * n_columns)

        except Exception as exc:
            self.fail('Raised unexpected exception: {}'.format(exc))
