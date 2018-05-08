# GUI builder for puppyplaydate

import sys
import threading

from Tkinter import *
from random import *
import json
from puppyplaydate import *

class PuppyPlaydateGui(Frame):
    def __init__(self, firstpeer, hops=2, maxpeers=5, serverport=3000, master=None):
        Frame.__init__( self, master )
        self.grid()
        self.createWidgets()
        self.master.title( "Puppy Playdate %d" % serverport )
        self.btpeer = PuppyPlaydate( maxpeers, serverport )

        self.bind( "<Destroy>", self.__onDestroy )
        host,port = firstpeer.split(':')
        self.btpeer.buildpeers( host, int(port), hops )
        self.updatePeerList()

        t = threading.Thread( target = self.btpeer.mainloop, args = [] )
        t.start()

        self.btpeer.startstabilizer( self.btpeer.checklivepeers, 3 )
        #      self.btpeer.startstabilizer( self.onRefresh, 3 )
        self.after( 3000, self.onTimer )


    def onTimer(self):
        self.onRefresh()
        self.after( 3000, self.onTimer )

    def __onDestroy(self, event):
        self.btpeer.shutdown = True

    def updatePeerList( self ):
      if self.peerList.size() > 0:
         self.peerList.delete(0, self.peerList.size() - 1)
      for p in self.btpeer.getpeerids():
         self.peerList.insert( END, p )

    def updateDogList( self ):
      if self.dogList.size() > 0:
         self.dogList.delete(0, self.dogList.size() - 1)
      for f in self.btpeer.dogs:
         p = json.dumps(self.btpeer.dogs[f])
         if f == self.btpeer.myid:
            p += '(local)'
         self.dogList.insert( END, "%s:%s" % (f,p) )

    def updateMeetupList( self ):
      if self.meetupList.size() > 0:
         self.meetupList.delete(0, self.meetupList.size() - 1)
      for peerid in self.btpeer.meetups:
         meetup_data = json.dumps(self.btpeer.meetups[peerid])
         self.meetupList.insert( END, "%s:%s" % (peerid,meetup_data) )

    def createWidgets( self ):
      """
      Set up the frame widgets
      """
      meetupFrame = Frame(self)
      dogFrame = Frame(self)
      peerFrame = Frame(self)

      meetupReplyFrame = Frame(self)
      rebuildFrame = Frame(self)
      searchFrame = Frame(self)
      adddogFrame = Frame(self)
      pbFrame = Frame(self)
      meetupRequestFrame = Frame(self)

      meetupFrame.grid(row=0, column=0, sticky=N+S)
      dogFrame.grid(row=0, column=1, sticky=N+S)
      peerFrame.grid(row=0, column=2, sticky=N+S)
      pbFrame.grid(row=3, column=2)
      meetupReplyFrame.grid(row=3, column=0)
      adddogFrame.grid(row=3, column=1)
      searchFrame.grid(row=4, column=1)
      rebuildFrame.grid(row=4, column=2)

      Label( meetupFrame, text='Meetup Requests' ).grid()
      Label( dogFrame, text='Known Dogs' ).grid()
      Label( peerFrame, text='Online Peers' ).grid()

      # MEETUP LIST
      meetupListFrame = Frame(meetupFrame)
      meetupListFrame.grid(row=1, column=0)
      meetupScroll = Scrollbar( meetupListFrame, orient=VERTICAL)
      meetupScroll.grid(row=0, column=1, sticky=N+S)

      self.meetupList = Listbox(meetupListFrame, height=5, width=50,
                                yscrollcommand=meetupScroll.set)
      self.meetupList.grid(row=0, column=0, sticky=N+S)
      meetupScroll["command"] = self.meetupList.yview

      self.meetupYes = Button(meetupReplyFrame, text='Yes',
                             command=self.onYes, padx=45)
      self.meetupYes.grid(row=0, column=0)

      self.meetupNo = Button(meetupReplyFrame, text='No',
                       command=self.onNo, padx=45)
      self.meetupNo.grid(row=0, column=1)

      # DOG LIST
      dogListFrame = Frame(dogFrame)
      dogListFrame.grid(row=1, column=0)
      dogScroll = Scrollbar( dogListFrame, orient=VERTICAL )
      dogScroll.grid(row=0, column=1, sticky=N+S)

      self.dogList = Listbox(dogListFrame, height=5, width=50,
                        yscrollcommand=dogScroll.set)
      self.dogList.grid(row=0, column=0, sticky=N+S)
      dogScroll["command"] = self.dogList.yview

      self.adddogEntry = Entry(adddogFrame, width=25)
      self.adddogButton = Button(adddogFrame, text='Add Dog',
                           command=self.onAdd)
      self.adddogEntry.grid(row=0, column=0)
      self.adddogButton.grid(row=0, column=1)

      self.searchEntry = Entry(searchFrame, width=25)
      self.searchButton = Button(searchFrame, text=' Search  ',
                           command=self.onSearch)
      self.searchEntry.grid(row=0, column=0)
      self.searchButton.grid(row=0, column=1)

      # PEER LIST
      peerListFrame = Frame(peerFrame)
      peerListFrame.grid(row=1, column=0)
      peerScroll = Scrollbar( peerListFrame, orient=VERTICAL )
      peerScroll.grid(row=0, column=1, sticky=N+S)

      self.peerList = Listbox(peerListFrame, height=5, width=50,
                        yscrollcommand=peerScroll.set)
      #self.peerList.insert( END, '1', '2', '3', '4', '5', '6' )
      self.peerList.grid(row=0, column=0, sticky=N+S)
      peerScroll["command"] = self.peerList.yview

      self.removeButton = Button( pbFrame, text='Remove',
                                  command=self.onRemove )
      self.refreshButton = Button( pbFrame, text='Refresh',
                                   command=self.onRefresh)

      self.meetupRequestEntry = Entry(pbFrame, width=25)
      self.meetupRequestButton = Button(pbFrame, text='Request Meetup',
                                        command=self.onMeetupRequest)

      self.rebuildEntry = Entry(rebuildFrame, width=25)
      self.rebuildButton = Button( rebuildFrame, text = 'Add Peer',
                            command=self.onRebuild, padx=35)

      self.refreshButton.grid(row=0, column=0)
      self.removeButton.grid(row=0, column=1)
      self.meetupRequestEntry.grid(row=1, column=0)
      self.meetupRequestButton.grid(row=1,column=1)
      self.rebuildEntry.grid(row=2, column=0)
      self.rebuildButton.grid(row=2, column=1)

    def onMeetupRequest(self):
        sels = self.peerList.curselection()
        if len(sels)==1:
            peerid = self.peerList.get(sels[0])
            meetup_data = self.meetupRequestEntry.get().lstrip().rstrip()
            self.btpeer.sendtopeer( peerid, MEET,
                                            "%s %s" % (peerid, meetup_data))


    def onAdd(self):
      dog = self.adddogEntry.get()
      if dog.lstrip().rstrip():
         dogInfo = dog.lstrip().rstrip()
         self.btpeer.addlocaldog( dogInfo )
      self.adddogEntry.delete( 0, len(dog) )
      self.updateDogList()


    def onSearch(self):
      data = self.searchEntry.get()
      print "Searching for ", data
      self.searchEntry.delete( 0, len(data) )

      for p in self.btpeer.getpeerids():
         print "Sending search query to:", p
         self.btpeer.sendtopeer( p,
                                 QUERY, "%s %s" % ( self.btpeer.myid, data ) )


    def onYes(self):
        print "Yes"
    def onNo(self):
        print "No"

    # def onFetch(self):
    #   sels = self.dogList.curselection()
    #   if len(sels)==1:
    #      sel = self.dogList.get(sels[0]).split(':')
    #      if len(sel) > 2:  # fname:host:port
    #         fname,host,port = sel
    #         resp = self.btpeer.connectandsend( host, port, FILEGET, fname )
    #         if len(resp) and resp[0][0] == REPLY:
    #            fd = file( fname, 'w' )
    #            fd.write( resp[0][1] )
    #            fd.close()
    #            self.btpeer.files[fname] = None  # because it's local now


    def onRemove(self):
      sels = self.peerList.curselection()
      if len(sels)==1:
         peerid = self.peerList.get(sels[0])
         self.btpeer.sendtopeer( peerid, QUIT, self.btpeer.myid )
         self.btpeer.removepeer( peerid )


    def onRefresh(self):
      self.updatePeerList()
      self.updateDogList()
      self.updateMeetupList()


    def onRebuild(self):
      print "REBUILDING", self.btpeer.maxpeersreached()
      if not self.btpeer.maxpeersreached():
         peerid = self.rebuildEntry.get()
         self.rebuildEntry.delete( 0, len(peerid) )
         peerid = peerid.lstrip().rstrip()
         try:
            host,port = peerid.split(':')
            #print "doing rebuild", peerid, host, port
            self.btpeer.buildpeers( host, port, hops=3 )
         except:
            if self.btpeer.debug:
               traceback.print_exc()
    #         for peerid in self.btpeer.getpeerids():
    #            host,port = self.btpeer.getpeer( peerid )

if __name__ == '__main__':
   if len(sys.argv) < 4:
      print "Syntax: %s server-port max-peers peer-ip:port" % sys.argv[0]
      sys.exit(-1)
   serverport = int(sys.argv[1])
   maxpeers = sys.argv[2]
   peerid = sys.argv[3]
   app = PuppyPlaydateGui( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport )
   app.mainloop()
