import experiments
import pygame
import sys
import time

pygame.init()

size = 800, 600

BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

screen = pygame.display.set_mode(size)


def fill_black():
    screen.fill(BLACK)
    pygame.display.flip()


def fill_red():
    screen.fill(RED)
    pygame.display.flip()


def fill_blue():
    screen.fill(BLUE)
    pygame.display.flip()


def wait_two():
    time.sleep(2)


trial = experiments.SerialTrial(
    [
        experiments.TrialItem(render=fill_black, post=wait_two),
        experiments.TrialItem(render=fill_red, post=wait_two),
        experiments.TrialItem(render=fill_blue, post=wait_two),
    ]
)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    trial.run()
# Save results
