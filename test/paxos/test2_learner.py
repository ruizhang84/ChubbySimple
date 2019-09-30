from paxos.learner.runners import *
import multiprocessing


def process_work(uid, localhost, nserver, output):
    a = Learner(uid, localhost, nserver, output)
    a.start()


for i in range(3):
    args = (str(i), ("localhost", 1024+i),3, "test_output")
    process = multiprocessing.Process(target=process_work, args=args)
    process.start()


