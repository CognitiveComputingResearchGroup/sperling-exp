import collections
import os
import time
import multiprocessing
from queue import Empty, Full

Message = collections.namedtuple('Message', ['pid', 'time', 'content'])


def get_msg_queue():
    return multiprocessing.Queue(maxsize=5)

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
        while len(msgs) < max:
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
