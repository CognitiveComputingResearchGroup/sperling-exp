import random
import pygame
import collections
import experiments
from experiments.view import CharacterGridWithArrowCues
import copy

# In millis
DEFAULT_DURATIONS = {
    experiments.constants.FIXATION: experiments.constants.UNLIMITED_DURATION,
    experiments.constants.POST_FIXATION_MASK: 500,
    experiments.constants.STIMULUS: 50,
    experiments.constants.RESPONSE: experiments.constants.UNLIMITED_DURATION,
    experiments.constants.FEEDBACK: experiments.constants.UNLIMITED_DURATION
}


class Experiment(object):
    def __init__(self, screen, font, stimulus_spec, duration_overrides):
        """
        :param screen (pygame.Surface):
        :param font (pygame.font.SysFont):
        :param stimulus_spec (GridSpec):
        :param duration_overrides (dict):
        """
        self.screen = screen
        self.font = font
        self.stimulus_spec = stimulus_spec
        self.durations = collections.defaultdict(int)
        self.durations.update(DEFAULT_DURATIONS)
        self.durations.update(duration_overrides)
        self.results = []

    def _setup(self):
        # clear display
        self.screen.fill(experiments.constants.BLACK)

        screen_dims = experiments.datatypes.Dimensions(*self.screen.get_size())

        self._trial_items = collections.OrderedDict()

        # 1 - fixation period on crosshairs (advance on ENTER)
        crosshair_width = 100
        crosshairs = experiments.view.CrossHairs(
            size=crosshair_width,
            color=experiments.constants.WHITE)

        crosshairs.rect.x = (screen_dims.width - crosshair_width) // 2
        crosshairs.rect.y = (screen_dims.height - crosshair_width) // 2

        self._trial_items[experiments.constants.FIXATION] = experiments.TrialItem(
            renderer=experiments.view.SpriteRenderer(self.screen, crosshairs),
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[experiments.constants.FIXATION])

        # 2 - pre-stimulus mask
        self._trial_items[experiments.constants.POST_FIXATION_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(self.screen, color=experiments.constants.BLACK),
            duration=self.durations[experiments.constants.POST_FIXATION_MASK])

        # 3 - grid stimulus
        self.stimulus_grid = self.stimulus_spec.create_grid()

        char_grid = experiments.view.CharacterGrid(grid=self.stimulus_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2

        self._trial_items[experiments.constants.STIMULUS] = experiments.TrialItem(
            renderer=experiments.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y)),
            duration=self.durations[experiments.constants.STIMULUS])

        # 4 = response grid (advance on ENTER)
        self.response_grid = [['?'] * len(self.stimulus_grid[0]) for row in range(len(self.stimulus_grid))]

        char_grid = experiments.view.CharacterGrid(grid=self.response_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2 + 200

        response_renderer = experiments.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y))
        response_event_processor = experiments.view.GridEventHandler(
            grid=char_grid, view=response_renderer, terminal_event=pygame.K_RETURN)
        response_post_processor = experiments.ResponseStatsProcessor(self.stimulus_grid, self.response_grid,
                                                                     self.results)

        self._trial_items[experiments.constants.RESPONSE] = experiments.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor, post=response_post_processor,
            duration=self.durations[experiments.constants.RESPONSE])

        # 5 = feedback grid (advance on ENTER)
        feedback_renderer = experiments.view.FeedbackGridRenderer(
            surface=self.screen, grid=char_grid, correct_response=self.stimulus_grid,
            actual_response=self.response_grid)

        self._trial_items[experiments.constants.FEEDBACK] = experiments.TrialItem(
            renderer=feedback_renderer,
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[experiments.constants.FEEDBACK])

    def run(self, fps=20):
        self._setup()

        runner = experiments.SerialTrialRunner(
            trial=self._trial_items.values(),
            clock=pygame.time.Clock(),
            surface=self.screen,
            fps=fps)

        return runner.run()
