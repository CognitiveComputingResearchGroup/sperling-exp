from unittest import TestCase

import experiments


class TestSerialDisplayer(TestCase):

    def test_init(self):
        # Test no items returns error
        with self.assertRaises(ValueError) as context:
            experiments.SerialDisplayer(items=[])
        self.assertEqual(str(context.exception), 'items must not be empty')

        # Test non-iterable returns error
        with self.assertRaises(TypeError) as context:
            experiments.SerialDisplayer(items=1)

        # Test iterable containing objects that are not DisplayItems returns error
        with self.assertRaises(TypeError) as context:
            experiments.SerialDisplayer(items='invalid')
        self.assertIn('item of invalid type', str(context.exception))

        # Valid input
        try:
            items = [experiments.DisplayItem(render=lambda x: x) for item in range(10)]

            display = experiments.SerialDisplayer(items)
            self.assertEqual(display.items, items)

        except Exception as exc:
            self.fail('Received unexpected exception: {}'.format(exc))

    def test_len(self):

        items = [experiments.DisplayItem(render=lambda x: x) for item in range(10)]
        display = experiments.SerialDisplayer(items)

        self.assertEqual(len(display), len(items))

class TestDisplayItem(TestCase):
    def test_init(self):

        # A render callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            experiments.DisplayItem(render=10)
        self.assertEqual(str(context.exception), 'render must be a callable')

        # A pre callback must be provided and a callable
        with self.assertRaises(ValueError) as context:
            experiments.DisplayItem(render=experiments.no_op, pre='invalid')
        self.assertEqual(str(context.exception), 'pre, if defined, must be a callable')

        # A post callback, if provided, must be a callable
        with self.assertRaises(ValueError) as context:
            experiments.DisplayItem(render=experiments.no_op, post='invalid')
        self.assertEqual(str(context.exception), 'post, if defined, must be a callable')

        # A interrupt time, if provided, must be a callable
        with self.assertRaises(ValueError) as context:
            experiments.DisplayItem(render=experiments.no_op, interrupt_after=-1)
        self.assertEqual(str(context.exception),
                         'interrupt_after, if defined, must be positive: received {}'.format(-1))

        # Valid input
        try:
            pre = lambda x: 1
            render = lambda x: 2
            post = lambda x: 3
            interrupt_after = 1234

            item = experiments.DisplayItem(render, pre, post, interrupt_after)

            self.assertEqual(item.render, render)
            self.assertEqual(item.pre, pre)
            self.assertEqual(item.post, post)
            self.assertEqual(item.interrupt_after, interrupt_after)

        except Exception as exc:
            self.fail('Received unexpected exception: {}'.format(exc))


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
            'Invalid Number of Grid Rows: Must be > 0 and < {}.'.format(experiments.MAX_GRID_ROWS),
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=experiments.MAX_GRID_ROWS + 1, n_columns=1, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of Grid Rows: Must be > 0 and < {}.'.format(experiments.MAX_GRID_ROWS),
            str(context.exception))

        # Check Column Bounds
        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=0, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of Grid Columns: Must be > 0 and < {}.'.format(experiments.MAX_GRID_COLUMNS),
            str(context.exception))

        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=experiments.MAX_GRID_COLUMNS + 1, charset_id='consonants')

        self.assertEqual(
            'Invalid Number of Grid Columns: Must be > 0 and < {}.'.format(experiments.MAX_GRID_COLUMNS),
            str(context.exception))

        # Check Invalid Charset
        with self.assertRaises(ValueError) as context:
            experiments.GridSpec(n_rows=1, n_columns=1, charset_id='invalid')

        self.assertEqual(
            'Invalid Grid Character Set: Must be one of {}'.format(','.join(
                sorted(experiments.SUPPORTED_CHARSETS_DICT.keys()))),
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
