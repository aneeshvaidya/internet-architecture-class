from BasicTest import *

class FastRetransmitTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            pack = p.full_packet.split('|')
            if int(pack[1]) > 1:
                if int(pack[1]) == 2:
                    self.drops += 1
            else:
                self.forwarder.out_queue.append(p)
        self.forwarder.in_queue = []
