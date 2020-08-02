from telnetlib import Telnet
from getpass import getpass
from files.validations import validate_ip
from time import sleep
import sys
import os
import json

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "../files")


class IndividualDevice:
    def __init__(self):
        self.ip_addr = ""
        self.vty_username = ""
        self.vty_password = ""
        self.enable_password = ""
        self.conn_type = ""
        self.obj_connect = None
"""
    def get_device_info(self):
        self.telnet_or_ssh()
        clear()
        print("\n" + " " * 20 + "CONFIGURING INDIVIDUAL DEVICE\n")
        while self.ip_addr == "":
            try:
                self.ip_addr = validate_ip(input("[->] IP address of the device: "))[1]
            except ValueError as e:
                print(e)
                sleep(0.5)
                clear()
        self.vty_username = input("[->] VTY Username: ")
        self.vty_password = getpass(prompt="[->] VTY Password: ")
        self.enable_password = getpass(prompt="[->] Enable secret: ")

    def connection(self):
        self.get_device_info()
        if self.conn_type == "23":
            self.obj_connect = Telnet(self.ip_addr, self.conn_type, 5)
            self.obj_connect.read_until(b"Username:", 2)
            self.obj_connect.write(self.vty_username.encode('ascii') + b"\n")
            sleep(0.5)
            self.obj_connect.read_until(b"Password:", 2)
            self.obj_connect.write(self.vty_password.encode('ascii') + b"\n")
            sleep(0.5)
            self.obj_connect.write(b"enable\n")
            self.obj_connect.read_until(b"Password:", 2)
            self.obj_connect.write(self.enable_password.encode('ascii') + b"\n")
            sleep(0.5)
            self.configure_device()
        else:
            print("SSH was choosen :)")

    def telnet_or_ssh(self):
        clear()
        try:
            option = int(input("""
            \r                   CONNECTION TYPE\n
            \r[0] Configure over Telnet
            \r[1] Configure over SSH\n
            \r--> """))
        except ValueError:
            self.telnet_or_ssh()
        else:
            if option not in (0, 1):
                self.telnet_or_ssh()
            else:
                if option == 0:
                    self.conn_type = "23"
                else:
                    self.conn_type = "22"

    def scripts_options(self):
        clear()
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
            self.scripts_options()
        else:
            return choice

    def configure_device(self):
        code = ""
        while code not in list(range(10)):
            code = self.scripts_options()
        clear()
        variables = {"DEVICE_HOSTNAME": "",
                     "ENABLE_PASSWORD": self.enable_password}
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
"""
    def identify_errors(self):
        console_output = self.obj_connect.read_eager().decode('ascii')
        if 'Bad secrets' in console_output:
            print("\n[!] Wrong enable secret! Connect again.")
            sleep(2)
            self.get_device_info()

