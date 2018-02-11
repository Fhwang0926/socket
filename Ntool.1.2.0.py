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
        ################################################## server_side
        self.btn_server_run.clicked.connect(self.run_server_ex)
        self.btn_server_send.clicked.connect(self.common_input_send)
        self.input_server_msg.returnPressed.connect(self.common_input_send)
        self.th_server.client_connection_sig.connect(self.client_manager)
        self.th_server.client_all_disconnection_sig.connect(self.client_manager)

        ################################################## client_side
        self.btn_client_run.clicked.connect(self.run_client_ex)
        self.btn_client_send.clicked.connect(self.common_input_send)
        self.input_client_msg.returnPressed.connect(self.common_input_send)
        self.th_client.client_msg_update_sig.connect(self.msg_all_client.append)
        self.th_client.msg_box_sig.connect(self.msg_box)
        self.th_client.client_con_cnt_sig.connect(self.client_con_cnt.setText)
        self.th_client.client_exit_sig.connect(self.run_client_ex)

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
            self.input_server_host.setEnabled(False)
            self.input_server_port.setEnabled(False)
            self.l_server_state_rs.setText("Running")
            self.btn_server_run.setText("Stop")
            self.th_server.s = socket()
            self.th_server.start()
            print("Running Server.....ok")
        else:
            if self.th_client.run_bool:
                self.msg_box("Hey!!", "Please disconnection client first !!")
            else:
                self.input_server_host.setEnabled(True)
                self.input_server_port.setEnabled(True)
                self.l_server_state_rs.setText("Stopped")
                self.btn_server_run.setText("Start")
                self.th_server.run_bool = False
                self.th_server.run_bool = False
                self.client_manager(0, "all")


    def run_client_ex(self, ex_type):
        ex_type = True if not (ex_type) and self.l_client_state_rs.text() != "Running" else False
        if  ex_type:
            self.host = self.input_client_host.text() if self.input_client_host.text() else self.host;
            self.input_client_host.setText(self.host)
            self.th_client.host = self.host
            self.port = self.input_client_port.text() if self.input_client_port.text() else self.port;
            self.input_client_port.setText(str(self.port))
            self.th_client.port = self.port
            self.btn_client_run.setText("Stop")
            self.input_client_host.setEnabled(False)
            self.input_client_port.setEnabled(False)
            self.l_client_state_rs.setText("Running")
            self.th_client.con = socket()
            self.th_client.run_bool = True
            self.th_client.start()
        else:
            self.input_client_host.setEnabled(True)
            self.input_client_port.setEnabled(True)
            self.l_client_state_rs.setText("Stopped")
            self.btn_client_run.setText("Start")

            self.client_con_cnt.setText("0")
            self.msg_all_client.append("exit connection")
            if self.th_client.run_bool:
                self.th_client.run_bool = False
                self.th_client.con.send("FLAG|exit".encode("UTF-8"))
            self.con = socket()

    def common_input_send(self):
        if self.tab_col.currentIndex() == 0:
            data = self.input_server_msg.text()
            if data != "" :
                if self.th_server.run_bool and len(self.client_c) > 0: #서버가 동작중인가 확인
                    data = "Notice | "+data # 공지 누가 전송하는지를 저장
                    self.send_msg_all(data) #공지
                    self.input_server_msg.setText("") # 메세지 보내고 초기화
                else:
                    self.msg_box("Notice", "No, server run or client is Zero") #서버가 일하지 않을 때
            else:
                self.msg_box() # 공백일때
            self.input_server_msg.setFocus()
        else:
            data = self.input_client_msg.text()
            if data != "":
                if self.th_client.run_bool:
                    send_data = str(self.th_client.con.getsockname()[0])
                    send_data += ":"
                    send_data += str(self.th_client.con.getsockname()[1])
                    send_data += "|"
                    send_data += data
                    self.send_msg_all(send_data)
                    self.input_client_msg.setText("")  # 메세지 보내고 초기화
                else:
                    self.msg_box("Notice", "No, Other connection")
            else:
                self.msg_box()
            self.input_client_msg.setFocus()

    # send msg all
    def send_msg_all(self, data = ""):
        if data == "":
            self.msg_box()
            return False
        if self.th_server.run_bool:
            if not ("FLAG" in data):
                self.msg_all_server.append(data)
            for client in self.client_c:
                try:
                    self.client_c[client]['thread'].con.send(data.encode('utf-8'))
                except Exception as e:
                    print(e)
                    self.client_manager(0, self.client_c)
        elif self.th_client.run_bool:
            try:
                self.input_client_msg.setText("")
                self.th_client.con.send(data.encode("utf-8"))
            except Exception as e:
                self.msg_all_client.append(str(e))
                print(e)

    def client_manager(self, type = 1, connection = ""):
        if type:#add connection
            who  = connection.getpeername()[0]+":"+str(connection.getpeername()[1])
            print(who)
            self.list_update(1, who)
            th_bypass = by_pass_msg_thread()
            th_bypass.run_bool = True
            th_bypass.con = connection
            self.client_c.update({who : {"thread" : th_bypass}})
            self.client_c[who]['thread'].msg_rebind_sig.connect(self.send_msg_all)
            self.client_c[who]['thread'].client_exit_sig.connect(self.list_update)
            self.client_c[who]['thread'].start()
            flag = "FLAG|refresh|"+str(len(self.client_c))
            self.send_msg_all(flag)
        else:#del connection
            flag = "FLAG|exit"
            if str(connection) == "all":
                if len(self.client_c) > 0:
                    for client in self.client_c:
                        try:
                            self.msg_all_server.append("disconnection | "+str(client))
                            self.client_c[client]['thread'].run_bool = False
                            self.client_c[client]['thread'].con.send(flag.encode("UTF-8"))
                        except Exception as e:
                            print(str(e))
                    self.client_c = []
                    self.list_clients.clear()
                self.th_server.s.close()
            else:
                who = connection
                self.list_update(0, who) # 리스트 제거 및 연경 종료 표시
                try:
                    self.client_c[who]['thread'].con.send(flag)
                finally:
                    if self.th_server.run_bool:
                        self.client_c.pop(who)
                        print("remove disconnection client")
        print(flag)

    # common msg func
    def msg_box(self, title = "Notice", msg = "No, blank!!!", kill_type = ""):
        if "Error" in msg:
            limit = msg.rindex("]")+1
            title = msg[:limit]
            msg = msg[limit+1:]
        QMessageBox.about(self, title, msg)
        print("msg box | "+title+":"+msg)
        if kill_type == "server":
            self.run_server_ex(0)
        if kill_type == "client":
            self.run_client_ex(0)

    def list_update(self, type=1, who = ""):
        if who != "":
            if type:
                self.list_clients.addItem(who)
                self.msg_all_server.append("connection | " + who)
            else:
                if self.th_server.run_bool:
                    self.client_c.pop(who)
                    self.msg_all_server.append("disconnection | "+who)
                    self.list_clients.clear()
                    for who in self.client_c:
                        self.list_clients.addItem(who)
            self.send_msg_all("FLAG|refresh|"+str(len(self.client_c)))
        else:
            self.msg_box()

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

class client_thread(QThread):
    client_msg_update_sig = pyqtSignal(str)
    msg_box_sig = pyqtSignal(str, str, str)
    client_con_cnt_sig = pyqtSignal(str)
    client_exit_sig = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = False
        self.host = ""
        self.port = 0
        self.con = socket()
        self.me = ""

    def run(self):
        try:
            self.con.connect((self.host, int(self.port))) #connect socket
            me = str(self.con.getsockname()[0]) + ":" + str(self.con.getsockname()[1]) #get who once
            while self.run_bool: # client run code
                self.msleep(100) #wait 0.1 sec execute thread
                data_recive = self.con.recv(1024).decode("utf-8").split("|") # client recived  data
                if (data_recive[0] != ""):
                    if data_recive[0] == "FLAG": # communication code with server
                        if data_recive[1] == "exit": #exit code
                            break
                        elif data_recive[1] == "refresh": # connection refresh code
                            self.client_con_cnt_sig.emit(data_recive[2]) #update connection info
                        continue # keep going loop
                    elif data_recive[0] == me:
                        rs = "me : "+data_recive[1] # send me
                    else:
                        rs = data_recive[0]+"|"+data_recive[1] # send pthers
                    self.client_msg_update_sig.emit(rs)  #client update signal send main process
        except Exception as e:
            self.msg_box_sig.emit("Notice", str(e), "") #notice alert error msg

        if self.run_bool:
            self.client_exit_sig.emit(0)
            self.run_bool = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()