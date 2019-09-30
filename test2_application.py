from api.applications import *
server_ips = ["localhost", "localhost", "localhost", "localhost", "localhost"]
app = APISender(server_ips, port=1024)
app.start()

app.write("123")
app.write("123456")

# app.read()
