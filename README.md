# pythonpuppyplaydate
Python P2P Playdate Application

# Acknowledgements
Python P2P framework provided by [Nabdeem Adbdul Hamid](http://cs.berry.edu/~nhamid/p2p/index.html). To run his Python P2P File Sharing App, run `python filergui.py <server-port> <max-peers> <peer-ip:port>`

# Running
`python app.py`

# P2P Messages

## INFO
Queries for information of the target node.

## LIST
Queries for the friend list of the target node.

## ADDFRIEND
Requests to be added to target node's friend list.

## DOG
Requests information about target node's dog.

## MEET *location* *date* *time*
Asks target node if they'd like to meet at specified time/date/location.

## AFFR *msg*
Generic confirmation response for any of the above messages, with specific payload.

## ERROR
Generic error response for any of the above messages, with specific payload.
