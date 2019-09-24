import itertools
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

import sperling
import pygame

import sperling.constants

pygame.init()
screen = pygame.display.set_mode((32, 24))
font = pygame.font.SysFont("consolas", size=1)


class TestSerialTrialRunner(TestCase):

    def setUp(self):
        self._items = [
            sperling.TrialItem(name='',
                               renderer=MagicMock(), event_processor=MagicMock(), pre=MagicMock(), post=MagicMock(),
                               duration=50)
            for i in range(10)]

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]))
    def test_run_terminates_on_escape(self):
        with self.assertRaises(InterruptedError):
            self._execute_basic_runner()

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.QUIT, {})]))
    def test_run_terminates_on_quit(self):
        with self.assertRaises(InterruptedError):
            self._execute_basic_runner()

    def test_run_terminates_after_duration(self):
        self._execute_basic_runner()

    @patch('pygame.event.get', MagicMock(return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)]))
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
        runner = sperling.SerialTrialRunner(trial=self._items,
                                            clock=pygame.time.Clock(),
                                            surface=screen,
                                            fps=100)

        total_elapsed_time = runner.run()
        return runner, total_elapsed_time


class TestTrialItem(TestCase):
    def test_init(self):

        # A renderer callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            sperling.TrialItem(name='', renderer=1)
        self.assertEqual(str(context.exception), 'renderer must be a callable')

        # A event_processor callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            sperling.TrialItem(name='', renderer=sperling.constants.NO_OP, event_processor=1)
        self.assertEqual(str(context.exception), 'event_processor, if defined, must be a callable')

        # A pre callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            sperling.TrialItem(name='', renderer=sperling.constants.NO_OP, pre='invalid')
        self.assertEqual(str(context.exception), 'pre, if defined, must be a callable')

        # A post callback, if provided, must be a callable
        with self.assertRaises(ValueError) as context:
            sperling.TrialItem(name='', renderer=sperling.constants.NO_OP, post='invalid')
        self.assertEqual(str(context.exception), 'post, if defined, must be a callable')

        with self.assertRaises(ValueError) as context:
            sperling.TrialItem(name='', renderer=sperling.constants.NO_OP, duration=-1)
        self.assertEqual(str(context.exception), 'duration, if defined, must be non-negative')

        # Valid input
        try:
            name = 'item name'
            pre = lambda x: 1
            render = lambda x: 2
            event_p = lambda x: 3
            post = lambda x: 4
            duration = 100

            item = sperling.TrialItem(name=name, renderer=render, event_processor=event_p, pre=pre, post=post,
                                      duration=duration)

            self.assertEqual(item.name, name)
            self.assertEqual(item.renderer, render)
            self.assertEqual(item.event_processor, event_p)
            self.assertEqual(item.pre, pre)
            self.assertEqual(item.post, post)
            self.assertEqual(item.duration, duration)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))


class TestGridGenerator(TestCase):

    def test_valid_grid_specs(self):
        try:
            # Test row and column bounds
            sperling.GridGenerator(n_rows=1, n_columns=1, charset=sperling.constants.CONSONANTS)
            sperling.GridGenerator(n_rows=1, n_columns=10, charset=sperling.constants.CONSONANTS)
            sperling.GridGenerator(n_rows=10, n_columns=1, charset=sperling.constants.CONSONANTS)

        except Exception as exc:
            self.fail('Raised unexpected exception: {}'.format(exc))

    def test_invalid_grid_spec_raises_value_error(self):
        # Check row bounds
        with self.assertRaises(ValueError) as context:
            sperling.GridGenerator(n_rows=0, n_columns=1, charset=sperling.constants.CONSONANTS)

        self.assertEqual(
            'Invalid Number of CharacterGrid Rows: Must be > 0.',
            str(context.exception))

        # Check Column Bounds
        with self.assertRaises(ValueError) as context:
            sperling.GridGenerator(n_rows=1, n_columns=0, charset=sperling.constants.CONSONANTS)

        self.assertEqual(
            'Invalid Number of CharacterGrid Columns: Must be > 0.',
            str(context.exception))

    def test_create_grid(self):

        n_rows = 5
        n_columns = 4
        charset_id = 'consonants'

        try:
            spec = sperling.GridGenerator(n_rows, n_columns, charset_id)
            grid = spec()

            self.assertIsInstance(grid, list)
            self.assertEqual(len(grid), n_rows)

            for row in grid:
                self.assertEqual(len(row), n_columns)

                for char in row:
                    self.assertIn(char, spec.charset)

            # Verify characters are unique
            self.assertEqual(sum(1 for row in grid for char in row), n_rows * n_columns)

        except Exception as exc:
            self.fail('Raised unexpected exception: {}'.format(exc))

    def test_randomized_spec(self):
        generate_grid = sperling.GridGenerator.get_random_spec(
            range_rows=(1, 1),
            range_columns=(5, 5),
            charset=sperling.constants.CONSONANTS)

        grid = generate_grid()
        self.assertEqual(len(grid), 1)
        self.assertEqual(len(grid[0]), 5)
        self.assertTrue(all(map(lambda c: c in sperling.constants.CONSONANTS, itertools.chain.from_iterable(grid))))

        row_low, row_high = 1, 5
        column_low, column_high = 3, 5
        for _ in range(100):
            generate_grid = sperling.GridGenerator.get_random_spec(
                range_rows=(row_low, row_high),
                range_columns=(column_low, column_high),
                charset=sperling.constants.CONSONANTS)

            self.assertTrue(row_low <= len(generate_grid()) <= row_high)

            for row in generate_grid():
                self.assertTrue(column_low <= len(row) <= column_high)
                self.assertTrue(
                    all(map(lambda c: c in sperling.constants.CONSONANTS, itertools.chain.from_iterable(row))))

    def test_to_string(self):
        generator = sperling.GridGenerator(n_rows=3, n_columns=4, charset=sperling.constants.ALPHANUM,
                                           allow_repeats=False)

        expected_string = 'n_rows: {}, n_columns: {}, charset: {}, allow_repeats: {}'.format(generator.n_rows,
                                                                                             generator.n_columns,
                                                                                             generator.charset,
                                                                                             generator.allow_repeats)
        self.assertEqual(str(generator), expected_string)


class TestSession(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.subject = 'Roy E. Subject'
        cls.experiments = [sperling.experiments.Experiment1(screen, font)]
        cls.session_id = '123-456-789'
        cls.prng_seed = 8675309

    def test_create_session(self):
        try:
            session = sperling.Session(subject=self.subject, experiments=self.experiments)

            # verify field values initialized properly from arguments
            self.assertEqual(session.subject, self.subject)
            self.assertListEqual(session.experiments, self.experiments)
            self.assertIsNotNone(session.session_id)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))

    def test_run(self):
        exp1 = sperling.experiments.Experiment1(screen, font)
        exp1.run = Mock(return_value=None)

        exp2 = sperling.experiments.Experiment1(screen, font)
        exp2.run = Mock(return_value=None)

        session = sperling.Session(self.subject, experiments=[exp1, exp2])

        try:
            session.run()

            exp1.run.assert_called_once()
            exp2.run.assert_called_once()

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))


class TestExperiment(TestCase):

    @patch('sperling.SerialTrialRunner.run')
    def test_run(self, run):
        experiment = sperling.experiments.Experiment1(screen, font, n_trials=10)

        try:
            experiment.run()

            self.assertEqual(run.call_count, experiment.n_trials)

        except Exception as exc:
            self.fail('Unexpected exception: {}'.format(exc))
