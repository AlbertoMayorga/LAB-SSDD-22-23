"""Module containing a template for a main service."""

import logging
import sys
import uuid
import threading

import Ice
import IceStorm
Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix  # pylint:disable=import-error

id_server = str(uuid.uuid4())

class Announcement(IceFlix.Announcement):
    def __init__(self):
        self.authenticator_list = []
        self.catalog_list = []
        self.file_list = []
        self.mains = {}

    def announce(self, service, serviceId, current=None):
        "Announcements handler."
        services = list(self.authenticator_list) + list(self.catalog_list) + list(self.file_list) + list(self.mains.values())
        if service not in services:
            if serviceId != id_server:
                if service.ice_isA('::IceFlix::Authenticator'):
                    print(f'New AuthServer: {serviceId}')
                    self.authenticator_list.append(IceFlix.AuthenticatorPrx.uncheckedCast(service))

                if service.ice_isA('::IceFlix::MediaCatalog'):
                    print(f'New CatalogServer: {serviceId}')
                    self.catalog_list.append(IceFlix.MediaCatalogPrx.uncheckedCast(service))

                if service.ice_isA('::IceFlix::FileService'):
                    print(f'New FileServer: {serviceId}')
                    self.file_list.append(IceFlix.FileServicePrx.uncheckedCast(service))

                if service.ice_isA('::IceFlix::Main'):
                    print(f'New MainServer: {serviceId}')
                    self.mains.update({serviceId:service})


class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    def __init__(self, annoucement_server, timer):
        self._id_ = id_server
        self.announcement = annoucement_server
        self.timer = timer

    def getAuthenticator(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        if len(self.annoucement_server.authenticator_list) != 0:
            for i in self.annoucement_server.authenticator_list:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.AuthenticatorPrx.checkedCast(i)
                except Ice.ConnectionRefusedException as exception:
                    print(exception)
        raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
        if len(self.annoucement_server.catalog_list) != 0:
            for i in self.annoucement_server.catalog_list:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.MediaCatalogPrx.checkedCast(i)
                except Ice.ConnectionRefusedException as exception:
                    print(exception)
        raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current=None): # pylint:disable=invalid-name, unused-argument
        "Return the stored FileService proxy."
        if len(self.annoucement_server.file_list) != 0:
            for i in self.annoucement_server.file_list:
                print(i)
                try:
                    i.ice_ping()
                    return IceFlix.FileServicePrx.checkedCast(i)
                except Ice.ConnectionRefusedException as exception:
                    print(exception)
        raise IceFlix.TemporaryUnavailable()


class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""
    def __init__(self):
        super().__init__()
        self.announcement_server = Announcement()
        self.timerr = threading.Timer(3, print("First Main!!"))
        self.servant = Main(self.announcement_server, self.timerr)
        self.proxy = None
        self.adapter = None


    def annoucement(self, announcement_server_proxy, proxy):
        """Annoucement method"""
        announcement_server_proxy.announce(proxy, id_server)
        self.timer = threading.Timer(10, self.annoucement, (announcement_server_proxy, proxy))
        self.timer.start()

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")

        comm = self.communicator()
        self.adapter = comm.createObjectAdapterWithEndpoints('Main', 'tcp')

        topic_manager_str_prx = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(self.communicator().stringToProxy(topic_manager_str_prx), )
        if not topic_manager:
            raise RuntimeError("Invalid TopicManager proxy")
        
        topic_name = "Announcements"
        try: 
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists:
            topic = topic_manager.retrieve(topic_name)

        qos = {}

        announcement_server_proxy = self.adapter.addWithUUID(self.announcement_server)
        publisher = topic.subscribeAndGetPublisher(qos, announcement_server_proxy)

        self.proxy = self.adapter.addWithUUID(self.servant)
        self.adapter.activate()
        print(self.proxy)
        topic.subscribeAndGetPublisher(qos, self.proxy)
        announcement_server_proxy = IceFlix.AnnouncementPrx.uncheckedCast(topic.getPublisher())
        announcement_server_proxy.announce(self.proxy, id_server)

        self.timerr.start()

        self.timer = threading.Timer(10, self.annoucement, (announcement_server_proxy, self.proxy))
        self.timer.start()

        print("Main Server: " +str(self.proxy), flush=True)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()
        self.timer.cancel()
        self.timerr.cancel()

        return 0

Main = MainApp()
sys.exit(Main.main(sys.argv))
