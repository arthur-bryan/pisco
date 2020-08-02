from telnetlib import Telnet
from modules import auxiliar_functions
from modules.device import Device
from time import sleep
from getpass import getpass
import os
import json


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "../files")


class Manager:

    def __init__(self):
        self.devices = []
        self.connection_type = None     # telnet or ssh
        self.obj_connect = None     # telnet or ssh client object

    def get_device_type(self):
        auxiliar_functions.clear()
        try:
            device_type = int(input("""
            \r                 Device Type
            \r[0] Switch L2
            \r[1] Switch L3
            \r[2] Router\n
            \r--> """))
        except ValueError:
            self.get_device_type()
        else:
            if device_type in range(3):
                if device_type == 0:
                    return "switch l2"
                elif device_type == 1:
                    return "switch l3"
                else:
                    return "router"
            else:
                self.get_device_type()

    def individual_or_multiple_devices(self):
        auxiliar_functions.clear()
        try:
            option = int(input("""
            \r                    Configure Devices\n
            \r[0] Individual device
            \r[1] Multiple devices\n
            \r--> """))
        except ValueError:
            self.individual_or_multiple_devices()
        else:
            if option in range(2):
                if option == 0:
                    self.get_connection_type()
                    self.create_individual_device_obj()
                else:
                    pass
                    # self.create_multiples_devices_obj()
            else:
                self.individual_or_multiple_devices()

    def create_individual_device_obj(self):
        device_type = self.get_device_type()
        auxiliar_functions.clear()
        print("\n" + " " * 20 + "CONFIGURING INDIVIDUAL DEVICE\n")
        while True:
            try:
                ip_addr = auxiliar_functions.validate_ip(input("[->] IP address of the device: "))
            except ValueError as e:
                print(e)
                sleep(0.5)
                auxiliar_functions.clear()
            else:
                break
        vty_username = input("[->] VTY Username (leave empty if not required): ")
        vty_password = getpass(prompt="[->] VTY Password: ")
        enable_password = getpass(prompt="[->] Enable secret: ")
        self.devices.append(Device(device_type, ip_addr[1], vty_username, vty_password, enable_password))

    def configure_device(self):
        for device in self.devices:
            self.connect_to_device(device)
            code = self.choose_script()
            while code not in list(range(10)):
                code = self.choose_script()
            auxiliar_functions.clear()
            variables = {"DEVICE_HOSTNAME": "",
                         "ENABLE_PASSWORD": device.enable_secret}
            keys = list(variables.keys())
            with open(os.path.join(FILES_FOLDER, 'config.json'), "r") as file:
                data = json.load(file)
                if code == 0:
                    print("\n" + " " * 20 + "DEFAULT CONFIG\n")
                    commands = list(data['DEFAULT_CONFIG'].values())[0]
                    [self.send_command(command, keys, variables) for command in commands]
                    print("\n\n" + " " * 20 + "Default config done!")
                    sleep(2)
                    self.configure_device()
                elif code == 1:
                    print("\n" + " " * 20 + "SET HOSTNAME\n")
                    variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
                    commands = list(data['SET_HOSTNAME'].values())[0]
                    [self.send_command(command, keys, variables) for command in commands]
                    print("\n\n" + " " * 20 + "Hostname config done!")
                    sleep(2)
                    self.configure_device()

    def choose_script(self):
        auxiliar_functions.clear()
        try:
            choice = int(input("""
            \r                    SCRIPTS\n
            \r[0] Load default
            \r[1] Set Hostname
            \r[2] Create VLANs
            \r[3] Setup VLANs
            \r[4] Setup SSH access
            \r[5] VTP mode access
            \r[6] VTP mode trunk
            \r[7] Erase NVRAM
            \r[8] Show interfaces info
            \r[9] Exit\n
            \r--> """))
        except ValueError:
            self.choose_script()
        else:
            return choice

    def get_connection_type(self):
        auxiliar_functions.clear()
        try:
            option = int(input("""
            \r                   CONNECTION TYPE\n
            \r[0] Configure over Telnet
            \r[1] Configure over SSH\n
            \r--> """))
        except ValueError:
            self.get_connection_type()
        else:
            if option not in (0, 1):
                self.get_connection_type()
            else:
                if option == 0:
                    self.connection_type = "telnet"
                else:
                    self.connection_type = "ssh"

    def connect_to_device(self, device):
        if self.connection_type == "telnet":
            while True:
                try:
                    self.obj_connect = Telnet(device.ip_address, "23", 5)
                except OSError:
                    print("\n[!]Cold not connect! Please, verify IP settings.")
                    sleep(2)
                    auxiliar_functions.clear()
                    self.create_individual_device_obj()
                else:
                    break
            if device.vty_username != "":
                self.obj_connect.read_until(b"Username:", 2)
                self.obj_connect.write(device.vty_username.encode('ascii') + b"\n")
                sleep(0.5)
            else:
                self.obj_connect.read_until(b"Password:", 2)
                self.obj_connect.write(device.vty_password.encode('ascii') + b"\n")
                sleep(0.5)
                self.obj_connect.write(b"enable\n")
                self.obj_connect.read_until(b"Password:", 2)
                self.obj_connect.write(device.vty_password.encode('ascii') + b"\n")
                sleep(0.5)

    def send_command(self, command, keys, variables):
        found_key = list(filter(lambda key: key in command, keys))		# search for strings to be replaced on command
        if len(found_key) > 0:		# if there is string to replace...
            self.obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
            print(self.obj_connect.read_very_eager().decode('ascii'), end="")
            sleep(1)
        else:
            self.obj_connect.write(command.encode('ascii'))
            print(self.obj_connect.read_very_eager().decode('ascii'), end="")
            sleep(1)

    def start_manager(self):
        self.individual_or_multiple_devices()
        self.configure_device()
