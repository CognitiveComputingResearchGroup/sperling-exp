from multiprocessing import Process, Queue
import random
import time

import ipc


def start_agent(actions_queue, stimuli_queue):
    print('Starting LIDA agent')
    ipc.display_process_info()

    while True:
        msgs = ipc.recv_msgs(stimuli_queue)
        if msgs:
            for msg in msgs:
                print('received stimuli: ', msg)

        ipc.send_msgs(actions_queue, msgs=[random.randint(1, 10)])
        time.sleep(.01)


def start_env(actions_queue, stimuli_queue):
    print('Starting environment')
    ipc.display_process_info()

    while True:
        msgs = ipc.recv_msgs(actions_queue)
        if msgs:
            for msg in msgs:
                print('received action: ', msg)

        ipc.send_msgs(stimuli_queue, msgs=[random.randint(1, 10) for n in range(1, 4)])
        time.sleep(.01)


if __name__ == '__main__':
    actions_queue = ipc.get_msg_queue()
    stimuli_queue = ipc.get_msg_queue()

    procs = []
    procs.append(Process(target=start_agent, name='agent', args=(actions_queue, stimuli_queue)))
    procs.append(Process(target=start_env, name='env', args=(actions_queue, stimuli_queue)))

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
