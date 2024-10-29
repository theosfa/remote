# Remote

Remote module for UNET

## Specs

1. network communication modes:
  * client -> make a connection to a remote server (TCP or UDP)
  * server -> listen for incoming connections (TCP or UDP)

2. network protocol support:
  * IP, IPv6 -> should handle both IPv4 and IPv6 with no exceptions

3. transport protocols:
  * TCP, UDP -> must be able to listen or initiate connections using the TCP and UDP protocols

4. dual mode
  * must allow to act as a server or as a client

5. bidirectional data transfer:
  * data sent and received across the network should be supported in both modes (client/server) with full duplex capabilities (simultaneous read/write)

6. port specification
  * must allow specifying a port number on which to listen or connect

7. address specification
  * must be able to resolve addresses when they are supplied as hostnames

8. interfaces specification
  * must be able to use the appropriate interface for the supplied destination, i.e. if not specified use the default routing interface

### Help menu

host         host to connect to
port         port to connect to (default: random)

-6, --ip6                 use IPv6
-n                        do not do any DNS lookups on the supplied host
-l, --listen              listen for incoming connections (connect by default)
-p, --port <port>         port on which to listen (default: random)
-u, --udp                 use UDP (TCP by default)
-b                        bind socket to the interface
-i <name>                 use the supplied interface
-s, --send <in file>      send <in file> to the destination host
-r, --receive <file|None> receive <file> with name <file> or auto name
-a <addr>                 use <addr> as the source address
-T <timeout>              TCP connection timeout (in seconds)
-d <delay>                send data with delay

### Interfaces

__AF_QIPCRTR__ is a Linux-only socket based interface for communicating with services running on co-processors in Qualcomm platforms. The address family is represented as a (node, port) tuple where the node and port are non-negative integers.

__AF_HYPERV__ is a Windows-only socket based interface for communicating with Hyper-V hosts and guests. The address family is represented as a (vm_id, service_id) tuple where the vm_id and service_id are UUID strings.