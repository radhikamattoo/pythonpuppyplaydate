# This performs the under-the-hood logic for puppyplaydate using btpeer

from btpeer import *
import json

# Define message types
LISTPEERS = "LIST"
ADDFRIEND = "ADDF"
INFO = "INFO"
MEET = "MEET"
MEETREPLY = "MREP"
QUERY = "QUER"
QRESP = "QRES"
QUIT = "QUIT"
REPLY="REPL"
ERROR="ERRO"

## TODO: Implement List Peers functionality in another GUI box?
## Comment/cleanup code, update README, delete unneeded files

class PuppyPlaydate(BTPeer):
    def __init__(self, maxpeers, serverport):
    	BTPeer.__init__(self, maxpeers, serverport)

        self.meetups = {} # Requested and Sent meetup information
    	self.dogs = {}  # Known dogs in format of { peerid: [{owner, name, age, breed}, ...]}

    	self.addrouter(self.__router)
    	handlers = {LISTPEERS : self.handle_listpeers,
    		    ADDFRIEND : self.handle_insertpeer,
    		    INFO: self.handle_peername,
    		    MEET: self.handle_meet,
                MEETREPLY: self.handle_meet_reply,
                QRESP: self.handle_qresponse,
                QUERY: self.handle_query,
                QUIT: self.handle_quit
    		   }
    	for mt in handlers:
    	    self.addhandler(mt, handlers[mt])

    def handle_quit(self, peerconn, data):
    	self.peerlock.acquire()
    	try:
    	    peerid = data.lstrip().rstrip()
    	    if peerid in self.getpeerids():
        		msg = 'Quit: peer removed: %s' % peerid
        		self.__debug(msg)
        		peerconn.senddata(REPLY, msg)
        		self.removepeer(peerid)
    	    else:
        		msg = 'Quit: peer not found: %s' % peerid
        		self.__debug(msg)
        		peerconn.senddata(ERROR, msg)
    	finally:
    	    self.peerlock.release()

    def handle_listpeers(self, peerconn, data):
    	self.peerlock.acquire()
    	try:
    	    self.__debug('Listing peers %d' % self.numberofpeers())
    	    peerconn.senddata(REPLY, '%d' % self.numberofpeers())
    	    for pid in self.getpeerids():
    		host,port = self.getpeer(pid)
    		peerconn.senddata(REPLY, '%s %s %d' % (pid, host, port))
    	finally:
    	    self.peerlock.release()

    def handle_insertpeer(self, peerconn, data):
    	self.peerlock.acquire()
    	try:
    	    try:
                peerid,host,port = data.split()
                if self.maxpeersreached():
        		    self.__debug('maxpeers %d reached: connection terminating'
        				  % self.maxpeers)
        		    peerconn.senddata(ERROR, 'Join: too many peers')
        		    return

        		# peerid = '%s:%s' % (host,port)
                if peerid not in self.getpeerids() and peerid != self.myid:
        		    self.addpeer(peerid, host, port)
        		    print'added peer:' +peerid
        		    peerconn.senddata(REPLY, 'Join: peer added: %s' % peerid)
                else:
        		    peerconn.senddata(ERROR, 'Join: peer already inserted %s'
        				       % peerid)
            except:
        		self.__debug('invalid insert %s: %s' % (str(peerconn), data))
        		peerconn.senddata(ERROR, 'Join: incorrect arguments')
    	finally:
    	    self.peerlock.release()

    def handle_peername(self, peerconn, data):
        peerconn.senddata(REPLY, self.myid)

    def buildpeers(self, host, port, hops):
    	if self.maxpeersreached() or not hops:
    	    return
    	peerid = None
    	self.__debug("Building peers from (%s,%s)" % (host,port))

    	try:
    	    _, peerid = self.connectandsend(host, port, INFO, '')[0]
    	    self.__debug("contacted " + peerid)
    	    resp = self.connectandsend(host, port, ADDFRIEND,
    					'%s %s %d' % (self.myid,
    						      self.serverhost,
    						      self.serverport))[0]
    	    self.__debug(str(resp))

    	    self.addpeer(peerid, host, port)

    	except:
    	    if self.debug:
    		traceback.print_exc()
    	    self.removepeer(peerid)

    def addlocaldog(self, data):
        """
        Adds new dog info, should be following structure:
        owner:name:breed:age
        """
        owner, name, breed, age = data.split()
        try:
            self.dogs[self.myid].append({'owner': owner, 'name': name, 'breed': breed, 'age': age})
        except:
            self.dogs[self.myid] = []
            self.dogs[self.myid].append({'owner': owner, 'name': name, 'breed': breed, 'age': age})

    def handle_query(self, peerconn, data):
        """
        This handles the QUERY message type
        and will check if their dog matches the sent data,
        else will propagate the message to immediate neighbors.
        Data should be in following format:
            returnPID owner name breed age
        """
        try:
            ret_pid, owner, name, breed, age = data.split()
            t = threading.Thread(target=self.process_full_query, args=[ret_pid, owner, name, breed, age])
            t.start()
        except:
            try:
                ret_pid, owner = data.split()
                t = threading.Thread(target=self.process_owner_query, args=[ret_pid, owner])
                t.start()
            except:
                ret_pid = data
                t = threading.Thread(target=self.process_peerid_query, args=[peerconn, ret_pid])
                t.start()

    def process_full_query(self, ret_pid, owner, name, breed, age):
        for peerid, dogList in self.dogs.iteritems():
            for dog in dogList:
                if owner == dog['owner'] and name == dog['name'] and breed == dog['breed'] and age == dog['age']:
                    host, port = ret_pid.split(":")
                    data = { peerid: dogList }
                    self.connectandsend(host, int(port), QRESP, json.dumps(data, encoding='utf-8'), pid=ret_pid)
                    return
        # Dog not found in known dogs, propagate to peers
        for next in self.getpeerids():
            data = ret_pid + ' ' + data
            self.sendtopeer(next, QUERY, data)

    def process_peerid_query(self, peerconn, ret_pid):
        host, port = ret_pid.split(':')
        try:
            data = { self.myid: self.dogs[self.myid] }
        except:
            data = { self.myid: [] }
        self.connectandsend(host, int(port), QRESP, json.dumps(data, encoding='utf-8'), pid=ret_pid)

    def process_owner_query(self, ret_pid, owner):
        for peerid, dogList in self.dogs.iteritems():
            for dog in dogList:
                if owner == dog['owner']: #send back all dogs
                    host, port = ret_pid.split(':')
                    data = { peerid: dogList }
                    self.connectandsend(host, int(port), QRESP, json.dumps(data, encoding='utf-8'), pid=ret_pid)
                    return
        # Owner not found in known dogs, propagate to peers
        for next in self.getpeerids():
            self.sendtopeer(next, QUERY, '%s:%s' % (ret_pid, owner))

    def handle_qresponse(self, peerconn, data):
        try:
            data = json.loads(data) #{peerid: [{}, {}]}
            peerid = next(iter(data))
            dogList = data[peerid] #[{}, {}]
            self.dogs[peerid] = []
            for dog in dogList:
                dog['owner'] = dog['owner'].encode('ascii', 'replace')
                dog['name'] = dog['name'].encode('ascii', 'replace')
                dog['breed'] = dog['breed'].encode('ascii', 'replace')
                dog['age'] = dog['age'].encode('ascii', 'replace')
                self.dogs[peerid].append({'owner': dog['owner'], 'name': dog['name'], 'breed': dog['breed'], 'age': dog['age']})
        except:
            self._debug('Error handling query response.')

    def handle_meet(self, peerconn, data):
        """
        Handles a meetup request from a peer.
        """
        try:
            peerid, location, date, time = data.split()
            self.meetups[peerid] = { 'to': self.myid, 'location': location, 'date': date, 'time': time, 'accepted': None }
        except:
            peerconn.senddata(ERROR, 'Error delivering meetup request')

    def handle_meet_reply(self, peerconn, data):
        """
        Handles response to a meetup request (yes or no)
        If Yes, change the corresponding request's 'Accepted' parameter to True
        If No, change the corresponding request's 'Accepted' parameter to False
        """
        toId, answer = data.split()
        for fromId in self.meetups:
            if self.meetups[fromId]['to'] == toId:
                if answer == 'Yes':
                    self.meetups[fromId]['accepted'] = True
                else:
                    self.meetups[fromId]['accepted'] = False

    def __router(self, peerid):
    	if peerid not in self.getpeerids():
    	    return (None, None, None)
    	else:
    	    rt = [peerid]
    	    rt.extend(self.peers[peerid])
    	    return rt

    def __debug(self, msg):
    	if self.debug:
    	    btdebug(msg)
