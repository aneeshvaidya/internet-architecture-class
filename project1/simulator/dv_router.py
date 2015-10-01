"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics
import pdb


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  NO_LOG = True # Set to True on an instance to disable its logging
  POISON_MODE = False # Can override POISON_MODE here
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
    # send update on that port
    for dest in self.me.keys():
        self.send_one_update(dest,port)
    

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """
    self.neighbors[port] = INFINITY  
    if port in self.DV.keys():  # router fall off
        del self.DV[port]
    for dest,v in self.me.iteritems():
        l,p,t = v
        if p == port:
            self.me[dest] = (INFINITY, p, 0)
            if self.POISON_MODE:     # poisoning route
                send_all_update(dest)
            


  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.

    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #pdb.set_trace()
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())
    if isinstance(packet, basics.RoutePacket):
        #pdb.set_trace()
        # if packet.dst in self.vector.keys():
            # if len(packet.trace) < 16 and packet.latency < self.vectors[packet.dst]:
                # self.vectors[packet.dst] = [len(packet.trace), packet.latency, port, 0]
        # else:               
            # self.DV[packet.dst] = [len(packet.trace), packet.latency, port, 0]
        if not port in self.DV:
            self.DV[port] = {}
        self.DV[port][packet.destination] = (packet.latency, 0)
        self.chek_for_better_path(packet.destination)
    elif isinstance(packet, basics.HostDiscoveryPacket):
        #self.vectors[packet.src] = [1, self.neighbors[port], port, -1]
        self.me[packet.src] = (self.neighbors[port], port,-1) # set like {... h1:(1,8) ...} for own DV
    else:
        if self.me.get(packet.dst):
            packet.trace.append(self)
            l,p,t = self.me[packet.dst]
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
            l,t = v
            if t >= 15:
                obsolete.append(k)
            else:
                self.DV[port][k] = (l, t + 5)
        for i in obsolete:
            del vector[i] 

    #send update
    obsolete = []
    for dest in self.me.keys():
        l,p,t = self.me[dest]
        if t!= -1:
            t += 5
            self.me[dest] = (l,p,t)
        #pdb.set_trace()
        if t<15 and l!=INFINITY:
            self.send_all_update(dest)
        else:
            obsolete.append(dest)
            
    for i in obsolete:
        del self.me[i] 

  """
    Sends one route update to all neighbor routers (no hosts)
  """
  def send_one_update(self, dest, port):  
      latency,p,t = self.me[dest]
      # if t == -1:
        # return
      packet = basics.RoutePacket(dest, latency)
      #pdb.set_trace()
      if port!=p:                                   # split horizon      
        self.send(packet, port, flood=False)
      elif self.POISON_MODE and port == p:               # poison reverse
        packet = basics.RoutePacket(dest, INFINITY)
        self.send(packet, port, flood=False)
      
  def chek_for_better_path(self, dest):
      #pdb.set_trace()
      for k,v in self.DV.iteritems():
        latency,p,t = self.me[dest]
        l,ttl = v[dest]
        if l + neighbors[k] < latency:
            self.me[dest] = (l + neighbors[k],k, ttl)
            
  def send_all_update(self, dest):
      for port in self.neighbors.keys():
        self.send_one_update(dest, port)



