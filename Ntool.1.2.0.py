# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5 import uic
from socket import *
import sys, os, wmi, arp, requests, json, ssl

import server as s
import client as c
import concurrent.futures


from urllib.parse import urlparse
import http.client as http_
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
        self.th_arp_ping = arp.ping()
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
        self.input_url.setText("www.f1security.co.kr")
        self.http_req.setPlainText("GET / HTTP/1.1\r\nhost: " + str(self.input_url.text()) + "\r\n\r\n")
        self.input_url.textChanged.connect(self.http_req_update)
        # self.chk_http2_btn.clicked.connect(self.http2_chk)
        ################################################## arp side
        self.scan_btn.clicked.connect(self.run_arp)
        self.th_arp_ping.arp_find_sig.connect(self.arp_update)
        self.th_arp_ping.arp_ex_sig.connect(self.arp_ex)



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
        try:
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
        except:
            QMessageBox.about(self, title, "Insert Data Cause Broken Working\nPlease Check Insert Data")
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
    def http_req_update(self):
        # url = self.make_full_url(self.input_url.text())
        # self.input_url.seText(url)
        url = self.input_url.text()
        if url:
            url_split = url.split("://")
            url_split_more = url_split[len(url_split)-1].split("/")
            if len(url_split_more) < 2:
                path = "/"
                host = url_split_more[0]
            else:
                path = "".join(url_split_more).replace(url_split_more[0], "/")
                host = url_split_more[0]

            http_req_row = "GET "+path+" HTTP/1.1\r\nhost: " + host + "\r\n\r\n"
            self.http_req.setPlainText(http_req_row)

    def chk_http_type(self, url):
        try:
            http_url = "http://"+self.make_full_url(url)
            try:
                conn = http_.HTTPConnection(http_url)
                conn.request("HEAD", http_url.path)
                if conn.getresponse():
                    return http_url
                else:
                    return "https://"+http_url.split("://")[1]
            except:
                return "https://" + http_url.split("://")[1]
        except:
            return url

    def make_full_url(self, input_):
        if input_:
            if "://" in input_:
                if not("www." in input_):
                    url = "www." + input_.split("://")[1]
                else:
                    url = input_.split("://")[1]
            else:
                if not("www." in input_):
                    url = "www."+input_
        else:
            url = "www.example.com"

        return url


    def http_send(self):
        self.http_res.setPlainText("")
        if self.input_url.text():
            try:
                update_url = self.chk_http_type(self.input_url.text())
                rs_get = requests.get(url=update_url)

                cnt = 0
                self.http_cookies.clearContents()
                self.http_cookies.setRowCount(1)
                for cookie in rs_get.cookies:
                    if self.http_chkb_cookie.isChecked():
                        self.http_cookies.setRowCount(cnt + 1)
                        self.http_cookies.setItem(cnt, 0, QTableWidgetItem(cookie.name))
                        self.http_cookies.setItem(cnt, 1, QTableWidgetItem(cookie.value))
                        print(cnt, cookie.name, cookie.value)
                        cnt += 1
                rs = json.dumps(dict(rs_get.headers), indent=1)

                print_result = ""
                if self.http_chkb_result_headers.isChecked():
                    print_result += str(rs)
                if self.http_chkb_result_body.isChecked():
                    print_result += "\n\n"
                    print_result += str(rs_get.content.decode())
                self.http_res.setPlainText(print_result)
                if self.http_chkb_save_result.isChecked():
                    f = open(self.input_url.text(), "a")
                    f.write(rs)
                    f.write(rs_get.text)
                    f.close()

                print("[+]HTTP OK")
                self.http_log_list.addItem("\t".join([str(rs_get.status_code), update_url]))
            except Exception as e:
                print(e)
                self.msg_box(msg=str(e))

        else:
            self.msg_box()

    #arp side
    def arp_ex(self, rs):
        if rs:
            self.s_ip_1.setEnabled(True)
            self.s_ip_2.setEnabled(True)
            self.s_ip_3.setEnabled(True)
            self.s_ip_4.setEnabled(True)
            self.s_ip_4.setEnabled(True)
            self.e_ip_1.setEnabled(True)
            self.e_ip_2.setEnabled(True)
            self.e_ip_3.setEnabled(True)
            self.e_ip_4.setEnabled(True)
            self.scan_btn.setEnabled(True)
            self.th_arp_ping.read_list()
        else:
            self.s_ip_1.setEnabled(False)
            self.s_ip_2.setEnabled(False)
            self.s_ip_3.setEnabled(False)
            self.s_ip_4.setEnabled(False)
            self.e_ip_1.setEnabled(False)
            self.e_ip_2.setEnabled(False)
            self.e_ip_3.setEnabled(False)
            self.e_ip_4.setEnabled(False)
            self.scan_btn.setEnabled(False)
            self.arp_progressbar.setValue(0)


    def run_arp(self):
        ip_s = gethostbyname(gethostname()).split(".")


        self.s_ip_1.setText(ip_s[0])
        self.s_ip_2.setText(ip_s[1])
        self.s_ip_3.setText(ip_s[2])
        self.s_ip_4.setText("0")

        self.e_ip_1.setText(ip_s[0])
        self.e_ip_2.setText(ip_s[1])
        self.e_ip_3.setText(ip_s[2])
        self.e_ip_4.setText("255")


        ip_ = str(ip_s[0]) + "." + str(ip_s[1]) + "." + str(ip_s[2]) + "."


        try:
            import queue
            ip_q = queue.Queue()

            for last_ip in range(0, 5):
                ip = ip_+str(last_ip)
                ip_q.put(ip)
                tmp = arp.test(ip)
                tmp.start()
                tmp.wait()
            # arp_pro = arp.arp_thread_pool(256, ip_q)
            # arp_pro.run()

            print("chk queue content")

        except Exception as e:
            print(e)
        else:
            print("end")

    def arp_update(self, value):
        self.arp_progressbar.setValue(self.arp_progressbar.value() + 1)


    def arp_update_list(self, data_dic):
        print(data_dic)

    #beta area
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()