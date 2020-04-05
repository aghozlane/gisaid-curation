#!/usr/bin/env python3
# coding: utf-8


"""
@author gem, Institut Pasteur
April 2020
"""

import sys
import logging
from logging import FileHandler
import pandas as pd
import unidecode



def cure_metadata(file_in):
    """
    file_in in xls format
    """
    # dict to put {original_value: new_value} (new_value can be the same as original one)
    # to avoid re-checking next time we see this value
    locations_list = {}
    dates_list = {}
    details_list = {}
    vnames_list = []  # list of virus names
    md = pd.read_excel(file_in, sheet_name=1, header=0, dtype=str)
    # Empty cells -> put empty string
    md = md.fillna("")
    # print(md.dtypes)
    # print(md["covv_passage"].head(n=13))
    # print(md["submitter"])
    for index, line in md.iterrows():
        # Skip 2nd header line
        if "filename" in line["fn"]:
            continue
        check_location(line, locations_list)
        # check_vname(line, vnames_list)
        check_details(line, details_list)
        # check_date(line, dates)


    print(locations_list)
    print(details_list)
    print(vnames_list)
    # print(dates)
        # check_virus_name(line)

        # print(line)
        # break
    # print(md["covv_passage"].head(n=13))


def check_location(line, locations):
    """
    Check Location column

    line = pandas.core.series.Series
    locations -> dict {prev_loc: new_loc}
    """
    location = line["covv_location"]
    # If we already saw this field, and it was valid, just skip checking this time
    if location in locations:
        return

    # Separate by continent, country, region
    sep = location.strip().split("/")
    sep = [f.strip() for f in sep]
    formatted_sep = checked_location_format(location, locations)
    final_location = " / ".join(formatted_sep)
    unicode_location = unidecode.unidecode(final_location)
    answer = input(f"Is location '{unicode_location}' ok? ([Y]/n)")
    while answer.lower() not in ["yes", "y", "no", "n", ""]:
        if unidecode_location != location:
            print(f"{location} was corrected.")
        answer = input(f"Is location '{unicode_location}' ok? ([Y]/n)")
    if answer.lower() in ["n", "no"]:
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country / Region'\n")
        formatted_sep = checked_location_format(answer, locations)
    location = " / ".join(formatted_sep)
    final_location = unidecode.unidecode(location)
    if location != final_location:
        logger.info(f"'Location' column: changed '{location}' to '{final_location}'.")
    if final_location not in locations:
        locations[location] = final_location
    line["covv_location"] = location


def checked_location_format(location, locations):
    """
    Check if Location is in expected format: Continent / Country / Region

    location -> str
    locations -> dict {prev_loc: new_loc}
    """
    sep = location.strip().split("/")
    # Keep only elements without ' ' & co
    sep = [f.strip() for f in sep]
    new_sep = sep

    # Check that location has at least continent, and at most 3 fields
    # If not, ask user for location field
    while len(new_sep) < 2:
        print(f"Wrong format for location: {location}")
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country / Region'\n") 
        new_sep = answer.strip().split("/")
        new_sep = [f.strip().capitalize() for f in new_sep]
    # If fields changed, re-do location
    if sep != new_sep:
        final_location = " / ".join(new_sep)
        if location not in locations:
            locations[location] = final_location
    return new_sep


def check_vnames(line, vnames_list):
    """
    line = pandas.core.series.Series
    vnames_list : dict
    """
    # Get given virus name, and given location (to compare with 2nd field of virus name)
    vname = line["covv_virus_name"]
    location = line["covv_location"]

    # If vname already exists : problem
    uniq = False
    while not uniq:
        if vname not in vnames_list:
            uniq = True
        else:
            print(f"ERROR: {vname} already exists! Virus names must be unique.")
            answer = input("Please give correct virus name or type 'STOP' "
                           "to stop program and go back yourself to the xls file.")
            if answer == "STOP":
                sys.exit(1)

    # We are now sure that the virus name is unique. Let's check if it has the 4 required fields.
    fields_ok = False
    while not fields_ok:
        if len(fields) == 4:
            fields_ok = True
        else:
            print(f"'{vname}' is not a valid virus name. It should follow this format: "
                  "hCoV-19/Country/Identifier/2020.")
            answer = input("Please give correct virus name, or type 'STOP' "
                           "to stop program and go back yourself to the xls file.")
            if answer == "STOP":
                sys.exit(1)

    # We are now sure that virus name is uniq, and there are 4 fields
    # Fields required for a virus name
    final_vname = checked_vname_format(vname, vnames_list, location)
    vnames_list.append(final_vname)
    line["covv_virus_name"] = final_vname
    # Log if we changed something
    if vname != final_vname:
        logger.info(f"Changed sequence name '{vname}' to '{final_vname}'.")


def checked_vname_format(vname, vnames_list, location):
    """
    Check if vname is in expected format: hCoV-19/Country/Identifier/2020

    vname -> str
    vnames -> list of virus names
    location : str
    """
    name = ""
    country = ""
    v_id = ""
    date = ""
    fields = vname.split("/")

    # Check if all fields are as expected
    for field in fields:
        if field == "hCoV-19":
            name = field
        elif field == "2020":
            date = field
        elif field in location:
            country = field
        # not a date, location nor covid19 -> must be the id
        else:
            v_id = field
    if not name or not date:
        name = "hCoV-19"
        date = "2020"
    # If some required field missing -> error message
    if not country:
        fields_location = location.split("/")
        if len(final_location) == 1:
            country = fields_location[0].strip()
        else:
            country = location.split("/")[1].strip()
        print(f"'{vname}' is not a valid virus name. It should follow this format: "
               "hCoV-19/Country/Identifier/2020. Here, 'Country' does not correspond "
               "to what is given in 'Location' column. We took the correct contry directly "
               "from this 'Location' column: ")

    final_vname = "/".join([name, country, v_id, date])
    return final_vname


def check_details(line, details_list):
    """
    line = pandas.core.series.Series
    """
    details = line["covv_passage"]
    seq = line["covv_virus_name"]
    # If we already saw this field, and it was valid, just skip checking this time
    if details in details_list:
        return

    # If empty: put 'unknown'
    if not details or details.lower() == "unknown":
        final_details = "unknown"
    # Put first letter in upper case, and remove accents
    else:
        final_details = details.capitalize()
        final_details = unidecode.unidecode(final_details)
    # If something changed, write to log
    if final_details != details:
        logger.info(f"In {seq}, 'Passage details/history' column changed from '{details}' "
                    f"to '{final_details}'.")
    # Add this to detail_list so that, next time, we do not need to check if
    # we have the same details input
    if not details in details_list:
        details_list[details] = final_details
    line["covv_passage"] = final_details


def check_date(line, dates_list):
    """
    line = pandas.core.series.Series
    """
    date = str(line["covv_collection_date"])
    seq = line["covv_virus_name"]
    if date in dates_list:
        return
    if not date or date.lower() == "unknown":
        line["covv_collection_date"] = "unknown"
        return
    correct_format = False
    numbers = date
    while not correct_format:
        try:
            numbers = numbers.split("-")
            numbers = [int(n.strip()) for n in numbers]
            if len(numbers) == 0 or len(numbers) > 3:
                raise ValueError
            if len(str(numbers[0])) != 4:
                raise ValueError("Year not in YYYY format")
            if len(numbers) > 1 and len(str(numbers[1])) != 2:
                raise ValueError("Month not in MM format")
            if len(numbers)> 2 and len(str(numbers[2])) != 2:
                raise ValueError("Day not in DD format")
            correct_format = True
        except ValueError as e:
            print()
            if "not in" in str(e):
                print(e)
            numbers = input(f"Wrong format for collection date: {date}. \n"
                            "Please enter correct collection date in YYYY or "
                            "YYYY-MM or YYYY-MM-DD format:")
    str_numbers = [str(n) for n in numbers]
    date_ok = "-".join(str_numbers)
    dates[date] = date_ok
    line["covv_collection_date"] = date_ok


# def check_date_format(date):
#     """
#     Check that date format is YYYY or YYYY-MM or YYYY-MM-DD

#     date -> str
#     """
#     answer = date
#     try:
        
#     except ValueError:
#         answer = input(f"Wrong format for collection date: {date}"
#                         "Please enter correct collection date in YYYY or "
#                         "YYYY-MM or YYYY-MM-DD format ")
#         break


def init_logger(logfile):
    """
    Start logger with appropriate format
    """
    logger = logging.getLogger("cure_metadata")
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


if __name__ == '__main__':
    metadata = sys.argv[1]
    logger = init_logger(f"{metadata}.log")
    logger = cure_metadata(metadata)
