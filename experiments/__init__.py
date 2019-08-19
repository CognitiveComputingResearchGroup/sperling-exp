import collections
import random

import pygame

import experiments.constants
import experiments.datatypes
import experiments.functions
import experiments.view

MAX_DURATION = 60000


class SerialTrialRunner(object):
    def __init__(self, trial, clock, surface, fps):
        self.trial = trial
        self.clock = clock
        self.surface = surface
        self.fps = fps

    def run(self):
        total_elapsed_time = 0
        for item in self.trial:
            total_elapsed_time += self.execute_item(item, self)

        return total_elapsed_time

    @classmethod
    def execute_item(cls, item, runner):
        elapsed_time = 0

        terminal_event = False
        while not terminal_event and elapsed_time <= (item.duration or MAX_DURATION):

            # Pre-render processing
            item.pre()

            # Process Events
            for event in pygame.event.get():

                # Global termination events
                if view.is_terminal_event(event):
                    raise InterruptedError('User terminated experiment')

                # Item specific event processing
                terminal_event = item.process_event(event)

            # Render surface updates
            item.render(runner.surface)
            pygame.display.flip()

            elapsed_time += runner.clock.get_time()

            # Pre-render processing
            item.post()

            # Advance clock
            runner.clock.tick(runner.fps)

        return elapsed_time


class TrialItem(object):
    def __init__(self, renderer, event_processor=experiments.functions.no_op, pre=experiments.functions.no_op,
                 post=experiments.functions.no_op, duration=0):
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


CHARSET_ALPHANUM = 'alphanum'
CHARSET_ALPHA = 'alpha'
CHARSET_CONSONANTS = 'consonants'

charsets_dict = {
    CHARSET_CONSONANTS: constants.CONSONANTS,
    CHARSET_ALPHA: constants.ALPHA,
    CHARSET_ALPHANUM: constants.ALPHANUM}


class GridSpec:
    def __init__(self, n_rows, n_columns, charset_id):
        self.n_rows = n_rows
        self.n_columns = n_columns

        if self.n_rows <= 0:
            raise ValueError('Invalid Number of CharacterGrid Rows: Must be > 0.')

        if self.n_columns <= 0:
            raise ValueError('Invalid Number of CharacterGrid Columns: Must be > 0.')

        try:
            self.charset = charsets_dict[charset_id]
        except KeyError:
            raise ValueError(
                'Invalid CharacterGrid Character Set: Must be one of {}'.format(','.join(
                    sorted(charsets_dict.keys()))))

    def create_grid(self):
        chars = random.sample(self.charset, k=self.n_rows * self.n_columns)
        return [chars[i * self.n_columns:(i + 1) * self.n_columns] for i in range(self.n_rows)]
