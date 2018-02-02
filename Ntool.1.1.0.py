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
        self.btn_server_send.clicked.connect(self.notice)
        self.input_server_msg.returnPressed.connect(self.notice)
        self.th_server.clinet_connection_sig.connect(self.client_manager)
        self.th_server.clinet_all_disconnection_sig.connect(self.client_manager)
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
            self.th_server.port = int(self.port)
            self.th_server.run_bool = True
            self.th_server.start()
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
            self.th_server.run_bool = False
            s = socket()
            s.connect((self.host, int(self.port)))
            s.close()
            self.th_server.exit()

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

    # send msg all
    def send_msg_all(self, data):
        for index in range(0, len(self.client_c)):
            try:
                self.client_c[index][0].send(data.encode('utf-8'))
            except Exception as e:
                print(e)
                self.client_manager(0, self.client_c)
    # client add/ del func
    def client_manager(self, type = 1, connection = ""):
        if connection == "": print("tests")
        if type:#add connection
            who  = connection.getpeername()[0]+":"+str(connection.getpeername()[1])
            print(who)
            th_bypass = by_pass_msg_thread()
            th_bypass.run_bool = True
            th_bypass.con = connection
            self.client_c.update({who : {"con" : connection, "thread" : th_bypass}})
            th_bypass.start()

        else:#del connection
            if str(connection) == "all":
                if len(self.client_c) > 0:
                    for client_index in range(0, len(self.client_c)):
                        self.client_c[client_index][0].close()
                        self.client_c[client_index][1].run_bool = False
                        self.client_c[client_index][1].terminate()

            else:
                who = connection.getpeername()[0] + ":" + str(connection.getpeername()[1])
                self.client_c[who][0] = ""
                self.client_c[who][1].terminate()

    def notice(self):
        data = self.input_server_msg.text()
        self.send_msg_all(data)
class server_thread(QThread):
    clinet_connection_sig = pyqtSignal(int, socket)
    clinet_all_disconnection_sig = pyqtSignal(int, str)

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
                    self.clinet_all_disconnection_sig.emit(0, "all")
                    break
                else:
                    self.clinet_connection_sig.emit(1, conn)# 클라이언트 추가 접속 시그널
            pass
            conn.close()
        s.close()
        print("finish server run thread")


class by_pass_msg_thread(QThread):
    msg_rebind_sig = pyqtSignal(str)
    client_exit_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.run_bool = False
        self.con = socket()
        self.index = 0

    def run(self):
        try:
            while self.run_bool:
                self.msleep(150)
                data = self.con.recv(1024).decode("utf-8")
                if data:
                    who = str(self.con.getpeername()[0]) + ":" + str(self.con.getpeername()[1])
                    print("rebinding : " + who + " ==> " + data)
                    self.msg_rebind_sig.emit(data)
        except Exception as error:
            print(str(error))
        who = str(self.con.getpeername()[0]) + ":" + str(self.con.getpeername()[1])
        self.client_exit_sig.emit(who)
        print("client_exit")
        print("thread exit client side close")

class client_thread(QThread):
    print("test")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()