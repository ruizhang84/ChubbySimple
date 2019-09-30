import socketserver
from paxos.proposer.runners import *
from paxos.sockets import *


class Receiver:
    def __init__(self, uid, server_lst, host):
        self.uid = uid
        self.proposer = Proposer(uid, server_lst)
        self.receiver = APIReceiver(host, APIReceiverHandler)

    def start(self):
        self.receiver.receiver_start(self.proposer, self.uid)


class APIReceiver(socketserver.ThreadingTCPServer):
    def receiver_start(self, proposer, uid):
        self.proposer = proposer
        self.master = False
        self.uid = uid
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        self.server_close()
        self.proposer.messenger.close()


class APIReceiverHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            header, data = recv_all(self.request, 3, BUF_SIZE)
            msg_type, uid = header
            # propose, promise
            if msg_type == WRITE:
                succeed = self.server.proposer.write(data)
                send_all(self.request, [msg_type, self.server.uid], str(succeed))
            elif msg_type == LOCK:
                succeed = self.server.proposer.lock()
                send_all(self.request, [msg_type, self.server.uid], str(succeed))
            elif msg_type == RELEASE:
                succeed = self.server.proposer.lock()
                send_all(self.request, [msg_type, self.server.uid], str(succeed))
            elif msg_type == IS_MASTER:
                send_all(self.request, [msg_type, self.server.uid], str(self.server.master))
            elif msg_type == SET_MASTER: # vote for master
                self.server.master = True
                send_all(self.request, [msg_type, self.server.uid], str(self.server.master))
            elif msg_type == GET_ID:
                send_all(self.request, [msg_type, self.server.uid], ".")

