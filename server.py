from socket import *
from PyQt5.QtCore import *

class server_thread(QThread):
    client_connection_sig = pyqtSignal(int, socket)
    client_all_disconnection_sig = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = False
        self.host = ""
        self.port = 0
        self.s = socket()

    # server thread main
    def run(self):
        # create socket
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #bscoket bind from port
        self.s.bind((self.host, self.port))
        # can client connection 5 client
        self.s.listen(5)
        try:
            while self.run_bool:
                self.msleep(100)
                conn, addr = self.s.accept()
                if conn:
                    if not self.run_bool:
                        conn.close()
                        break
                    else:
                        self.client_connection_sig.emit(1, conn)
            self.s.close()
        except Exception as e:
            print("th_server_error | "+str(e))
        print("server thread finished")

class by_pass_msg_thread(QThread):
    msg_rebind_sig = pyqtSignal(str)
    client_exit_sig = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.run_bool = False
        self.con = socket()
        self.index = 0

    def run(self):
        print("pybass thread start")
        who = str(self.con.getpeername()[0]) + ":" + str(self.con.getpeername()[1])
        try:
            while self.run_bool:
                self.msleep(150)
                data = self.con.recv(1024).decode("utf-8")
                if data.split("|")[0] == "FLAG":
                    print(data)
                    self.run_bool = False
                    break
                elif data[0]:
                    self.msg_rebind_sig.emit(data)
        except Exception as e:
            print("th_bypass_error | "+str(e))
        self.client_exit_sig.emit(0, who)
        self.con.close()
        print("bypass thread finished")
