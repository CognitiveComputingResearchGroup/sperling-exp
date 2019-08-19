import random
import pygame
import collections
import experiments

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
    POST_FIXATION_MASK: 5000,
    STIMULUS: 500,
    POST_STIMULUS_MASK: 100,
    CUE: 500,
    POST_CUE_MASK: 0,
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
        screen_dims = experiments.datatypes.Dimensions(*self.screen.get_size())

        self._trial_items = collections.OrderedDict()

        # 1 - fixation period on crosshairs (advance on ENTER)
        crosshairs = experiments.view.CrossHairs(
            screen=self.screen,
            pos=(screen_dims.width // 2, screen_dims.height // 2),
            width=100,
            color=experiments.constants.WHITE)

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
        self._trial_items[STIMULUS] = experiments.TrialItem(
            renderer=experiments.view.GridRenderer(self.screen, grid=self.stimulus_grid, font=self.font,
                                                   padding=experiments.datatypes.Dimensions(50, 50)),
            duration=self.durations[STIMULUS])

        # 4 = post-stimulus mask
        self._trial_items[POST_STIMULUS_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(self.screen, color=experiments.constants.BLACK),
            duration=self.durations[POST_STIMULUS_MASK])

        # 5 - cue
        self.cue_index = random.randint(0, len(self.stimulus_grid) - 1)

        # TODO:

        # 6 = response grid (advance on ENTER)
        self.response_grid = [['?'] * len(self.stimulus_grid[0]), ]
        response_renderer = experiments.view.GridRenderer(
            screen=self.screen, grid=self.response_grid, font=self.font,
            padding=experiments.datatypes.Dimensions(50, 50))
        response_event_processor = experiments.view.GridEventHandler(
            grid=self.response_grid, view=response_renderer, terminal_event=pygame.K_RETURN)

        self._trial_items[RESPONSE] = experiments.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor, duration=self.durations[RESPONSE])

        # 7 = feedback grid (advance on ENTER)
        print('cue: ', self.cue_index)

        feedback_renderer = experiments.view.FeedbackGridRenderer(
            screen=self.screen, correct_response=[self.stimulus_grid[self.cue_index]],
            actual_response=self.response_grid,
            font=self.font, padding=experiments.datatypes.Dimensions(50, 50))

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
            fps=20)

        return runner.run()
