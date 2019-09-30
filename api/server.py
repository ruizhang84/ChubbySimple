from paxos.acceptor.runners import *
from paxos.learner.runners import *
from api.receiver import *
import multiprocessing      # since call is blocking, multi-thread is impossible.
import random

def proposer_work(uid, server_lst, host):
    a = Receiver(uid, server_lst, host)
    a.start()


def acceptor_work(server_lst, host):
    b = Acceptor(server_lst, host)
    b.start()


def learner_work(uid, server_lst, nserver):
    c = Learner(uid, server_lst, nserver)
    c.start()


class ChubbyServer:
    def __init__(self, uid, proposer_addr_lst, acceptor_addr_lst, learner_addr_lst):
        self.uid = uid
        self.proposer_addr_lst = proposer_addr_lst
        self.acceptor_addr_lst = acceptor_addr_lst
        self.learner_addr_lst = learner_addr_lst

    def learner_start(self):
        args = (self.uid, self.learner_addr_lst[int(self.uid)], len(self.learner_addr_lst))
        process = multiprocessing.Process(target=learner_work, args=args)
        process.start()
        return process

    def acceptor_start(self):
        args = (self.learner_addr_lst, self.acceptor_addr_lst[int(self.uid)])
        process = multiprocessing.Process(target=acceptor_work, args=args)
        process.start()
        return process

    def proposer_start(self):
        args = (self.uid, self.acceptor_addr_lst, self.proposer_addr_lst[int(self.uid)])
        process = multiprocessing.Process(target=proposer_work, args=args)
        process.start()
        return process


class Server:
    def __init__(self, server_ips, port=1024, waiting=5):
        """
        set up servers
        :param server_ips: the ip address for available chubby server
        :param port:    the default starting port number
        :param waiting: the waiting time for server to go online
        """
        self.server_ips = server_ips
        self.port = port
        self.tiemout = waiting
        self.proposer_addr_lst = []
        self.acceptor_addr_lst = []
        self.learner_addr_lst = []
        self.servers = []
        self.proposer_queue = []
        self.acceptor_queue = []
        self.learner_queue = []
        for i in range(len(server_ips)):
            host = server_ips[i]
            self.proposer_addr_lst.append((host, port))
            port += 1
        for i in range(len(server_ips)):
            host = server_ips[i]
            self.acceptor_addr_lst.append((host, port))
            port += 1
        for i in range(len(server_ips)):
            host = server_ips[i]
            self.learner_addr_lst.append((host, port))
            port += 1

    def start(self):
        for i in range(len(self.server_ips)):
            uid = str(i)
            server = ChubbyServer(uid, self.proposer_addr_lst, self.acceptor_addr_lst, self.learner_addr_lst)
            self.servers.append(server)

        for server in self.servers:
            process = server.learner_start()
            self.learner_queue.append(process)

        time.sleep(self.tiemout) # wait for starting

        for server in self.servers:
            process = server.acceptor_start()
            self.acceptor_queue.append(process)

        time.sleep(self.tiemout) # wait for starting

        for server in self.servers:
            process = server.proposer_start()
            self.proposer_queue.append(process)

        print("Server is up and run!")

    def random_kill(self):
        select = random.randint(0, len(self.server_ips)-1)
        process = self.proposer_queue.pop(select)
        process.terminate()
        process = self.acceptor_queue.pop(select)
        process.terminate()
        process = self.learner_queue.pop(select)
        process.terminate()


