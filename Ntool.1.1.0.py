# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from socket import *
import sys

form_class = uic.loadUiType("socket_ui.ui")[0]

class MyWindow(QMainWindow, form_class):

    host = "127.0.0.1"
    port = 4444
    client_c = {}

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        # make thread
        self.th_client = client_thread()
        self.th_server = server_thread()
        self.th_bypass_msg = by_pass_msg_thread()

        ################################################## server_side
        self.btn_server_run.clicked.connect(self.run_server_ex)
        self.th_server.clinet_connection_sig()
        ################################################## client_side
        self.btn_client_run.clicked.connect(self.run_client_ex)

    def run_server_ex(self, ex_type):
        ex_type = True if not (ex_type) and self.l_server_state_rs.text() != "Running" else False
        if ex_type:
            self.host = self.input_server_host.text() if self.input_server_host.text() else self.host;
            self.input_server_host.setText(self.host)
            self.port = self.input_server_port.text() if self.input_server_port.text() else self.port;
            self.input_server_port.setText(str(self.port))
            self.th_server.host = self.host
            self.th_server.port = self.port
            self.th_server.run_bool = True
            self.btn_server_run.setText("Stop")
            self.input_server_host.setEnabled(False)
            self.input_server_port.setEnabled(False)
            self.l_server_state_rs.setText("Running")
            print("Running Server.....ok")
        else:
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")

    def run_client_ex(self, ex_type):
        ex_type = True if not(ex_type) and self.l_client_state_rs.text() != "Running" else False
        if  ex_type:
            self.host = self.input_client_host.text() if self.input_client_host.text() else self.host;
            self.input_client_host.setText(self.host)
            self.port = self.input_client_port.text() if self.input_client_port.text() else self.port;
            self.input_client_port.setText(str(self.port))
            self.btn_client_run.setText("Stop")
            self.input_client_host.setEnabled(False)
            self.input_client_port.setEnabled(False)
            self.l_client_state_rs.setText("Running")
            print("Running Client.....ok")
        else:
            self.input_client_host.setEnabled(True)
            self.input_client_port.setEnabled(True)
            self.l_client_state_rs.setText("Stopped")
            self.btn_client_run.setText("Start")

    def send_msg_all(self, all_connectons, data):
        for connection in all_connectons:
            connection.send(data.encode('utf-8'))
    def client_mnager(self, type = 1, connection = ""):
        if connection == "": print("tests")
        if type:#add connection
            who  = connection.getpeername()[0]+":"+str(connection.getpeername()[1])
            print(who)
            self.client_c.update(who:[connection, ])

        else:#del connection
    def notice(self, msg):
        print("test")
class server_thread(QThread):
    clinet_connection_sig = pyqtSignal(int, socket)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = False
        self.host = ""
        self.port = 0

    # server thread main
    def run(self):
        # var set socket type
        s = socket()
        # create socket
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #bscoket bind from port
        s.bind((self.host, self.port))
        # can client connection 5 client
        s.listen(5)

        # check thread excute from self.run_bool
        while self.run_bool:
            print("client wait start")
            self.msleep(300)
            conn, addr = s.accept()
            if conn:
                if not self.run_bool:
                    s.close()
                    for client_c in self.client:
                        try:
                            client_c.close()
                        except:
                            pass
                    self.client = []
                    break
                else:
                    self.clinet_connection_sig.emit(1, conn)# 클라이언트 추가 접속 시그널

            pass


class by_pass_msg_thread(QThread):
    print("test")

class client_thread(QThread):
    print("test")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()