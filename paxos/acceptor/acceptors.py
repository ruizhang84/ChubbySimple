import socketserver
import threading
from paxos.sockets import *


class AcceptorReceiver(socketserver.ThreadingTCPServer):
    def receiver_start(self, senders=None):
        self.timestamp = 0
        self.uid = 0
        self.opt = ""
        self.data = ""
        self.promised = False
        self.senders = senders
        self.lock = threading.Semaphore()
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        self.server_close()
        self.senders.close()

    def accept(self, timestamp, uid, opt, data):
        self.lock.acquire()
        if self.promised:
            accepted = False
        elif timestamp == self.timestamp:
            accepted = self.uid <= uid
        else:
            accepted = self.timestamp < timestamp
        if accepted:
            self.update(timestamp, uid, opt, data)
        self.lock.release()
        return accepted

    def update(self, timestamp, uid, opt, data):
        self.timestamp = timestamp
        self.uid = uid
        self.opt = opt
        self.data = data
        self.promised = True

    def equal(self, timestamp, uid):
        return self.timestamp == timestamp and self.uid == uid


class AcceptorReceiverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            header, data = recv_all(self.request, 4, BUF_SIZE)
            msg_type, timestamp, uid, opt = retrieve_header(header)
            # propose, promise
            if msg_type == PROPOSE_MSG:
                if self.server.accept(timestamp, uid, opt, data):
                    header = init_header(PROMISE_MSG, timestamp, uid, opt)
                else:
                    header = init_header(NO_PROMISE_MSG, self.server.timestamp, self.server.uid, self.server.opt)
                send_all(self.request, header, self.server.data)
            elif msg_type == ACCEPT_MSG:
                # print (self.server.promised, self.server.timestamp, timestamp)
                if self.server.promised and self.server.equal(timestamp, uid):
                    self.server.promised = False
                    if self.server.senders is not None:
                        header = init_header(LEARN_MSG, timestamp, uid, opt)
                        self.server.senders.broadcast(header, data)
                        # print (header, uid, opt, data)
                    # pass

