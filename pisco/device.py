from time import sleep
import os


class Device:
    """ The class that represents the device to be configured and its attributes."""

    def __init__(self, ip_address, vty_password, enable_secret, vty_username=""):
        """ Args:
                ip_address (str): The device IP address that will be used by the manager to stablish econnection.
                vty_password (str): The VTY password to access de device.
                enable_secret (str): The secret of the enable mode to configure the device.
                vty_username (str, optional): The username to connect to device. (Default "" means no user required.

        """
        self.__connection_protocol = None
        self.__domain_name = "lan.com"
        self.ip_address = ip_address
        self.vty_username = vty_username if vty_username != "" else ""
        self.vty_password = vty_password
        self.enable_secret = enable_secret
        self.__interfaces = []

    @property
    def connection_protocol(self):
        """ str: Specifies the protocol used to remote access (Telnet/SSH). """

        return self.__connection_protocol

    @connection_protocol.setter
    def connection_protocol(self, protocol):
        if protocol.upper() == 'TELNET':
            self.__connection_protocol = 'TELNET'
        elif protocol.upper() == 'SSH':
            self.__connection_protocol = 'SSH'
        else:
            raise ValueError(f"[ ! ] Invalid protocol: {protocol}.")

    @property
    def domain_name(self):
        """ str: The domain name used in some IP configurations like setting up SSH. Default is 'lan.com'."""

        return self.__domain_name

    @domain_name.setter
    def domain_name(self, domain):
        try:
            self.__domain_name = domain
        except Exception as e:
            print(f"[ ! ] {e}.")


