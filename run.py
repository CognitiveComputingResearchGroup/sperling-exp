import pygame
import experiments

from experiments.experiment1 import Experiment

pygame.init()

screen = pygame.display.set_mode((1024, 768))
font = pygame.font.SysFont("courier", size=72)

experiment = Experiment(
    screen=screen,
    font=font,
    stimulus_spec=experiments.GridSpec(n_rows=3, n_columns=4, charset_id=experiments.CHARSET_CONSONANTS),
    duration_overrides={})

try:
    total_elapsed_time = experiment.run()
except Exception as exc:
    print(exc)

# TODO: Stats
