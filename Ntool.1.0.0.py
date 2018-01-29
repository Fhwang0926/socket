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

        #common object
        self.th_server = run_server_thread(parent=self)
        self.th_client = run_client_thread(parent=self)

        # server side click
        self.btn_server_run.clicked.connect(self.run_server)
        self.btn_server_send.clicked.connect(self.send_msg_common)
        self.input_server_msg.returnPressed.connect(lambda: self.send_msg_common(""))

        # client side click
        self.btn_client_run.clicked.connect(self.run_client)
        self.btn_client_send.clicked.connect(self.send_msg_common)
        self.input_client_msg.returnPressed.connect(lambda: self.send_msg_common(""))


        # 각각 함수로 무엇을 할지를 정의한다
        # 시그널 사용자 정의 함수
        self.th_client.exception_mbox_sig.connect(self.mbox) #소켓 연결 오류 알림

        # server side signal
        self.th_server.msg_sig.connect(self.client_new) # 서버 메세지 바인딩 로그
        self.th_server.client_thread_new_sig.connect(self.client_thread_new) #클라이언트 스레드 새로 생성
        self.th_server.client_thread_exit_sig.connect(self.client_thread_exit) # 클라이어트 스레드 인덱스로 종료하기
        self.th_server.client_exit_sig.connect(self.client_exit) #종료 클라이언트 서버에서 목록 지우기

        # client side signal
        self.th_client.client_sig.connect(self.client_new) #신규 클라이언트 연결 정보 msg에 갱신
        self.th_client.client_get_msg_sig.connect(self.msg_update_client)#클라이언트 받은 메세지 갱신
        self.th_client.add_client_con_sig.connect(self.add_client_only_client_ex)
        self.th_client.client_exit_sig.connect(self.client_exit) #종료 클라이언트 서버에서 목록 지우기

        # finished signal from thread
        self.th_server.finished.connect(self.thread_finished) #server thread finished
        self.th_client.finished.connect(self.thread_finished) #client thread finished

    #common func
    def mbox(self, msg, is_error):
        if is_error == 1:
            index = int(msg.rindex("]"))
            msg_rs = msg[:index+1]+"\n"+msg[index+1:].strip()
            if self.tab_col.currentIndex() == 1:
                self.run_clien_ex(0)
        else:
            msg_rs = msg
        QMessageBox.about(self, "Notice", msg_rs)

    # client execute func
    def run_clien_ex(self, ex_type):
        if not ex_type:
            self.input_client_host.setEnabled(True)
            self.input_client_port.setEnabled(True)
            self.l_client_state_rs.setText("Stopped")
            self.btn_client_run.setText("Start")
            self.th_client.run_bool = False
            self.th_client.client_s.close()
            self.th_client.client_s = socket()
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

    # server execute func
    def run_server_ex(self, ex_type):
        if not ex_type:
            self.input_server_host.setEnabled(True)
            self.input_server_port.setEnabled(True)
            self.l_server_state_rs.setText("Stopped")
            self.btn_server_run.setText("Start")
            self.th_server.run_bool = False
            self.client_thread_exit()
            self.th_server.send_close_connection()
        else:
            self.th_server.run_bool = True
            self.th_server.start() #서버 스레드 시작
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


    ##################################################### client side
    # client btn click func
    def run_client(self):
        if not (self.l_client_state_rs.text() == "Running"):
            self.run_clien_ex(1)
        else:
            self.run_clien_ex(0)

    # client get msg and show msg
    def client_get_msg(self, data):
        data_recive = data.decode("utf-8").split("|") #split who and mssg
        if data_recive[0] == str(self.th_client.s.getsockname()[0]) + ":" + str(self.th_client.s.getsockname()[1]): #check who sender
            who = "me : "
        else:
            who = data_recive[0] + ":"
        self.msg_update_client(str(who) + str(data_recive[1])) #client mg update
        print(str(who) + str(data_recive[1])) #print client msg

    ##################################################### server side

    # server btn click func
    def run_server(self):
        if not (self.l_server_state_rs.text() == "Running"):
            self.run_server_ex(1)
        else:
            self.run_server_ex(0)

    # client thread kill
    def client_thread_exit(self, i = ""):
        try:
            if i == "": #인덱스가 없다면 클라이언트 스레드 전부 종료 있다면 인덱스 스레드만 종료
                for th in self.thread:
                    try:
                        th.run_bool = False
                        th.terminate()
                    finally:
                        print("thread exit")
            else:
                self.thread[i].run_bool = False
                self.thread[i].terminate()
        except:
            self.thread.pop(i)
        finally:
            print("End all client thread")



        # QMessageBox.about(self, "message", "hello")

    # clinet & server send msg common function
    def send_msg_common(self, msg_data):
        if self.tab_col.currentIndex() == 0:
            #server
            if not msg_data:
                msg_data = self.input_server_msg.text()
                self.input_server_msg.setText("")
                print(str(msg_data) + " sending msg from server")
            if not self.th_server.send_msg(msg_data):
                print("No client")
                QMessageBox.about(self, "Notice", "No Client connections or MSG\nPlease check client to to sending, or MSG")
        else:
            #client
            msg_data = self.input_client_msg.text() if msg_data == "" else msg_data
            if msg_data == "":
                QMessageBox.about(self, "Notice", "Please,input MSG")
            else:
                who = str(self.th_client.client_s.getsockname()[0])
                who += ":"
                who += str(self.th_client.client_s.getsockname()[1])
                self.th_server.send_msg(self.input_client_msg.text(), who)
                self.input_client_msg.setText("")
                print(str(msg_data) + " sending msg from clinet")

    # log server binding thread finished
    def thread_finished(self):
        if self.tab_col.currentIndex() == 1:
            self.msg_all_client.append("Stopped Client.......ok")
        else:
            self.msg_all_server.append("Stopped Server.......ok")
        print("thread finished & memory free ok")

    # client new
    def client_new(self, client_str):
        if self.th_client.run_bool: #클라이언트가 동작중일 경우 서버쪽에도 갱신
            self.msg_update_client(client_str+"....connected!")
        if self.th_server.run_bool: #서버가 동작중일 경우 서버쪽에도 갱신
            self.msg_update_server(client_str+"....connected!")
            self.list_clients.addItem(str(client_str))

    # client close
    def client_exit(self, client_str):
        # self.list_clients.takeItem(client_str)
        if self.th_client.run_bool:  # 클라이언트가 동작중일 경우 서버쪽에도 갱신
            self.msg_update_client(client_str + "....disconnected!")
        if self.th_server.run_bool:  # 서버가 동작중일 경우 서버쪽에도 갱신
            self.msg_update_server(client_str + "....disconnected!")

    # msg add server function
    def msg_update_server(self, data):
        self.msg_all_server.append(str(data))

    # msg add client function
    def msg_update_client(self, data):
        self.msg_all_client.append(str(data))

    #run client thread catch msg from client
    def client_thread_new(self, con):
        # add thread object
        client_threads = run_client_bypass() #메세지 바인딩 스레드 생성 및 저장
        client_threads.msg_rebind_sig.connect(self.msg_update_server) #메세지 바인딩시 서버쪽에 갱신
        client_threads.client_exit_sig.connect(self.client_new) # 연결 종료시 서버쪽에 갱신
        self.thread.append(client_threads) #클라이언트 메세지 대기 스레드 배열에 저장
        self.thread[len(self.thread) - 1].index = (len(self.thread) - 1) #연결 소켓 인덱스 스레드 변수에 저장
        self.thread[len(self.thread) - 1].con = con #연결 소켓 스레드 소켓에 저장
        self.thread[len(self.thread)-1].start() #클라이언트로부터 메세지 수신 대기 스레드 시작

    # add client socket, using server send_msg func
    def add_client_only_client_ex(self, client_c):
        if self.th_server.run_bool == False:
            self.th_server.client.append(client_c)

# serverside thread
class run_server_thread(QThread):
    client_thread_exit_sig = pyqtSignal(int)
    client_thread_new_sig = pyqtSignal(socket) # can return signal parameter socket object
    client_exit_sig = pyqtSignal(str)
    msg_sig = pyqtSignal(str) # 메세지 바인딩 시그널
    client = []

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
                    self.client.append(conn) #클라이언트 추가
                    self.client_thread_new_sig.emit(conn) # 클라이언트 스레드 추가 시그널
                    # can't access ui object, using signal or slot
            pass

    # sending connection for close
    def send_close_connection(self):
        end_s = socket()
        end_s.connect((self.host, int(self.port)))

    # server Notice function
    def send_msg(self, data="", who="", connection = ""):
        connection = connection if connection != "" else self.client
        who = ("Server notice" if who == "" else who)

        if (len(connection) and data):
            for i in range(0, len(connection)):
                if connection[i] != "":
                    try:
                        connection[i].send((who+"|"+str(data)).encode("utf-8"))
                    except:
                        # close connection remove
                        self.client_exit_sig.emit(str(connection[i].getpeername()[0])+":"+str(connection[i].getpeername()[1])) #목록 지우는 시그널
                        self.client.pop(i) #클라이언트 소켓 삭제
                        self.client_thread_exit_sig.emit(i) #클라이어트 스레드 종료
            self.msg_sig.emit(who +" | "+ str(data) + " ==>  broadcast") #메세지 전송 서버쪽에 기록
            return True
        else:
            return False

# client side thread
class run_client_thread(QThread):
    exception_mbox_sig = pyqtSignal(str, int)  # 에외 처리시 메세지 발송
    add_client_con_sig = pyqtSignal(socket) #
    client_sig = pyqtSignal(str) #signal when client connected
    client_get_msg_sig = pyqtSignal(str) #signal when client msg get
    client_exit_sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.run_bool = False
        self.client_s = socket()
        self.host = ""
        self.port = 0

    def run(self):
        try:
            self.client_s.connect((self.host, self.port))
            who = str(self.client_s.getsockname()[0]) + ":" + str(self.client_s.getsockname()[1])
            self.client_sig.emit(who)
            self.add_client_con_sig.emit(self.client_s) #send socket when not run server and only use client tool
            while self.run_bool:
                self.msleep(150) #wait 0.15
                data_recive = self.client_s.recv(1024).decode("utf-8").split("|") # session timeout exit recv method
                if (data_recive[0]):
                    is_me_chk = str(self.client_s.getsockname()[0]) + " : " + str(self.client_s.getsockname()[1])
                    if data_recive[0].replace(" ","") == is_me_chk.replace(" ", ""): #check sender is who?
                        who = "me : "
                    else:
                        who = data_recive[0] + " : "
                    data = str(who) + str(data_recive[1]) #make data uing who and msg
                    self.client_get_msg_sig.emit(data) #send signal when client msg get
        except Exception as err:
            if self.run_bool:
                print("socket creation failed with error %s" % (err)) #no working serve
                self.exception_mbox_sig.emit(str(err), 1)

# client_msg bypass thread
class run_client_bypass(QThread):
    msg_rebind_sig = pyqtSignal(str)
    client_exit_sig = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.run_bool_bypass = True
        self.con = socket()
        self.index = 0

    def run(self):
        try:
            while self.run_bool_bypass:
                self.msleep(150)
                data = self.con.recv(1024).decode("utf-8")
                if data:
                    server = run_server_thread()
                    who = str(self.con.getpeername()[0])+":"+str(self.con.getpeername()[1])
                    check_data = data.split("|")
                    data = check_data[1] if len(check_data) == 2 else check_data[0]
                    if len(server.client) == 1:
                        data = "No client"
                        who = ""
                    server.send_msg(data, who)
                    self.msg_rebind_sig.emit("rebinding : " + who+" ==> "+data)
        except Exception as error:
            print(str(error))
        who = str(self.con.getpeername()[0]) + ":" + str(self.con.getpeername()[1])
        self.client_exit_sig.emit(who)
        print("thread exit client side close")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()