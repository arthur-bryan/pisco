from time import sleep
import os
import csv


class Device:

    def __init__(self, ip_address, vty_password, enable_secret, vty_username="", domain_name=""):
        self.__category = None
        self.__connection_protocol = None
        self.__domain_name = domain_name if domain_name != "" else "lan.com"
        self.ip_address = ip_address
        self.vty_username = vty_username if vty_username != "" else ""
        self.vty_password = vty_password
        self.enable_secret = enable_secret
        self.__interfaces = []

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, device_category):
        if device_category.upper() == 'SWITCH':
            self.__category = 'SWITCH'
        elif device_category.upper() == 'ROUTER':
            self.__category = 'ROUTER'
        else:
            raise ValueError(f"[ ! ] Invalid device category: {device_category}.")

    @property
    def connection_protocol(self):
        return self.__connection_protocol

    @connection_protocol.setter
    def connection_protocol(self, protocol):
        if protocol.upper() == 'TELNET':
            self.__connection_protocol = 'TELNET'
        elif protocol.upper() == 'SSH':
            self.__connection_protocol = 'SSH'
        else:
            raise ValueError(f"[ ! ] Invalid protocol: {protocol}.")

    @property
    def domain_name(self):
        return self.__domain_name

    @domain_name.setter
    def domain_name(self, domain):
        try:
            self.__domain_name = domain
        except Exception as e:
            print(f"[ ! ] {e}.")

    def export_interfaces_info(self, option, connection_protocol, client_obj):
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
        if connection_protocol == 'telnet':
            client_obj.write(option_commands[option].encode())
            sleep(0.5)
            output = client_obj.read_very_eager().decode('ascii')
        else:
            client_obj.send(option_commands[option].encode())
            sleep(0.5)
            output = client_obj.recv(65535).decode('ascii')
        # writes output to a .txt file.
        txt_file_name = ('interfaces-ip.txt' if option == 'ip' else 'interfaces-status.txt')
        with open(f"data/{txt_file_name}", "w") as file:
            if option == "ip":
                file.write("\n")    # blank line to help formating file on this output
            file.write(str(output).replace("\n", ""))
            file.close()
        # opens the .txt with interface data and create a .csv from it.
        with open(f"data/{txt_file_name}", "r") as file:
            csv_file_name = ('interfaces-ip.csv' if option == 'ip' else 'interfaces-status.csv')
            csv_interface_file = open(f"data/{csv_file_name}", "w")
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
            os.remove("data/{txt_file_name}")  # removes txt file when it get useless
            return csv_interface_file
