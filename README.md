# pythonpuppyplaydate
Interact with other dog owners & enthusiasts via direct message passing over a distributed network of nodes - no servers involved!

 How you implement the front & backend is up to you - simply use the `puppyplaydate.py` file as you'd like. In this repository, I've created a front-end Python GUI via`puppyplaydategui.py` to demonstrate the abilities of the application.

# Acknowledgements
Big thank you to [Nabdeem Adbdul Hamid](http://cs.berry.edu/~nhamid/p2p/index.html), whose Python P2P Framework made this application possible.

# Running
No installation necessary! This applications runs on pure socket connections with threading.

Run the application with the following command:

`python puppyplaydategui.py <server-port> <max-peers> <peer-ip:port>`

For example, `python puppyplaydategui.py 3000 0 localhost:5000`
runs the program on `localhost:3000` with an unlimited amount of `max-peers`, and the first node it connects to/knows is `localhost:5000`

# P2P Messages

## GPER
Requests the target node for all their known peers

## GREP
Handles the response from the GPER request

## ADDF
Requests to be added to target node's list of known peers.

## QUER *dogdata*
1. Query a node and all its peers for a dog by passing in: `owner, name, breed, age`
2. Query a node and all its peers with just the owner to get all of their dogs: `owner`
3. Query a direct peer for all of its dogs

All of these queries will return the full list of dogs from the peer that has the information.

## QRES
Handles response to query.

## MEET *peerid* *location* *date* *time*
Asks target node if they'd like to meet at specified time/date/location.

# MREP
Handles 'Yes' or 'No' to meetup request from node.

# QUIT
Node wants to disconnect from a peer's network, or 'unfriend' the specified peer.
