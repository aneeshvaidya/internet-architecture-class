"""
Test routing with a link failure

Creates a topology like:

h1 -- s1 -------------- s2 -- h2


Sends a ping from h1 to h2.
Waits a while.
Sends a ping from h1 to h2.

The test passes if h2 gets two pings.
"""

import sim
import sim.api as api
import sim.basics as basics


from test_simple import GetPacketHost


def launch ():
  h1 = GetPacketHost.create("h1")
  h2 = GetPacketHost.create("h2")

  s1 = sim.config.default_switch_type.create('s1')
  s2 = sim.config.default_switch_type.create('s2')


  h1.linkTo(s1)
  h2.linkTo(s2)

  s1.linkTo(s2)


  def test_tasklet ():
    yield 11 # Wait five seconds for routing to converge

    api.userlog.debug("Sending test ping 1")
    h1.ping(h2)

    yield 5

    api.userlog.debug("Sending test ping 2")
    h1.ping(h2)

    yield 5

    if h2.pings != 2:
      api.userlog.error("h2 got %s packets instead of 2", h2.pings)
    else:
      api.userlog.debug("Test passed successfully!")

    # End the simulation and (if not running in interactive mode) exit.
    import sys
    sys.exit(0)

  api.run_tasklet(test_tasklet)
