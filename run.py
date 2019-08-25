import pygame
import sperling
import statistics

pygame.init()

flags = pygame.FULLSCREEN
# flags = 0
screen = pygame.display.set_mode((1024, 768), flags=flags)
font = pygame.font.SysFont("consolas", size=32)

# hide mouse cursor
pygame.mouse.set_visible(False)

N_SESSIONS = 10
N_TRIALS_PER_SESSION = 50

try:
    for session in range(N_SESSIONS):
        experiment = sperling.experiments.Experiment3(
            screen=screen,
            font=font,
            duration_overrides={})

        for trial in range(N_TRIALS_PER_SESSION):
            total_elapsed_time = experiment.run()
            print(experiment.results[-1])

            # Stats
            avg_correct = statistics.mean([sperling.n_correct(result) for result in experiment.results])
            print('Average correct: {:.2f}'.format(avg_correct))

except InterruptedError as exc:
    print(exc)
