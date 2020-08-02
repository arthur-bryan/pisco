from modules import auxiliar_functions


class Device:

    def __init__(self, device_type, ip_address, vty_username, vty_password, enable_secret):
        self.device_type = device_type
        self.ip_address = ip_address
        self.vty_username = vty_username
        self.vty_password = vty_password
        self.enable_secret = enable_secret
        self.interfaces = []
