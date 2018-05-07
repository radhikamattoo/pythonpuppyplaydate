# This performs the under-the-hood logic for puppyplaydate, and
# leverages the existing btfiler code to create handle different
# message types

from btpeer import *
from btfiler import *

# Define global commands
LISTPEERS = "LIST"
ADDFRIEND = "ADDF"
DOGINFO = "DINFO"
MEET = "MEET"
REPLY = "REPLY"
ERROR = "ERRO"
QUERY = "QUER"

class PuppyPlaydate(BTPeer):
    def __init__(self, maxpeers, serverport):
    	BTPeer.__init__(self, maxpeers, serverport)

    	self.dog = {}  # available files: name --> peerid mapping

    	self.addrouter(self.__router)

    	handlers = {LISTPEERS : btfiler.handle_listpeers, # GOOD
    		    ADDFRIEND : btfiler.handle_insertpeer, # GOOD
    		    DOGINFO: self.handle_peername, # MY OWN?
    		    MEET: self.handle_meet, #MY OWN
    		    REPLY: self.handle_qresponse, #MY OWN
                QUERY: self.handle_query
    		   }
    	for mt in handlers:
    	    self.addhandler(mt, handlers[mt])

    def addlocaldog(self, dogInfo):
        """
        Adds new dog info, should be following structure:
        {
            name: string
            breed: string
            age: number
        }
        """
        self.dog = dogInfo

    def handle_query(self, peerconn, data):
        """
        This handles the QUERY message type
        and will check if their dog matches the sent data,
        else will propagate the message to immediate neighbors.
        Data should be in following format:
        {
            returnPID: string
            name: string
            breed: string
            age: number
        }
        """
        try:
            ret_pid, name, breed, age = data.split()
            peerconn.senddata(REPLY, 'Querying for: %s', data)
        except:
            self.__debug('Invalid query: %s', data)
            peerconn.senddata(ERROR, 'Invalid query')

        t = threading.Thread(target=self.process_query, args=[ret_pid, name, breed, age])

    def process_query(self, ret_pid, name, breed, age):
        data = ' '.join([name, breed, age])
        if name == self.dog.name and breed = self.dog.breed and age = self.dog.breed:
            host, port = ret_pid.split(":")
            data += ' ' + self.myid
            self.connectandsend(host, int(port), REPLY, str, pid=ret_pid)
        else:
            for next in self.getpeerids():
                self.sendtopeer(next, QUERY, data)

    def handle_peername(self, peerconn, data):
        peerconn.senddata(REPLY, self.myid)
