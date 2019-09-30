from paxos.acceptor.acceptors import *
from paxos.acceptor.senders import *


class Acceptor:
    def __init__(self, server_addr_lst, host_addr):
        self.server_addr_lst = server_addr_lst
        self.host = host_addr
        self.senders = AcceptorSender(server_addr_lst)
        self.acceptors = AcceptorReceiver(host_addr, AcceptorReceiverHandler)

    def start(self):
        self.acceptors.receiver_start(self.senders)

