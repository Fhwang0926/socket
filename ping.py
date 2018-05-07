#!/usr/bin/env python3
# https://gist.github.com/chidea/955cea841e5c76a7e5ee8aa02234409d
# http://dk0d.blogspot.kr/2016/07/code-for-sending-arp-request-with-raw.html
import time
import socket
import struct
import select
import random
import asyncore
from PyQt5.QtCore import *

class PING(QThread):


    def __init__(self):
        self.VERBOSE = False

        self.ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.

        self.ICMP_CODE = socket.getprotobyname('icmp')
        self.ERROR_DESCR = {
            1: ' - Note that ICMP messages can only be '
               'sent from processes running as root.',
            10013: ' - Note that ICMP messages can only be sent by'
                   ' users or processes with administrator rights.'
        }

        # self.__all__ = ['create_packet', 'do_one', 'ping', 'PingQuery', 'multi_ping_query']
        # self.__all__ = ['create_packet', 'do_one', 'ping']


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


    def do_one(self, dest_addr, timeout=1):
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
        delay = self.receive_ping(my_socket, packet_id, time.time(), timeout)
        my_socket.close()
        return delay


    def receive_ping(self, my_socket, packet_id, time_sent, timeout):
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
            icmp_header = rec_packet[20:28]
            type, code, checksum, p_id, sequence = struct.unpack(
                'bbHHh', icmp_header)
            if p_id == packet_id:
                return time_received - time_sent
            time_left -= time_received - time_sent
            if time_left <= 0:
                return


    def ping(self, dest_addr, timeout=2, count=2):
        avg = 0
        suc = 0

        for i in range(count):
            if self.VERBOSE: print('ping {}...'.format(dest_addr))
            delay = self.do_one(dest_addr, timeout)
            if delay == None:
                if self.VERBOSE: print('failed. (Timeout within {} seconds.)'.format(timeout))
            else:
                delay = round(delay * 1000.0, 4)
                avg += delay
                suc += 1
                if self.VERBOSE: print('get ping in {} milliseconds.'.format(delay))
        return (avg / suc) if avg else None


# class PingQuery(asyncore.dispatcher):
#     def __init__(self, host, p_id, timeout=0.5, ignore_errors=False):
#         asyncore.dispatcher.__init__(self)
#         try:
#             self.create_socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
#         except socket.error as e:
#             if e.errno in ERROR_DESCR:
#                 # Operation not permitted
#                 raise socket.error(''.join((e.args[1], ERROR_DESCR[e.errno])))
#             raise  # raise the original error
#         self.time_received = 0
#         self.time_sent = 0
#         self.timeout = timeout
#         # Maximum for an unsigned short int c object counts to 65535 so
#         # we have to sure that our packet id is not greater than that.
#         self.packet_id = int((id(timeout) / p_id) % 65535)
#         self.host = host
#         self.packet = create_packet(self.packet_id)
#         if ignore_errors:
#             # If it does not care whether an error occured or not.
#             self.handle_error = self.do_not_handle_errors
#             self.handle_expt = self.do_not_handle_errors
#
#     def writable(self):
#         return self.time_sent == 0
#
#     def handle_write(self):
#         self.time_sent = time.time()
#         while self.packet:
#             # The icmp protocol does not use a port, but the function
#             # below expects it, so we just give it a dummy port.
#             sent = self.sendto(self.packet, (self.host, 1))
#             self.packet = self.packet[sent:]
#
#     def readable(self):
#         # As long as we did not sent anything, the channel has to be left open.
#         if (not self.writable()
#                 # Once we sent something, we should periodically check if the reply
#                 # timed out.
#                 and self.timeout < (time.time() - self.time_sent)):
#             self.close()
#             return False
#         # If the channel should not be closed, we do not want to read something
#         # until we did not sent anything.
#         return not self.writable()
#
#     def handle_read(self):
#         read_time = time.time()
#         packet, addr = self.recvfrom(1024)
#         header = packet[20:28]
#         type, code, checksum, p_id, sequence = struct.unpack("bbHHh", header)
#         if p_id == self.packet_id:
#             # This comparison is necessary because winsocks do not only get
#             # the replies for their own sent packets.
#             self.time_received = read_time
#             self.close()
#
#     def get_result(self):
#         """Return the ping delay if possible, otherwise None."""
#         if self.time_received > 0:
#             return self.time_received - self.time_sent
#
#     def get_host(self):
#         """Return the host where to the request has or should been sent."""
#         return self.host
#
#     def do_not_handle_errors(self):
#         # Just a dummy handler to stop traceback printing, if desired.
#         pass
#
#     def create_socket(self, family, type, proto):
#         # Overwritten, because the original does not support the "proto" arg.
#         sock = socket.socket(family, type, proto)
#         sock.setblocking(0)
#         self.set_socket(sock)
#         # Part of the original but is not used. (at least at python 2.7)
#         # Copied for possible compatiblity reasons.
#         self.family_and_type = family, type
#
#     # If the following methods would not be there, we would see some very
#     # "useful" warnings from asyncore, maybe. But we do not want to, or do we?
#     def handle_connect(self):
#         pass
#
#     def handle_accept(self):
#         pass
#
#     def handle_close(self):
#         self.close()


# def multi_ping_query(hosts, timeout=1, step=512, ignore_errors=False):
#     results, host_list, id = {}, [], 0
#     for host in hosts:
#         try:
#             host_list.append(socket.gethostbyname(host))
#         except socket.gaierror:
#             results[host] = None
#     while host_list:
#         sock_list = []
#         for ip in host_list[:step]:  # select supports only a max of 512
#             id += 1
#             sock_list.append(PingQuery(ip, id, timeout, ignore_errors))
#             host_list.remove(ip)
#         # Remember to use a timeout here. The risk to get an infinite loop
#         # is high, because noone can guarantee that each host will reply!
#         asyncore.loop(timeout)
#         for sock in sock_list:
#             results[sock.get_host()] = sock.get_result()
#     return results


if __name__ == '__main__':

    # Testing
    # ping('172.30.1.254');
    # print('')
    # start = time.time()
    # for x in range(100):
    #   ping('google.com');
    # end = time.time()
    # print("time", end - start)

    # host_list = ['google.com', '127.0.0.1']
    # for host, ping in multi_ping_query(host_list).items():
    #     print(host, '=', ping)

    tmp = PING()
    tmp.VERBOSE = True
    tmp.ping('172.30.1.254');
    start = time.time()
    for x in range(10):
        tmp.ping('google.com');
    end = time.time()
    print("end:", end-start)