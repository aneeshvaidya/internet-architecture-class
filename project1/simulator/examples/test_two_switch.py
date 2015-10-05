"""
A simple test

Creates some hosts connected to a single central switch/router.
Sends some pings.
Makes sure the right number of pings reach expected destinations and no pings
reach unexpected destinations.
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
  h2 = NoPacketHost.create("h2")

  s1 = sim.config.default_switch_type.create("s1")
  s2 = sim.config.default_switch_type.create("s2")
  s3 = sim.config.default_switch_type.create("s3")

  h1.linkTo(s1)
  h2.linkTo(s2)

  s1.linkTo(s3)
  s2.linkTo(s3)


  def test_tasklet ():
    yield 5 # Wait five seconds for routing to converge

    api.userlog.debug("Sending test pings")
    h2.ping(h1)

    yield 1 # Wait a bit before sending last ping

    h2.ping(h1)

    yield 5 # Wait five seconds for pings to be delivered

    if h1.pings == 2:
      api.userlog.debug("Test passed successfully!")
    else:
        api.userlog.debug("Test failed, h1 only received " + h1.pings + " pings")

    # End the simulation and (if not running in interactive mode) exit.
    import sys
    sys.exit(0)

  api.run_tasklet(test_tasklet)
