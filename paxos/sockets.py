import socket

BUF_SIZE = 2048
PROMISE_MSG = "promise"
NO_PROMISE_MSG = "impossible"
PROPOSE_MSG = "proposal"
ACCEPT_MSG = "accept"
ACCEPTED_MSG = "accepted"
LEARN_MSG = "learned"
LEARNED_MSG = "learned"
TIMEOUT = 3
WRITE = "write"
LOCK = "lock"
RELEASE = "release"
GET_ID = "ID?"
IS_MASTER = "is_master?"
SET_MASTER = "set_master"
FAILURE = "Fails"
SUCCEED = "True"

def retrieve_opt(opt):
    operation = None
    sequence = None
    for i in range(len(opt)):
        if opt[i] == "-":
            operation = opt[:i]
            sequence = opt[i+1:]
    return operation, int(sequence)


def init_opt(operation, sequence):
    return operation + "-" + str(sequence)


def retrieve_header(header):
    msg_type, timestamp, uid, opt = header
    return msg_type, int(timestamp), int(uid), opt


def init_header(msg_type, timestamp, uid, opt):
    return [msg_type, timestamp, uid, opt]


def pack_msg(header, data):
    """
    :param data: a list of sending info
    :param header: parameter
    :return: msg packed in string
    """
    msg = "\\".join(str(h) for h in header) + "\\" + str(data)
    return str(len(data)) + "\\" + msg


def unpack_msg(msg, nums):
    """
    :param msg: a string of msg
    :param nums: number of parameter in header
    :return: a tuple of receiving data
    """
    header = []
    size = BUF_SIZE
    data = ""
    # get message size
    for i in range(len(msg)):
        if msg[i] == "\\":
            size = int(msg[:i])
            data = msg[i+1:]
            break
    # unpack
    for _ in range(nums):
        for i in range(len(data)):
            if data[i] == "\\":
                header.append(data[:i])
                data = data[i+1:]
                break
    return size, header, data


def recv_all(handler, header_num=4, buf_size=BUF_SIZE):

    msg = handler.recv(buf_size).decode()
    # print (msg)
    size, header, data = unpack_msg(msg, header_num)
    while len(data) < size:
        data += handler.recv(buf_size).decode()
    return header, data


def send_all(handler, header, data):
    msg = pack_msg(header, data)
    handler.sendall(msg.encode())


class Socket:
    def __init__(self):
        self.handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handler.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

