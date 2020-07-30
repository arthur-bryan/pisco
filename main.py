from telnetlib import Telnet
from time import sleep
from getpass import getpass
from validations import validate_ip

class IndividualDevice:
    def __init__(self, enable_password=None):
        self.ip_addr = None
        self.vty_username = None
        self.vty_password = None
        self.enable_password = None


    def get_device_info(self):
        while self.ip_addr == None:
            try:
                self.ip_addr = validate_ip(input("[->] IP address of the device: "))[1]
            except ValueError as e:
                print(e)
        self.vty_username = input("[->] VTY Username: ")
        self.vty_password = getpass(prompt="[->] VTY Password: ")
        self.enable_password = getpass(prompt="[->] Enable secret: ")


    def telnet_connection(self):
        self.get_device_info()
        tn = Telnet(self.ip_addr, "23")
        tn.set_debuglevel(1)
        tn.read_until(b"Username:", 2)
        tn.write(self.vty_username.encode('ascii') + b"\n")
        tn.read_until(b"Password:", 2)
        tn.write(self.vty_password.encode('ascii') + b"\n")
        sleep(1)
        while True:
            print(tn.read_very_eager())
            tn.write(input("Command: ").encode('ascii') + b"\n")
            sleep(1)
        tn.close()

def main():
    device = IndividualDevice()
    device.telnet_connection()


if __name__ == '__main__':
    main()

