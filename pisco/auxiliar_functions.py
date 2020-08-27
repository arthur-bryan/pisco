from time import sleep
import sys


def validate_ip(ip):
    """ Validate if a string have an correct IP format.
        Args:
            ip (str):   The string to be verified.
        Returns:
            ip (str):   The string with a valid IP format.
        Raises:
            ValueError: In case the string hasn't a valid IP format.
    """
    splitted_ip = str(ip).split('.')
    if len(splitted_ip) != 4:
        raise ValueError("[!] Invalid IP!")
    for octet in splitted_ip:
        if (int(octet) < 0 or int(octet) > 255) or (len(octet) > 1 and octet.startswith('0')):
            raise ValueError("[!] Invalid IP!")
    return ip


def clear():
    """ Clear the terminal screen. """
    # \33[<N>D = move the cursor backward N columns
    # \33[<N>A = move the cursor up A lines
    # \33[2J = clear screen and move to 0,0
    sys.stdout.write("\033[1200D\33[1200A\033[2J")
    sys.stdout.flush()


def close():
    """ Clear the terminal screen and close the program. """
    print("\n[...] Exiting...")
    sleep(2)
    clear()
    sys.exit(0)
