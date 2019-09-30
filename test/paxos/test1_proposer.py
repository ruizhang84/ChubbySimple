from paxos.proposer.runners import *
import multiprocessing      # since call is blocking, multi-thread is impossible.


def process_work(uid, server_lst, dataset):
    a = Proposer(uid, server_lst)
    # a.write(dataset)
    while True:
        if a.write(dataset):
            print ("TRUE")
            print ()
            print ()
            break


# python -m test.paxos.test1
server_list = [("localhost", 1024), ("localhost", 1025),  ("localhost", 1026)]
data = ""
for i in range(2):
    data += str(i)
    args = (i, server_list, data)
    process = multiprocessing.Process(target=process_work, args=args)
    process.start()

