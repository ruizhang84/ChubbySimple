from paxos.sockets import *
import threading

class APISender:
    def __init__(self, server_ips, port=1024, timeout=TIMEOUT):
        self.server_addr_lst = []
        for i in range(len(server_ips)):
            host = server_ips[i]
            self.server_addr_lst.append((host, port))
            port += 1
        self.targets = []
        self.lock = threading.Semaphore()
        self.series = threading.Semaphore()
        self.timeout = timeout
        self.master = None

    def start(self):
        process = threading.Thread(target=self.connect, args=())
        process.start()
        print("api starts!")


    def connect(self):
        self.series.acquire()
        for host, port in self.server_addr_lst:
            args = (host, port)
            process = threading.Thread(target=self.open_connect, args=args)
            process.start()
            process.join(TIMEOUT)
        self.series.release()
        try:
            while True:
                continue
        except KeyboardInterrupt:
            pass
        self.close()

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
        target.handler.close()

    def update_server(self, server_addr_lst):
        self.server_addr_lst = server_addr_lst

    def find_master(self):
        highest_uid = -1
        master_candid = None
        for target in self.targets:
            msg_type, uid, data = self.send(target, [IS_MASTER, -1], ".")
            if data == "True":
                self.master = target
                return self.master
            elif uid > highest_uid:
                master_candid = target
                highest_uid = uid
        self.master = master_candid
        self.send(self.master, [SET_MASTER, -1], ".")
        return self.master

    def write(self, data):
        self.series.acquire()
        target = self.find_master()
        msg_type, _, status = self.send(target, [WRITE, -1], data)
        self.series.release()
        return msg_type != FAILURE and status == SUCCEED

    def lock(self):
        self.series.acquire()
        target = self.find_master()
        msg_type, _, status = self.send(target, [LOCK, -1], ".")
        self.series.release()
        return msg_type != FAILURE and status == SUCCEED

    def release(self):
        self.series.acquire()
        target = self.find_master()
        msg_type, _, status = self.send(target, [RELEASE, -1], ".")
        self.series.release()
        return msg_type != FAILURE and status == SUCCEED

    def read(self, filename="output.txt"):
        target = self.find_master()
        msg_type, uid, _ = self.send(target, [GET_ID, -1], ".")
        if msg_type == FAILURE:
            return False
        try:
            output = str(uid) + "_" + filename
            with open(output, 'r') as f:
                for line in f:
                    print(line)
        except:
            print ("can not find destination!")
        return True

    def send(self, target, header, data):
        try:
            send_all(target.handler, header, data)
            header, data = recv_all(target.handler, 3, BUF_SIZE)
            msg_type, uid = header
            return msg_type, int(uid), data
        except:
            return FAILURE, -1, data


