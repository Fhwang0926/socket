# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'socket_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import threading
from socket import *
from multiprocessing import Process

class Ui_MainWindow(object):

    global mode
    global s
    global host
    global port
    global client
    global data
    global client
    global client_thread
    global server

    client = []
    client_thread = []




    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 817)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(20)
        self.formLayout.setObjectName("formLayout")
        self.l_host = QtWidgets.QLabel(self.centralwidget)
        self.l_host.setObjectName("l_host")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.l_host)
        self.input_host = QtWidgets.QLineEdit(self.centralwidget)
        self.input_host.setText("")
        self.input_host.setObjectName("input_host")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.input_host)
        self.l_port = QtWidgets.QLabel(self.centralwidget)
        self.l_port.setObjectName("l_port")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.l_port)
        self.input_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_port.setText("")
        self.input_port.setObjectName("input_port")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.input_port)
        self.l_conn = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.l_conn.setFont(font)
        self.l_conn.setObjectName("l_conn")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.l_conn)
        self.label_status = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_status.setFont(font)
        self.label_status.setObjectName("label_status")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_status)
        self.l_type = QtWidgets.QLabel(self.centralwidget)
        self.l_type.setObjectName("l_type")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.l_type)
        self.label_type = QtWidgets.QLabel(self.centralwidget)
        self.label_type.setObjectName("label_type")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_type)
        self.verticalLayout.addLayout(self.formLayout)
        self.btn_conn = QtWidgets.QPushButton(self.centralwidget)
        self.btn_conn.setObjectName("btn_conn")
        self.verticalLayout.addWidget(self.btn_conn)
        self.msg_all = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.msg_all.setObjectName("msg_all")
        # self.msg_all.setReadOnly(True)
        self.verticalLayout.addWidget(self.msg_all)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.input_msg = QtWidgets.QLineEdit(self.centralwidget)
        self.input_msg.setObjectName("input_msg")
        self.horizontalLayout_2.addWidget(self.input_msg)
        self.send_btn = QtWidgets.QPushButton(self.centralwidget)
        self.send_btn.setObjectName("send_btn")
        self.horizontalLayout_2.addWidget(self.send_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menuhttp = QtWidgets.QMenu(self.menubar)
        self.menuhttp.setObjectName("menuhttp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionserver = QtWidgets.QAction(MainWindow)
        self.actionserver.setCheckable(True)
        self.actionserver.setChecked(True)
        self.actionserver.setObjectName("actionserver")
        self.actionclient = QtWidgets.QAction(MainWindow)
        self.actionclient.setCheckable(True)
        self.actionclient.setObjectName("actionclient")
        self.actionarp = QtWidgets.QAction(MainWindow)
        self.actionarp.setObjectName("actionarp")
        self.actionip = QtWidgets.QAction(MainWindow)
        self.actionip.setObjectName("actionip")
        self.actionhttp = QtWidgets.QAction(MainWindow)
        self.actionhttp.setObjectName("actionhttp")
        self.menu.addAction(self.actionserver)
        self.menu.addAction(self.actionclient)
        self.menuhttp.addAction(self.actionarp)
        self.menuhttp.addAction(self.actionip)
        self.menuhttp.addAction(self.actionhttp)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menuhttp.menuAction())

        self.retranslateUi(MainWindow) #set init setting or data

        # self.send_btn.clicked.connect(MainWindow.send)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    #set
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SS[Sunday_Study] Networking Tool"))
        self.l_host.setText(_translate("MainWindow", "Host"))
        self.input_host.setPlaceholderText(_translate("MainWindow", "ex) 127.0.0.1 or domain"))
        self.l_port.setText(_translate("MainWindow", "Port"))
        self.input_port.setPlaceholderText(_translate("MainWindow", "ex) 8080 / default 7878"))
        self.l_conn.setText(_translate("MainWindow", "Status"))
        self.label_status.setText(_translate("MainWindow", "stop"))
        self.l_type.setText(_translate("MainWindow", "Type"))
        self.label_type.setText(_translate("MainWindow", "Server"))
        self.btn_conn.setText(_translate("MainWindow", "Start"))
        self.label_4.setText(_translate("MainWindow", "msg"))
        self.send_btn.setText(_translate("MainWindow", "Send"))
        self.menu.setTitle(_translate("MainWindow", "socket"))
        self.menuhttp.setTitle(_translate("MainWindow", "send packet"))
        self.actionserver.setText(_translate("MainWindow", "Server side"))
        self.actionclient.setText(_translate("MainWindow", "Client side"))
        self.actionarp.setText(_translate("MainWindow", "arp"))
        self.actionip.setText(_translate("MainWindow", "ip"))
        self.actionhttp.setText(_translate("MainWindow", "http"))
        self.btn_conn.clicked.connect(self.conn)
        self.actionclient.triggered.connect(self.set_client)
        self.actionserver.triggered.connect(self.set_server)


    def conn(self):
        if self.label_status.text() != "running":

            if self.label_type.text() == "Server":
                self.msg_all.setPlainText("Start "+str(self.label_type.text()))
                self.label_status.setText("running")
                self.btn_conn.setText("Server stop")
                # self.server_mode()
                self.server = threading.Thread(target=self.server_mode)
                self.server.start()

            else:
                print("clint")
        else:
            self.server_exit()
            self.server.stop()
            self.server.join()
            self.btn_conn.setText("Server start")
            self.label_status.setText("stop")




    def socket_common(self):
        print("asdasd")
    def set_server(self):
        self.actionclient.setChecked(False)
        self.actionserver.setChecked(True)
        self.label_type.setText("Server")
        self.label_4.setText("Notice")
        self.btn_conn.setText("Server start")


    def set_client(self):
        self.actionclient.setChecked(True)
        self.actionserver.setChecked(False)
        self.label_type.setText("Client")
        self.label_4.setText("msg")
        self.btn_conn.setText("Start connect")

    # msg data binding
    def recive(self, conn):
        while True:
            data = conn.recv(1024).decode("utf-8")
            if (data):
                self.send(data)

    def notice_server(self):
        while 1:
            if mode:
                notice = input("Notice : ")
                if (notice):
                    for client_c in client:
                        who = client_c.getpeername()
                        client_c.send(("server : " + str(port) + "`" + str(notice)).encode("utf-8"))
                    print("send notice")

    # msg sending
    def send(self, data):
        if (data):
            for client_c in client:
                who = client_c.getpeername()
                who_details = str(who[0]) + ":" + str(who[1])
                client_c.send((who_details + "`" + str(data)).encode("utf-8"))
                self.msg_all.appendPlainText(who_details + " <==== " + str(data))
            mode = 1

    def server_mode(self):

        host = self.input_host.text() if self.input_host.text() else "127.0.0.1"; self.input_host.setText("127.0.0.1")

        port = self.input_port.text() if self.input_port.text() else 7878; self.input_port.setText("7878")
        self.msg_all.appendPlainText("staring..... " + host + " : " + str(port))
        s = socket()  # save connection object

        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # create socket
        s.bind((host, port))
        # can client connection 5 client
        s.listen(5)


        while True:
            print("listen client start")
            conn, addr = s.accept()
            client.append(conn)
            sub = threading.Thread(target=self.recive, args=(conn,))
            sub.start()
            client_thread.append(sub)
            # index = len(client)
            self.msg_all.appendPlainText("connect....."+str(addr[0])+" : "+str(addr[1]))
            self.btn_conn.setText("Server stop | connection : "+str(len(client)))

    def server_exit(self):
        for client_c in self.client:
            try:
                client_c.shotdown()
            finally:
                print("close all connection")
        for thread in self.client_thread:
            try:
                thread.stop()
                thread.quit()
                thread.join()
            finally:
                print("finish all process")
        print("print end application")



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

