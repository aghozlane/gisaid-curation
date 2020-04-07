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
    open(logfile, "w").close()  # empty logfile if already existing
    logfile_handler = FileHandler(logfile, 'w')

    # set level to the same as the logger level
    logfile_handler.setLevel(level)
    logfile_handler.setFormatter(formatterFile)  # add formatter
    logger.addHandler(logfile_handler)  # add handler to logger
    return logger