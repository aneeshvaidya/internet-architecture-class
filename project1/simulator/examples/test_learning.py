"""
This test will create a link between two switches and send a ping. Then it will destroy
the link, and then relink and send a ping. The result is two received pings
"""

import sim
import sim.api as api
import sim.basics as basics


class GetPacketHost (basics.BasicHost):
    """
    A host that expects to see a ping
    """
    pings = 0
    def handle_rx (self, packet, port):
        if isinstance(packet, basics.Ping):
             self.pings += 1


class NoPacketHost (basics.BasicHost):
    """
    A host that expects to NOT see a ping
    """
    bad_pings = 0
    def handle_rx (self, packet, port):
        if isinstance(packet, basics.Ping):
            NoPacketHost.bad_pings += 1


def launch ():
    
    h1 = GetPacketHost.create("h1")
    h2 = GetPacketHost.create("h2")
    h3 = GetPacketHost.create("h3")
    
    s1 = sim.config.default_switch_type.create("s1")
    s2 = sim.config.default_switch_type.create("s2")
    s3 = sim.config.default_switch_type.create("s3")
    
    h1.linkTo(s1)
    h2.linkTo(s2)
    h3.linkTo(s3)

    s2.linkTo(s1)
    s2.linkTo(s3)

    def test_tasklet ():
        yield 5 # Wait five seconds for routing to converge

        api.userlog.debug("Sending test pings")
        h2.ping(h1)

        yield 5 # Wait a bit before sending last ping

        if h1.pings == 1:
            api.userlog.debug("Recieved first ping from h2")

        api.userlog.debug(s2.table)
        api.userlog.debug(s1.table)
        api.userlog.debug(s3.table)
        api.userlog.debug("Removing link from s1 to s2")
        s2.unlinkTo(s1)
        yield 5
        api.userlog.debug(s2.table)
        api.userlog.debug(s1.table)

        yield 5 # Wait five seconds for pings to be delivered


        # End the simulation and (if not running in interactive mode) exit.
        import sys
        sys.exit(0)

    api.run_tasklet(test_tasklet)
