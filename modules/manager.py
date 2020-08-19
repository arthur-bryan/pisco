from telnetlib import Telnet
from paramiko import SSHClient, AutoAddPolicy
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
                self.terminal_virtual (None): the shell invoket by SSHClient.
        """
        self.devices = []
        self.connection_method = None
        self.obj_connect = None
        self.virtual_terminal = None
        self.current_device = 0

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
                    self.get_connection_method()
                    self.create_multiples_devices_obj()
            else:
                self.individual_or_multiple_devices()

    def create_individual_device_obj(self):
        """ Asks the device info, create the Device object then put it into devices list."""
        device_type = self.get_device_type()
        auxiliar_functions.clear()
        while True:
            try:
                ip_addr = auxiliar_functions.validate_ip(input("[->] IP address of the device: "))
            except ValueError as error:
                print(error)
                sleep(1)
                auxiliar_functions.clear()
            else:
                break
        vty_username = input("[->] VTY Username (leave empty if not required): ")
        vty_password = getpass(prompt="[->] VTY Password: ")
        enable_secret = getpass(prompt="[->] Enable secret: ")
        domain_name = input("[->] Domain name (default is lan.com): ")
        self.devices.append(Device(device_type, ip_addr, vty_username, vty_password, enable_secret, domain_name))

    def create_multiples_devices_obj(self):
        device_type = self.get_device_type()
        auxiliar_functions.clear()
        ip_range = list(input("""\n            TYPE THE RANGE OF IP'S\n
              \rSeparate individuals with ',' or use a range with '-', eg:
              \r10.0.0.5,10.0.0.6,10.0.0.10 or 10.0.0.5-10.0.0.20
              \n\n\r[Type the range ->] """).split(','))
        auxiliar_functions.clear()
        print('\n' + ' ' * 10 + "THE CREDENTIALS MUST BE THE SAME IN ALL DEVICES!\n")
        vty_username = input("[->] VTY Username: ")
        vty_password = getpass(prompt="[->] VTY Password: ")
        enable_secret = getpass(prompt="[->] Enable secret: ")
        domain_name = input("[->] Domain name (default is lan.com): ")
        for ip in ip_range:
            string_ip = ""
            if '-' in ip:
                ip = ip.split('-')
                start_half = ip[0].split('.')[0:3]
                for ip_addr in range(int(ip[0].split('.')[-1]), int(ip[1].split('.')[-1]) + 1):
                    for octet in start_half:
                        string_ip += octet + '.'
                    string_ip += str(ip_addr)
                    try:
                        ip_result = auxiliar_functions.validate_ip(string_ip)[1]
                        string_ip = ""
                    except Exception as e:
                        print(e)
                        sleep(1)
                        self.create_multiples_devices_obj()
                    else:
                        if ip_result not in list(map(lambda device: device.ip_address, self.devices)):
                            self.devices.append(Device(device_type, ip_result, vty_username, vty_password,
                                                       enable_secret, domain_name))
            else:
                try:
                    auxiliar_functions.validate_ip(ip)
                except Exception as e:
                    print(e)
                    sleep(1)
                    self.create_multiples_devices_obj()
                else:
                    if ip not in list(map(lambda device: device.ip_address, self.devices)):
                        self.devices.append(Device(device_type, ip, vty_username, vty_password,
                                                   enable_secret, domain_name))

    def configure_devices(self):
        """ Starts the configuration of devices on the devices list. """
        code = self.choose_script()
        while code not in list(range(13)):
            code = self.choose_script()
        if self.connection_method == 'telnet':
            for device in self.devices:
                self.current_device += 1
                self.connect_over_telnet(device)
                device.export_interfaces_info('ip', self.connection_method, self.obj_connect)
                self.send_commands_over_telnet(device, code)
            self.current_device = 0
            self.configure_devices()
        else:
            for device in self.devices:
                self.current_device += 1
                self.connect_over_ssh(device)
                device.export_interfaces_info('status', self.connection_method, self.virtual_terminal)
                self.send_commands_over_ssh(device, code)
            self.current_device = 0
            self.configure_devices()

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
            \r[4] Setup for SSH-only access
            \r[5] Setup for Telnet-only access
            \r[6] Setup allow SSH/Telnet access
            \r[7] VTP mode access
            \r[8] VTP mode trunk
            \r[9] Erase NVRAM
            \r[10] Show interfaces status
            \r[11] Show interfaces IPs
            \r[12] Back\n
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

    def connect_over_telnet(self, device):
        """ Creates the object client (telnet) then connect to device.
            Args:
                device (class Device): the device which the manager will connect to.
        """
        try:
            self.obj_connect = Telnet(device.ip_address, "23", 5)
            # self.obj_connect.set_debuglevel(1) # uncomment this line to enable debug for Telnet obj.
        except Exception as error:
            print(f"\n\n[!]{error}")
            sleep(2)
            auxiliar_functions.close()
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

    def connect_over_ssh(self, device):
        """ Creates the object client (ssh) then connect to device.
            Args:
                device (class Device): the device which the manager will connect to.
        """
        self.obj_connect = SSHClient()
        self.obj_connect.load_system_host_keys()
        self.obj_connect.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.obj_connect.connect(device.ip_address, 22, device.vty_username, device.vty_password)
        except Exception as error:
            print(f"\n\n[!] {error}")
            sleep(2)
            auxiliar_functions.close()
        else:
            self.virtual_terminal = self.obj_connect.invoke_shell()
            self.identify_errors()
            self.virtual_terminal.send(b"enable\n")
            sleep(0.5)
            self.virtual_terminal.send(device.enable_secret.encode() + b"\n")
            sleep(0.5)
            self.identify_errors()

    def send_commands_over_telnet(self, device, code):
        """ Handle the command and send it to the device over telnet client object.
            Args:
                device (class Device): the device which will receive the commands.
                code (int): the script code choosen to run on thevice.
        """
        auxiliar_functions.clear()
        variables = {"DEVICE_HOSTNAME": "",
                     "DOMAIN_NAME": device.domain_name,
                     "ENABLE_PASSWORD": device.enable_secret}
        keys = list(variables.keys())  # keywords that will be replaced if found on 'config.json' commands.
        code_keywords_dict = {0: 'DEFAULT_CONFIG', 1: 'SET_HOSTNAME', 4: 'SETUP_SSH_ONLY',
                              5: 'SETUP_TELNET_ONLY', 6: 'SETUP_SSH_TELNET', 10: 'SHOW_INTERFACES_STATUS',
                              11: 'SHOW_INTERFACES_IP'}
        with open(os.path.join(FILES_FOLDER, 'config.json'), "r") as file:
            data = json.load(file)
            if code == 1:
                variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
            elif code == 12:
                self.devices.clear()
                self.start_manager()
            commands = list(data[code_keywords_dict[code]].values())[0]
            print(f"\n{' '* 20} CONFIGURING {self.current_device}º DEVICE...\n")
            for command in commands:
                found_key = list(filter(lambda key: key in command, keys))  # founds commands to be replaced.
                if len(found_key) > 0:
                    self.obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
                    self.identify_errors()
                    sleep(0.6)  # timeout before send another command to prevent errors.
                else:
                    self.obj_connect.write(command.encode('ascii'))
                    self.identify_errors()
                    sleep(0.6)
            if code in range(10, 12):
                input("\n\n[->] Press enter to continue...")

    def send_commands_over_ssh(self, device, code):
        """ Handle the command and send it to the device over ssh client object.
            Args:
                device (class Device): the device which will receive the commands.
                code (int): the script code choosen to run on thevice.
        """
        auxiliar_functions.clear()
        variables = {"DEVICE_HOSTNAME": "",
                     "ENABLE_PASSWORD": device.enable_secret,
                     "DOMAIN_NAME": device.domain_name}
        keys = list(variables.keys())  # keywords that will be replaced if found on 'config.json' commands.
        code_keywords_dict = {0: 'DEFAULT_CONFIG', 1: 'SET_HOSTNAME', 4: 'SETUP_SSH_ONLY',
                              5: 'SETUP_TELNET_ONLY', 6: 'SETUP_SSH_TELNET', 10: 'SHOW_INTERFACES_STATUS',
                              11: 'SHOW_INTERFACES_IP'}
        with open(os.path.join(FILES_FOLDER, 'config.json'), "r") as file:
            data = json.load(file)
            if code == 1:
                variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
            elif code == 10:
                self.devices.clear()
                auxiliar_functions.close()
            print(f"\n{' '* 20} CONFIGURING {self.current_device}º DEVICE...\n")
            commands = list(data[code_keywords_dict[code]].values())[0]
            for command in commands:
                found_key = list(filter(lambda key: key in command, keys))
                if len(found_key) > 0:
                    self.virtual_terminal.send(command.replace(found_key[0], variables[found_key[0]]))
                    self.identify_errors()
                    sleep(0.6)
                else:
                    self.virtual_terminal.send(command.encode())
                    self.identify_errors()
                    sleep(0.6)
            if code in range(8, 10):
                input("\n\n[->] Press enter to continue...")

    def identify_errors(self):
        """ Handle the command output to verify if there is errors based on a dict with some errors keywords
            and its descriptions."""
        def find_error_on_line(output_line):
            found_error = list(filter(lambda error: error in output_line, errors_keywords))
            if len(found_error) > 0:
                print(errors_dict[found_error[0]])
                sleep(2)
                self.devices.pop()
                self.individual_or_multiple_devices()
                self.configure_devices()
            else:
                print(output_line, end='')

        errors_dict = {'% Login invalid': "\n\n[!] Invalid VTY login credentials!",
                       '% Bad passwords': "\n\n[!] Invalid VTY password!",
                       '% Bad secrets': "\n\n[!] Invalid secret! Can't configure",
                       '% No password set': "\n\n[!] No enable password configured on device! Cant run scripts.",
                       'Translating': "\n\n[!] Username not configured on device. Set a username or leave it blank."}
        errors_keywords = [key for key in errors_dict]
        if self.connection_method == 'telnet':
            errors_keywords = [key for key in errors_dict]
            line = self.obj_connect.read_very_eager().decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.obj_connect.write(b'yes\n')
                sleep(1)
                self.obj_connect.write(b'2048\n')
                sleep(2)
            find_error_on_line(line)
        else:
            line = self.virtual_terminal.recv(65535).decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.virtual_terminal.send(b'yes\n')
                sleep(1)
                self.virtual_terminal.send(b'2048\n')
                sleep(2)
            find_error_on_line(line)

    def start_manager(self):
        self.individual_or_multiple_devices()
        self.configure_devices()
