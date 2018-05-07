# This performs the under-the-hood logic for puppyplaydate, and
# leverages the existing btfiler code to create handle different
# message types

from btpeer import *
from btfiler import *
import json

# Define message types
LISTPEERS = "LIST"
ADDFRIEND = "ADDF"
INFO = "INFO"
DOGINFO = "DINF"
MEET = "MEET"
MEETREPLY = "MREP"
REPLY = "REPLY"
QUERY = "QUER"
QRESP = "QRES"
ERROR = "ERRO"

class PuppyPlaydate(BTPeer):
    def __init__(self, maxpeers, serverport):
    	BTPeer.__init__(self, maxpeers, serverport)
        self.meetups = {} # Requested meetup dates, user can reply Y or N or nothing at all.
    	self.dogs = {}  # Known dogs in format of { peerid: {name, age, breed}, ...}

    	self.addrouter(self.__router)
    	handlers = {LISTPEERS : FilerPeer.handle_listpeers, # GOOD
    		    ADDFRIEND : FilerPeer.handle_insertpeer, # GOOD
    		    INFO: FilerPeer.handle_peername, # GOOD
                DOGINFO: self.handle_doginfo, #GOOD
    		    MEET: self.handle_meet, # GOOD
                MEETREPLY: self.handle_meet_reply, # GOOD
                QRESP: self.handle_qresponse, #MY OWN
                QUERY: self.handle_query #MY OWN
    		   }
    	for mt in handlers:
    	    self.addhandler(mt, handlers[mt])

    def __debug(self, msg):
	if self.debug:
	    btdebug(msg)

    def buildpeers(self, host, port, hops):
    	if self.maxpeersreached() or not hops:
    	    return

    	peerid = None

    	self.__debug("Building peers from (%s,%s)" % (host,port))

    	try:
    	    _, peerid = self.connectandsend(host, port, PEERNAME, '')[0]

    	    self.__debug("contacted " + peerid)
    	    resp = self.connectandsend(host, port, INSERTPEER,
    					'%s %s %d' % (self.myid,
    						      self.serverhost,
    						      self.serverport))[0]
    	    self.__debug(str(resp))
    	    if (resp[0] != REPLY) or (peerid in self.getpeerids()):
    		return

    	    self.addpeer(peerid, host, port)

    	    # do recursive depth first search to add more peers
    	    resp = self.connectandsend(host, port, LISTPEERS, '',
    					pid=peerid)
    	    if len(resp) > 1:
    		resp.reverse()
    		resp.pop()    # get rid of header count reply
    		while len(resp):
    		    nextpid,host,port = resp.pop()[1].split()
    		    if nextpid != self.myid:
    			self.buildpeers(host, port, hops - 1)
    	except:
    	    if self.debug:
    		traceback.print_exc()
    	    self.removepeer(peerid)


    def __router(self, peerid):
    	if peerid not in self.getpeerids():
    	    return (None, None, None)
    	else:
    	    rt = [peerid]
    	    rt.extend(self.peers[peerid])
    	    return rt


    def addlocaldog(self, dog):
        """
        Adds new dog info, should be following structure:
        {
            name: string
            breed: string
            age: number
        }
        """
        self.dog[self.myid] = dog

    def handle_query(self, peerconn, data):
        """
        This handles the QUERY message type
        and will check if their dog matches the sent data,
        else will propagate the message to immediate neighbors.
        Data should be in following format:
            returnPID name breed age
        """
        try:
            ret_pid, name, breed, age = data.split()
            peerconn.senddata(REPLY, 'Querying for: %s', data)
        except:
            peerconn.senddata(ERROR, 'Invalid query')

        t = threading.Thread(target=self.process_query, args=[ret_pid, name, breed, age])
        t.start()

    def process_query(self, ret_pid, name, breed, age):
        data = ' '.join([name, breed, age])
        for peerid, dog in self.dogs.iteritems():
            if name == dog.name and breed == dog.breed and age == dog.age:
                host, port = ret_pid.split(":")
                data = peerid + ' ' + data
                self.connectandsend(host, int(port), QRESP, data, pid=ret_pid)
                return

        # Dog not found in known dogs, propagate to peers
        for next in self.getpeerids():
            data = ret_pid + data
            self.sendtopeer(next, QUERY, data)

    def handle_meet(self, peerconn, data):
        """
        Handles a meetup request from a peer.
        """
        try:
            peerid, location, date, time = data.split()
            meetups[peerid] = { 'location': location, 'date': date, 'time': time }
            peerconn.senddata(REPLY, 'Meetup request delivered: %s', data)
        except:

            peerconn.senddata(ERROR, 'Error delivering meetup request')

    def handle_meet_reply(self, peerconn, data):
        """
        User will input Y or N for a given meetup request. Data will be in format:
            Y/N location date time
        """
        try:
            answer, location, date, time = data.split()
            meetup = ''.join([location, date, time])
            if answer == 'Y':
                peerconn.senddata(MEETREPLY, 'User has accepted your meetup %s', meetup)
            else:
                peerconn.senddata(MEETREPLY, 'User has rejected your meetup %s', meetup)
        except:
            print "Error parsing reply"

    def handle_qresponse(self, peerconn, data):
        try:
            peerid, name, breed, age = data.split()
            dog =  { 'name': name, 'breed': breed, 'age': age }
            self.dogs[peerid] = dog
        except:
            print "Problem handling query response"

    def handle_doginfo(self, peerconn, data):
        peerconn.senddata(REPLY, json.dumps(self.dogs[self.myid]))
