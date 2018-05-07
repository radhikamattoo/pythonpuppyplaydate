# pythonpuppyplaydate
Python P2P Playdate Application

# Acknowledgements
Big thank you to [Nabdeem Adbdul Hamid](http://cs.berry.edu/~nhamid/p2p/index.html), whose Python P2P Framework made this application possible.

# Running
`python app.py <server-port> <max-peers> <peer-ip:port>`

# P2P Messages

## INFO
Queries for information of the target node.

## LIST
Queries for the friend list of the target node.

## ADDF
Requests to be added to target node's friend list.

## DINF
Requests information about target node's dog.

## QUER *dogdata*
Asks node if they are the owner of the specified dog.

## MEET *location* *date* *time*
Asks target node if they'd like to meet at specified time/date/location.

## REPL *msg*
Response for any of the above messages, with specific payload.

## ERRO
Generic error response for any of the above messages, with specific payload.
