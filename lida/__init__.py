import multiprocessing
import pygame

import ipc
import time
import random

import sperling
import lida.modules


class Agent(object):
    def __init__(self):
        self.sensory_mem = None
        self.pam = None
        self.pwrkspace = None
        self.gw = None
        self.proc_mem = None
        self.action_sel = None
        self.smm = None
        self.spatial_mem = None
        self.tem = None
        self.declare_mem = None

    def sense(self, environment):
        msgs = environment.receive_stimuli('visual')
        if msgs:
            for msg in msgs:
                print('received stimuli: ', msg)

    def act(self, environment):
        motor_command = random.randint(1, 100)
        environment.update(motor_command)


class Environment(object):
    def __init__(self):
        self._visual_sensory_queue = ipc.get_msg_queue()
        self._action_queue = ipc.get_msg_queue()

    def update(self, actions):
        ipc.send_msgs(self._action_queue, actions)

    def receive_stimuli(self, modality):
        return ipc.recv_msgs(self._visual_sensory_queue)

    def step(self):
        pass


def launch_agent(agent, environment):
    print('Starting LIDA agent')
    ipc.display_process_info()

    while True:
        agent.receive_stimuli(environment)
        agent.act(environment)
        time.sleep(.01)


def launch_experiment(environment):
    print('Starting experiment')
    ipc.display_process_info()

    pygame.init()

    flags = 0
    screen = pygame.display.set_mode((256, 192), flags)

    # hide mouse cursor
    pygame.mouse.set_visible(False)

    # find available system font
    font = None
    try:
        font = sperling.view.find_font(acceptable_fonts=['consolas', 'ubuntumono'], size=16)
    except EnvironmentError as e:
        print(e)
        exit(1)

    experiments = [
        sperling.experiments.Experiment1(screen=screen, font=font, n_trials=50)
    ]

    try:
        session = sperling.Session('agent', experiments=experiments)
        session.run()
    except InterruptedError as exc:
        print(exc)


def run(agent, environment):
    try:
        procs = []
        procs.append(multiprocessing.Process(target=launch_experiment, name='env', args=(environment)))
        procs.append(multiprocessing.Process(target=launch_agent, name='agent', args=(agent, environment)))

        for proc in procs:
            proc.start()

        for proc in procs:
            proc.join()

    except Exception as e:
        print(e)
        exit(1)
