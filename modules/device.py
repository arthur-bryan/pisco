from modules import auxiliar_functions
from time import sleep
import os
import csv

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "../files")

class Device:

    def __init__(self, device_type, ip_address, vty_username, vty_password, enable_secret):
        self.device_type = device_type
        self.ip_address = ip_address
        self.vty_username = vty_username
        self.vty_password = vty_password
        self.enable_secret = enable_secret
        self.interfaces = []

    def export_interfaces_info(self, option, manager):
        """ Stores the interfaces status command output to a txt and then
            create a csv based on it.
            :param str option: must be 'status' or 'ip'
            :param Manager manager: the object manager that manages the device
        """
        if option == 'status':
            command = 'show interfaces status\n'
        else:
            command = 'show ip interface brief\n'
        manager.write(command.encode())
        sleep(0.5)
        output = manager.read_very_eager().decode('ascii')
        # opens a .txt and writes the 'show interfaces status' output to it.
        with open(f"{FILES_FOLDER}/interface.txt", "w") as file:
            if option == "ip":
                file.write("\n")	# blank line to help formating file on this output
            file.write(str(output).replace("\n", ""))
            file.close()
        # opens the .txt with interface data and create a .csv from it.
        with open(f"{FILES_FOLDER}/interface.txt", "r") as file:
            csv_interface_file = open(f"{FILES_FOLDER}/interface.csv", "w")
            csv_writer = csv.writer(csv_interface_file)
            number_of_lines = len(file.readlines())
            file.seek(0)
            lines = []
            for i, line in enumerate(file.readlines()):
                if i == 2 and i < number_of_lines -1:   # ignores the firsts and last useless lines.
                    line = line.split()
                    lines.append(line)
                elif i > 2 and i < number_of_lines - 1:
                    line = line.split()
                    line.insert(1, "")
                    lines.append(line)
            csv_writer.writerows(lines)
            csv_interface_file.close()
            os.remove(f"{FILES_FOLDER}/interface.txt") # removes txt file when it get useless.

