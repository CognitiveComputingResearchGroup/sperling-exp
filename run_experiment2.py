import pygame
import sperling
import statistics

pygame.init()

flags = pygame.FULLSCREEN
screen = pygame.display.set_mode((1024, 768), flags=flags)
font = pygame.font.SysFont("consolas", size=48)

# hide mouse cursor
pygame.mouse.set_visible(False)

experiments = [
    sperling.experiments.Experiment2(screen=screen, font=font, n_trials=50)
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
avg_correct = statistics.mean([sperling.n_correct(result) for result in experiments[0].results])
print('Average correct: {:.2f}'.format(avg_correct))
