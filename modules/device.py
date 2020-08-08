from modules import auxiliar_functions
from time import sleep
import os
import csv

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "../files")


class Device:

    def __init__(self, device_type, ip_address, vty_username, vty_password, enable_secret, domain_name):
        self.device_type = device_type
        self.ip_address = ip_address
        self.vty_username = vty_username
        self.vty_password = vty_password
        self.enable_secret = enable_secret
        self.interfaces = []
        self.is_configured = False
        if domain_name == "":
            self.domain_name = 'lan.com'
        else:
            self.domain_name = domain_name

    def export_interfaces_info(self, option, connection_method, client_obj):
        """ Stores the interfaces status command output to a txt and then
            create a csv based on it.
            Params:
                option (str):  must be 'status' or 'ip'.
                connection_method (str): 'telnet' or 'ssh'.
                client_obj: the telnet or ssh client to send commands to device.
            Returns:
                csv_interface_file
        """
        option_commands = {'status': 'show interfaces status\n',
                           'ip': 'show ip interface brief\n'}
        if connection_method == 'telnet':
            client_obj.write(option_commands[option].encode())
            sleep(0.5)
            output = client_obj.read_very_eager().decode('ascii')
        elif connection_method == 'ssh':
            client_obj.send(option_commands[option].encode())
            sleep(0.5)
            output = client_obj.recv(65535).decode('ascii')
        # writes output to a .txt file.
        with open(f"{FILES_FOLDER}/interface.txt", "w") as file:
            if option == "ip":
                file.write("\n")    # blank line to help formating file on this output
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
                if i == 2 and i < number_of_lines - 1:   # ignores the 2 firsts and last useless lines.
                    line = line.split()
                    lines.append(line)
                elif 2 < i < number_of_lines - 1:
                    line = line.split()
                    if option == "status" and len(line) < 7:
                        line.insert(1, "")
                    lines.append(line)
            csv_writer.writerows(lines)
            csv_interface_file.close()
            os.remove(f"{FILES_FOLDER}/interface.txt")  # removes txt file when it get useless.
            return csv_interface_file
