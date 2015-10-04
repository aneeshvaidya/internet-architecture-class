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

        # destination -> (latency, port, ttl)
        self.vector = {}
        # port -> {destination -> (latency, port, ttl)}
        self.neighbors = {}
        # port -> latency
        self.ports = {}

    def handle_link_up (self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed in.
        """
        #print "Link up on port ", port, "with latency ", latency, "with node ", api.get_name(self)
        self.ports[port] = latency
        for dst in self.vector.keys():
            self.send_update(dst)
        #we should send updates here too, all vectors in self.vector

    def handle_link_down (self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.
        """
        neighbor_vector = self.neighbors[port] 
        for key in neighbor_vector.keys():
            if self.vector.get(key):
                if self.POISON_MODE:
                    self.send_update(key)
                del self.vector[key]
        del self.neighbors[port]

    def handle_rx (self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.
        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        #print api.get_name(self), "received packet from ", packet.src, " of type ", type(packet)
        #Gives us packet.destination, packet.latency, packet.src
        if isinstance(packet, basics.RoutePacket):
#            print "Latency: ", packet.latency
#            print "Destination: ", packet.destination
            self._handle_route_packet(packet, port)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self._handle_discovery_packet(packet, port)
        else:
            if self.vector.get(packet.dst):
                self.send(packet, port=self.vector[packet.dst][1], flood=False)
                
    def _handle_route_packet(self, packet, port):
        if port not in self.neighbors.keys():
            self.neighbors[port] = {}
        self.neighbors[port][packet.destination] = [packet.latency + self.ports[port], port, 15]
        self.update_vector(port, packet.destination)

    def _handle_discovery_packet(self, packet, port):
        if packet.src in self.vector.keys():
            latency, port, hops = self.vector.get(packet.src)
            if latency > self.ports[port] and hops < 16:
                self.vector[packet.src] = [self.ports[port], port, 15]
        else:
            self.vector[packet.src] = [self.ports[port], port, 15]
            print self.vector

    def handle_timer (self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It also might
        not be a bad place to check for whether any entries have expired.
        """
        for k in self.vector.keys():
            if self.vector[k][2] <= 0:
                del self.vector[k]
            else:
                self.vector[k][2] -= 5
                self.send_update(k)
#        for k, v in self.neighbors.iteritems():
#            if self.neighbors[k][2] <= 0:
#                del self.neighbors[k]
#            else:
#                self.neighbors[k][2] -= 5

    def send_update(self, destination):
        """
        Find our vector for a given destination. We know that destination is reached from
        some port, so flood every port except that one. If poison mode is enabled, we send
        on that port a poisoned reversed route
        """
        latency, port, ttl = self.vector[destination]
        packet = basics.RoutePacket(destination, latency)
        self.send(packet, port=port, flood=True)
        if self.POISON_MODE:
            poison = basics.RoutePacket(destination, INFINITY)
            self.send(poison, port=port)

    def update_vector(self, port, destination):
        """
        Updates our instance vector to all reachable destinations.

        Iterate through every neighbor vector. 
        """
        neighbor_vector = self.neighbors[port][destination]
        my_vector = self.vector.get(destination)
        if my_vector:
            if my_vector[0] > neighbor_vector[0] and neighbor_vector[0] < 16:
                self.vector[destination] = neighbor_vector
        else:
            self.vector[destination] = neighbor_vector
         
