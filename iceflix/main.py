"""Module containing a template for a main service."""

#pylint: disable=line-too-long

import logging
import sys
import uuid
import threading
import random

import Ice
import IceStorm
Ice.loadSlice('iceflix/iceflix.ice')
import IceFlix  # pylint:disable=import-error, wrong-import-position

logging.basicConfig(level=logging.DEBUG)

ID_SERVER = str(uuid.uuid4())

class Announcement(IceFlix.Announcement):
    "Announcement class"
    def __init__(self):
        logging.debug("Initializing Announcement class.")
        self.authenticator_list = {}
        self.catalog_list = {}
        self.file_list = {}
        self.mains = {}
        self.timers = {}

    def remove_service(self, serviceId, list_name, current=None): # pylint:disable=invalid-name, unused-argument
        "Removing a service."
        logging.debug("Removing service %s from %s", serviceId, list_name)
        if serviceId in self.timers:
            self.timers[serviceId].cancel()
        if list_name == "authenticator_list":
            del self.authenticator_list[serviceId]
        elif list_name == "catalog_list":
            del self.catalog_list[serviceId]
        elif list_name == "file_list":
            del self.file_list[serviceId]
        elif list_name == "mains":
            del self.mains[serviceId]
        del self.timers[serviceId]

    def announce(self, service, serviceId, current=None): # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        logging.debug("Received announcement from service: %s", serviceId)
        services = list(self.authenticator_list.values()) + list(self.catalog_list.values()) + list(self.file_list.values()) + list(self.mains.values())
        if service not in services:
            if serviceId != ID_SERVER:
                if service.ice_isA('::IceFlix::Authenticator'):
                    logging.debug('New AuthServer: %s', serviceId)
                    # check if there is a timer for this service
                    if serviceId in self.timers:
                        self.timers[serviceId].cancel()
                    self.timers[serviceId] = threading.Timer(10, self.remove_service, args=(serviceId, 'authenticator_list'))
                    self.timers[serviceId].start()
                    self.authenticator_list[serviceId] = IceFlix.AuthenticatorPrx.uncheckedCast(service)

                if service.ice_isA('::IceFlix::MediaCatalog'):
                    logging.debug('New CatalogServer: %s' ,serviceId)
                    # check if there is a timer for this service
                    if serviceId in self.timers:
                        self.timers[serviceId].cancel()
                    self.timers[serviceId] = threading.Timer(10, self.remove_service, args=(serviceId, 'catalog_list'))
                    self.timers[serviceId].start()
                    self.catalog_list[serviceId] = IceFlix.MediaCatalogPrx.uncheckedCast(service)

                if service.ice_isA('::IceFlix::FileService'):
                    logging.debug('New FileServer: %s', serviceId)
                    # check if there is a timer for this service
                    if serviceId in self.timers:
                        self.timers[serviceId].cancel()
                    self.timers[serviceId] = threading.Timer(10, self.remove_service, args=(serviceId, 'file_list'))
                    self.timers[serviceId].start()
                    self.file_list[serviceId] = IceFlix.FileServicePrx.uncheckedCast(service)

                if service.ice_isA('::IceFlix::Main'):
                    logging.debug('New MainServer: %s', serviceId)
                    # check if there is a timer for this service
                    if serviceId in self.timers:
                        self.timers[serviceId].cancel()
                    self.timers[serviceId] = threading.Timer(10, self.remove_service, args=(serviceId, 'mains'))
                    self.timers[serviceId].start()
                    self.mains[serviceId] = IceFlix.MainPrx.uncheckedCast(service)
        else:
            logging.debug("Announcement from service: %s has not been stored", serviceId)

class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """
    def __init__(self, annoucement_server, timer):
        logging.debug("Initializing Main class.")
        self._id_ = ID_SERVER
        self.announcement = annoucement_server
        self.timer = timer

    def getAuthenticator(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        proxies = list(self.announcement.authenticator_list.values())
        if len(proxies) != 0:
            found = False
            while not found:
                random_key = random.choice(list(self.announcement.authenticator_list.keys()))
                random_proxy = self.announcement.authenticator_list[random_key]
                try:
                    random_proxy.ice_ping()
                    found = True
                    logging.debug("Returning an Authenticator proxy")
                    return IceFlix.AuthenticatorPrx.checkedCast(random_proxy)
                except ConnectionRefusedError as exception:
                    logging.error("Connection error: %s", exception)
                    del self.announcement.authenticator_list[random_key]
        raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current=None):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
        proxies = list(self.announcement.catalog_list.values())
        if len(proxies) != 0:
            found = False
            while not found:
                random_key = random.choice(list(self.announcement.catalog_list.keys()))
                random_proxy = self.announcement.catalog_list[random_key]
                try:
                    random_proxy.ice_ping()
                    found = True
                    logging.debug("Returning a Catalog proxy")
                    return IceFlix.MediaCatalogPrx.checkedCast(random_proxy)
                except ConnectionRefusedError as exception:
                    logging.error("Connection error: %s", exception)
                    del self.announcement.catalog_list[random_key]
        raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current=None): # pylint:disable=invalid-name, unused-argument
        "Return the stored FileService proxy."
        proxies = list(self.announcement.file_list.values())
        if len(proxies) != 0:
            found = False
            while not found:
                random_key = random.choice(list(self.announcement.file_list.keys()))
                random_proxy = self.announcement.file_list[random_key]
                try:
                    random_proxy.ice_ping()
                    found = True
                    logging.debug("Returning a File proxy")
                    return IceFlix.FileServicePrx.checkedCast(random_proxy)
                except ConnectionRefusedError as exception:
                    logging.error("Connection error: %s", exception)
                    del self.announcement.file_list[random_key]
        raise IceFlix.TemporaryUnavailable()


class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""
    def __init__(self):
        logging.debug("Initializing Main App.")
        super().__init__()
        self.timer = None
        self.timerr = None
        self.adapter = None
        self.servant = None
        self.proxy = None

    def first_service(self, current=None):# pylint:disable=unused-argument
        """Method to the first Service"""
        print("First Main!!")

    def annoucement(self, announcement_server_proxy, proxy, current=None): # pylint:disable=unused-argument
        """Annoucement method"""
        announcement_server_proxy.announce(proxy, ID_SERVER)
        self.timer = threading.Timer(10, self.annoucement, args=(announcement_server_proxy, proxy))
        self.timer.start()

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")

        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        announcement_server = Announcement()

        #topic_manager_str_prx = "IceStorm/TopicManager -t:tcp -h localhost -p 10000"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(self.communicator().propertyToProxy("IceStorm.TopicManager")) #pylint: disable=no-member
        if not topic_manager:
            raise RuntimeError("Invalid TopicManager proxy")

        topic_name = "Announcements"
        try:
            topic = topic_manager.create(topic_name)
        except IceStorm.TopicExists: #pylint: disable=no-member
            topic = topic_manager.retrieve(topic_name)

        announcement_server_proxy = self.adapter.addWithUUID(announcement_server)
        topic.subscribeAndGetPublisher({}, announcement_server_proxy)

        self.timerr = threading.Timer(3, self.first_service)

        self.servant = Main(announcement_server, self.timerr)
        self.proxy = self.adapter.addWithUUID(self.servant)

        self.adapter.activate()

        publisher = topic.getPublisher()
        announcement_server_proxy = IceFlix.AnnouncementPrx.uncheckedCast(publisher)
        if not announcement_server_proxy:
            raise RuntimeError("Invalid publisher proxy")

        announcement_server_proxy.announce(self.proxy, ID_SERVER)

        self.timerr.start()

        self.timer = threading.Timer(10, self.annoucement, args=(announcement_server_proxy, self.proxy))
        self.timer.start()

        print("Main Server: " +str(self.proxy), flush=True)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()
        self.timerr.cancel()
        self.timer.cancel()

        return 0

app = MainApp()
sys.exit(app.main(sys.argv))
