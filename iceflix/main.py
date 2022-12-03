"""Module containing a template for a main service."""

import logging
import sys
import uuid

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

        return


    def announce(self, proxy, service_id, current=None):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        if proxy in (list(authenticatorList) + list(catalogList) + list(fileList) + list(mains.values())) or service_id == str(uuid.uuid4()):
            return

        if proxy.ice_isA('::IceFlix::Authenticator'):
            print(f'New Authenticator service: {service_id}')
            self.authenticatorList.append(IceFlix.AuthenticatorPrx.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::MediaCatalog'):
            print(f'New Catalog service: {service_id}')
            self.catalogList.append(IceFlix.MediaCatalogPrx.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::FileService'):
            print(f'New File service: {service_id}')
            self.fileList.append(IceFlix.FileService.uncheckedCast(proxy))

        if proxy.ice_isA('::IceFlix::Main'):
            print(f'New Main service: {service_id}')
            self.mains.update({service_id:proxy})

class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.servant = Main()
        self.proxy = None
        self.adapter = None

    def initial(self, current=None):
        print("First! Main")

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")
        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()

        self.proxy = self.adapter.addWithUUID(self.servant)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0

Main = MainApp()
sys.exit(Main.main(sys.argv))