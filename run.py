import pygame
import experiments

from experiments.experiment1 import Experiment

pygame.init()

flags = pygame.FULLSCREEN
# flags = 0
screen = pygame.display.set_mode((1024, 768), flags=flags)
font = pygame.font.SysFont("consolas", size=32)

# hide mouse cursor
pygame.mouse.set_visible(False)

experiment = Experiment(
    screen=screen,
    font=font,
    stimulus_spec=experiments.GridSpec(n_rows=2, n_columns=5, charset_id=experiments.CHARSET_CONSONANTS),
    duration_overrides={experiments.constants.STIMULUS: 50})

try:
    while True:
        total_elapsed_time = experiment.run()
        print(experiment.results[-1])

except InterruptedError as exc:
    print(exc)

# TODO: Stats
