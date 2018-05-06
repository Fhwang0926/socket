import re, os, locale, socket, queue, time
import concurrent.futures
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from scapy.all import srp, send, Ether, ARP
import netaddr
from multiprocessing import Process
from struct import pack
from uuid import getnode as get_mac



class ping(QThread):
    arp_find_sig = pyqtSignal(int)
    arp_ex_sig = pyqtSignal(int)
    def __init__(self, parent=None):
        self.Active_Q = queue.Queue(256)

        super().__init__()
        self.main = parent
        self.ip_list = ""
        self.ip_ok = []
        self.progressbar_value = 256*2
        self.ping_queue = queue.Queue()

    def set_ip_list(self, ip_list):
        self.ip_list = ip_list

    def run(self):
        try:
            os.system("echo New File > ./\\list.txt") #init
            self.arp_ex_sig.emit(0)
            for ip in self.ip_list:
                response = os.system("ping -w 1 -n 2 " + ip + " >> .\\list.txt")

                if response == 0:
                    rs = 1
                    self.progressbar_value += rs
                    self.ip_ok.append(ip)
                else:
                    rs = 0
                    self.progressbar_value += 2
                print(ip)
                self.arp_find_sig.emit(rs)
            self.arp_ex_sig.emit(1)
        except Exception as e:
            rs.update({"rs": "Error"})
            rs.update({"e": "Need check arp_thread"})

    def read_list(self):
        rs = {"rs": True, "e": "","ip": "", "time": 0, "ttl": 0, "average": 0, "loss": 0}
        try:
            data = open("list.txt").read()
            system_info = locale.getdefaultlocale()
            for index in range(0, len(self.ip_ok)-1):
                print("index : "+str(index))
                ip = self.ip_ok[index]

                if "ko" in system_info[0]:

                    time = int(re.findall(r"시간=(\d+)", data)[index])
                    ttl = int(re.findall(r"TTL=(\d+)", data)[index])
                    average = int(re.findall(r"평균 = (\d+)", data)[index])
                    loss = int(re.findall(r"손실 = (\d+)", data)[index])

                else:
                    time = int(re.findall(r"Time=(\d+)", data)[index])
                    ttl = int(re.findall(r"TTL=(\d+)", data)[index])
                    average = int(re.findall(r"Average = (\d+)", data)[index])
                    loss = int(re.findall(r"Lost = (\d+)", data)[index])
                self.arp_do(ip)
                rs.update({"ip":ip,"time": time, "ttl": ttl, "average": average, "loss": loss, "os": self.chk_ttl(ttl), "mac": "00:00:00:00:00:00"})
                print(rs)
                self.ip_list.append(rs)
            # self.arp_do(self.ip_list)
        except Exception as e:
            rs.update({"rs": "Error"})
            rs.update({"e": e})
            print(rs)
            print("WTF")

    def addQ(self, queue, data):
        return queue.put(data)

    def chk_ttl(self, ttl):
        try:
            mapping = {
                "255": "Stratus",
                "64": "Linux",
                "255": "Linux",
                "32": "Windows",
                "128": "Windows",
                "256": "Cisco",
            }
            rs = mapping[str(ttl)]
        except:
            rs = "????"

        return rs

class arp_process(Process):
    def __init__(self):
        pass
class arp_thread_pool:

    def __init__(self, ThreadCount, ip_q):
        self.state = False
        self.result_q = queue.Queue()
        self.th_list = []
        self.threadPool = ThreadCount-1
        print(self.threadPool)
        self.ip_queue = ip_q
        self.init()
        print("init complete")

    def init(self):
        try:
            for th_index in range(0, self.threadPool):
                self.th_list.append(arp_pro(th_index))
                self.th_list[th_index].rs_sig.connect(self.push_thread)
                self.th_list[th_index].set_ip(self.chk_and_return_ip())
        except Exception as e:
            print(e)
        pass

    def th_all_start(self):
        for th in self.th_list:
            th.set_runbool(True)
            th.start()
    def th_select_start(self, index):
        self.th_list[index].set_index(index)
        self.th_list[index].set_ip(self.chk_and_return_ip())
        self.th_list[index].set_runbool(True)
        self.th_list[index].start()

    def run(self, index = -1):
        if index == -1:
            self.th_all_start()
        else:
            self.th_select_start(index)
    def th_all_wait(self):
        for th in self.th_list:
            try:
                th.wait()
            except:
                print("was close th")
    def push_thread(self, index, data):
        print("[+]", index, data)
        self.result_q.put(data)
        if self.state == False:
            self.th_list[index].set_runbool(False)
            self.th_list[index].set_index(index)
            self.th_list[index].set_ip(self.chk_and_return_ip())
            self.th_list[index].start()

    def chk_and_return_ip(self):
        if not self.ip_queue.empty():
            return self.ip_queue.get()
        else:
            self.state = True
            print("wait all")
            # self.th_all_wait()




class arp_pro(QThread):
    rs_sig = pyqtSignal(int, str)
    import random
    def __init__(self, index):
        super().__init__()
        self.ip = ""
        self.index = index
        self.runbool = False
        self.delay = self.random.Random().randint(0, 1000)

    def set_runbool(self, bool):
        self.runbool = bool

    def set_index(self, index):
        self.index = index

    def set_ip(self, ip):
        self.ip = ip

    def run(self):

        try:
            if self.ip != None:
                # self.usleep(self.delay)
                start = time.time()
                snd, rcv = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(self.ip)), timeout=1)
                mac = snd.res[0][1].src
                end = time.time()
                print("[+]", self.ip, mac, end-start)
                # self.rs_sig.emit(self.index, "|".join([str(mac), str(self.ip), str(end-start)[:4]]))
        except Exception as e:
            # print(e)
            print("[-]", self.ip)

class test(QThread):

    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        pass
    def run(self):
        # QThread.time(1)
        print(self.ip, "is run")


if __name__ == '__main__':
    import queue

    ip_q = queue.Queue()
    ip_ = "192.168.0."
    for last_ip in range(50, 60):
        ip = ip_ + str(last_ip)
        ip_q.put(ip)
        print(ip)
    arp_pro = arp_thread_pool(10, ip_q)
    arp_pro.run()