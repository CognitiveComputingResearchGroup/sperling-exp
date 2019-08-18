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

# In millis
DEFAULT_DURATIONS = {
    FIXATION: experiments.constants.UNLIMITED_DURATION,
    POST_FIXATION_MASK: 5000,
    STIMULUS: 100,
    POST_STIMULUS_MASK: 100,
    CUE: 500,
    POST_CUE_MASK: 0,
    RESPONSE: experiments.constants.UNLIMITED_DURATION,
}


class Experiment(object):
    def __init__(self, screen, font, stimulus_spec, duration_overrides):
        """
        :param screen (pygame.Surface):
        :param font (pygame.font.SysFont):
        :param stimulus_spec (GridSpec):
        :param duration_overrides (dict):
        """
        self.durations = collections.defaultdict(int)
        self.durations.update(DEFAULT_DURATIONS)
        self.durations.update(duration_overrides)

        screen_dims = experiments.datatypes.Dimensions(*screen.get_size())

        self._trial_items = collections.OrderedDict()

        # 1 - fixation period on crosshairs (advance on ENTER)
        crosshairs = experiments.view.CrossHairs(
            pos=(screen_dims.width // 2, screen_dims.height // 2),
            width=100,
            color=experiments.constants.WHITE)

        self._trial_items[FIXATION] = experiments.TrialItem(
            renderer=experiments.view.SpriteRenderer(screen, crosshairs),
            event_processor=experiments.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[FIXATION])

        # 2 - pre-stimulus mask
        self._trial_items[POST_FIXATION_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(screen, color=experiments.constants.BLACK),
            duration=self.durations[POST_FIXATION_MASK])

        # 3 - grid stimulus
        stimulus_grid = stimulus_spec.create_grid()
        self._trial_items[STIMULUS] = experiments.TrialItem(
            renderer=experiments.view.GridRenderer(screen, grid=stimulus_grid, font=font,
                                                   padding=experiments.datatypes.Dimensions(50, 50)),
            duration=self.durations[STIMULUS])

        # 4 = post-stimulus mask
        self._trial_items[POST_STIMULUS_MASK] = experiments.TrialItem(
            renderer=experiments.view.MaskRenderer(screen, color=experiments.constants.BLACK),
            duration=self.durations[POST_STIMULUS_MASK])

        # 5 - cue
        # TODO:

        # 6 = response grid (advance on ENTER)
        response_grid = [['?'] * len(stimulus_grid[0]), ]
        response_renderer = experiments.view.GridRenderer(
            screen=screen, grid=response_grid, font=font, padding=experiments.datatypes.Dimensions(50, 50))
        response_event_processor = experiments.view.GridEventHandler(
            grid=response_grid, view=response_renderer, terminal_event=pygame.K_RETURN)

        self._trial_items[RESPONSE] = experiments.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor, duration=self.durations[RESPONSE])

        self._runner = experiments.SerialTrialRunner(
            trial=self._trial_items.values(),
            clock=pygame.time.Clock(),
            surface=screen,
            fps=20)

    def run(self):
        return self._runner.run()
