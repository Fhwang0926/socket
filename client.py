from socket import *
from PyQt5.QtCore import *

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