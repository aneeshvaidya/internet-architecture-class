import sys
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
    TIMEOUT = 500

    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug

    # Main sending loop.
    def start(self):

        
        data = self.filename.read(1472)
      pass

    def _send_syn(self):
        self.seqno = random.randint(0, sys.maxint)
        packet = self.make_packet('syn', self.seqno)
        self.send(packet)

    def _send_fin(self):
        packet = self.make_packet('fin', self.seqno + 1)
        self.send(packet)

    def _send_ack(self):
        packet = self.make_packet('ack', self.seqno + 1)
        self.send(packet)

    def _send_data(self, data):
        packet = self.make_packet('dat', self.seqno, data)
        self.send(packet)
        
    def set_connection(self):
        seqnumber = random.randint(0, sys.maxint)
        packet = self.make_packet('syn', seqnumber)
        now = time.time()
        self.send(packet)
        try:
            message, address = self.receive()
            msg_type, seqno, data, checksum = self._split_message(message)
            try:
                seqno = int(seqno)
            except:
                raise ValueError
            if debug:
                print "Sender.py: received %s|%d|%s|%s" % (msg_type, seqno, data[:5], checksum)
            if Checksum.validate_checksum(message) and msg_type == 'ack' and secno = secnumber+1:
                self.secno = secnumber+1
                return True
                
            elif self.debug:
                print "Receiver.py: checksum failed: %s|%d|%s|%s" % (msg_type, seqno, data[:5], checksum)

            if time.time() - now > self.TIMEOUT:
                return False
                
        except socket.timeout:
            self._cleanup()
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
