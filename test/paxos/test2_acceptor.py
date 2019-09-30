from paxos.acceptor.senders import *
import multiprocessing      # since call is blocking, multi-thread is impossible.


def process_work(server_lst, header, data):
    a = AcceptorSender(server_lst)
    a.broadcast(header, data)


server_list = [("localhost", 1024), ("localhost", 1025), ("localhost", 1026)]
headers = [LEARN_MSG, '0', '0', 'write']
data = ""
for i in range(3):
    if i < 2:
        data = "123456"
        headers = [LEARN_MSG, '0', '0', 'write-1']
    else:
        data = "123"
        headers = [LEARN_MSG, '0', '1', 'write-2']
    args = (server_list, headers, data)
    process = multiprocessing.Process(target=process_work, args=args)
    process.start()

