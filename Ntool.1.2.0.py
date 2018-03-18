# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5 import uic
from socket import *
from netaddr import IPAddress
import sys, os, wmi, ipaddress
import server as s
import client as c
import requests, ssl
form_class = uic.loadUiType("socket_ui.ui")[0]

class MyWindow(QMainWindow, form_class):

# chatting side

    host = "127.0.0.1"
    port = 4444
    client_c = {}

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.th_client = c.client_thread()
        self.th_server = s.server_thread()
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

        ################################################## http side
        self.input_url.returnPressed.connect(self.http_send)
        self.send_btn.clicked.connect(self.http_send)
        self.input_url.setText("google.com")
        self.http_req.setPlainText(
            str(self.send_type.currentText())
            + " / " + str(self.http_type.currentText()) + "\r\nhost: " + str(self.input_url.text()) + "\r\n\r\n"
        )
        self.send_type.currentIndexChanged.connect(self.http_req_update)
        self.http_type.currentIndexChanged.connect(self.http_req_update)
        self.input_url.textChanged.connect(self.http_req_update)
        self.chk_http2_btn.clicked.connect(self.http2_chk)
        ################################################## arp side
        self.scan_btn.clicked.connect(self.test)

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
        if ex_type:
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
            if data != "":
                if self.th_server.run_bool and len(self.client_c) > 0:  # 서버가 동작중인가 확인
                    data = "Notice | " + data  # 공지 누가 전송하는지를 저장
                    self.send_msg_all(data)  # 공지
                    self.input_server_msg.setText("")  # 메세지 보내고 초기화
                else:
                    self.msg_box("Notice", "No, server run or client is Zero")  # 서버가 일하지 않을 때
            else:
                self.msg_box()  # 공백일때
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
    def send_msg_all(self, data=""):
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

    def client_manager(self, type=1, connection=""):
        if type:  # add connection
            who = connection.getpeername()[0] + ":" + str(connection.getpeername()[1])
            print(who)
            self.list_update(1, who)
            th_bypass = s.by_pass_msg_thread()
            th_bypass.run_bool = True
            th_bypass.con = connection
            self.client_c.update({who: {"thread": th_bypass}})
            self.client_c[who]['thread'].msg_rebind_sig.connect(self.send_msg_all)
            self.client_c[who]['thread'].client_exit_sig.connect(self.list_update)
            self.client_c[who]['thread'].start()
            flag = "FLAG|refresh|" + str(len(self.client_c))
            self.send_msg_all(flag)
        else:  # del connection
            flag = "FLAG|exit"
            if str(connection) == "all":
                if len(self.client_c) > 0:
                    for client in self.client_c:
                        try:
                            self.msg_all_server.append("disconnection | " + str(client))
                            self.client_c[client]['thread'].run_bool = False
                            self.client_c[client]['thread'].con.send(flag.encode("UTF-8"))
                        except Exception as e:
                            print(str(e))
                    self.client_c = []
                    self.list_clients.clear()
                self.th_server.s.close()
            else:
                who = connection
                self.list_update(0, who)  # 리스트 제거 및 연경 종료 표시
                try:
                    self.client_c[who]['thread'].con.send(flag)
                finally:
                    if self.th_server.run_bool:
                        self.client_c.pop(who)
                        print("remove disconnection client")
        print(flag)

    # common msg func
    def msg_box(self, title="Notice", msg="No, blank!!!", kill_type=""):
        if "Error" in msg:
            limit = msg.rindex("]") + 1
            title = msg[:limit]
            msg = msg[limit + 1:]
        QMessageBox.about(self, title, msg)
        print("msg box | " + title + ":" + msg)
        if kill_type == "server":
            self.run_server_ex(0)
        if kill_type == "client":
            self.run_client_ex(0)

    def list_update(self, type=1, who=""):
        if who != "":
            if type:
                self.list_clients.addItem(who)
                self.msg_all_server.append("connection | " + who)
            else:
                if self.th_server.run_bool:
                    self.client_c.pop(who)
                    self.msg_all_server.append("disconnection | " + who)
                    self.list_clients.clear()
                    for who in self.client_c:
                        self.list_clients.addItem(who)
            self.send_msg_all("FLAG|refresh|" + str(len(self.client_c)))
        else:
            self.msg_box()

    #http side
    def http2_chk(self):
        rs = ""
        self.http_res.setPlainText("")
        domain = self.input_url.text()
        headers = {'Accept': '*/*', 'user-agent': 'h2-check/1.0.1', 'Connection': 'Upgrade, HTTP2-Settings',
                   'Upgrade': 'h2c', 'HTTP2-Settings': '<base64url encoding of HTTP/2 SETTINGS payload>'}
        # send GET request with the upgrade headers
        r = requests.get('http://' + domain, headers=headers, allow_redirects=True)
        # check the status code if it is 101 Switching Protocols based on http1.1 first
        if r.status_code == 101:
            rs += "[+] "+domain+' HTTP Support\n'
        # the status code must be 200 ok or something else based on http1.1 if the server does not support http/2
        else:
            rs += "[-] "+domain+' HTTP Not Support\n'

        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['h2', 'spdy/3', 'http/1.1'])

        conn = ctx.wrap_socket(
            socket(AF_INET, SOCK_STREAM), server_hostname=domain)
        conn.connect((domain, 443))

        # check the selected protocol by the server

        if conn.selected_alpn_protocol() == 'h2':
            rs+= '[+]'+domain+' HTTPS Support\n'
        else:
            rs+= '[-]'+domain+' HTTPS Not Support\n'
        self.http_res.setPlainText(rs)

    def http_req_update(self):
        self.http_req.setPlainText(
            str(self.send_type.currentText())
            + " / "+str(self.http_type.currentText())+"\r\nhost: " + str(self.input_url.text()) + "\r\n\r\n"
        )

    def http_send(self):
        try:
            # url = self.input_url.text()
            url = self.input_url.text()

            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(
                create_connection((url, 443)),
                server_hostname=url
            )

            if str(self.send_type.currentText()) == "GET":
                sock.sendall(bytes(self.http_req.toPlainText().encode()))
            else:
                sock.sendall(bytes(self.http_req.toPlainText().encode()))
            self.http_res.setPlainText(self.recvall(sock))
        except Exception as e:
            print(e)

    def recvall(self, sock):
        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
        return data.decode()

    #arp side


    def test(self):
        gateway = None
        subnet = None
        cmd_rs = str(os.popen("ipconfig", "r", -1).read())


        for nic in wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=1):
            if nic.DHCPServer in cmd_rs:
                ip = nic.IPAddress[0]
                gateway = nic.DHCPServer


        ip_s = ip.split(".")
        sub_s = gateway.split(".")

        if ip_s[0] == sub_s[0] and ip_s[1] == sub_s[1] and ip_s[2] == sub_s[2]:

            self.s_ip_1.setText(ip_s[0])

            self.s_ip_2.setText(ip_s[1])

            self.s_ip_3.setText(ip_s[2])
            self.s_ip_4.setText("0")

            self.e_ip_1.setText(ip_s[0])
            self.e_ip_2.setText(ip_s[1])
            self.e_ip_3.setText(ip_s[2])
            self.e_ip_4.setText("255")

            self.s_ip_1.setEnabled(False)
            self.s_ip_2.setEnabled(False)
            self.s_ip_3.setEnabled(False)
            self.s_ip_4.setEnabled(False)
            self.e_ip_1.setEnabled(False)
            self.e_ip_2.setEnabled(False)
            self.e_ip_3.setEnabled(False)
            self.e_ip_4.setEnabled(False)

            ip_ = str(ip_s[0]) + "." + str(ip_s[1]) + "." + str(ip_s[2]) + "."

            for last_ip in range(0, 255):
                ip = ip_+str(last_ip)
                print(ip)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()