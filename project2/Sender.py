import sys
import socket
import random
import getopt
import time
import pdb

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
        self.window = {}
        self.seqno = 0      #initial sequence
        self.seqbase = self.seqno + 1           #window low end      
        self.seqmax = self.seqno + Sender.WINDOW    #window high end
        self.seqfinack = -1     # test
        self.last_ack = 0
        self.dup_acks = 0
        self.updates = []
        if sackMode:
            self.last_sacks = [-1]        
            self.ack_type = 'sack'
        else:
            self.ack_type = 'ack'

    # Main sending loop.
    def start(self):
        """
        Sending loop for the Sender.
        Read from the file and place it into the buffer. 
        """
        self.send_syn()
        self.prepare_window()
        self.send_window()
        self.updates = []
        
        while True:
            if len(self.window) == 0:
                return
            response = self.receive(Sender.TIMEOUT)
            if response and Checksum.validate_checksum(response):
                msg_type, seqno, data, checksum = self.split_packet(response)
                
                if sackMode:
                    seqno, sacks_str = seqno.split(';')
                    #print str(sacks_str.split(','))
                    
                    if sacks_str:
                        sacks = [int(i) for i in sacks_str.split(',')]
                        if sacks[-1] > self.last_sacks[-1]:       # sackMode logic
                            self.last_sacks = sacks                         #

                seqno = int(seqno)                        
                if msg_type == self.ack_type and seqno > self.seqbase:

                    # fast retransmit logic
                    if seqno == self.last_ack:
                        self.dup_acks += 1
                        if self.dup_acks >= 4:
                            if sackMode:
                                self.retransmit_sacks()
                            else:
                                self.send(self.window[self.last_ack])
                            self.dup_acks = 0
                            continue
                            
                    elif seqno > self.last_ack:
                        self.last_ack = seqno
                        
                    # window logic    
                    for i in range(self.seqbase, seqno):
                        del self.window[i]
                    self.seqmax += seqno - self.seqbase
                    self.seqbase = seqno
                    self.prepare_window()
                    self.send_updates()  # MK changes

                # if msg_type == 'sack' and int(seqno) == self.seqfinack:
                    # return
            else:
                if self.sackMode:
                    self.retransmit_sacks()   
                else:
                    self.send_window()                
           

    def prepare_window(self):
        """
        Prepares window from seqbase to seqmax for sending
        """
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
                self.updates.append(i)
        #print "updates " + str(self.updates)
        return 
    
    def send_window(self):
        """
        Sends packets in seqno window, if there is a packet
        for that sequence number
        """
        for i in range(self.seqbase, self.seqmax):
            if self.window.get(i):
                self.send(self.window[i])
                
    def send_updates(self):
        """
        Sends only new packets in seqno window, 
        """
        for s in self.updates:
            self.send(self.window[s])
        self.updates = []
           
    def send_syn(self):
        """
        Creates a new syn packet and then sends it to the sender function.
        """
        packet = self.make_packet('syn', self.seqno, '')
        response = None
        while not response:
            self.send(packet)
            response = self.receive(Sender.TIMEOUT)
        return response
        
    def retransmit_sacks(self):
        """
        Sends only new packets in seqno window, 
        """
        for i in range(self.seqbase, self.seqmax):
            if self.window.get(i) and i not in self.last_sacks:
                self.send(self.window[i])

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
