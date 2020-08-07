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
        """ Instance attributes:
                self.devices (list): the list that will receive the devices to be configured.
                self.connection_type (None): ssh/telnet depending on  the user's choice.
                self.obj_connect (None): ssh/telnet client object depending on the user's choice.
        """
        self.devices = []
        self.connection_method = None
        self.obj_connect = None

    def get_device_type(self):
        """ Menu to choose the type of device to be configured.
            Returns:
                str: the device type to be configured.
        """
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
        """ Menu to choose if the manager will configure 1 or more devices."""
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
                    self.get_connection_method()
                    self.create_individual_device_obj()
                else:
                    pass
                    # self.create_multiples_devices_obj()
            else:
                self.individual_or_multiple_devices()

    def create_individual_device_obj(self):
        """ Asks the device info, create the Device object then put it into devices list."""
        device_type = self.get_device_type()
        auxiliar_functions.clear()
        print("\r\n               CONFIGURING INDIVIDUAL DEVICE\n")
        while True:
            try:
                ip_addr = auxiliar_functions.validate_ip(input("[->] IP address of the device: "))
            except ValueError as error:
                print(error)
                sleep(0.5)
                auxiliar_functions.clear()
            else:
                break
        vty_username = input("[->] VTY Username (leave empty if not required): ")
        vty_password = getpass(prompt="[->] VTY Password: ")
        enable_secret = getpass(prompt="[->] Enable secret: ")
        self.devices.append(Device(device_type, ip_addr[1], vty_username, vty_password, enable_secret))

    def configure_devices(self):
        """ Starts the configuration of devices on the devices list. """
        code = self.choose_script()
        while code not in list(range(11)):
            code = self.choose_script()
        for device in self.devices:
            if not device.is_configured:
                self.connect_to_device(device)
                device.export_interfaces_info('ip', self.obj_connect)
                auxiliar_functions.clear()
                variables = {"DEVICE_HOSTNAME": "",
                             "ENABLE_PASSWORD": device.enable_secret}
                keys = list(variables.keys())   # keywords that will be replaced if found on 'config.json' commands.
                with open(os.path.join(FILES_FOLDER, 'config.json'), "r") as file:
                    data = json.load(file)
                    if code == 0:
                        print("\n" + " " * 20 + "DEFAULT CONFIG\n")
                        commands = list(data['DEFAULT_CONFIG'].values())[0]
                        [self.send_command(command, keys, variables) for command in commands]
                        print("\n\n" + " " * 20 + "Default config done!")
                        sleep(2)
                        if len(self.devices) == 1:
                            self.configure_devices()
                        else:
                            device.is_configured = True
                            self.configure_devices()
                    elif code == 1:
                        print("\n" + " " * 20 + "SET HOSTNAME\n")
                        variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
                        commands = list(data['SET_HOSTNAME'].values())[0]
                        [self.send_command(command, keys, variables) for command in commands]
                        print("\n\n" + " " * 20 + "Hostname config done!")
                        sleep(2)
                        if len(self.devices) == 1:
                            self.configure_devices()
                        else:
                            device.is_configured = True
                            self.configure_devices()
                    elif code == 8:
                        print("\n" + " " * 12 + "SHOW DEVICE INTERFACES STATUS\n")
                        commands = list(data['SHOW_INTERFACES_STATUS'].values())[0]
                        [self.send_command(command, keys, variables) for command in commands]
                        input("\n\n[->] Press enter to continue..")
                        if len(self.devices) == 1:
                            self.configure_devices()
                        else:
                            device.is_configured = True
                            self.configure_devices()
                    elif code == 9:
                        print("\n" + " " * 12 + "SHOW DEVICE INTERFACES IP\n")
                        commands = list(data['SHOW_INTERFACES_IP'].values())[0]
                        [self.send_command(command, keys, variables) for command in commands]
                        input("\n\n[->] Press enter to continue..")
                        if len(self.devices) == 1:
                            self.configure_devices()
                        else:
                            device.is_configured = True
                            self.configure_devices()
                    elif code == 10:
                        self.devices.pop()
                        auxiliar_functions.close()

    def choose_script(self):
        """ Menu to choose the script to run on the device(s).
            Returns:
                int: the code of the choosen option.
         """
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

    def get_connection_method(self):
        """ Asks the connection method to use when connecting to device(s)."""
        auxiliar_functions.clear()
        try:
            option = int(input("""
            \r                   CONNECTION TYPE\n
            \r[0] Configure over Telnet
            \r[1] Configure over SSH\n
            \r--> """))
        except ValueError:
            self.get_connection_method()
        else:
            if option not in (0, 1):
                self.get_connection_method()
            else:
                if option == 0:
                    self.connection_method = "telnet"
                else:
                    self.connection_method = "ssh"

    def connect_to_device(self, device):
        """ Creates the object client (ssh or telnet) then connect to device.
            Params:
                device (class Device): the device which the manager will connect to.
        """
        if self.connection_method == "telnet":
            try:
                self.obj_connect = Telnet(device.ip_address, "23", 5)
                # self.obj_connect.set_debuglevel(1) # uncomment this line to enable debug for Telnet obj.
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
        """ Handle the command and send it to the device.
            Args:
                command (str): command that sits on the 'config.json' file to be handle and sent.
                keys (list): the list with the keywords to be replaced if found on command.
                variables (dict): the dict with the keywords ant its values to help replacing strings.
        """
        found_key = list(filter(lambda key: key in command, keys))  # founds commands to be replaced.
        if len(found_key) > 0:
            self.obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
            self.identify_errors()
            sleep(0.6)  # timeout before send another command to prevent errors.
        else:
            self.obj_connect.write(command.encode('ascii'))
            self.identify_errors()
            sleep(0.6)

    def identify_errors(self):
        """ Handle the command output to verify if there is errors based on a dict with some errors keywords
            and its descriptions."""
        errors_dict = {'% Login invalid': '\n\n[!] Invalid VTY login credentials!',
                       '% Bad passwords': '\n\n[!] Invalid VTY password!',
                       '% Bad secrets': '\n\n[!] Invalid secret!',
                       '% No password set': '\n\n[!] No enable password configured on device! Cant run scripts.',
                       'Translating': '\n\n[!] Username not configured on device. Set a username or leave it blank.'}
        errors_keywords = [key for key in errors_dict]
        line = self.obj_connect.read_very_eager().decode('ascii')
        found_error = list(filter(lambda error: error in line, errors_keywords))
        if len(found_error) > 0:
            print(errors_dict[found_error[0]])
            sleep(2)
            self.devices.pop()
            self.create_individual_device_obj()
            self.configure_devices()
        else:
            print(line, end='')

    def start_manager(self):
        self.individual_or_multiple_devices()
        self.configure_devices()
