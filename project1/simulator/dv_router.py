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
        # port -> latency
        self.ports = {}
        # destination -> (latency, port, ttl)
        self.vector = {}
        # port -> {destination -> (latency, port, ttl)}
        self.neighbors = {}

    def handle_link_up (self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.
        The port attached to the link and the link latency are passed in.

        We put the port and latency into our dictionary mapping. We also send 
        all of our tables to our neighbors.
        """
        self.ports[port] = latency
        self.send_all_tables()
        #send tables here

    def handle_link_down (self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.
        """
        if port in self.neighbors.keys():
            for dest in self.neighbors[port]:
                if dest in self.vectors.keys():
        for dest in self.vectors.keys():
            if port == self.vectors[dest][1]:



    def handle_rx (self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.
        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            self.handle_route_packet(packet, port)
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.handle_discovery_packet(packet, port)
        else:
            # If the packet destination is in our lookup table and not on the port we got it on, send it out.
            if packet.dst in self.vector.keys():
                if port != self.vector[packet.dst][1]:
                    self.send(packet, port=self.vector[packet.dst][1])
          

    def handle_discovery_packet(packet, port):
        """
        Handles disocvery packets.
        
        Since discovery packets are only sent when a host is first connected
        to a switch, there are two cases:
        1) First time a host is brought up
        2) Host is brought up after a link going down

        Currently we only handle the first case.

        """
        if packet.src in self.vector.keys():
            l, p, t = self.vector[packet.src]
            if l > self.ports[port]:
                self.vector[packet.src] = [self.ports[port], port, -1]
        else:
            self.vector[packet.src] = [self.ports[port], port, -1]
        self.send_one_table(packet.src)

    def handle_route_packet(packet, port):
        """
        Handles RoutePackets received at switch
        
        If we've never seen this port, it's a new neighbor, add it to the table.
        Add the destination of the packet to the vector of that neighbor, adding our
        port latency to the packet latency. Then update our tables.
        """
        if port not in self.neighbors.keys():
            self.neighbors[port] = {}
        self.neighbors[port][packet.destination] = [packet.latency + self.ports[port], port, 0]
        #self.update_one_table(packet.destination)
        self.update_all_tables()


    def handle_timer (self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It also might
        not be a bad place to check for whether any entries have expired.
        """
        self.increment_ttl()
        self.send_all_tables()

    def increment_ttl(self):
        """
        Goes through neighbor and own vector tables and increments ttl. Removes
        invalid entries as well.
        """
        for port in self.neighbors.keys():
            neighbor = self.neighbors[port]
            for dest in neighbor.keys():
                l, p, t = neighbor[dest]

    def update_all_tables(self):
        """
        Updates tables of our vectors. Additionally, sends all changed tables through 
        self.send_one_table() (Trigerred Updates).

        """
        updated = []

        for port in self.neighbors.keys():
            neighbor = self.neighbors[port]
            for dest in neighbor.keys():
                n_v = neighbor[dest] #neighbor_vector = n_v
                if dest not in self.vector.keys() and n_v[0] < INFINITY:
                    self.vector[dest] = n_v 
                else:
                    l, p, t = self.vector[dest]
                    if l > n_v + self.ports[n_v[1]] and n_v[2] < INFINITY:
                        self.vector[dest] = neighbor_vector
                        updated.append(dest)
        for dest in updated:
            self.send_one_table(dest)


    def update_one_table(self, destination):
        """
        Updates vector table for one destination.
        """
        for port in self.neighbors.keys():
            if destination in self.neighbors[port]:
                n_v = self.neighbors[port][destination]
                curr_v = self.vector[destination]
        pass 

    def send_all_tables(self):
        """
        Sends our vector tables to all neighbors.

        For every destination in our table we create a RoutePacket and then flood it.
        We flood every port except the one which we use to get to that destination. 
        Otherwise we're not obeying split horizon, because we're telling our neighbors
        that we use to get to dest that they have a route to dest through us.
        """
        for dest in self.vector.keys():
            l, p, t = self.vector[dest]
            packet = basics.RoutePacket(dest, l)
            self.send(packet, port=p, flood=True)


    def send_one_table(self, dest):
        """
        Sends specific vector to all neighbors.

        """
        if dest in self.vector.keys():
            l, p, t = self.vector[dest]
            packet = basics.RoutePacket(dest, l)
            self.send(packet, port=p, flood=True)

