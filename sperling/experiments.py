import sperling
import pygame
import random
import collections


class Experiment(object):
    def __init__(self, screen, font, duration_overrides):
        self.screen = screen
        self.font = font
        self.durations = collections.defaultdict(int)
        self.durations.update(sperling.constants.DEFAULT_DURATIONS)
        self.durations.update(duration_overrides)

        self.trial_items = collections.OrderedDict()
        self.results = []

        # vertical pixel shift (below center) for response grid
        self.response_grid_vertical_offset = 200

    def reset(self):
        self.results = self.results.clear()

    def _pre_run(self):
        pass

    def _post_run(self):
        pass

    def generate_grid(self):
        pass

    def run(self, fps=20):
        self._pre_run()

        runner = sperling.SerialTrialRunner(
            trial=self.trial_items.values(),
            clock=pygame.time.Clock(),
            surface=self.screen,
            fps=fps)

        trial_elapsed_time = runner.run()

        self._post_run()

        return trial_elapsed_time


class Experiment1(Experiment):
    def __init__(self, screen, font, duration_overrides):
        super().__init__(screen, font, duration_overrides)

        self._grid_specs = [
            # single row with 3-7 consonants
            *[sperling.GridSpec(n_rows=1, n_columns=n_cols, charset=sperling.constants.CONSONANTS, allow_repeats=True)
              for n_cols in range(3, 7 + 1)],

            # 3/3
            sperling.GridSpec(n_rows=2, n_columns=3, charset=sperling.constants.CONSONANTS, allow_repeats=True),

            # 4/4
            sperling.GridSpec(n_rows=2, n_columns=4, charset=sperling.constants.CONSONANTS, allow_repeats=True),

            # 3/3/3
            sperling.GridSpec(n_rows=3, n_columns=3, charset=sperling.constants.CONSONANTS, allow_repeats=True),
        ]

        self._grid_spec = random.choice(self._grid_specs)
        self._grid_generator = sperling.GridGenerator(n_rows=self._grid_spec.n_rows,
                                                      n_columns=self._grid_spec.n_columns,
                                                      charset=self._grid_spec.charset,
                                                      allow_repeats=self._grid_spec.allow_repeats)

    def generate_grid(self):
        return self._grid_generator()

    def _pre_run(self):
        screen_dims = sperling.view.Dimensions(*self.screen.get_size())

        # clear display
        self.screen.fill(sperling.constants.BLACK)

        # 1 - fixation period on crosshairs (advance on ENTER)
        crosshairs_width = 100
        crosshairs = sperling.view.CrossHairs(
            size=crosshairs_width,
            color=sperling.constants.WHITE)

        crosshairs.rect.x = (screen_dims.width - crosshairs_width) // 2
        crosshairs.rect.y = (screen_dims.height - crosshairs_width) // 2

        self.trial_items[sperling.constants.FIXATION] = sperling.TrialItem(
            renderer=sperling.view.SpriteRenderer(self.screen, crosshairs),
            event_processor=sperling.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[sperling.constants.FIXATION])

        # 2 - pre-stimulus mask
        self.trial_items[sperling.constants.POST_FIXATION_MASK] = sperling.TrialItem(
            renderer=sperling.view.MaskRenderer(self.screen, color=sperling.constants.BLACK),
            duration=self.durations[sperling.constants.POST_FIXATION_MASK])

        # 3 - grid stimulus
        stimulus_grid = self.generate_grid()

        char_grid = sperling.view.CharacterGrid(grid=stimulus_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2

        self.trial_items[sperling.constants.STIMULUS] = sperling.TrialItem(
            renderer=sperling.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y)),
            duration=self.durations[sperling.constants.STIMULUS])

        # 4 = response grid (advance on ENTER)
        self.response_grid = [['?'] * len(stimulus_grid[0]) for _ in range(len(stimulus_grid))]

        char_grid = sperling.view.CharacterGrid(grid=self.response_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2 + self.response_grid_vertical_offset

        response_renderer = sperling.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y))
        response_event_processor = sperling.view.GridEventHandler(
            grid=char_grid, view=response_renderer, terminal_event=pygame.K_RETURN)
        response_post_processor = sperling.ResponseProcessor(stimulus_grid, self.response_grid,
                                                             self.results)

        self.trial_items[sperling.constants.RESPONSE] = sperling.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor, post=response_post_processor,
            duration=self.durations[sperling.constants.RESPONSE])

        # 5 = feedback grid (advance on ENTER)
        feedback_renderer = sperling.view.FeedbackGridRenderer(
            surface=self.screen, grid=char_grid, correct=stimulus_grid,
            actual=self.response_grid)

        self.trial_items[sperling.constants.FEEDBACK] = sperling.TrialItem(
            renderer=feedback_renderer,
            event_processor=sperling.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[sperling.constants.FEEDBACK])

        return {'grid generator': self._grid_spec, 'grid': stimulus_grid}


class Experiment3(Experiment):
    def __init__(self, screen, font, duration_overrides):
        super().__init__(screen, font, duration_overrides)

        self._grid_specs = [

            # 3/3
            sperling.GridSpec(n_rows=2, n_columns=3, charset=sperling.constants.CONSONANTS, allow_repeats=True),

            # 4/4
            sperling.GridSpec(n_rows=2, n_columns=4, charset=sperling.constants.CONSONANTS, allow_repeats=True),

            # 3/3/3
            sperling.GridSpec(n_rows=3, n_columns=3, charset=sperling.constants.CONSONANTS, allow_repeats=True),

            # 4/4/4
            sperling.GridSpec(n_rows=3, n_columns=4, charset=sperling.constants.CONSONANTS, allow_repeats=True),
        ]

        self._grid_spec = random.choice(self._grid_specs)
        self._grid_generator = sperling.GridGenerator(n_rows=self._grid_spec.n_rows,
                                                      n_columns=self._grid_spec.n_columns,
                                                      charset=self._grid_spec.charset,
                                                      allow_repeats=self._grid_spec.allow_repeats)

    def generate_grid(self):
        return self._grid_generator()

    def _pre_run(self):
        # clear display
        self.screen.fill(sperling.constants.BLACK)

        screen_dims = sperling.view.Dimensions(*self.screen.get_size())

        # 1 - fixation period on crosshairs (advance on ENTER)
        crosshairs_width = 100
        crosshairs = sperling.view.CrossHairs(
            size=crosshairs_width,
            color=sperling.constants.WHITE)

        crosshairs.rect.x = (screen_dims.width - crosshairs_width) // 2
        crosshairs.rect.y = (screen_dims.height - crosshairs_width) // 2

        self.trial_items[sperling.constants.FIXATION] = sperling.TrialItem(
            renderer=sperling.view.SpriteRenderer(self.screen, crosshairs),
            event_processor=sperling.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[sperling.constants.FIXATION])

        # 2 - pre-stimulus mask
        self.trial_items[sperling.constants.POST_FIXATION_MASK] = sperling.TrialItem(
            renderer=sperling.view.MaskRenderer(self.screen, color=sperling.constants.BLACK),
            duration=self.durations[sperling.constants.POST_FIXATION_MASK])

        # 3 - grid stimulus
        stimulus_grid = self.generate_grid()

        char_grid = sperling.view.CharacterGrid(grid=stimulus_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2

        self.trial_items[sperling.constants.STIMULUS] = sperling.TrialItem(
            renderer=sperling.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y)),
            duration=self.durations[sperling.constants.STIMULUS])

        # 4 = post-stimulus mask
        self.trial_items[sperling.constants.POST_STIMULUS_MASK] = sperling.TrialItem(
            renderer=sperling.view.MaskRenderer(self.screen, color=sperling.constants.BLACK),
            duration=self.durations[sperling.constants.POST_STIMULUS_MASK])

        # 5 - cue
        cue_index = random.randint(0, len(stimulus_grid) - 1)

        arrow_grid = sperling.view.CharacterGridWithArrowCues(char_grid, cue_row=cue_index)

        x = (screen_dims.width - arrow_grid.image.get_width()) // 2
        y = (screen_dims.height - arrow_grid.image.get_height()) // 2

        cue_renderer = sperling.view.GridRenderer(surface=self.screen, grid=arrow_grid, pos=(x, y))

        self.trial_items[sperling.constants.CUE] = sperling.TrialItem(
            renderer=cue_renderer,
            event_processor=sperling.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[sperling.constants.CUE])

        # 6 = response grid (advance on ENTER)
        response_grid = [['?'] * len(stimulus_grid[0])]

        char_grid = sperling.view.CharacterGrid(grid=response_grid, font=self.font)

        x = (screen_dims.width - char_grid.image.get_width()) // 2
        y = (screen_dims.height - char_grid.image.get_height()) // 2 + self.response_grid_vertical_offset

        response_renderer = sperling.view.GridRenderer(surface=self.screen, grid=char_grid, pos=(x, y))
        response_event_processor = sperling.view.GridEventHandler(
            grid=char_grid, view=response_renderer, terminal_event=pygame.K_RETURN)

        response_post_processor = sperling.ResponseProcessor(
            correct=[stimulus_grid[cue_index]],
            actual=response_grid,
            results=self.results)

        self.trial_items[sperling.constants.RESPONSE] = sperling.TrialItem(
            renderer=response_renderer, event_processor=response_event_processor,
            post=response_post_processor, duration=self.durations[sperling.constants.RESPONSE])

        # 7 = feedback grid (advance on ENTER)
        feedback_renderer = sperling.view.FeedbackGridRenderer(
            surface=self.screen, grid=char_grid,
            correct=[stimulus_grid[cue_index]],
            actual=response_grid)

        self.trial_items[sperling.constants.FEEDBACK] = sperling.TrialItem(
            renderer=feedback_renderer,
            event_processor=sperling.view.WaitUntilKeyHandler(pygame.K_RETURN),
            duration=self.durations[sperling.constants.FEEDBACK])

        return {'_grid_generator': self._grid_spec, 'grid': stimulus_grid, 'cue_index': cue_index}
