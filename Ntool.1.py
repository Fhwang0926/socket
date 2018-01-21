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
        self.setupUi(self)
        #여기서 ,ui 파일을 보고 직접 바인딩되는 이벤트 객체 핸들러를 지정해야된다
        #setupUi(self) 가 객체를 가지고 있어 미리 바인딩이 되지 않는다 ㅇㅋ?
        #모르면 참고 https://wikidocs.net/5228
        self.btn_server_run.clicked.connect(self.run_server)
        self.btn_server_send.clicked.connect(self.notice_send)
        self.th_server = run_server_thread(parent=self)

        # 각각 함수로 무엇을 할지를 정의한다
        # 시그널 사용자 정의 함수
        self.th_server.update_client_sig.connect(self.update_client_cnt)
        self.th_server.update_disclient_sig.connect(self.update_client_cnt)
        self.th_server.msg_sig.connect(self.msg_all_update)
        self.th_server.client_thread_sig.connect(self.client_thread)
        self.th_server.client_thread_exit_sig.connect(self.client_thread_exit)




        # 종료 시그널 발생시 실행되는 함수
        self.th_server.finished.connect(self.thread_finished)

    # thread all kill
    def clinet_thread_all(self):
        for th in self.thread:
            try:
                th.run_bool = False
                th.terminate()
            finally:
                pass
        print("End all client thread")




    # @pyqtSlot()
    def run_server(self):

        if self.l_server_state_rs.text() == "Running":
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")
            self.th_server.run_bool = False
            self.clinet_thread_all()
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
        self.msg_all_server.append("Stopped Server.......ok")
        print("Client wait thread finished")
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
            self.msg_all_server.append(client_str + ".....connected ")
            print(client_str + ".....connected ")
        else:
            cnt = int(self.btn_server_run.text().split(":")[1])
            cnt = "Stop / client:" + str(cnt-1)
            self.btn_server_run.setText(cnt)
            self.msg_all_server.append(client_str + ".....disconnected")
            print(client_str + ".....disconnected")
    # msg add function
    def msg_all_update(self, data):
        self.msg_all_server.append(str(data))

    def client_thread(self, con):
        # add thread object
        client_thread = run_client_bypass()
        self.thread.append(client_thread)
        # thread run bit set
        # self.thread[len(self.thread)-1].run_bool = True
        # store conn
        self.thread[len(self.thread) - 1].index = (len(self.thread) - 1)
        self.thread[len(self.thread) - 1].con = con
        # start recive thread
        self.thread[len(self.thread)-1].start()

    def client_thread_exit(self, i):
        self.thread[i].run_bool = False
        self.thread[i].terminate()
        self.thread.pop(i)




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
    def send_msg(self, data="", who=""):
        if (len(self.client) and data):
            for i in range(0, len(self.client)):
                who = ("Server notice : " if who == "" else who)
                if self.client[i] != "":
                    try:
                        self.client[i].send((who+"|"+str(data)).encode("utf-8"))
                        self.msg_sig.emit(who+str(data) + " ==>  broadcast")
                    except:
                        # close connection remove
                        self.update_disclient_sig.emit(str(self.client[i].getpeername()[0])+":"+str(self.client[i].getpeername()[1]), "-")
                        self.client.pop(i)
                        self.client_thread_exit_sig.emit(i)

            return True
        else:
            return False
    # client_msg bypass thread

# class run_client_thread(QThread):
#
#     def __init__(self):
#         pass
#     def run(self):
#         pass

class run_client_bypass(QThread):

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

        print("end client bypass")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()