import sys
import random
import getopt
import time
import socket
import pdb

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
        

    # Main sending loop.
    def start(self):
        self.set_connection()
        data = self.infile.read(1458)
        while data:
            if len(data) == 1458:
                self.send_data(data)
            else:
                self.send_fin(data)
                return
            data = self.infile.read(1458)
        # while not self.close_connection():

    def send_fin(self, data):
        packet = self.make_packet('fin', self.seqno, data)
        old_seqno = self.seqno
        while self.seqno == old_seqno:
            self.try_data(packet)
        print 'Finished with sec# = ' + str(self.seqno) 

    def send_data(self, data):
        #pdb.set_trace()
        packet = self.make_packet('dat', self.seqno, data)
        old_seqno = self.seqno
        while self.seqno == old_seqno:
            self.try_data(packet)
        print 'sent data with sec# = ' + str(self.seqno)
        
    def set_connection(self):
        seqnumber = 0#random.randint(0, sys.maxint)
        packet = self.make_packet('syn', seqnumber, '')
        self.seqno = seqnumber
        while self.seqno == seqnumber:
            self.try_data(packet)
        print 'connection set with sec# = ' + str(self.seqno)

    def try_data(self, packet):  
        now = time.time()
        self.send(packet)
        try:
            message = self.receive(self.TIMEOUT)
            if message:
                msg_type, seq, data, checksum = self.split_packet(message)
                try:
                    seq = int(seq)
                except:
                    raise ValueError
                if debug:
                    print "Sender.py: received %s|%d|%s|%s" % (msg_type, seq, data[:5], checksum)
                if Checksum.validate_checksum(message) and msg_type == 'ack' and seq == self.seqno +1 and time.time() - now < self.TIMEOUT:
                    self.seqno = seq
                return
                
        except socket.timeout:
            print "timeout"
        except (KeyboardInterrupt, SystemExit):
            exit()
        except ValueError, e:
            if self.debug:
                print "Receiver.py:" + str(e)
            pass # ignore        
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
