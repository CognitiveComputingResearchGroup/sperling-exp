import pygame
import sperling
import statistics

from sperling.view import find_font

pygame.init()

# flags = pygame.FULLSCREEN
flags = 0
screen = pygame.display.set_mode((1024, 768), flags)
# screen = pygame.display.set_mode((256, 192), flags)

# hide mouse cursor
pygame.mouse.set_visible(False)

# find available system font
font = None
try:
    font = find_font(acceptable_fonts=['consolas', 'ubuntumono'], size=48)
    # font = find_font(acceptable_fonts=['consolas', 'ubuntumono'], size=16)
except EnvironmentError as e:
    print(e)
    exit(1)

experiments = [
    sperling.experiments.Experiment3(screen=screen, font=font, n_trials=50)
]

try:
    session = sperling.Session('S', experiments=experiments)
    session.run()
except InterruptedError as exc:
    print(exc)

# results
for experiment in experiments:
    for result in experiment.results:
        print(result)

# stats
if len(experiments[0].results) > 0:
    avg_correct = statistics.mean([sperling.n_correct(result) for result in experiments[0].results])
    print('Average correct: {:.2f}'.format(avg_correct))
