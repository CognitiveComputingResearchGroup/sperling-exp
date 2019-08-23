import random
import pygame
import collections
import experiments
from experiments.view import CharacterGridWithArrowCues

FIXATION = 'FIXATION'
POST_FIXATION_MASK = 'POST_FIXATION_MASK'
STIMULUS = 'STIMULUS'
POST_STIMULUS_MASK = 'POST_STIMULUS_MASK'
CUE = 'CUE'
POST_CUE_MASK = 'POST_CUE_MASK'
RESPONSE = 'RESPONSE'
FEEDBACK = 'FEEDBACK'

# In millis
DEFAULT_DURATIONS = {
    FIXATION: experiments.constants.UNLIMITED_DURATION,
    POST_FIXATION_MASK: 500,
    STIMULUS: 50,
    POST_STIMULUS_MASK: 1,
    CUE: 500,
    POST_CUE_MASK: 1,
    RESPONSE: experiments.constants.UNLIMITED_DURATION,
    FEEDBACK: experiments.constants.UNLIMITED_DURATION
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

        self._trial_items[FIXATION] = experiments.TrialItem(
            renderer=experiments.view.SpriteRenderer(self.screen, crosshairs),
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[FIXATION])

        # 2 - pre-stimulus mask
        self._trial_items[POST_FIXATION_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(self.screen, color=experiments.constants.BLACK),
            duration=self.durations[POST_FIXATION_MASK])

        # 3 - grid stimulus
        self.stimulus_grid = self.stimulus_spec.create_grid()

        char_grid = experiments.view.CharacterGrid(grid=self.stimulus_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2

        self._trial_items[STIMULUS] = experiments.TrialItem(
            renderer=experiments.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y)),
            duration=self.durations[STIMULUS])

        # 4 = post-stimulus mask
        self._trial_items[POST_STIMULUS_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(self.screen, color=experiments.constants.BLACK),
            duration=self.durations[POST_STIMULUS_MASK])

        # 5 - cue
        self.cue_index = random.randint(0, len(self.stimulus_grid) - 1)

        arrow_grid = CharacterGridWithArrowCues(char_grid, cue_row=self.cue_index)

        x = (screen_dims.width - arrow_grid.image.get_width()) // 2
        y = (screen_dims.height - arrow_grid.image.get_height()) // 2

        cue_renderer = experiments.view.GridRenderer(surface=self.screen, grid=arrow_grid, pos=(x, y))

        self._trial_items[CUE] = experiments.TrialItem(
            renderer=cue_renderer,
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[CUE])

        # 6 = response grid (advance on ENTER)
        self.response_grid = [['?'] * len(self.stimulus_grid[0])]

        char_grid = experiments.view.CharacterGrid(grid=self.response_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2 + 200

        response_renderer = experiments.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y))
        response_event_processor = experiments.view.GridEventHandler(
            grid=char_grid, view=response_renderer, terminal_event=pygame.K_RETURN)

        self._trial_items[RESPONSE] = experiments.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor, duration=self.durations[RESPONSE])

        # 7 = feedback grid (advance on ENTER)
        correct_response = [self.stimulus_grid[self.cue_index]]

        feedback_renderer = experiments.view.FeedbackGridRenderer(
            surface=self.screen, grid=char_grid, correct_response=correct_response, actual_response=self.response_grid)

        self._trial_items[FEEDBACK] = experiments.TrialItem(
            renderer=feedback_renderer,
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[FEEDBACK])

    def run(self, fps=20):
        self._setup()

        runner = experiments.SerialTrialRunner(
            trial=self._trial_items.values(),
            clock=pygame.time.Clock(),
            surface=self.screen,
            fps=fps)

        return runner.run()
