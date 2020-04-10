#!/usr/bin/env python3
# coding: utf-8


#############################################################################
# This program provides some help for GISAID bulk data curation             #
#                                                                           #
# Authors: Amandine PERRIN                                                  #
# Copyright (c) 2020  Institut Pasteur, Paris                               #
#                                                                           #    
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU Affero General Public License as            # 
# published by the Free Software Foundation, either version 3 of the        #
# License, or (at your option) any later version.                           #
#                                                                           #           
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            # 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU Affero General Public License for more details.                       #
#                                                                           #
# You should have received a copy of the GNU Affero General Public License  #
# along with this program.  If not, see <https://www.gnu.org/licenses/>.    #
#                                                                           #
#############################################################################


import sys
import logging
from logging import FileHandler
import argparse

def init_logger(logfile, logname):
    """
    Start logger with appropriate format
    """
    logger = logging.getLogger(logname)
    level = logging.DEBUG
    logger.setLevel(level)
    # create formatter for log messages (only logs in logfile)
    formatterFile = logging.Formatter('%(levelname)s :: %(message)s')
    # formatterStream = logging.Formatter('  * %(message)s')

    # Create logfile handler: writing to 'logfile'. mode 'write'.
    # To write all changes done
    logfile_log = logfile + ".changes.log"
    open(logfile_log, "w").close()  # empty logfile if already existing
    logfile_handler1 = FileHandler(logfile_log, 'w')

    # Create logfile handler: writing to 'logfile'. mode 'write'.
    # To write things that must be sent to submitter (warning), and if 
    # sequence cannot be released (error)
    logfile_contact = logfile + ".contact_sub.log"
    open(logfile_contact, "w").close()  # empty logfile if already existing
    logfile_handler2 = FileHandler(logfile_contact, 'w')

    # set level of changes.log to the same as the logger level
    logfile_handler1.setLevel(level)
    logfile_handler1.setFormatter(formatterFile)  # add formatter
    logger.addHandler(logfile_handler1)  # add handler to logger

    # set level of contact_sub.log to warning level
    logfile_handler2.setLevel(logging.WARNING)
    logfile_handler2.setFormatter(formatterFile)  # add formatter
    logger.addHandler(logfile_handler2)  # add handler to logger

    return logger


def make_parser(argu):
    """
    generate args parser
    """
    my_parser = argparse.ArgumentParser(description="help for GISAID metadata curation")
    my_parser.add_argument("-f", dest="xls_file",
                           help="xls file containing metadata of your bulk.", required=True)
    args = my_parser.parse_args(argu)
    return args
