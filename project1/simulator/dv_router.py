"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  #POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    self.vectors = {}
    self.host_ports = {}

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.host_ports[port] = latency
    

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    for k,v in self.vectors.iteritems():
        if port in v and v[0] == 1:
            del self.host_ports[port]
            del self.vectors[k]
            #send update
        elif port in v:
            del self.host_ports[port]
            #recalculation and update

  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())
    if isinstance(packet, basics.RoutePacket):
        if packet.destination in self.vector.keys():
            if len(packet.trace) < 16 and packet.latency < self.vectors[packet.destination]:
                self.vectors[packet.destination] = [len(packet.trace), packet.latency, port, 0]
        else:
            self.vectors[packet.destination] = [len(packet.trace), packet.latency, port, 0]

    elif isinstance(packet, basics.HostDiscoveryPacket):
        self.vectors[packet.src] = [1, self.host_ports[port], port, -1]
        #flood to neighbors probably as method
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      # self.send(packet, port=port)
        if self.vectors.get(packet.destination):
            packet.trace.append(self)
            self.send(packet, port=self.vectors[packet.destination][2])

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    for k,v in self.vectors.iteritems():
        if v[3] >= 15:
            del self.vectors[k]
        else:
            v[3] += 5
        #send update

  """
    Sends update to neighbors
  """
  def send_update(self, destination):  
      packet = basics.RoutePacket(destination, self.vectors[destination][1])
      self.send(packet, self.vectors[destination][2], flood=True)
    



