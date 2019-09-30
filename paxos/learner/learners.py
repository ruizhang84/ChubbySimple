import socketserver
import threading
from paxos.sockets import *


class Operation:
    def __init__(self, nums):
        self.receives = {}
        self.log = set()        # log excuted operations
        self.lock = threading.Semaphore()
        self.nums = nums

    def add(self, opt, data):
        self.lock.acquire()
        if opt not in self.log:
            if opt not in self.receives:
                self.receives[opt] = (0, data)
            self.receives[opt] = (self.receives[opt][0]+1, self.receives[opt][1])
        self.lock.release()

    def vote(self):
        majority = None
        self.lock.acquire()
        for opt in self.receives:
            if self.receives[opt][0] > self.nums//2:
                data = self.receives[opt][1]
                majority = (opt, data)
                self.receives.clear()
                self.log.add(opt)
                break
        self.lock.release()
        return majority


class LearnerReceiver(socketserver.ThreadingTCPServer):
    def receiver_start(self, operator, executor):
        self.operator = operator
        self.executor = executor
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        self.server_close()


class LearnerReceiverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            header, data = recv_all(self.request, 4, BUF_SIZE)
            msg_type, timestamp, uid, opt = retrieve_header(header)
            # learned
            if msg_type == LEARN_MSG:
                self.server.operator.add(opt, data)
                majority = self.server.operator.vote()

                if majority is not None:
                    opt, data = majority
                    self.server.executor.execute(opt, data)
                    # print (opt, data)

