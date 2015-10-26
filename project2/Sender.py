import sys
import socket
import random
import getopt
import time

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    WINDOW = 7
    TIMEOUT = 0.5 
    SEGMENT_SIZE = 1458 

    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug
        self.base = 0
        self.window = {}
        self.seqno = 0 
        self.seqbase = self.seqno + 1
        self.seqmax = self.seqno + Sender.WINDOW + 1
        self.seqfinack = -1

    # Main sending loop.
    def start(self):
        """
        Sending loop for the Sender.
        Read from the file and place it into the buffer. 
        """
        self.send_syn()
        self.prepare_window()
        self.send_window()
        while True:
            if len(self.window) == 0:
                return
            response = self.receive(Sender.TIMEOUT)
            if response and Checksum.validate_checksum(response):
                print "Sender.py: received ", response
                msg_type, seqno, data, checksum = self.split_packet(response)
                seqno = int(seqno)
                if msg_type == 'ack' and seqno > self.seqbase:
                    for i in range(self.seqbase, seqno):
                        del self.window[i]
                    self.seqmax += seqno - self.seqbase
                    self.seqbase = seqno
                    self.prepare_window()
                    self.send_window()
            else:
                self.send_window()
           

    def prepare_window(self):
        for i in range(self.seqbase, self.seqmax):
            if self.window.get(i):
                continue
            else:
                data = self.infile.read(Sender.SEGMENT_SIZE)
                if len(data) != Sender.SEGMENT_SIZE and data != '':
                    packet = self.make_packet('fin', i, data)
                    self.seqfinack = i + 1
                elif data:
                    packet = self.make_packet('dat', i , data)
                else:
                    continue
                self.window[i] = packet
        return 
    
    def send_window(self):
        for i in range(self.seqbase, self.seqmax):
            if self.window.get(i):
                self.send(self.window[i])

    def send_dat(self, data):
        """
        Handles sending of dat packets. Windowing and timeouts are delegated here 
        as well.
        """
        self.seqno += 1
        packet = self.make_packet('dat', self.seqno, data) 
        return self._send_packet(packet)
            
           
    def send_syn(self):
        """
        Creates a new syn packet and then sends it to the sender function.
        """
        packet = self.make_packet('syn', self.seqno, '')
        return self._send_packet(packet)

    def send_fin(self, data):
        """
        Creates a fin packet from the last data in the buffer and sends it to 
        the sender function.
        """
        self.seqno += 1
        packet = self.make_packet('fin', self.seqno, data) 
        return self._send_packet(packet)


    def get_file_segment(self):
        """
        Reads next file segment from self.infile
        """
        return self.infile.read(Sender.SEGMENT_SIZE) 

    def _send_packet(self, packet):
        """
        Handles sending of syn and fin packets. 
        """
        response = None
        while not response:
            self.send(packet)
            response = self.receive(timeout=self.TIMEOUT)
        return response
        
'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest,port,filename,debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
