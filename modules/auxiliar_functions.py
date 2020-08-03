from time import sleep
import sys


def validate_ip(ip):
    splitted_ip = ip.split('.')
    if len(splitted_ip) != 4:
        raise ValueError("[!] Invalid IP!")
    for octet in splitted_ip:
        if int(octet) < 0 or int(octet) > 255:
            raise ValueError("[!] Invalid IP!")
        if len(octet) > 1 and octet.startswith('0'):
            raise ValueError("[!] Invalid IP!")
    return True, ip


def clear():
    """
    Clear the screen.
        '\33[<N>D' = move the cursor backward N columns
        '\33[<N>A' = move the cursor up A lines
        '\33[2J' = clear screen and move to 0,0
    """
    sys.stdout.write("\033[1200D\33[1200A\033[2J")
    sys.stdout.flush()


def close():
    print("[...] Exiting...")
    sleep(0.5)
    clear()
    sys.exit(0)
