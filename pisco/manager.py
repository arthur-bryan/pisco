from telnetlib import Telnet
from paramiko import SSHClient, AutoAddPolicy
from pisco import auxiliar_functions
from time import sleep
import os
import json
import sys

config_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')


class Manager:

    def __init__(self):
        """ Instance attributes:
                self.devices (list): the list that will receive the devices to be configured.
                self.connection_type (None): ssh/telnet depending on  the user's choice.
                self.obj_connect (None): ssh/telnet client object depending on the user's choice.
                self.terminal_virtual (None): the shell invoket by SSHClient.
        """
        self.__devices = []
        self.__obj_connect = None
        self.__virtual_terminal = None

    def add_device(self, device):
        self.__devices.append(device)

    def configure_devices(self):
        """ Starts the configuration of devices on the devices list. """
        try:
            commands_code = self.choose_script()
        except Exception as e:
            print(f"[ ! ] {e}.")
            self.configure_devices()
        else:
            while commands_code not in list(range(13)):
                commands_code = self.choose_script()
            for device in self.__devices:
                if device.connection_protocol == 'TELNET':
                    try:
                        self.login_over_telnet(device)
                        self.send_commands_over_telnet(device, commands_code)
                    except Exception as e:
                        print(e)
                        auxiliar_functions.close()
                else:
                    try:
                        self.login_over_ssh(device)
                        self.send_commands_over_ssh(device, commands_code)
                    except Exception as e:
                        print(e)
                        auxiliar_functions.close()

    def choose_script(self):
        """ Menu to choose the script to run on the device(s).
            Returns:
                int: the code of the choosen option.
         """
        auxiliar_functions.clear()
        commands_code = int(input("""
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
        \r[12] Exit\n
        \r--> """))
        return commands_code

    def login_over_telnet(self, device):
        """ Connect to the device by a telnet client.
            Args:
                device: the device which the manager will connect to.
        """
        try:
            self.__obj_connect = Telnet(device.ip_address, "23", 5)
            # self.obj_connect.set_debuglevel(1) # uncomment this line to enable debug for Telnet obj.
        except Exception as error:
            print(f"[ ! ] {error}.")
            auxiliar_functions.close()
        else:
            if device.vty_username != "":
                self.__obj_connect.read_until(b"Username:", 2)
                self.__obj_connect.write(device.vty_username.encode('ascii') + b"\n")
                sleep(0.5)
            self.__obj_connect.read_until(b"Password:", 2)
            self.__obj_connect.write(device.vty_password.encode('ascii') + b"\n")
            sleep(0.5)
            self.identify_errors(device)
            self.__obj_connect.write(b"enable\n")
            self.__obj_connect.read_until(b"Password:", 2)
            self.__obj_connect.write(device.enable_secret.encode('ascii') + b"\n")
            sleep(0.5)
            self.identify_errors(device)

    def login_over_ssh(self, device):
        """ Connect to the device by a SSH client.
            Args:
                device: the device which the manager will connect to.
        """
        self.__obj_connect = SSHClient()
        self.__obj_connect.load_system_host_keys()
        self.__obj_connect.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.__obj_connect.connect(device.ip_address, 22, device.vty_username, device.vty_password)
            self.__virtual_terminal = self.__obj_connect.invoke_shell()
        except Exception as error:
            print(f"[ ! ] {error}")
            self.__obj_connect.close()
            auxiliar_functions.close()
        else:
            self.identify_errors(device)
            self.__virtual_terminal.send(b"enable\n")
            sleep(0.5)
            self.__virtual_terminal.send(device.enable_secret.encode() + b"\n")
            sleep(0.5)
            self.identify_errors(device)

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
        codes_dict = {0: 'DEFAULT_CONFIG', 1: 'SET_HOSTNAME', 4: 'SETUP_SSH_ONLY',
                      5: 'SETUP_TELNET_ONLY', 6: 'SETUP_SSH_TELNET', 10: 'SHOW_INTERFACES_STATUS',
                      11: 'SHOW_INTERFACES_IP'}
        with open(config_file, "r") as file:
            data = json.load(file)
            if code == 1:
                variables["DEVICE_HOSTNAME"] = input("[ -> ] Set hostname: ")
            elif code == 12:
                auxiliar_functions.close()
            commands = list(data[codes_dict[code]].values())[0]
            for command in commands:
                found_key = list(filter(lambda key: key in command, keys))  # found commands to be replaced.
                if len(found_key) > 0:
                    self.__obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
                    self.identify_errors(device)
                    sleep(0.6)  # timeout before send another command to prevent errors.
                else:
                    self.__obj_connect.write(command.encode('ascii'))
                    self.identify_errors(device)
                    sleep(0.6)
            if code in range(10, 12):
                input("\n\r[->] Press enter to continue...")

    def send_commands_over_ssh(self, device, code):
        """ Run the commands on the tevice over SSH according to code.
            Args:
                device: the device which will receive the commands.
                code (int): the script code choosen to run on thevice.
        """
        variables = {"DEVICE_HOSTNAME": "",
                     "ENABLE_PASSWORD": device.enable_secret,
                     "DOMAIN_NAME": device.domain_name}
        keys = list(variables.keys())  # keywords that will be replaced if found on 'config.json' commands.
        codes_dict = {0: 'DEFAULT_CONFIG', 1: 'SET_HOSTNAME', 4: 'SETUP_SSH_ONLY',
                      5: 'SETUP_TELNET_ONLY', 6: 'SETUP_SSH_TELNET', 10: 'SHOW_INTERFACES_STATUS',
                      11: 'SHOW_INTERFACES_IP'}
        with open(config_file, "r") as file:
            data = json.load(file)
            if code == 1:
                variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
            elif code == 10:
                auxiliar_functions.close()
            commands = list(data[codes_dict[code]].values())[0]
            for command in commands:
                found_key = list(filter(lambda key: key in command, keys))
                if len(found_key) > 0:
                    self.__virtual_terminal.send(command.replace(found_key[0], variables[found_key[0]]))
                    self.identify_errors(device)
                    sleep(0.6)
                else:
                    self.__virtual_terminal.send(command.encode())
                    self.identify_errors(device)
                    sleep(0.6)
            if code in range(10, 12):
                input("\n\n[ -> ] Press enter to continue...")

    def identify_errors(self, device):
        """ Handle the command output to verify if there is errors based on a dict with some errors keywords
            and its descriptions."""

        def find_error_on_line(output_line):
            found_error = list(filter(lambda error: error in output_line, errors_keywords))
            if len(found_error) > 0:
                print(f"[ ! ] {errors_dict[found_error[0]]}.")
                self.__devices.pop()
            else:
                print(output_line, end='')

        errors_dict = {'% Login invalid': "\n\n[!] Invalid VTY login credentials!",
                       '% Bad passwords': "\n\n[!] Invalid VTY password!",
                       '% Bad secrets': "\n\n[!] Invalid secret! Can't configure",
                       '% No password set': "\n\n[!] No enable password configured on device! Cant run scripts.",
                       'Translating': "\n\n[!] Username not configured on device. Set a username or leave it blank."}
        errors_keywords = [key for key in errors_dict]
        if device.connection_protocol == 'TELNET':
            errors_keywords = [key for key in errors_dict]
            line = self.__obj_connect.read_very_eager().decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.__obj_connect.write(b'yes\n')
                sleep(1)
                self.__obj_connect.write(b'2048\n')
                sleep(2)
            find_error_on_line(line)
        else:
            line = self.__virtual_terminal.recv(65535).decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.__virtual_terminal.send(b'yes\n')
                sleep(1)
                self.__virtual_terminal.send(b'2048\n')
                sleep(2)
            find_error_on_line(line)
