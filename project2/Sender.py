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

    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug
        self.buff = []
        self.d_index = 0

    # Main sending loop.
    def start(self):
        """
        Sending loop for the Sender.
        Read from the file and place it into the buffer. 
        """
        self.initialize_buffer()
        self.send_syn()
        while self.d_index < len(self.buff):
            self.send_data()
            if self.d_index == len(self.buff) - 1:
                print 'Sending fin'
                self.send_fin()
                return
            self.d_index += 1
        return
    
    def initialize_buffer(self):
        """
        Initializes the buffer with data from self.infile
        """
        r = self.infile.read(1458)
        while r:
            self.buff.append(r)
            r = self.infile.read(1458)
        return

    def send_data(self):
        self.seqno += 1
        packet = self.make_packet('dat', self.seqno, self.buff[self.d_index])
        response = None
        while not response:
            self.send(packet)
            response = self.receive(timeout=self.TIMEOUT)
        return response

            
           
    def send_syn(self):
        """
        Handles sending a syn packet, as well as the ACK to follow.
        We set a new sequence number, and create our syn packet. Then we 
        send, and timeout if there's no data response and retry till we
        get an ack.
        """
        self.seqno = random.randint(0, sys.maxint)
        packet = self.make_packet('syn', self.seqno, '')
        data = None
        while not data:
            self.send(packet)
            data = self.receive(timeout=self.TIMEOUT)
        return data 

    def send_fin(self):
        """
        Handles sending of a fin packet, containing the last data
        in the buffer, as well as waiting for ack of the closed
        connection.
        """
        self.seqno += 1
        packet = self.make_packet('fin', self.seqno, self.buff[-1])
        response = None
        while not response:
            self.send(packet)
            response = self.receive(timeout=self.TIMEOUT)
        return



        
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
