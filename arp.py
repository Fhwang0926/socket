import time, socket, struct, select, random, concurrent.futures, subprocess, os
from multiprocessing import Process, Queue

#  this module has some bug
# this module can scan C class

class ARP:

    def __init__(self, ip_list=None):
        # ARP Scanner using ICMP Protocol, is ICMP packet row
        os.system("netsh interface ip delete arpcache") ## working only windows OS
        self.ip_list = ip_list
        self.process = None
        self.Q = Queue(256)
        self.runbool = False
        # self.rs_q.maxsize = 256
        self.hosts_info = None # This frist scan result
        self.ping_pro = PING(100)
        self.TempQueue = Queue(256)

    def set_ip_list(self, ip_list):
        self.ip_list = ip_list

    def run(self):
        self.ping_pro.VERBOSE = True
        self.process = Process(target=self.ping_pro.run_th_ping, args=(self.ip_list, self.Q,))
        self.runbool = True
        self.process.start()
        print("start ping Process")

    def wait(self):
        if self.process != None:
            self.process.join()
            self.runbool = False
        else:
            raise()

    def update_mac_info(self, ip_, icmp_q): # src : icmp_q, dist :
        self.hosts_info = self.ping_pro.get_mac_dic(ip_) # this mac & ip address


        while not(icmp_q.empty()):
            item = icmp_q.get()
            if (item["host"] in self.hosts_info.keys()):
                # self.hosts_info[item]['mac'] = item['mac']# mac
                self.hosts_info[item["host"]]["DELAY"] = round(item["data"]["DELAY"], 3)# mac
                self.hosts_info[item["host"]]["TTL"] = item["data"]["TTL"]  # mac
                self.hosts_info[item["host"]]["OS"] = self.ping_pro.chk_ttl(item["data"]["TTL"])
            else:
                self.hosts_info.update({
                    item["host"] :
                        {
                            "MAC": "??-??-??-??-??-??",
                            "TTL" : str(item["data"]["TTL"]),
                            "DELAY" : str(item["data"]["DELAY"]),
                            "OS" : self.ping_pro.chk_ttl(item["data"]["TTL"])}
                })
        else:
            print("{+} Host info")
            print("{+} MAC info")
            print("{+} TTL info")
            print("{+} OS info")



class PING:

    def __init__(self, use_thread_count):
        super().__init__()
        self.VERBOSE = False
        self.use_thread_count = use_thread_count
        self.ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.
        self.ICMP_CODE = socket.getprotobyname('icmp')
        self.ERROR_DESCR = {
            1: ' - Note that ICMP messages can only be '
               'sent from processes running as root.',
            10013: ' - Note that ICMP messages can only be sent by'
                   ' users or processes with administrator rights.'
        }

    def get_rs_list(self):
        return self.rs

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

    def checksum(self, source_string):
        # I'm not too confident that this is right but testing seems to
        # suggest that it gives the same answers as in_cksum in ping.c.
        sum = 0
        l = len(source_string)
        count_to = (l / 2) * 2
        count = 0
        while count < count_to:
            this_val = source_string[count + 1] * 256 + source_string[count]
            sum = sum + this_val
            sum = sum & 0xffffffff  # Necessary?
            count = count + 2
        if count_to < l:
            sum = sum + source_string[l - 1]
            sum = sum & 0xffffffff  # Necessary?
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer


    def create_packet(self, id):
        """Create a new echo request packet based on the given "id"."""
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        header = struct.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0, 0, id, 1)
        data = 192 * b'Q'
        # Calculate the checksum on the data and the dummy header.
        my_checksum = self.checksum(header + data)
        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0,
                             socket.htons(my_checksum), id, 1)
        return header + data


    def do_one(self, dest_addr, timeout=2):
        """
      Sends one ping to the given "dest_addr" which can be an ip or hostname.
      "timeout" can be any integer or float except negatives and zero.
      Returns either the delay (in seconds) or None on timeout and an invalid
      address, respectively.
      """
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.ICMP_CODE)
        except socket.error as e:
            if e.errno in self.ERROR_DESCR:
                # Operation not permitted
                raise socket.error(''.join((e.args[1], self.ERROR_DESCR[e.errno])))
            raise  # raise the original error
        try:
            host = socket.gethostbyname(dest_addr)
        except socket.gaierror:
            return
        # Maximum for an unsigned short int c object counts to 65535 so
        # we have to sure that our packet id is not greater than that.
        packet_id = int((id(timeout) * random.random()) % 65535)
        packet = self.create_packet(packet_id)
        while packet:
            # The icmp protocol does not use a port, but the function
            # below expects it, so we just give it a dummy port.
            sent = my_socket.sendto(packet, (dest_addr, 1))
            packet = packet[sent:]
        delay = self.receive_ping(my_socket, packet_id, time.time(), timeout, dest_addr)
        my_socket.close()
        return delay


    def receive_ping(self, my_socket, packet_id, time_sent, timeout, target):
        # Receive the ping from the socket.
        time_left = timeout

        while True:
            started_select = time.time()
            ready = select.select([my_socket], [], [], time_left)
            how_long_in_select = time.time() - started_select
            if ready[0] == []:  # Timeout
                return
            time_received = time.time()
            rec_packet, addr = my_socket.recvfrom(1024)
            mac = []

            {mac.append("{:0>2}".format(mac_oct)) : mac_oct for mac_oct in rec_packet[6:11]}
            mac = ":".join(mac)
            # ether_header = rec_packet[0:11]
            # preamble, dest_mac, source_mac, type= struct.unpack(
            #     'q', ether_header, )
            print("TTL : ", rec_packet[36], target) # why TTL byte position index 36 ???
            icmp_header = rec_packet[20:28]
            #byte size 1,1,2,2,2
            type, code, checksum, p_id, sequence = struct.unpack(
                'bbHHh', icmp_header)
            if p_id == packet_id:
                return [rec_packet[36], time_received - time_sent, mac]
            time_left -= time_received - time_sent
            if time_left <= 0:
                return
                # mac address using icmp


    def ping(self, dest_addr, timeout=2, count=2):
        avg = 0
        suc = 0
        for i in range(count):
            # if self.VERBOSE: print('ping {}...'.format(dest_addr))

            result = self.do_one(dest_addr, timeout)
            if result != None:
                delay = result[1]
                ttl = result[0]
                mac = result[2]
            else:
                delay = None
                ttl = None
            if delay == None:
                pass
                # if self.VERBOSE: print('failed. (Timeout within {} seconds.)'.format(timeout))
            else:
                delay = round(delay * 1000.0, 4)
                avg += delay
                suc += 1
                # if self.VERBOSE: print('{} to get ping in {} milliseconds. TTL is {}'.format(mac, delay, ttl))
            if dest_addr == "END" : return None
        return { "host" : dest_addr , "data" : {"DELAY" : (avg / suc), "TTL" : ttl}} if avg else None


    def run_th_ping(self, ip_list, rs_q):
        ip_list.append("END")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.use_thread_count) as executor:
            # Start the load operations and mark each future with its URL
            ex_pool = {executor.submit(self.ping, ip) : ip for ip in ip_list}
            for future in concurrent.futures.as_completed(ex_pool):
                rs = future.result()
                if rs != None : rs_q.put(rs)

    def getRemoteHostName(self):
        import python_arptable
        python_arptable.get_arp_table()

    def get_mac_dic(self, ip_):
        try:
            p = subprocess.Popen(["arp", "-a"], stdout=subprocess.PIPE, shell=False)
            (output, err) = p.communicate()
            p.wait()
            rs = output.decode("cp949").split()
            mac_dic = {}
            index = 0
            while True:
                # print(rs[index])
                if ip_ in rs[index] and rs[index + 1] != "---":
                    mac_dic.update({rs[index] : { "MAC" : rs[index + 1]}})
                elif index + 1 == len(rs):
                    break
                index += 1
            # print(mac_dic)
            # print(len(mac_dic))
        except Exception as e:
            return e
        return mac_dic






# class ARP_state_checker(QThread):
#     update_sig = pyqtSignal(str, str, str, str, int)
#     # PC name, ip, MAC, OS, ping Speed
#     def __init__(self, watching_queue):
#         super().__init__()
#         self.watching_queue = watching_queue
#         self.runbool = True
#
#
#     def exit(self, kill):
#         self.runbool = kill
#
#     def run(self):
#         print("run watching queue")
#         count = 0
#         while self.runbool:
#             if not self.watching_queue.empty():
#                 rs = self.watching_queue.get()
#                 if rs == "END" or rs == None:
#                     print("exit code", rs, "total", count)
#                     break
#                 else:
#                     print(rs)
#                     count+=1
#             else:
#                 QThread.usleep(500)
#         print("exit watching thread")

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    ip_s = s.getsockname()[0].split(".")
    ip_s[3] = ""
    ip_ = ".".join(ip_s)


    ip_list = []
    {ip_list.append(ip_ + str(last_ip)): last_ip for last_ip in range(13, 255)}
    arp_pro = ARP(ip_list)
    arp_pro.run()
    arp_pro.wait()
    arp_pro.update_mac_info(ip_, arp_pro.Q)

    # th_ARP_checker = ARP_state_checker(arp_pro.Q)
    # th_ARP_checker.start()
    # th_ARP_checker.wait()

    ## network subnet calc re using network module