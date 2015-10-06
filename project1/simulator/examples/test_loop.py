"""
Test routing with a link failure

Creates a topology like:

            s5
        /   |    \
h1 -- s1 -- s2 -- s4 -- h2
        \   |    /
            s3 

Sends a ping from h1 to h2.
Waits a while.
Sends a ping from h1 to h2.

The test passes if h2 gets two pings.
"""

import sim
import sim.api as api
import sim.basics as basics

import pdb 


from test_simple import GetPacketHost

class TestPacket(basics.Ping):
    pass    


def launch ():
  h1 = GetPacketHost.create("h1")
  h2 = GetPacketHost.create("h2")

  s1 = sim.config.default_switch_type.create('s1')
  s2 = sim.config.default_switch_type.create('s2')
  s3 = sim.config.default_switch_type.create('s3')
  s4 = sim.config.default_switch_type.create('s4')
  s5 = sim.config.default_switch_type.create('s5')

  h1.linkTo(s1)
  h2.linkTo(s4)

  s1.linkTo(s2, latency =4)

  s1.linkTo(s3)
  s1.linkTo(s5)
  s4.linkTo(s3)
  s4.linkTo(s2)
  s4.linkTo(s5)
  s5.linkTo(s2)
  s3.linkTo(s2)

  def test_tasklet ():
    yield 5 # Wait five seconds for routing to converge

    api.userlog.debug("Sending test ping 1")
    h1.ping(h2)

    yield 5

    api.userlog.debug("Adding fast s1-s2 link ")
    #pdb.set_trace()
    #s1.unlinkTo(s2)
    #s1.linkTo(s2, latency=2)
    yield 10


    api.userlog.debug("Sending test ping 2")
    #t = TestPacket(dst=h2)
    #h1.send(t, flood=True)
    #pdb.set_trace()
    h1.ping(h2)
    yield 10



    if h2.pings != 2:
      api.userlog.error("h2 got " + str(h2.basic_pings) + " basic pings")
      api.userlog.error("h2 got " + str(h2.test_packets) + " test packets")
      api.userlog.error("h2 got %s packets instead of 2", h2.pings)
    else:
      api.userlog.debug("Test passed successfully!")

    # End the simulation and (if not running in interactive mode) exit.
    import sys
    sys.exit(0)

  api.run_tasklet(test_tasklet)
