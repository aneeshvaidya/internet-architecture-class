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
    
    # dictionary: port -> dest -> (latency, ttl) 
    self.DV = {}
    
    # own DV: dest -> (latency, port, ttl)
    self.me = {}
    
    # dictionary: port -> latency
    self.neighbors = {}
    

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.neighbors[port] = latency
    

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
        # if packet.destination in self.vector.keys():
            # if len(packet.trace) < 16 and packet.latency < self.vectors[packet.destination]:
                # self.vectors[packet.destination] = [len(packet.trace), packet.latency, port, 0]
        # else:               
            # self.DV[packet.destination] = [len(packet.trace), packet.latency, port, 0]
        self.DV[port][packet.destination] = (packet.latency, 0)
        chek_for_better_path(packet.destination)
    elif isinstance(packet, basics.HostDiscoveryPacket):
        #self.vectors[packet.src] = [1, self.neighbors[port], port, -1]
        self.me[packet.src] = (self.neighbors[port], port,-1) # set like {... h1:(1,8) ...} for own DV
    else:
        if self.me.get(packet.destination):
            packet.trace.append(self)
            l,p,t = self.me[packet.destination]
            self.send(packet, port = p)

  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    # check for obsolete records
    for port,vector in self.DV.iteritems():
        obsolete = []
        for k,v in vector.iteritems():
            if v[1] >= 15:
                obsolete.append(k)
            else:
                v[1] += 5
        for i in obsolete:
            del vector[i] 

    #send update
    for dest in self.me.keys():
        send_update(dest)
    

  """
    Sends one route update to all neighbor routers (no hosts)
  """
  def send_update(self, dest):  
      latency,p,t = self.me[dest]
      packet = basics.RoutePacket(dest, latency)      
       #   self.send(packet, self.vectors[destination][2], flood=True)      
      for port in self.me.keys():
          self.send(packet, port, flood=False)
      
  def chek_for_better_path(dest):
      for k,v in self.DV.iteritems():
        latency,p,t = self.me[dest]
        l,ttl = v[dest]
        if l + neighbors[k] < latency:
            self.me[dest] = (l + neighbors[k],k, ttl)
    



