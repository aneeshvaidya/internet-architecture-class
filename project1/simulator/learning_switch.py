"""
Your learning switch warm-up exercise for CS-168

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0
"""

import sim.api as api
import sim.basics as basics


class LearningSwitch (api.Entity):
  """
  A learning switch

  Looks at source addresses to learn where endpoints are.  When it doesn't
  know where the destination endpoint is, floods.

  This will surely have problems with topologies that have loops!  If only
  someone would invent a helpful poem for solving that problem...
  """

  def __init__ (self):
    """
    Do some initialization

    You probablty want to do something in this method.
    """
    self.table = {} 


  def handle_link_down (self, port):
    """
    Called when a port goes down (because a link is removed)

    You probably want to remove table entries which are no longer valid here.
    """
    print "Link is down on port ", port
    to_del = [k for k, v in self.table.iteritems() if v == port]
    for key in to_del:
        del self.table[key]
        

  def handle_rx (self, packet, in_port):
    """
    Called when a packet is received

    You most certainly want to process packets here, learning where they're
    from, and either forwarding them toward the destination or flooding them.
    """

    # The source of the packet can obviously be reached via the input port, so
    # we should "learn" that the source host is out that port.  If we later see
    # a packet with that host as the *destination*, we know where to send it!
    # But it's up to you to implement that.  For now, we just implement a
    # simple hub.
#    print "------------------------------------------------" 
#    print "Handling packets to router: ", api.get_name(self)
    if isinstance(packet, basics.HostDiscoveryPacket):
#        print "HostDiscoveryPacket from ", packet.src
        self.table[packet.src] = in_port
    else:
        self.table[packet.src] = in_port
        if packet.dst in self.table.keys(): 
#            print "Sending packet from ", packet.src, "to ", packet.dst, " through port ", self.table[packet.dst]
            self.send(packet, self.table[packet.dst])
        else:
#            print "Flooding packet from ", packet.src, " across all ports except ", in_port 
            self.send(packet, in_port, flood=True)
#    print self.table
