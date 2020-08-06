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
        print("\r\n               CONFIGURING INDIVIDUAL DEVICE\n")
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
        enable_secret = getpass(prompt="[->] Enable secret: ")
        self.devices.append(Device(device_type, ip_addr[1], vty_username, vty_password, enable_secret))

    def configure_device(self):
        code = self.choose_script()
        while code not in list(range(10)):
            code = self.choose_script()
        for device in self.devices:
            self.connect_to_device(device)
            device.export_interfaces_info('ip', self.obj_connect)
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
                elif code == 8:
                    print("\n" + " " * 12 + "SHOW DEVICE INTERFACES STATUS\n")
                    commands = list(data['SHOW_INTERFACES_STATUS'].values())[0]
                    [self.send_command(command, keys, variables) for command in commands]
                    input("\n\n[->] Press enter to continue..")
                    self.configure_device()
                elif code == 9:
                    print("\n" + " " * 12 + "SHOW DEVICE INTERFACES STATUS\n")
                    commands = list(data['SHOW_INTERFACES_IP'].values())[0]
                    [self.send_command(command, keys, variables) for command in commands]
                    input("\n\n[->] Press enter to continue..")
                    self.configure_device()
                elif code == 10:
                    auxiliar_functions.close()

    def choose_script(self):
        auxiliar_functions.clear()
        try:
            code = int(input("""
            \r                    SCRIPTS\n
            \r[0] Load default
            \r[1] Set Hostname
            \r[2] Create VLANs
            \r[3] Setup VLANs
            \r[4] Setup SSH access
            \r[5] VTP mode access
            \r[6] VTP mode trunk
            \r[7] Erase NVRAM
            \r[8] Show interfaces status
            \r[9] Show interfaces IPs
            \r[10] Exit\n
            \r--> """))
        except ValueError:
            self.choose_script()
        else:
            return code

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
            try:
                self.obj_connect = Telnet(device.ip_address, "23", 5)
                # self.obj_connect.set_debuglevel(1)
            except OSError:
                print("\n[!] Could not connect. Host is unreachable.")
                sleep(2)
                self.devices.pop()
                self.create_individual_device_obj()
                self.connect_to_device(self.devices[-1])
            else:
                if device.vty_username != "":
                    self.obj_connect.read_until(b"Username:", 2)
                    self.obj_connect.write(device.vty_username.encode('ascii') + b"\n")
                    sleep(0.5)
                self.obj_connect.read_until(b"Password:", 2)
                self.obj_connect.write(device.vty_password.encode('ascii') + b"\n")
                sleep(0.5)
                self.identify_errors()
                self.obj_connect.write(b"enable\n")
                self.obj_connect.read_until(b"Password:", 2)
                self.obj_connect.write(device.enable_secret.encode('ascii') + b"\n")
                sleep(0.5)
                self.identify_errors()

    def send_command(self, command, keys, variables):
        found_key = list(filter(lambda key: key in command, keys))		# search for strings to be replaced on command
        if len(found_key) > 0:		# if there is string to replace...
            self.obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
            self.identify_errors()
            sleep(1)
        else:
            self.obj_connect.write(command.encode('ascii'))
            self.identify_errors()
            sleep(1)

    def identify_errors(self):
        errors_dict = {'% Login invalid': '\n\n[!] Invalid VTY login credentials!',
                       '% Bad passwords': '\n\n[!] Invalid VTY password!',
                       '% Bad secrets': '\n\n[!] Invalid secret!',
                       '% No password set': '\n\n[!] No enable password configured on device!',
                       'Translating': '\n\n[!] Username not configured on device. Set a username or leave it blank.'}
        errors_keys = [key for key in errors_dict]
        line = self.obj_connect.read_very_eager().decode('ascii')
        found_error = list(filter(lambda error: error in line, errors_keys))
        if len(found_error) > 0:
            print(errors_dict[found_error[0]])
            sleep(2)
            self.devices.pop()
            self.create_individual_device_obj()
            self.connect_to_device(self.devices[-1])
        else:
            print(line, end='')

    def start_manager(self):
        self.individual_or_multiple_devices()
        self.configure_device()
