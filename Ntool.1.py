# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from socket import *
import sys

form_class = uic.loadUiType("socket_ui.ui")[0]

class MyWindow(QMainWindow, form_class):
    listen_client = pyqtSignal()
    host = "127.0.0.1"
    port = 4444

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #여기서 ,ui 파일을 보고 직접 바인딩되는 이벤트 객체 핸들러를 지정해야된다
        #setupUi(self) 가 객체를 가지고 있어 미리 바인딩이 되지 않는다 ㅇㅋ?
        #모르면 참고 https://wikidocs.net/5228
        self.btn_server_run.clicked.connect(self.run_server)
        self.btn_server_send.clicked.connect(self.send)
        self.th_server = run_server_thread(parent=self)
        # 각각 함수로 무엇을 할지를 정의한다
        # 시그널 사용자 정의 함수
        self.th_server.client_new_sig.connect(self.client_new)
        self.th_server.update_client_sig.connect(self.update_client)
        self.th_server.msg_sig.connect(self.msg_all_update)


        # 종료 시그널 발생시 실행되는 함수
        self.th_server.finished.connect(self.thread_finished)




    # @pyqtSlot()

    def run_server(self):

        if self.l_server_state_rs.text() == "Running":
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")
            self.th_server.run_bool = False
            self.send_close_connection()
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
            self.msg_all_server.append("Running Server")
            self.msg_all_server.append("Port binding start")


        # client_wait.client_sig.connect(self)


        # port 값을 str로 변환하지 않고 넣게 될 경우 타입 에러로 프로그램이 죽는 경우가 발생한다
        # QMessageBox.about(self, "message", "hello")
    def send(self, object):
        print(object)
        # self.th_server.wait()
        # self.th_server.quit()
    def client_new(self, socket_obj):
        print("client new : " + str(socket_obj))

    def thread_finished(self):
        self.msg_all_server.append("Stopped Server.......memory free & client wait thread finished")
        print("Client wait thread finished")

    def alram_to_user(self, code):
        # send alram to user from error or blank input
        if code == 1:
            QMessageBox.about(self, "Notice", "Please input right!!!")
        elif code == 2:
            QMessageBox.about(self, "Erorr", "Request developer your Error type")
        pass

    def update_client(self, client):
        cnt = self.btn_server_run.Text().split(":")[1]
        self.btn_server_run.setText("Stop / client:"+str(int(cnt)+1))


    def send_close_connection(self):
        end_s = socket()
        end_s.connect((self.host, int(self.port)))

    def msg_all_update(self, data):
        self.msg_all_server.append(str(data))

class run_server_thread(QThread):
    client_new_sig = pyqtSignal(socket)
    update_client_sig = pyqtSignal(str)
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
            self.sleep(1)
            # client wait
            conn, addr = s.accept()
            # client connected
            if conn:
                # press stop btn check
                if not self.run_bool:
                    # server side connection exit
                    s.close()
                    # client list reset
                    self.client = []
                    # exit loop
                    break
                else:
                    self.client.append(conn)
                    # can't acess ui object, using signal or slot
                    self.client_new_sig.emit(conn)
                    self.update_client_sig.emit(str(addr[0]) + " : " + str(addr[1]))
            pass
    def send_msg(self, data):
        if len(self.client) > 0 and data != "":
            for client_con in self.client:
                who = client_con.getpeername()
                who_details = str(who[0]) + ":" + str(who[1])
                client_con.send((who_details + "`" + str(data)).encode("utf-8"))
                self.msg_sig.emit(who_details + " ==>  broadcast")
        else:
            QMessageBox.about(self, "Notice", "No, connected clinet")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()