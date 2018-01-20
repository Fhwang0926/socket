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


        # 종료 시그널 발생시 실행되는 함수
        self.th_server.finished.connect(self.thread_finished)




    # @pyqtSlot()

    def run_server(self):

        if self.l_server_state_rs.text() == "Running":
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")
            self.msg_all_server.append("Stopped Server")
            self.th_server.run_bool = False
            self.clear_listen()
        else:
            self.th_server.start()
            self.th_server.run_bool = True
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
        self.msg_all_server.append("메모리 해제 및 스레드 종료")

    def my_event(self):
        # gets executed on my_signal
        QMessageBox.about(self, "message", "hello")
        pass
    def chk_input(self):
        print("입력값 유효성 검사 함수")

    def update_client(self, str):
        cnt = self.btn_server_run.Text().split(":")[1]
        self.btn_server_run.setText("Stop / client : "+str(int(cnt)+1))
        self.update_msg_all("server", str)


    def update_msg_all(self, who, msg):
        who == "server" if self.msg_all_server.append(str(msg)) else self.msg_all_client.append(str(msg))

    def clear_listen(self):
        try:
            s = socket()
            s.connect((self.host, self.port))
            s.close
        finally:
            print("Ready connection STOP, reset binding session")
            # self.update_msg_all("server", "Ready connection STOP, reset binding session")



class run_server_thread(QThread):
    client_new_sig = pyqtSignal(socket)
    update_client_sig = pyqtSignal(str)
    client = []

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = True
        self.host = ""
        self.port = 0


    def run(self):
        # 디버깅용
        # index = 0
        # while self.run_bool:
        #     index += 1
        #     self.client_sig.emit("test"+str(index))
        #     # print("host" + str(self.host) + "|" + "port :" + str(self.port))
        #     self.sleep(1)

        try:
            if not self.run_bool:
                self.s.shutdown()
                self.s.close()
        finally:
            s = socket()  # save connection object

        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # create socket

        s.bind((self.host, self.port))
        # can client connection 5 client
        s.listen(5)
        print("바인딩 오케이")

        while self.run_bool:

            self.sleep(1)
            print("listen client start")
            conn, addr = s.accept()
            if conn:
                self.client.append(conn)
                # thread 를 사용하기에  ui 객체에 접근 가능하다
                self.client_new_sig.emit(conn)
                # self.update_client_sig.emit(str(addr[0]) + " : " + str(addr[1]))
                print("Stop...connection : " + str(len(self.client)))
            pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()