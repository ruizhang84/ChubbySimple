from paxos.learner.learners import *

LOCKED = "locked"
UNLOCKED = "unlocked"


class Executor:
    def __init__(self, filename):
        self.log = {}       # simulate a log
        self.adviser = UNLOCKED
        self.loc = filename

    def execute(self, opt, data):
        if opt in self.log:
            return True
        self.log[opt] = data
        operation, _ = retrieve_opt(opt)
        if operation == WRITE:
            with open(self.loc, 'a+') as f:
                f.write(data)
            return True     # operation success
        elif operation == LOCK:
            if self.adviser == UNLOCKED:
                self.adviser = LOCKED
                return True
            else:
                return False
        elif operation == RELEASE:
            if self.adviser == LOCKED:
                self.adviser = UNLOCKED
                return True
            else:
                return False
        return False


class Learner:
    def __init__(self, uid, server_addr, nserver, output="output.txt"):
        self.uid = uid
        self.messenger = LearnerReceiver(server_addr, LearnerReceiverHandler)
        self.exec = Executor(self.name_output(output))
        self.operator = Operation(nserver)

    def name_output(self, output):
        return str(self.uid) + "_" + output

    def update_server(self, nserver):
        self.operator = Operation(nserver)
        self.messenger.operator = self.operator

    def update_output(self, output):
        self.exec = Executor(self.name_output(output))
        self.messenger.executor = self.exec

    def start(self):
        self.messenger.receiver_start(self.operator, self.exec)



