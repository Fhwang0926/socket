import sys, threading

if sys.platform == "win32":
    from socket import *
else:
    from socket import *


def send():
    while 1:
        data = input("msg > ")
        s.send(data.encode("utf-8"))

def recive():
    while 1:
        data_recive = s.recv(1024).decode("utf-8").split("`")
        if (data_recive[0]):
            if data_recive[0].split(":")[0] == get_ip():
                who = "me : "
            else:
                who = data_recive[0]+" : "
            print("\n"+str(who)+ data_recive[1])

def get_ip():
    s = socket()
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

global s
global host
global port
global data

data = ""
s = socket()
host = "127.0.0.1"
port = 4444

s.connect((host, port))
print("ok ", host)

t_send = threading.Thread(target=send)
t_send.start()
t_recive = threading.Thread(target=recive)
t_recive.start()
while True:
    pass
