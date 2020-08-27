from telnetlib import Telnet
from paramiko import SSHClient, AutoAddPolicy
from pisco import auxiliar_functions
from time import sleep
import os
import json

config_file = os.path.join(os.path.dirname(__file__), 'data', 'config.json')	# file with commands that will be run based on choosen script.


class Manager:
    """ The class that holds the methods used to configure the devices. """

    def __init__(self):
        self.__devices = []
        self.__obj_connect = None
        self.__virtual_terminal = None

    def add_device(self, device):
        """ Add the device (obj) to the list of devices to be configured.

            Args:
                device (:obj: `Device`): The device to be added.

        """
        self.__devices.append(device)

    def configure_devices(self):
        """ Starts the configuration of devices on the devices list. """
        try:
            commands_code = self.__choose_script()
        except Exception as e:
            print(f"[ ! ] {e}.")
            self.configure_devices()
        else:
            while commands_code not in list(range(13)):
                commands_code = self.__choose_script()
            for _, device in enumerate(self.__devices):
                auxiliar_functions.clear()
                print(f"\n[ + ] CONFIGURING  THE {_+1}º DEVICE...\n")
                if device.connection_protocol == "TELNET":
                    try:
                        self.__login_over_telnet(device)
                        self.__send_commands(device, commands_code)
                    except Exception as e:
                        print(e)
                        auxiliar_functions.close()
                else:
                    try:
                        self.__login_over_ssh(device)
                        self.__send_commands(device, commands_code)
                    except Exception as e:
                        print(e)
                    auxiliar_functions.close()

    def __choose_script(self):
        """ Menu of scripts to run on the device(s).

            Returns:
                commands_code (int): The code of the choosen option.

         """
        auxiliar_functions.clear()
        commands_code = int(input("""
 _______  ___   _______  _______  _______
|       ||   | |       ||       ||       |
|    _  ||   | |  _____||       ||   _   |
|   |_| ||   | | |_____ |       ||  | |  |
|    ___||   | |_____  ||      _||  |_|  |
|   |    |   |  _____| ||     |_ |       |
|___|    |___| |_______||_______||_______|
                v0.1.0a

        \r                SCRIPTS\n
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

    def __login_over_telnet(self, device):
        """ Creates an Telnet client object, then tries to login to the device using its attributes.

            Args:
                device (:obj: `Device`): The device that the manager will connect to.

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
            self.__identify_errors(device)
            self.__obj_connect.write(b"enable\n")
            self.__obj_connect.read_until(b"Password:", 2)
            self.__obj_connect.write(device.enable_secret.encode('ascii') + b"\n")
            sleep(0.5)
            self.__identify_errors(device)

    def __login_over_ssh(self, device):
        """ Creates an SSHClient object, load the keys, then tries to login to the device using its attributes.

            Args:
                device (:obj: `Device`): The device that the manager will connect to.

        """
        self.__obj_connect = SSHClient()
        self.__obj_connect.load_system_host_keys()
        self.__obj_connect.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.__obj_connect.connect(device.ip_address, 22, device.vty_username, device.vty_password)
            self.__virtual_terminal = self.__obj_connect.invoke_shell() # Opens a virtual shell to run commands.
        except Exception as error:
            print(f"[ ! ] {error}")
            self.__obj_connect.close()
            auxiliar_functions.close()
        else:
            self.__identify_errors(device)
            self.__virtual_terminal.send(b"enable\n")
            sleep(0.5)
            self.__virtual_terminal.send(device.enable_secret.encode() + b"\n")
            sleep(0.5)
            self.__identify_errors(device)

    def __send_commands(self, device, code):
        """ Loads the config file and run the commands based on the choosen code.

            Args:
                device (:obj: `Device`): The device that will receive the commands.
                code (int): The script code choosen to run on thevice.

        """
        variables = {"DEVICE_HOSTNAME": "",
                     "ENABLE_PASSWORD": device.enable_secret,
                     "DOMAIN_NAME": device.domain_name,
                     "VLAN_NUMBER": None}
        keys = list(variables.keys())  # keywords that will be replaced if found on 'config.json' commands.
        codes_dict = {0: 'DEFAULT_CONFIG', 1: 'SET_HOSTNAME', 3: "CREATE_VLAN", 4: 'SETUP_SSH_ONLY',
                      5: 'SETUP_TELNET_ONLY', 6: 'SETUP_SSH_TELNET', 10: 'SHOW_INTERFACES_STATUS',
                      11: 'SHOW_INTERFACES_IP'}
        with open(config_file, "r") as file:
            data = json.load(file)
            if code == 1:
                variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
            elif code == 3:
                vlans_to_create = input("\n\n[ -> ] Type the number of each VLAN separated by commas (eg: 5,15,20): ").split(',')
                for vlan in vlans_to_create:
                    if int(vlan) not in range(3968, 4048) and int(vlan) != 4094:
                        variables["VLAN_NUMBER"] = vlan
                        commands = list(data[codes_dict[code]].values())[0]
                        if device.connection_protocol == "SSH":
                            for command in commands:
                                found_key = list(filter(lambda key: key in command, keys))
                                if len(found_key) > 0:
                                    self.__virtual_terminal.send(command.replace(found_key[0], variables[found_key[0]]))
                                    self.__identify_errors(device)
                                    sleep(0.6)
                                else:
                                    self.__virtual_terminal.send(command.encode())
                                    self.__identify_errors(device)
                                    sleep(0.6)
                        else:
                            for command in commands:
                                found_key = list(filter(lambda key: key in command, keys))  # found commands to be replaced.
                                if len(found_key) > 0:
                                    self.__obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
                                    self.__identify_errors(device)
                                    sleep(0.6)  # timeout before send another command to prevent errors.
                                else:
                                    self.__obj_connect.write(command.encode('ascii'))
                                    self.__identify_errors(device)
                                    sleep(0.6)
                auxiliar_functions.close()
            elif code == 12:
                auxiliar_functions.close()
            commands = list(data[codes_dict[code]].values())[0]
            if device.connection_protocol == "SSH":
                for command in commands:
                    found_key = list(filter(lambda key: key in command, keys))
                    if len(found_key) > 0:
                        self.__virtual_terminal.send(command.replace(found_key[0], variables[found_key[0]]))
                        self.__identify_errors(device)
                        sleep(0.6)
                    else:
                        self.__virtual_terminal.send(command.encode())
                        self.__identify_errors(device)
                        sleep(0.6)
            else:
                for command in commands:
                    found_key = list(filter(lambda key: key in command, keys))  # found commands to be replaced.
                    if len(found_key) > 0:
                        self.__obj_connect.write(command.replace(found_key[0], variables[found_key[0]]).encode('ascii'))
                        self.__identify_errors(device)
                        sleep(0.6)  # timeout before send another command to prevent errors.
                    else:
                        self.__obj_connect.write(command.encode('ascii'))
                        self.__identify_errors(device)
                        sleep(0.6)
            if code in range(10, 12):
                input("\n\n[ -> ] Press enter to continue...")

    def __identify_errors(self, device):
        """ Handle the command output to verify if there is errors based on a dict with some errors keywords
            and its descriptions.

            Args:
                device (:obj: `Device`): The current device being configurated.

        """

        def find_error_on_line(output_line):
            """ Verify if the output command line has errors based on a predefined dict.

                Args:
                    output_line (str): The device output command line to be verified.

            """
            found_error = list(filter(lambda error: error in output_line, errors_keywords))
            if len(found_error) > 0:
                print(f"[ ! ] {errors_dict[found_error[0]]}")
                auxiliar_functions.close()
            else:
                print(output_line, end='')

        errors_dict = {'% Login invalid': "\n\n[ ! ] Invalid VTY login credentials!",
                       '% Bad passwords': "\n\n[ ! ] Invalid VTY password!",
                       '% Bad secrets': "\n\n[ ! ] Invalid secret! Can't configure",
                       '% No password set': "\n\n[ ! ] No enable password configured on device! Cant run scripts.",
                       'Translating': "\n\n[ ! ] Username not configured on device. Set a username or leave it blank.",
                       'number which is out of the range 1..4094': "\n\n[ ! ] Invalid vlan number!"}
        errors_keywords = [key for key in errors_dict]
        if device.connection_protocol == 'TELNET':
            errors_keywords = [key for key in errors_dict]
            line = self.__obj_connect.read_very_eager().decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.__obj_connect.write(b'no\n')
            find_error_on_line(line)
        else:
            line = self.__virtual_terminal.recv(65535).decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.__virtual_terminal.send(b'no\n')
            find_error_on_line(line)
