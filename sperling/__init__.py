import collections
import itertools
import random
import copy
import pygame

import sperling.constants
import sperling.view
import sperling.experiments


class SerialTrialRunner(object):
    def __init__(self, trial, clock, surface, fps):
        self.trial = trial
        self.clock = clock
        self.surface = surface
        self.fps = fps

    def run(self):
        elapsed_time = 0
        for item in self.trial:
            pre_out = item.pre()
            time, events = self.execute_item(item, self)
            elapsed_time += time
            item.post(time=time, elapsed_time=elapsed_time, events=events, pre_out=pre_out)

        return elapsed_time

    def execute_item(self, item, runner):
        elapsed_time = 0
        terminal_event = False

        """
            pygame.event.event_name - get the string name from an event id
        """
        events = []

        while not terminal_event and elapsed_time <= (item.duration or constants.MAX_DURATION):
            # Process Events
            for event in pygame.event.get():
                events.append(event)

                # Global termination events
                if view.is_terminal_event(event):
                    raise InterruptedError('User terminated experiment')

                # Item specific event processing
                terminal_event = item.process_event(event)

            # Render surface updates
            item.render(self.surface)
            pygame.display.flip()

            elapsed_time += self.clock.get_time()

            # Advance clock
            self.clock.tick(runner.fps)

        return elapsed_time, events


class TrialItem(object):
    def __init__(self, renderer, event_processor=sperling.constants.NO_OP, pre=sperling.constants.NO_OP,
                 post=sperling.constants.NO_OP, duration=constants.MAX_DURATION):
        self.renderer = renderer
        self.event_processor = event_processor
        self.pre = pre
        self.post = post
        self.duration = duration

        self._validate()

    def _validate(self):
        if not callable(self.renderer):
            raise ValueError('renderer must be a callable')

        if self.event_processor and not callable(self.event_processor):
            raise ValueError('event_processor, if defined, must be a callable')

        if self.pre and not callable(self.pre):
            raise ValueError('pre, if defined, must be a callable')

        if self.post and not callable(self.post):
            raise ValueError('post, if defined, must be a callable')

        if self.duration and self.duration < 0:
            raise ValueError('duration, if defined, must be non-negative')

    def render(self, *args, **kwargs):
        self.renderer(args, kwargs)

    def process_event(self, event):
        return self.event_processor(event)


GridSpec = collections.namedtuple('GridSpec', ['n_rows', 'n_columns', 'charset', 'allow_repeats'])

class GridGenerator:
    def __init__(self, n_rows, n_columns, charset, allow_repeats=True):
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.charset = charset
        self.allow_repeats = allow_repeats

        if self.n_rows <= 0:
            raise ValueError('Invalid Number of CharacterGrid Rows: Must be > 0.')

        if self.n_columns <= 0:
            raise ValueError('Invalid Number of CharacterGrid Columns: Must be > 0.')

    def __call__(self, *args, **kwargs):
        chars = random.choices(list(self.charset), k=self.n_rows * self.n_columns) \
            if self.allow_repeats else random.sample(self.charset, k=self.n_rows * self.n_columns)
        return [chars[i * self.n_columns:(i + 1) * self.n_columns] for i in range(self.n_rows)]

    def __str__(self):
        return 'n_rows: {}, n_columns: {}, charset: {}, allow_repeats: {}'.format(self.n_rows,
                                                                                  self.n_columns,
                                                                                  self.charset,
                                                                                  self.allow_repeats)

    @classmethod
    def get_random_spec(cls, range_rows, range_columns, charset, allow_repeats=True):
        """ Generates a random grid spec with bounded dimensions.

        Args:
            range_rows (tuple): low/high range (inclusive) for number of grid rows
            range_columns (tuple): low/high range (inclusive) for number of grid columns
            charset (list): character set from which samples will be drawn

        Returns:
            GridGenerator: a rectangular, 2d-list of characters

        """
        n_rows = random.randint(*range_rows)
        n_columns = random.randint(*range_columns)

        return GridGenerator(n_rows=n_rows, n_columns=n_columns, charset=charset, allow_repeats=allow_repeats)


ResponseEntry = collections.namedtuple('ResponseEntry', ['response_time', 'actual_response', 'correct_response'])


class ResponseProcessor(object):
    def __init__(self, correct, actual, results):
        self.correct = correct
        self.actual = actual
        self.results = results

    def __call__(self, *args, **kwargs):
        entry = ResponseEntry(
            response_time=kwargs['time'],
            actual_response=copy.deepcopy(self.actual),
            correct_response=copy.deepcopy(self.correct)
        )
        self.results.append(entry)


def n_correct(result):
    return sum(1 for a, c in zip(itertools.chain.from_iterable(result.actual_response),
                                 itertools.chain.from_iterable(result.correct_response)) if a == c)
