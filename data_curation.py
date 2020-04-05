#!/usr/bin/env python3
# coding: utf-8


"""
@author gem, Institut Pasteur
April 2020
"""

import sys
import pandas as pd


def cure_metadata(file_in):
    """
    file_in in xls format
    """
    locations = {}  # to put old -> new location
    dates = {}
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
        check_location(line, locations)
        check_details(line)
        check_date(line, dates)


        break
    print(locations)
    print(dates)
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
    print(location)
    # try:
    sep = location.strip().split("/")
    sep = [f.strip() for f in sep]
    formatted_sep = checked_location_format(location, locations)
    location = " / ".join(formatted_sep)
    answer = input(f"Is location '{location}' ok? ([Y]/n)")
    while answer.lower() not in ["yes", "y", "no", "n", ""]:
        answer = input(f"Is location '{location}' ok? ([Y]/n)")
    if answer.lower() in ["n", "no"]:
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country / Region'\n")
        formatted_sep = checked_location_format(answer, locations)
    location = " / ".join(formatted_sep)
    print(f"location is {location}")
    line["covv_location"] = location


def checked_location_format(location, locations):
    """
    Check if Location is in expected format: Continent / Country / Region

    location -> str
    locations -> dict {prev_loc: new_loc}
    """
    sep = location.strip().split("/")
    sep = [f.strip() for f in sep]
    new_sep = sep
    while len(new_sep) < 2 or len(new_sep) > 3:
        print(f"Wrong format for location: {location}")
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country / Region'\n") 
        new_sep = answer.strip().split("/")
        new_sep = [f.strip().capitalize() for f in new_sep]
    if sep != new_sep:
        location = " / ".join(new_sep)
        locations[location] = location
    return new_sep


def check_details(line):
    """
    line = pandas.core.series.Series
    """
    details = line["covv_passage"]
    if not details or details.lower() == "unknown":
        line["covv_passage"] = "unknown"
    else:
        line["covv_passage"] = details.capitalize()
    details = line["covv_passage"]


def check_date(line, dates):
    """
    line = pandas.core.series.Series
    """
    date = str(line["covv_collection_date"])
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



def check_virus_name(line):
    """
    line = pandas.core.series.Series
    """
    # Get given virus name, and given location (to compare with 2nd field of virus name)
    virus_id = line["covv_virus_name"]
    location = line["covv_location"]
    # Fields required for a virus name
    name = ""
    country = ""
    v_id = ""
    date = ""
    fields = virus_id.split("/")
    # Check if all fields are present, and ok
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
    # If some required field missing -> error message
    if not name or not date or not country:
        print(f"Error in virus name: {virus_id}")

        # break
    virus_id = "/".join([name, country, v_id, date])
    line["covv_virus_name"] = virus_id





if __name__ == '__main__':
    metadata = sys.argv[1]
    cure_metadata(metadata)
