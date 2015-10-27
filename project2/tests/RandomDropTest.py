import random

from BasicTest import *

"""
This tests random packet drops. We randomly decide to drop about half of the
packets that go through the forwarder in either direction.

Note that to implement this we just needed to override the handle_packet()
method -- this gives you an example of how to extend the basic test case to
create your own.
"""
class RandomDropTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []

class FirstFinDropTest(BasicTest):
    def handle_packet(self):
        print "SELF.DROPPED:", self.dropped
        for p in self.forwarder.in_queue:
            if p.full_packet[:3] == 'fin' and not self.dropped:
                print "Dropping fin packet"
                self.dropped = True
            else:
                self.forwarder.out_queue.append(p)
        self.forwarder.in_queue = []

