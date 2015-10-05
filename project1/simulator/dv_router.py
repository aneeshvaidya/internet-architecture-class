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
    POISON_MODE = False# Can override POISON_MODE here
    DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

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


    def handle_link_down (self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.
        """
        #print "Port down: ", port
        #pdb.set_trace()
        for dest in self.vector.keys():
            l, p, t = self.vector[dest]
            if p == port:
                self.vector[dest] = (INFINITY, p, t)        
        

        if self.neighbors.get(port):        
            del self.neighbors[port]
            
        del self.ports[port]

                
        self.update_vector_all()


    def handle_rx (self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.
        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        #print api.get_name(self), "received packet from ", packet.src, " of type ", type(packet)
        #pdb.set_trace()

        #Gives us packet.destination, packet.latency, packet.src
        if isinstance(packet, basics.RoutePacket):
            self._handle_route_packet(packet, port)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self._handle_discovery_packet(packet, port)
        else:
            rout = self.vector.get(packet.dst)
            if rout and port != rout[1] and rout[0] != INFINITY :#and rout[2] < 16:
                #print api.get_name(self) + " sent packet to " + api.get_name(packet.dst)
                self.send(packet, port=rout[1], flood=False)
                
    def _handle_route_packet(self, packet, port):
        #if api.get_name(self) == "s3": pdb.set_trace()
        if port not in self.neighbors.keys():
            self.neighbors[port] = {}
        self.neighbors[port][packet.destination] = (packet.latency, port, 0)
        if packet.destination in self.vector.keys():
            self.recalculate_dest(packet.destination)
        else:
            self.set_dest(packet.destination, packet.latency + self.ports[port], port, 0)
        #print api.get_name(self) + "'s vector is: " + str(self.vector)

    def _handle_discovery_packet(self, packet, port):
    
        if packet.src in self.vector.keys():
            latency, port, ttl = self.vector.get(packet.src)
            if latency > self.ports[port]:
                self.set_dest(packet.src, self.ports[port], port, -1)
        else:
            self.set_dest(packet.src, self.ports[port], port, -1)

    def handle_timer (self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It also might
        not be a bad place to check for whether any entries have expired.
        """
        self.increment_ttl()   #increments ttl on all vectors and expires routes
        self.update_vector_all() #updates vector according to expired routes
        

    def send_update(self, destination):
        """
        Find our vector for a given destination. We know that destination is reached from
        some port, so flood every port except that one. If poison mode is enabled, we send
        on that port a poisoned reversed route
        """
        latency, p, ttl = self.vector[destination]
        packet = basics.RoutePacket(destination, latency)
        self.send(packet, port=p, flood=True)
        if self.POISON_MODE:
            poison = basics.RoutePacket(destination, INFINITY)
            self.send(poison, port=port, flood=False)

            
    def increment_ttl(self):            # increment ttl for neigbor vectors
        for n in self.neighbors.keys():
            for dest in self.neighbors[n].keys():
                l,p,t = self.neighbors[n][dest] 
                if t >= 0:
                    self.neighbors[n][dest] = (l,p,t + self.DEFAULT_TIMER_INTERVAL)
                if self.neighbors[n][dest][2] >= INFINITY:
                    del self.neighbors[n][dest]
                
        for dest in self.vector.keys():
            l,p,t = self.vector[dest]
            if t >=0:
                self.vector[dest] = (l,p,t + self.DEFAULT_TIMER_INTERVAL)
            if self.vector[dest][2] >= INFINITY:
                del self.vector[dest]
                #print "Neighbors: ", self.neighbors
        
        print api.get_name(self), "'s vector: ", self.vector
                
    def update_vector_all(self): 
        if not self.neighbors:
            for dest in self.vector.keys():
                self.send_update(dest)
                
        for dest in self.vector.keys():
            self.recalculate_dest(dest)
    
    def recalculate_dest(self, dest):
        """
        Updates vector to particular destinations.
        Assumes destination in the vector
        Iterate through every neighbor vector. 
        """
        #print "Updating one vector for ", api.get_name(self)
        #if api.get_name(self) == "s1" and not self.ports.get(1): pdb.set_trace()
        is_updated = False
        
        l,p,t = self.vector.get(dest)
        for n in self.neighbors.keys():
            neighbor_vector = self.neighbors[n].get(dest)
            if neighbor_vector:
                nl,np,nt = neighbor_vector
                if l > neighbor_vector[0] + n:
                    #print "Updated " + str(self.vector[dest]) + " to " + str(neighbor_vector)
                    self.vector[dest] = (nl + n, np, nt)
                    is_updated = True
        
        # trying to lower ttl of vector destination if reciving update from neighbor
        # second is forse propagation of broken link route
        n = self.neighbors.get(p)
        if not is_updated and n:
            if n.get(dest):
                if n[dest][2] < t:
                    self.vector[dest] = (l, p, n[dest][2])
                if n[dest][0] == INFINITY and t!= -1:
                    self.vector[dest] = (INFINITY, p, t)
        
        #if is_updated or l == INFINITY:
        self.send_update(dest)
            
    def set_dest(self, dest,l,p,t):
        self.vector[dest] = (l, p, t)
        self.send_update(dest)
            
            
    
