import os
from modules import auxiliar_functions
from modules.device_manager import Manager


EXECUTABLE_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_FOLDER = os.path.join(CURRENT_DIR, "files")


def menu():
    auxiliar_functions.clear()
    try:
        choice = int(input("""
        \r==================== Pisco | v0.1 ====================\n
        \r[0] Start
        \r[1] Help
        \r[2] Exit\n
        \r--> """))
    except ValueError:
        menu()
    else:
        if choice not in range(3):
            menu()
        else:
            if choice == 0:
                device_manager = Manager()
                device_manager.start_manager()
            elif choice == 1:
                auxiliar_functions.clear()
                with open(os.path.join(FILES_FOLDER, "help.txt"), 'r') as file:
                    print(file.read())
                    input("\n[...]Press any key to quit..")
                    file.close()
                    menu()
            elif choice == 2:
                auxiliar_functions.close()


def main():
    try:
        auxiliar_functions.clear()
        menu()
    except KeyboardInterrupt:
        auxiliar_functions.close()


if __name__ == '__main__':
    main()
