from multiprocessing import Process, Queue
import random
import os
import time
import collections
from queue import Empty, Full

Message = collections.namedtuple('Message', ['pid', 'time', 'content'])


def current_time_in_millis():
    return int(round(time.time() * 1000))


def display_process_info():
    print('process id: ', os.getpid())
    print('parent process id: ', os.getppid())


def is_stale_msg(msg, threshold_in_millis=20):
    return current_time_in_millis() - msg.time > threshold_in_millis


def recv_msgs(queue, max=5):
    msgs = []
    try:
        for read_count in range(max):
            msg = queue.get(block=False)
            if is_stale_msg(msg):
                print('dropping stale message: {}'.format(msg))
            else:
                msgs.append(msg)
    except Empty as e:
        pass

    return msgs


def send_msgs(queue, msgs):
    try:
        for content in msgs:
            msg = Message(pid=os.getpid(), time=current_time_in_millis(), content=content)
            queue.put(msg, block=False)
    except Full as e:
        print('queue is full')


def start_agent(actions_queue, stimuli_queue):
    print('Starting LIDA agent')
    display_process_info()

    while True:
        msgs = recv_msgs(stimuli_queue)
        if msgs:
            for msg in msgs:
                print('received stimuli: ', msg)

        send_msgs(actions_queue, msgs=[random.randint(1, 10)])
        time.sleep(.01)


def start_env(actions_queue, stimuli_queue):
    print('Starting environment')
    display_process_info()

    while True:
        msgs = recv_msgs(actions_queue)
        if msgs:
            for msg in msgs:
                print('received action: ', msg)

        send_msgs(stimuli_queue, msgs=[random.randint(1, 10) for n in range(1,4)])
        time.sleep(.01)


if __name__ == '__main__':
    actions_queue = Queue(maxsize=5)
    stimuli_queue = Queue(maxsize=5)

    procs = []
    procs.append(Process(target=start_agent, name='lida agent(sperling exp)', args=(actions_queue, stimuli_queue)))
    procs.append(Process(target=start_env, name='env(sperling exp)', args=(actions_queue, stimuli_queue)))

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
