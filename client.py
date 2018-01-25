import sys, threading, time, subprocess

if sys.platform == "win32":
    from socket import *
else:
    from socket import *


def send():
    while 1:
        time.sleep(1)
        data = input("msg > ")
        s.send(data.encode("utf-8"))

def recive():
    while 1:
        time.sleep(1)
        data_recive = s.recv(1024).decode("utf-8").split("|")
        if (data_recive[0]):
            if data_recive[0] == str(s.getsockname()[0])+":"+str(s.getsockname()[1]):
                who = "me : "
            else:
                who = data_recive[0]+" : "
            print(str(who)+ str(data_recive[1]))

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
try:
    s.connect((host, port))
    print("ok ", host)
    print(s.getpeername())
except:
    print("Please, chekck IP or Port")
    sys.exit()
t_send = threading.Thread(target=send)
t_send.start()
t_recive = threading.Thread(target=recive)
t_recive.start()
while True:
    pass
