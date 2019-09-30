import threading
from paxos.sockets import *


class Store:
    def __init__(self):
        self.info = []
        self.lock = threading.Semaphore()

    def clear(self):
        self.lock.acquire()
        self.info.clear()
        self.lock.release()

    def add(self, header, data):
        """
        atomic add header and data info
        """
        self.lock.acquire()
        self.info.append((header, data))
        self.lock.release()


class ProposerSender:
    def __init__(self, server_addr_lst, store):
        self.server_addr_lst = server_addr_lst
        self.storage = store
        self.targets = []
        self.lock = threading.Semaphore()
        self.init_connect()

    def init_connect(self):
        for host, port in self.server_addr_lst:
            args = (host, port)
            process = threading.Thread(target=self.open_connect, args=args)
            process.start()
            process.join()

    def open_connect(self, host, port):
        target = Socket()
        target.handler.connect((host, port))
        self.lock.acquire()
        self.targets.append(target)
        self.lock.release()

    def close(self):
        for target in self.targets:
            self.close_connect(target)

    def close_connect(self, target):
        try:
            target.handler.close()
        except:
            print ("connection is already closed!")

    def update_server(self, server_addr_lst):
        self.server_addr_lst = server_addr_lst

    def broadcast(self, header, data):
        for target in self.targets:
            args = (target, header, data)
            process = threading.Thread(target=self.send, args=args)
            process.start()

    def send(self, target, header, data):
        send_all(target.handler, header, data)
        # receive incoming
        header, data = recv_all(target.handler, 4, BUF_SIZE)
        self.storage.add(header, data)




