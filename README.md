# pythonpuppyplaydate
Python P2P Playdate Application

# Acknowledgements
Big thank you to [Nabdeem Adbdul Hamid](http://cs.berry.edu/~nhamid/p2p/index.html), whose Python P2P Framework made this application possible.

# Running
`python app.py <server-port> <max-peers> <peer-ip:port>`

# P2P Messages

## INFO
Queries for information of the target node.

## ADDF
Requests to be added to target node's list of known peers.

## QUER <*dogdata*>
1. Query a node and all its peers for a dog by passing in: `owner, name, breed, age`
2. Query a node and all its peers with just the owner to get all of their dogs: `owner`
3. Query a direct peer for all of its dogs

All of these queries will return the full list of dogs from the peer that has the information.

## QRES
Responds to a user query about a dog.

## MEET *peerid* *location* *date* *time*
Asks target node if they'd like to meet at specified time/date/location.

# MREP
User can reply `Yes` or `No` using the GUI to a pending meetup request by another user.

# QUIT
Node wants to disconnect from a peer's network, or 'unfriend' the specified peer.
