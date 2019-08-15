import string
import yaml
import collections
import random

Screen = collections.namedtuple('Screen', ["width", "height"])

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600


class Experiment:

    def __init__(self, config):
        self._config = None

        with open(config, 'r') as stream:
            self._config = yaml.safe_load(stream)

        self.screen = Screen(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        self._load_global(self._config)
        self._load_specific(self._config)

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def _load_global(self, config):
        print("Processing global config")

        self.screen = Screen(width=config['screen']['width'],
                             height=config['screen']['height'])

    def _load_specific(self, config):
        pass


MAX_GRID_ROWS = 5
MAX_GRID_COLUMNS = 5

ALPHA = set(string.ascii_uppercase)
ALPHANUM = ALPHA.union(string.digits)
VOWELS = set('AEIOUY')
CONSONANTS = ALPHA.difference(VOWELS)

CHARSET_CONSONANTS = ''
SUPPORTED_CHARSETS_DICT = {
    'consonants': CONSONANTS,
    'alpha': ALPHA,
    'alphanum': ALPHANUM}


class GridSpec:
    def __init__(self, n_rows, n_columns, charset_id):
        self.n_rows = n_rows
        self.n_columns = n_columns

        if not 0 < self.n_rows <= MAX_GRID_ROWS:
            raise ValueError('Invalid Number of Grid Rows: Must be > 0 and < {}.'.format(MAX_GRID_ROWS))

        if not 0 < self.n_columns <= MAX_GRID_COLUMNS:
            raise ValueError('Invalid Number of Grid Columns: Must be > 0 and < {}.'.format(MAX_GRID_COLUMNS))

        try:
            self.charset = SUPPORTED_CHARSETS_DICT[charset_id]
        except KeyError:
            raise ValueError(
                'Invalid Grid Character Set: Must be one of {}'.format(','.join(
                    sorted(SUPPORTED_CHARSETS_DICT.keys()))))

    def create_grid(self):
        chars = random.sample(self.charset, k=self.n_rows * self.n_columns)
        return [chars[i * self.n_columns:(i + 1) * self.n_columns] for i in range(self.n_rows)]


class Experiment1(Experiment):

    def __init__(self, config):
        super().__init__(config)

        self.grid_spec = None

    def _load_specific(self, config):
        print("Processing experiment specific config")

        grid = config['grid']
        self.grid_spec = GridSpec(n_rows=grid['n_rows'],
                                  n_columns=grid['n_columns'],
                                  charset_id=grid['charset'])


def no_op():
    pass


class DisplayItem(object):
    def __init__(self, render, pre=no_op, post=no_op, interrupt_after=None):
        self.render = render
        self.pre = pre
        self.post = post
        self.interrupt_after = interrupt_after

        self._validate()

    def _validate(self):
        if not callable(self.render):
            raise ValueError('render must be a callable')

        if self.pre and not callable(self.pre):
            raise ValueError('pre, if defined, must be a callable')

        if self.post and not callable(self.post):
            raise ValueError('post, if defined, must be a callable')

        if self.interrupt_after and self.interrupt_after <= 0:
            raise ValueError('interrupt_after, if defined, must be positive: received {}'.format(self.interrupt_after))


class SerialDisplayer(object):
    def __init__(self, items):
        self.items = items

        self._validate()

    def _validate(self):
        # Check that items is iterable
        iter(self.items)

        # Check that items not empty
        if not self.items:
            raise ValueError('items must not be empty')

        # Check that all items are of DisplayItem type
        for item in self.items:
            if not isinstance(item, DisplayItem):
                raise TypeError('item of invalid type: {}'.format(type(item)))

    def __len__(self):
        return len(self.items)
