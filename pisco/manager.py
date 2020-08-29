from telnetlib import Telnet
from paramiko import SSHClient, AutoAddPolicy
from pisco import auxiliar_functions
from time import sleep
import os
import json


class Manager:
    """ The class that holds the methods used to configure the devices. """

    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
    variables = {"DEVICE_HOSTNAME": None,
                 "ENABLE_PASSWORD": None,
                 "DOMAIN_NAME": None,
                 "VLAN_NUMBER": None}
    keys = list(variables.keys())  # keywords that will be replaced if found on 'config.json' commands.
    configuration_keywords = ('DEFAULT_CONFIG', 'SET_HOSTNAME', "CREATE_VLAN", 'ACCESS_SSH_ONLY',
                              'ACCESS_TELNET_ONLY', 'ACCESS_SSH_TELNET', 'SHOW_INTERFACES_STATUS',
                              'SHOW_INTERFACES_IP')
    config_file = open(CONFIG_FILE_PATH, "r")
    config_json = json.load(config_file)

    def __init__(self):
        self.__devices = []
        self.__obj_connect = None
        self.__shell = None

    def add_device(self, device):
        """ Add the device (obj) to the list of devices to be configured.

            Args:
                device (:obj: `Device`): The device to be added.

        """
        self.__devices.append(device)

    def configure_devices(self, *args):
        """ Starts the configuration of devices on the devices list. """
        for _, device in enumerate(self.__devices):
            self.variables['ENABLE_PASSWORD'] = device.enable_secret
            self.variables['DOMAIN_NAME'] = device.domain_name
            auxiliar_functions.clear()
            print(f"\n[ + ] CONFIGURING  THE {_+1}º DEVICE...\n")
            if len(args) < 1:
                print(f"\n\n[ ! ] You must choose at least one configuration (see README or documentation).")
                auxiliar_functions.close()
            if device.connection_protocol == "TELNET":
                try:
                    self.__login_over_telnet(device)
                    self.__configure(device, args)
                    self.__obj_connnect.close()
                except Exception as e:
                    print(f"\n\n{e}")
                    auxiliar_functions.close()
            else:
                try:
                    self.__login_over_ssh(device)
                    self.__configure(device, args)
                    self.__obj_connect.close()
                except Exception as e:
                    print(f"\n\n{e}")
                    auxiliar_functions.close()

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
            self.__shell = self.__obj_connect.invoke_shell() # Opens a shell to run commands.
        except Exception as error:
            print(f"[ ! ] {error}")
            self.__obj_connect.close()
            auxiliar_functions.close()
        else:
            self.__identify_errors(device)
            self.__shell.send(b"enable\n")
            sleep(0.5)
            self.__shell.send(device.enable_secret.encode() + b"\n")
            sleep(0.5)
            self.__identify_errors(device)

    def __configure(self, device, configurations):
        """  Start running commands on device if the configurations keys exists on 'confin.json' file.

            Args:
                device (:obj: `Device`): The device to be configured.
                configurations (str): The command keys based on 'config.json'.

        """
        for config_key in configurations:
            if config_key in self.configuration_keywords:
                if config_key == 'SET_HOSTNAME':
                    variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
                elif config_key == 'CREATE_VLAN':
                    vlans_to_create = input("\n\n[ -> ] Type the number of each VLAN separated by commas (eg: 5,15,20): ").split(',')
                    for vlan in vlans_to_create:
                        if int(vlan) not in range(3968, 4048) and int(vlan) != 4094:
                            self.variables["VLAN_NUMBER"] = vlan
                            self.__send_commands(device, config_key)
                    auxiliar_functions.close()
                self.__send_commands(device, config_key)
            else:
                print(f"\n\n[ ! ] There is no valid configuration for '{config_key}'.")
                auxiliar_functions.close()


    def __send_commands(self, device, config_key):
        """ Run the commands on the device based on the choosen configuration keyword.

            Args:
                device (:obj: `Device`): The device that will receive the commands.
                config_key (int): The configuration key to run based on the 'config.json' file.

        """
        commands = list(self.config_json[config_key].values())[0]
        if device.connection_protocol == "SSH":
            for command in commands:
                found_key = list(filter(lambda key: key in command, self.keys))
                if len(found_key) > 0:
                    self.__shell.send(command.replace(found_key[0], self.variables[found_key[0]]).encode('ascii'))
                    self.__identify_errors(device)
                    sleep(0.6)
                else:
                    self.__shell.send(command.encode())
                    self.__identify_errors(device)
                    sleep(0.6)
        else:
            for command in commands:
                found_key = list(filter(lambda key: key in command, self.keys))  # found commands to be replaced.
                if len(found_key) > 0:
                    self.__obj_connect.write(command.replace(found_key[0], self.variables[found_key[0]]).encode('ascii'))
                    self.__identify_errors(device)
                    sleep(0.6)  # timeout before send another command to prevent errors.
                else:
                    self.__obj_connect.write(command.encode('ascii'))
                    self.__identify_errors(device)
                    sleep(0.6)

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
            line = self.__shell.recv(65535).decode('ascii')
            if '% Do you really want to replace them?' in line or '% You already have RSA keys defined' in line:
                self.__shell.send(b'no\n')
            find_error_on_line(line)
