import ipc
import random


class SensoryMemory(object):
    def __init__(self, environment, modality):
        self.environment = environment
        self.modality = modality
        self.sensory_scene = {}

    def step(self):
        # Receive sensory stimuli from environment
        self.sensory_scene['pixel_layer'] = self.environment.receive_stimuli(self.modality)

        # Update
        # TODO: Update other layers in the sensory scene

        # Send
        # TODO: Send pixel layer to pre-conscious workspace


class SensoryMotorMemory(object):
    def __init__(self, environment):
        self.environment = environment

    def step(self):
        # TODO: Update with real motor command
        motor_command = random.randint(1, 10)

        # Execute motor command on environment
        self.environment.update(motor_command)



