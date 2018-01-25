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
    thread = []

    def __init__(self):
        super().__init__()
        # server
        self.setupUi(self)
        #여기서 ,ui 파일을 보고 직접 바인딩되는 이벤트 객체 핸들러를 지정해야된다
        #setupUi(self) 가 객체를 가지고 있어 미리 바인딩이 되지 않는다 ㅇㅋ?
        #모르면 참고 https://wikidocs.net/5228
        self.btn_server_run.clicked.connect(self.run_server)
        self.btn_server_send.clicked.connect(self.notice_send)
        self.th_server = run_server_thread(parent=self)
        self.th_client = run_client_thread(parent=self)
        # 각각 함수로 무엇을 할지를 정의한다
        # 시그널 사용자 정의 함수
        self.th_server.update_client_sig.connect(self.update_client_cnt)
        self.th_server.update_disclient_sig.connect(self.update_client_cnt)
        self.th_server.msg_sig.connect(self.msg_update_server)
        self.th_server.client_thread_sig.connect(self.client_thread)
        self.th_server.client_thread_exit_sig.connect(self.client_thread_exit)

        # 종료 시그널 발생시 실행되는 함수
        self.th_server.finished.connect(self.thread_finished)
        self.th_client.finished.connect(self.thread_finished)

        # client
        self.btn_client_run.clicked.connect(self.run_client)
        self.btn_client_send.clicked.connect(self.msg_send)
        self.th_client.client_sig.connect(self.msg_update_client)
        self.th_client.client_get_msg_sig.connect(self.msg_update_client)

    # client side
    def run_client(self):
        if self.l_client_state_rs.text() == "Running":
            self.input_client_host.setEnabled(True)
            self.input_client_port.setEnabled(True)
            self.l_client_state_rs.setText("Stopped")
            self.btn_client_run.setText("Start")
            self.th_client.run_bool = False
            # self.clinet_thread_all()
            # self.th_client.send_close_connection()
            self.msg_all_client.append("Stop Server.....ok")

        else:

            self.host = self.input_client_host.text() if self.input_client_host.text() else self.host;
            self.input_client_host.setText(self.host)
            self.th_client.host = self.host
            self.port = self.input_client_port.text() if self.input_client_port.text() else self.port;
            self.input_client_port.setText(str(self.port))
            self.th_client.port = int(self.port)
            self.btn_client_run.setText("Stop")
            self.input_client_host.setEnabled(False)
            self.input_client_port.setEnabled(False)
            self.l_client_state_rs.setText("Running")
            self.msg_all_client.append("Running Client.....ok")
            self.th_client.run_bool = True
            self.th_client.start()


    def msg_send(self):
        if self.input_client_msg.text() == "":
            QMessageBox.about(self, "Notice", "Please,input MSG")
        elif len(self.thread) < 2:
            QMessageBox.about(self, "Notice", "No, another client")
        else:
            who = str(self.th_client.client_s.getsockname()[0])+":"+str(self.th_client.client_s.getsockname()[1])
            self.th_server.send_msg(self.input_client_msg.text(), who)

    def client_get_msg(self, data):
        data_recive = data.decode("utf-8").split("|")
        if data_recive[0] == str(self.th_client.s.getsockname()[0]) + ":" + str(self.th_client.s.getsockname()[1]):
            who = "me : "
        else:
            who = data_recive[0] + " : "
        self.msg_update_client(str(who) + str(data_recive[1]))
        print("\n" + str(who) + str(data_recive[1]))


    # server side
    # thread all kill
    def clinet_thread_all_exit(self):
        for th in self.thread:
            try:
                th.run_bool = False
                th.terminate()
            finally:
                pass
        print("End all client thread")

    # client thread kill using index
    def client_thread_exit(self, i):
        self.thread[i].run_bool = False
        self.thread[i].terminate()
        self.thread.pop(i)
    # @pyqtSlot()
    def run_server(self):

        if self.l_server_state_rs.text() == "Running":
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")
            self.th_server.run_bool = False
            self.clinet_thread_all_exit()
            self.th_server.send_close_connection()
        else:
            self.th_server.run_bool = True
            self.th_server.start()
            self.host = self.input_server_host.text() if self.input_server_host.text() else self.host;
            self.input_server_host.setText(self.host)
            self.th_server.host = self.host
            self.port = self.input_server_port.text() if self.input_server_port.text() else self.port;
            self.input_server_port.setText(str(self.port))
            self.th_server.port = int(self.port)
            self.btn_server_run.setText("Stop")
            self.input_server_host.setEnabled(False)
            self.input_server_port.setEnabled(False)
            self.l_server_state_rs.setText("Running")
            self.msg_all_server.append("Running Server.....ok")

        # port 값을 str로 변환하지 않고 넣게 될 경우 타입 에러로 프로그램이 죽는 경우가 발생한다
        # QMessageBox.about(self, "message", "hello")
    # server send notice MSG
    def notice_send(self, msg_data):
        if not msg_data:
            msg_data = self.input_server_msg.text()
            self.input_server_msg.setText("")
            print(str(msg_data) + " sending msg")
        if not self.th_server.send_msg(msg_data):
            print("No client")
            QMessageBox.about(self, "Notice", "No Client connections or MSG\nPlease check client to to sending, or MSG")
    # log server binding thread finished
    def thread_finished(self):
        th_type = self.tab_col.tabText(self.tab_col.currentIndex())
        if th_type == "Client":
            self.msg_all_client.append("Stopped Client.......ok")
        else:
            self.msg_all_server.append("Stopped Server.......ok")
        print("thread finished")
        print("Memorey free....ok")
    # update client cnt when client new connection
    def update_client_cnt(self, client_str, calc="+"):
        if calc == "+":
            try:
                cnt = self.btn_server_run.text().split(":")[1]
                cnt = "Stop / client:" + str(int(cnt) + 1)
            except:
                cnt = "Stop / client:1"
            self.btn_server_run.setText(cnt)
            self.msg_update_server(client_str + ".....connected ")
            print(client_str + ".....connected ")
        else:
            cnt = int(self.btn_server_run.text().split(":")[1])
            cnt = "Stop / client:" + str(cnt-1)
            self.btn_server_run.setText(cnt)
            self.msg_update_server(client_str + ".....disconnected", 1)
            print(client_str + ".....disconnected")
    # msg add function
    def msg_update_server(self, data):
        self.msg_all_server.append(str(data))
    def msg_update_client(self, data):
        self.msg_all_client.append(str(data))

    #run client thread catch msg from client
    def client_thread(self, con):
        # add thread object
        client_thread = run_client_bypass()
        client_thread.msg_rebind_sig.connect(self.msg_update_server)
        self.thread.append(client_thread)
        # thread run bit set
        # self.thread[len(self.thread)-1].run_bool = True
        # store conn
        self.thread[len(self.thread) - 1].index = (len(self.thread) - 1)
        self.thread[len(self.thread) - 1].con = con
        # start recive thread
        self.thread[len(self.thread)-1].start()

    def client_exit(self):
        self.th_client.run_bool = False





class run_server_thread(QThread):
    client_thread_exit_sig = pyqtSignal(int)
    client_thread_sig = pyqtSignal(socket)
    # can return signal parameter socket object
    update_client_sig = pyqtSignal(str)
    update_disclient_sig = pyqtSignal(str, str)
    msg_sig = pyqtSignal(str)
    client = []

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = True
        self.host = ""
        self.port = 0

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
            # reduce schedule using sleep
            self.msleep(300)
            # client wait
            conn, addr = s.accept()
            # client connected
            if conn:
                # press stop btn check
                if not self.run_bool:
                    # server side connection exit
                    s.close()
                    # client list reset
                    for client_c in self.client:
                        try:
                            client_c.close()
                        except:
                            pass
                    self.client = []
                    # exit loop
                    break
                else:
                    # add client connection
                    self.client.append(conn)
                    # notice main process to start client msg recive thread
                    self.client_thread_sig.emit(conn)
                    # can't access ui object, using signal or slot
                    self.update_client_sig.emit(str(addr[0]) + " : " + str(addr[1]))
            pass

    # sending connection for close
    def send_close_connection(self):
        end_s = socket()
        end_s.connect((self.host, int(self.port)))
    # server Notice function
    def send_msg(self, data="", who="", connection = ""):
        connection = connection if connection != "" else self.client
        if (len(connection) and data):
            for i in range(0, len(connection)):
                who = ("Server notice : " if who == "" else who)
                if connection[i] != "":
                    try:
                        connection[i].send((who+"|"+str(data)).encode("utf-8"))
                    except:
                        # close connection remove
                        self.update_disclient_sig.emit(str(connection[i].getpeername()[0])+":"+str(connection[i].getpeername()[1]), "-")
                        self.client.pop(i)
                        self.client_thread_exit_sig.emit(i)
            self.msg_sig.emit(who +"|"+ str(data) + " ==>  broadcast")
            return True
        else:
            return False

class run_client_thread(QThread):
    exception_sig = pyqtSignal(str)
    client_sig = pyqtSignal(str)
    client_get_msg_sig = pyqtSignal(str)
    client_exit_sig = pyqtSignal()
    def __init__(self, parent=None):

        super().__init__()
        self.main = parent
        self.run_bool = True
        self.client_s = socket()
        self.host = ""
        self.port = 0

    def run(self):
        try:
            self.client_s.connect((self.host, self.port))
            print("ok ", self.host)
            who = str(self.client_s.getsockname()[0]) + ":" + str(self.client_s.getsockname()[1])
            self.client_sig.emit(who + "........connected")

            while self.run_bool:
                self.msleep(150)
                print("wait msg")
                data_recive = self.client_s.recv(1024).decode("utf-8").split("|")
                if (data_recive[0]):
                    is_me_chk = str(self.client_s.getsockname()[0]) + " : " + str(self.client_s.getsockname()[1])
                    if data_recive[0].replace(" ","") == is_me_chk.replace(" ", ""):
                        who = "me : "
                    else:
                        who = data_recive[0] + " : "
                    data = str(who) + str(data_recive[1])
                    self.client_get_msg_sig.emit(data)
                    print(data)
            if not self.run_bool:
                self.client_s.close()
                # self.client_exit_sig.emit()
        except:
            print("Please, chekck IP or Port")
            self.exception_sig.emit("Please, chekck IP or Port")




# client_msg bypass thread
class run_client_bypass(QThread):
    msg_rebind_sig = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.run_bool_bypass = True
        self.con = socket()
        self.index = 0

    def run(self):
        while self.run_bool_bypass:
            self.msleep(150)
            data = self.con.recv(1024).decode("utf-8")
            if data:
                server = run_server_thread()
                who = str(self.con.getpeername()[0])+":"+str(self.con.getpeername()[1])
                print("rebinding : " + who+" ==> "+data)
                server.send_msg(data, who)
                self.msg_rebind_sig.emit("rebinding : " + who+" ==> "+data)
        print("end client bypass")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()