"""Module containing a template for a main service."""

import logging
import sys
import uuid
import threading
import random

import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix  # pylint:disable=import-error

class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    def __init__(self, timer):
        self.authenticatorList = []
        self.catalogList = []
        self.fileList = []
        self.mains = {}
        self._id_ = str(uuid.uuid4())
        self.timer = timer 
        self.updated = False

    def getAuthenticator(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        if len(self.authenticatorList) != 0:
            for i in self.authenticatorList:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.AuthenticatorPrx.checkedCast(i)
                except Ice.ConnectionRefusedException as e:
                    print(e)
        raise IceFlix.TemporaryUnavaible()

    def getCatalog(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
        if len(self.catalogList) != 0:
            for i in self.catalogList:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.MediaCatalogPrx.checkedCast(i)
                except Ice.ConnectionRefusedException as e:
                    print(e)
        raise IceFlix.TemporaryUnavaible()

    def getFileService(self, current=None): # pylint:disable=invalid-name, unused-argument
        "Return the stored FileService proxy."
        if len(self.fileList) != 0:
            for i in self.fileList:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.FileServicePrx.checkedCast(i)
                except Ice.ConnectionRefusedException as e:
                    print(e)
        raise IceFlix.TemporaryUnavaible()

    def newService(self, proxy, service_id, current=None):  # pylint:disable=invalid-name, unused-argument
        "Receive a proxy of a new service."
        if service_id != str(uuid.uuid4()):
            if proxy.ice_isA('::IceFlix::Main'):
                proxyService = IceFlix.MainPrx.checkedCast(proxy)
                if str(uuid.uuid4()) != self._id_ and self.updated is False:
                    self.timer.cancel()
                    proxyService.authenticatorList = self.authenticatorList
                    proxyService.catalogList = self.catalogList
                    proxyService.fileList = self.fileList
                    self.updated = True
            if proxy.ice_isA('::IceFlix::Authenticator'):
                proxyService = IceFlix.AuthenticatorPrx.checkedCast(proxy)
                if str(uuid.uuid4()) != self._id_ and self.updated is False:
                    self.timer.cancel()
                    proxyService.authenticatorList = self.authenticatorList
                    proxyService.catalogList = self.catalogList
                    proxyService.fileList = self.fileList
                    self.updated = True
            if proxy.ice_isA('::IceFlix::MediaCatalog'):
                proxyService = IceFlix.MediaCatalogPrx.checkedCast(proxy)
                if str(uuid.uuid4()) != self._id_ and self.updated is False:
                    self.timer.cancel()
                    proxyService.authenticatorList = self.authenticatorList
                    proxyService.catalogList = self.catalogList
                    proxyService.fileList = self.fileList
                    self.updated = True
            if proxy.ice_isA('::IceFlix::FileService'):
                proxyService = IceFlix.FileServicePrx.checkedCast(proxy)
                if str(uuid.uuid4()) != self._id_ and self.updated is False:
                    self.timer.cancel()
                    proxyService.authenticatorList = self.authenticatorList
                    proxyService.catalogList = self.catalogList
                    proxyService.fileList = self.fileList
                    self.updated = True

    def announce(self, proxy, service_id, current=None):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        if proxy in (list(self.authenticatorList) + list(self.catalogList) + list(self.fileList) + list(self.mains.values())) or service_id == str(uuid.uuid4()):
            return

        if proxy.ice_isA('::IceFlix::Authenticator'):
            print(f'New AuthServer: {service_id}')
            self.authenticatorList.append(IceFlix.AuthenticatorPrx.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New CatalogServer: {service_id}')
            self.catalogList.append(IceFlix.MediaCatalogPrx.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::FileService'):
            print(f'New FileServer: {service_id}')
            self.fileList.append(IceFlix.FileServicePrx.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::Main'):
            print(f'New MainServer: {service_id}')
            self.mains.update({service_id:proxy})

class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""
    def __init__(self):
        super().__init__()
        self.timerr = threading.Timer(3, print("First Main!!"))
        self.servant = Main(self.timerr)
        self.proxy = None
        self.adapter = None

    def annoucement(self, servant, proxy):
        servant.announce(proxy, str(uuid.uuid4()))
        timer = threading.Timer((10+random.randint(-2,2)), self.annoucement, (servant, proxy))
        timer.start()

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")
        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.proxy = self.adapter.addWithUUID(self.servant)
        self.adapter.activate()

        self.servant.newService(self.proxy, str(uuid.uuid4()))

        self.timerr.start()

        timer = threading.Timer(10, self.annoucement, (self.servant, self.proxy))
        timer.start()

        print("Main Server: " +str(self.proxy), flush=True)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()
        timer.cancel()
        self.timerr.cancel()

        return 0

Main = MainApp()
sys.exit(Main.main(sys.argv))