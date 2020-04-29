#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==============================================================================
# MODULE DESCRIPTION
#==============================================================================
"""
Python main function
"""
#==============================================================================
# HEADER
#==============================================================================
__version__ = "1.0_beta"
#==============================================================================
# IMPORT
#==============================================================================
from os import path as os_path
from sys import path as sys_path, argv as sys_argv, exit
from PyQt5 import QtWidgets

sys_path.insert(0, os_path.abspath(os_path.dirname(sys_argv[0])))

import src.FenPrimary as Fp

CONST_HELP_LIST   = ["-h", "--help"]

#==============================================================================
# MAIN
#==============================================================================
def appHelp(argv, isHelpCalled):
    """!
        help function
        @param argv: the argument parameters list.
    """

    displayMsg = ""
    if isHelpCalled:
        displayMsg = "Help: Usage of script main.py\n"
    else:
        displayMsg = "Wrong usage of script main.py.\n"

    displayMsg += "If the script is called without any arguments, the application is launched in interractive mode.\n"
    displayMsg += "optional arguments:\n"
    displayMsg += "-h, --help  show this help message and exit\n"
    displayMsg += "only one argument must be used.\n"
    displayMsg += "EXIT"

    print(displayMsg)


def main(argv):
    """!
        main function
        @param argv: the argument parameters list.
        this list contain at least the file name and
        may contain the ini file name or the folder containing the ini files.
    """
    # Interactive mode
    if len(argv) == 1:
        app = QtWidgets.QApplication(sys_argv)
        win = Fp.FenPrimaryClass()
        win.show()
        exit(app.exec_())
    elif len(argv) == 2 and argv[1] in CONST_HELP_LIST:
        appHelp(argv, True)
    else:
        appHelp(argv, False)

if __name__ == "__main__":
    main(sys_argv)
