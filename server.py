import threading
from socket import *


global mode
global s
global host
global port
global client
global client_thread
global data


#msg data binding
def recive(conn):

    while True:
        data = conn.recv(1024).decode("utf-8")
        if (data):
            send(data)

def notice_server():
    while 1:
        if mode:
            notice = input("Notice : ")
            if (notice):
                for client_c in client:

                    client_c.send(("server : " +str(port)+ "`" + str(notice)).encode("utf-8"))
                print("send notice")

#msg sending
def send(data):
        if (data):
            for client_c in client:
                who = client_c.getpeername()
                who_details = str(who[0])+":"+str(who[1])
                client_c.send((who_details+"`"+str(data)).encode("utf-8"))
            print("\n"+who_details+" ==>  broadcast")
            mode = 1


mode = 1
client = []#save connection object
s = socket()
host = "127.0.0.1"
port = 4444

s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# create socket
s.bind((host, port))
# can client connection 5 client
s.listen(5)

print("server start demon")

threading.Thread(target=notice_server).start()
# index = 0
while True:

    conn, addr = s.accept()
    client.append(conn)

    threading.Thread(target=recive, args=(conn,)).start()
    # index = len(client)

    print("ok ", str(addr[0])+":"+str(addr[1]))
    print("total connection : "+str(len(client)))


#t_listen.start()





