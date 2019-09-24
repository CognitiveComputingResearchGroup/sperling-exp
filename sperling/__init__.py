import collections
import itertools
import random
import copy
import pygame
import uuid

import sperling.constants
import sperling.view
import sperling.experiments


class Session(object):

    def __init__(self, subject, experiments):
        self.subject = subject
        self.experiments = experiments

        self.session_id = Session._generate_session_id()

    @staticmethod
    def _generate_session_id():
        return uuid.uuid4()

    def run(self, fps=sperling.constants.DEFAULT_FPS):
        for experiment in self.experiments:
            experiment.run(fps)


class SerialTrialRunner(object):
    def __init__(self, trial, clock, surface, fps):
        self.trial = trial
        self.clock = clock
        self.surface = surface
        self.fps = fps

        self.times_per_item = collections.OrderedDict()

    def run(self):
        elapsed_time = 0
        for item in self.trial:
            item_time = 0
            elapsed_time = 0

            pre_out = item.pre()

            try:
                item_time = self._execute_item(item, self)
                self.times_per_item[item.name] = item_time
            except InterruptedError as exc:
                raise exc
            finally:
                item.post(time=item_time, elapsed_time=elapsed_time, pre_out=pre_out)

        return elapsed_time

    def _execute_item(self, item, runner):
        elapsed_time = 0

        terminated = False

        while not terminated and elapsed_time <= (item.duration or constants.MAX_DURATION):
            terminated = self._process_events(item)

            # Render surface updates
            item.render(self.surface)

            elapsed_time += self.clock.get_time()

            # Advance clock
            self.clock.tick(runner.fps)

        return elapsed_time

    def _process_events(self, item):
        is_terminal_event = False

        for event in pygame.event.get():
            # global termination events
            if view.is_terminal_event(event):
                raise InterruptedError('User terminated experiment')

            # item-specific event processing
            if event.type == pygame.KEYDOWN:

                is_terminal_event = item.process_event(event)
                if is_terminal_event:
                    break

        return is_terminal_event


class TrialItem(object):
    def __init__(self, name, renderer, event_processor=sperling.constants.NO_OP, pre=sperling.constants.NO_OP,
                 post=sperling.constants.NO_OP, duration=constants.MAX_DURATION):
        self.name = name
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
            allow_repeats (bool): specifies whether character values can appear more than once

        Returns:
            GridGenerator: a rectangular, 2d-list of characters

        """
        n_rows = random.randint(*range_rows)
        n_columns = random.randint(*range_columns)

        return GridGenerator(n_rows=n_rows, n_columns=n_columns, charset=charset, allow_repeats=allow_repeats)


ResponseEntry = collections.namedtuple('ResponseEntry',
                                       ['response_time', 'actual_response', 'correct_response', 'durations'])


class ResponseProcessor(object):
    def __init__(self, correct, actual, experiment):
        self.correct = correct
        self.actual = actual
        self.experiment = experiment

    def __call__(self, *args, **kwargs):
        entry = ResponseEntry(
            response_time=kwargs['time'],
            actual_response=copy.deepcopy(self.actual),
            correct_response=copy.deepcopy(self.correct),
            durations=self.experiment.durations
        )
        self.experiment.results.append(entry)


def n_correct(result):
    return sum(1 for a, c in zip(itertools.chain.from_iterable(result.actual_response),
                                 itertools.chain.from_iterable(result.correct_response)) if a == c)
