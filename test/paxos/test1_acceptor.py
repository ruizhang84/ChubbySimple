from paxos.acceptor.acceptors import *
import multiprocessing


def process_work(losthost, port):
    a = AcceptorReceiver((losthost, port), AcceptorReceiverHandler)
    a.receiver_start()


for i in range(3):
    args = ("localhost", 1024 + i)
    process = multiprocessing.Process(target=process_work, args=args)
    process.start()

# python -m test.paxos.test1

