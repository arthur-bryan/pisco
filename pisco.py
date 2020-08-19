# -*- coding: utf-8 -*-

__author__ = "Arthur Bryan"
__copyright__ = "Copyright (c) 2020 Arthur Bryan"
__license__ = "MIT License"
__version__ = "0.1.0-pre-alpha"
__maintainer__ = "Arthur Bryan"
__email__ = "arthurbryan2030@gmail.com"
__status__ = "Development"

from modules import auxiliar_functions


def main():
    try:
        auxiliar_functions.clear()
        auxiliar_functions.start_menu()
    except KeyboardInterrupt:
        auxiliar_functions.close()


if __name__ == '__main__':
    main()
