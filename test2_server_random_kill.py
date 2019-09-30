from api.server import *
import  time

server_ips = ["localhost", "localhost", "localhost", "localhost", "localhost"]
server = Server(server_ips, port=1024)
server.start()

# double kill..
time.sleep(4)
server.random_kill()

time.sleep(4)
server.random_kill()

time.sleep(4)
print("-----above error message---")
print ('process killed!')