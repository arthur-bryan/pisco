from telnetlib import Telnet
from getpass import getpass
from validations import validate_ip
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
        self.current_conn_type = ""
        self.obj_connect = None

    def get_device_info(self):
        self.telnet_or_ssh()
        clear()
        print(" " * 20 + "CONFIGURING INDIVIDUAL DEVICE\n")
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
        if self.current_conn_type == "23":
            self.obj_connect = Telnet(self.ip_addr, self.current_conn_type, 5)
            self.obj_connect.read_until(b"Username:", 2)
            self.obj_connect.write(self.vty_username.encode('ascii') + b"\n")
            self.obj_connect.read_until(b"Password:", 2)
            self.obj_connect.write(self.vty_password.encode('ascii') + b"\n")
            sleep(1)
            self.obj_connect.write(b"enable\n")
            self.obj_connect.read_until(b"Password:", 2)
            self.obj_connect.write(self.enable_password.encode('ascii') + b"\n")
            sleep(1)
            self.configure_device(self.scripts_options())
        else:
            print("SSH was choosen :)")

    def telnet_or_ssh(self):
        clear()
        option = int(input("""
    \n\r[0] Configure over Telnet
    \r[1] Configure over SSH\n
    \r--> """))
        while option not in (0, 1):
            clear()
            option = int(input("""
    \n\r[0] Configure over Telnet
    \r[1] Configure over SSH\n
    \r--> """))
        if option == 0:
            self.current_conn_type = "23"
        else:
            self.current_conn_type = "22"

    def scripts_options(self):
        clear()
        choice = int(input("""
    \n\r=============== SCRIPTS ===================

    \r[0] Load default
    \r[1] Set Hostname
    \r[2] Create VLANs
    \r[3] Setup VLANs
    \r[4] Setup SSH access
    \r[5] VTP mode access
    \r[6] VTP mode trunk
    \r[7] Erase NVRAM
    \r[8] Exit

    \r--> """))
        while choice not in list(range(9)):
            self.scripts_options()
        return choice

    def configure_device(self, code):
        clear()
        variables = {"DEVICE_HOSTNAME": "",
                     "ENABLE_PASSWORD": self.enable_password}
        with open(os.path.join(FILES_FOLDER, 'config.json'), "r") as file:
            data = json.load(file)
        if code == 0:
            self.run_default_setup(data, variables)
        elif code == 1:
            self.run_hostname_setup(data, variables)

    def run_default_setup(self, json_data, variables):
        print(" " * 20 + "Runnning default setup\n")
        commands = list(json_data['DEFAULT_CONFIG'].values())[0]
        self.send_commands(commands, variables)
        print("\n" + " " * 20 + "Default configs set!\n")
        sleep(2)
        self.configure_device(self.scripts_options())

    def run_hostname_setup(self, json_data, variables):
        print(" " * 20 + "Setting HOSTNAME\n")
        variables["DEVICE_HOSTNAME"] = input("[->] Set hostname: ")
        commands = list(json_data['SET_HOSTNAME'].values())[0]
        self.send_commands(commands, variables)
        print("\n" + " " * 20 + "Hostname set!\n")
        sleep(2)
        self.configure_device(self.scripts_options())

    def send_commands(self, commands, variables):
        keys = list(variables.keys())
        for command in commands:
            if keys[0] in str(command):
                self.obj_connect.write(command.replace(keys[0], variables[keys[0]]).encode('ascii'))
                print(self.obj_connect.read_very_eager().decode('ascii'))
                sleep(1)
            elif keys[1] in str(command):
                self.obj_connect.write(command.replace(keys[1], variables[keys[1]]).encode('ascii'))
                print(self.obj_connect.read_very_eager().decode('ascii'))
                sleep(1)
            else:
                self.obj_connect.write(command.encode('ascii'))
                print(self.obj_connect.read_very_eager().decode('ascii'))
                sleep(1)
        self.obj_connect.close()


def clear():
    """
    '\33[<N>D' = move the cursor backward N columns
    '\33[<N>A' = move the cursor up A lines
    '\33[2J' = clear screen and move to 0,0
    """
    sys.stdout.write("\033[1200D\33[1200A\033[2J")
    sys.stdout.flush()
