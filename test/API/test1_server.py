from api.server import *

server_ips = ["localhost", "localhost", "localhost", "localhost", "localhost"]
server = Server(server_ips, port=1024)
server.start()

