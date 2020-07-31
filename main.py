from managers.device_managers import IndividualDevice
from time import sleep
import sys
import os

EXECUTABLE_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "files")


def menu():
    clear()
    choice = int(input("""
    \r==================== Pisco ====================

    \r[0] Configure a individual device
    \r[1] Configure a list of devices
    \r[2] Help
    \r[3] Exit

    \r--> """))
    while choice not in (0, 1, 2, 3):
        menu()
    if choice == 0:
        clear()
        device = IndividualDevice()
        device.connection()
    elif choice == 1:
        print(" " * 20 + "Configuring a lot of devices...")
    elif choice == 2:
        clear()
        with open(os.path.join(FILES_FOLDER, "help.txt"), 'r') as file:
            print(file.read())
            input("\n[...]Press any key to quit..")
            file.close()
            menu()
    elif choice == 3:
        print("[...] Exiting...")
        sleep(0.5)
        clear()
        sys.exit(0)


def clear():
    """
    '\33[<N>D' = move the cursor backward N columns
    '\33[<N>A' = move the cursor up A lines
    '\33[2J' = clear screen and move to 0,0
    """
    sys.stdout.write("\033[1200D\33[1200A\033[2J")
    sys.stdout.flush()


def main():
    try:
        clear()
        menu()
    except KeyboardInterrupt:
        print("\n[...] Exiting...")
        sleep(0.5)
        clear()
        sys.exit(0)


if __name__ == '__main__':
    main()
