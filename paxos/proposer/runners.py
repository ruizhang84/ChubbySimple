from paxos.proposer.proposers import *
import time
import threading


class Proposer:
    """
    Proposer to send proposal and accept
    """
    def __init__(self, uid, server_addr_list):
        self.nserver = len(server_addr_list)
        self.storage = Store()
        self.messenger = ProposerSender(server_addr_list, self.storage)
        self.timestamp = 0
        self.uid = uid
        self.lock = threading.Semaphore()
        self.series = threading.Semaphore()
        self.sequence = 0

    def lock(self, timeout=TIMEOUT):
        self.series.acquire()
        self.sequence += 1
        opt = init_opt(LOCK, self.sequence)
        succeed = self.communicate(opt, ".", timeout)
        self.series.release()
        return succeed

    def release(self, timeout=TIMEOUT):
        self.series.acquire()
        self.sequence += 1
        opt = init_opt(LOCK, self.sequence)
        succeed = self.communicate(opt, ".", timeout)
        self.series.release()
        return succeed

    def write(self, data, timeout=TIMEOUT):
        self.series.acquire()
        self.sequence += 1
        opt = init_opt(WRITE, self.sequence)
        succeed =  self.communicate(opt, data, timeout)
        self.series.release()
        return succeed

    def communicate(self, opt, data, timeout=TIMEOUT):
        succeed = False
        self.timestamp += 1
        # proposal
        # opt = init_opt(WRITE, self.sequence)
        header = init_header(PROPOSE_MSG, self.timestamp, self.uid, opt)
        self.messenger.broadcast(header, data)   # propose
        # print (header, data)
        while True:
            time.sleep(timeout)  # wait, assumption as partial synchronous
            if len(self.get_info()) > self.nserver / 2.0:
                break

        # accept
        if self.proceed():
            header = init_header(ACCEPT_MSG, self.timestamp, self.uid, opt)
            succeed = True
        else:
            timestamp, uid, opt, data = self.select()
            header = init_header(ACCEPT_MSG, timestamp, uid, opt)
        # broadcast
        self.messenger.broadcast(header, data)
        return succeed

    def update_timestamp(self, timestamp):
        if self.timestamp <= timestamp:
            self.timestamp = timestamp + 1

    def get_info(self):
        info_lst = []
        self.lock.acquire()
        for info in self.storage.info:
            info_lst.append(info)
        self.lock.release()
        return info_lst

    def proceed(self):
        # If P does not receive any accepted operation from any of the acceptors
        for header, data in self.get_info():
            msg_type, timestamp, uid, opt = retrieve_header(header)
            if msg_type == PROMISE_MSG:
                continue
            else:
                return False
        self.storage.clear()
        return True

    def select(self):
        """
        decide what to accept
        :return: accept msg
        """

        # Otherwise, sending accept(t,
        # o0), where t is P's proposal timestamp and o0 is the operation with
        # proposal timestamp highest among all accepted operations
        timestamp_decide = -1
        uid_decide = -1
        opt_decide = None
        data_decide = None
        for header, data in self.get_info():
            msg_type, timestamp, uid, opt = retrieve_header(header)
            self.update_timestamp(timestamp)
            if msg_type == PROMISE_MSG:
                continue
            elif msg_type == NO_PROMISE_MSG:
                if timestamp > timestamp_decide or (timestamp == timestamp_decide and uid > uid_decide):
                    timestamp_decide = timestamp
                    uid_decide = uid
                    opt_decide = opt
                    data_decide = data
        self.storage.clear()
        return timestamp_decide, uid_decide, opt_decide, data_decide



