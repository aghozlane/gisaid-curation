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
import pandas as pd
import unidecode

import utils


def cure_metadata(file_in):
    """
    file_in in xls format
    """
    # dict to put {original_value: new_value} (new_value can be the same as original one)
    # to avoid re-checking next time we see this value
    locations_list = {}
    dates_list = {}
    details_list = {}
    hosts_list = {}
    countries = {}  # countries found in virus names.
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
        print()
        check_vnames(line, vnames_list, countries)
        print()
        # check_mandatory_fieldk(line, "covv_orig_lab")
        # check_mandatory_field(line, "covv_orig_lab_addr")
        # check_mandatory_field(line, "covv_subm_lab")
        # check_mandatory_field(line, "covv_subm_lab_addr")
        # check_mandatory_field(line, "covv_seq_technology", alert=True)
        # check_location(line, locations_list)
        # check_vname(line, vnames_list)
        # Check passage history/details column
        check_column(line, "covv_passage", details_list, capital=True)
        print()
        # Check host
        # check_column(line, "covv_host", hosts_list)
        # Check

        # check_date(line, dates)

    # location : at least 2 fields (pas uniquement le continent)
    # virus name: space in country. no accent at all (id, country)

    print(locations_list)
    print(details_list)
    print(vnames_list)
    # print(dates)
        # check_virus_name(line)

        # print(line)
        # break
    print(md["covv_orig_lab"].head(n=13))
    print(md["covv_orig_lab_addr"].head(n=13))
    print(md["covv_subm_lab"].head(n=13))
    print(md["covv_subm_lab_addr"].head(n=13))
    print(md["covv_seq_technology"].head(n=13))



def check_mandatory_field(line, column, alert=False):
    """
    For a mandatory field, check that there is something in it. If not, ask user to fill
    Works for:
    - originating lab
    - address originating lab
    - submitting lab
    - address submitting lab

    """
    text = line[column]
    seq = line["covv_virus_name"]
    new_text = text
    while not new_text:
        if alert:
            logger.warning(f"ALERT: {seq} has no {column} text. Filled to unknown. CONTACT SUBMITTER")
            new_text = "unknown"
            break
        print()
        print(f"For '{seq}' sequence, '{column}' column must be filled.")
        new_text = input("Please enter correct a value for this column'")
        check_mandatory_field(line, column, alert=alert)
    if text != new_text:
        logger.info(f"For sequence {seq}, '{column}' column: changed '{text}' to '{new_text}'.")
        line[column] = new_text



def check_location(line, locations):
    """
    Check Location column

    line = pandas.core.series.Series
    locations -> dict {prev_loc: new_loc}
    """
    write_warning = True

    location = line["covv_location"]
    # If we already saw this field, and it was valid, just skip checking this time
    if location in locations:
        return

    # Separate by continent, country, region
    sep = location.strip().split("/")
    sep = [f.strip() for f in sep]
    formatted_sep = checked_location_format(location, locations)
    final_location = " / ".join(formatted_sep)
    unidecode_location = unidecode.unidecode(final_location)
    if final_location != unidecode_location:
        print("------LOCATION checking-----")
        print(f"{location} was changed to {unidecode_location}.")
        write_warning = False
    if write_warning:
        print("------LOCATION checking-----")
    # Ask user to validate location
    answer = input(f"Is location '{unidecode_location}' ok? ([Y]/n)")
    # If answer not yes/no, re-ask question
    while answer.lower() not in ["yes", "y", "no", "n", ""]:
        answer = input(f"Is location '{unidecode_location}' ok? ([Y]/n)")
    # if answer is no, ask user for new text for location
    if answer.lower() in ["n", "no"]:
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country / Region'\n")
        # Check new given location is ok
        formatted_sep = checked_location_format(answer, locations)
    location = " / ".join(formatted_sep)
    final_location = unidecode.unidecode(location)
    if location != final_location:
        logger_log.info(f"'Location' column: changed '{location}' to "
                        f"'{final_location}'.")
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
        print("------LOCATION checking-----")
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


def check_vnames(line, vnames_list, countries, corresp_file):
    """
    line = pandas.core.series.Series
    vnames_list : dict
    """
    # Get given virus name, and given location (to compare with 2nd field of virus name)
    vname = line["covv_virus_name"]
    location = line["covv_location"]

    fields = vname.strip().split("/")
    fields = [f.strip() for f in fields]

    # If vname already exists : problem
    uniq = False
    orig_vname = vname   # same original virus name given
    while not uniq:
        if vname not in vnames_list:
            uniq = True
        else:
            print("------VIRUS NAME checking-----")
            print(f"ERROR: {vname} already exists! Virus names must be unique.")
            answer = input("Please give correct virus name or type 'STOP' "
                           "to stop program and go back yourself to the xls file.\n")
            if answer == "STOP":
                sys.exit(1)
            # Update fields with new answer
            fields = answer.strip().split("/")
            fields = [f.strip() for f in fields]
            vname = "/".join(fields)

    # We are now sure that the virus name is unique. Let's check if it has the 4 required fields.
    fields_ok = False
    while not fields_ok:
        if len(fields) == 4:
            fields_ok = True
        else:
            print("------VIRUS NAME checking-----")
            print(f"'{vname}' is not a valid virus name. It should follow this format: "
                  "hCoV-19/Country/Identifier/2020.")
            answer = input("Please give correct virus name, or type 'STOP' "
                           "to stop program and go back yourself to the xls file.\n")
            if answer == "STOP":
                sys.exit(1)
            fields = answer.strip().split("/")
            fields = [f.strip() for f in fields]
            vname = answer

    # We are now sure that virus name is uniq, and there are 4 fields
    # Fields required for a virus name
    final_vname = checked_vname_format(vname, vnames_list, location, countries)
    vnames_list.append(final_vname)
    line["covv_virus_name"] = final_vname
    # Log if we changed something
    if vname != final_vname:
        with open(corresp_file, "a") as cf:
            cf.write("\t".join([orig_vname, final_vname]) + "\n")
        logger_log.info(f"Changed sequence name '{orig_vname}' to '{final_vname}'.")
        logger_contact.info(f"Changed sequence name '{orig_vname}' to '{final_vname}'.")


def checked_vname_format(vname, vnames_list, location, countries):
    """
    Check if vname is in expected format: hCoV-19/Country/Identifier/2020

    vname -> str
    vnames -> list of virus names
    location : str
    countries: {ori_country_in_vname: new_country_in_vname}
    """
    name = "hCoV-19"
    country = ""
    v_id = ""
    date = "2020"
    fields = vname.split("/")

    # Check country is in location. Otherwise, get country
    if fields[1] not in location:
        # Country not in location, but already seen before -> replace as it 
        # has been replaced before
        if fields[1] in countries:
            country = countries[fields[1]]
        # Country not in location and never seen before: try to fix it
        else:
            country = location.split("/")[1].strip()
            print("------VIRUS NAME checking-----")
            print(f"'{vname}' is not a valid virus name. It should follow this format: "
                   "hCoV-19/Country/Identifier/2020. Here, 'Country' does not correspond "
                   "to what is given in 'Location' column. We took the correct country directly "
                   f"from this 'Location' column: {country}")
            answer = input(f"Is it ok (Y) or do you want to keep {fields[1]} (n)?")
            # no: keep fields[1], do not change country. Save this for next time
            if answer.lower() in ["n", "no"]:
                country = fields[1]
                countries[country] = country
            else:
                countries[fields[1]] = country
    # If country field corresponds to location column, keep it as is
    else:
        country = fields[1]

    # Get virus ID
    v_id = fields[2]
    final_vname = "/".join([name, country, v_id, date])
    # Will put name and date by default. If it was different before, then final_vname
    # will be different from vname, and we will log this change
    return final_vname


def check_column(line, column, column_list, capital=False):
    """
    line = pandas.core.series.Series
    column : str, header of column to check
    column_list : dict {ori_text:new_text}

    Works for 
    - passage details/history
    - host
    - sequencing technology
    - assembly method
    """
    text_ok = False
    column_text = line[column]
    final_column_text = ""
    while not text_ok:
        # If we already saw this field, and it was valid, just skip checking this time
        if column_text in column_list:
            final_column_text = column_list[column_text]
            text_ok = True
        # If empty or UNKNOWN: put 'unknown'
        elif not column_text or column_text.lower() == "unknown":
            final_column_text = "unknown"
            text_ok = True
        else:
            # Put first letter in upper case if asked
            if capital:
                final_column_text = column_text.capitalize()
            # Remove accents
            final_column_text = unidecode.unidecode(final_column_text)
            text_ok = True

    if not column_text in column_list:
        column_list[column_text] = final_column_text
        line[column] = final_column_text

    if final_column_text != column_text:
        logger_log.info(f"'{column}' column: changed '{column_text}' to '{final_column_text}'.")


def check_mandatory_field(line, column, column_list, alert=False):
    """
    For a mandatory field, check that there is something in it. If not, ask submitter user 
    to fill it.
    Works for:
    - originating lab
    - address originating lab
    - submitting lab
    - address submitting lab

    """
    text = line[column]
    seq = line["covv_virus_name"]
    if text in column_list:
        new_text = column_list[text]
        return
    else:
        new_text = text
    while not new_text:
        if alert:
            logger_contact.warning(f"{seq} has no {column} text. Filled to unknown. "
                                    "Please give this information. NO RELEASE")
        else:
            logger_contact.warning(f"{seq} has no {column} text. Filled to unknown. "
                                    "Please give this information. Can be released.")
        logger_log.warning(f"ALERT: {seq} has no {column} text. Filled to unknown. "
                           "- contact submitter")
        
        new_text = "unknown"
        print(f"------{column.upper()} checking-----")
        print(f"For '{seq}' sequence, '{column}' column must be filled.")
    # Remove accents
    unidecode.unidecode(final_column_text)
    if text != new_text:
        logger_log.info(f"For sequence {seq}, '{column}' column: changed '{text}' to '{new_text}'.")
        line[column] = new_text
        column_list[text] = new_text


def check_date(line, dates_list):
    """
    line = pandas.core.series.Series
    """
    ori_date = line["covv_collection_date"]
    # Try to convert date to string, if it was in date format in excel
    try:
        ori_date = pd.to_datetime(ori_date).strftime("%Y-%m-%d")
    # If not able to convert, stay as it is, and it will be checked as a string
    except:
        pass
    seq = line["covv_virus_name"]
    # If we already saw and checked this, reuse what has been done
    if ori_date in dates_list:
        return
    # If no date given, put unknown
    if not ori_date or ori_date.lower() == "unknown":
        line["covv_collection_date"] = "unknown"
        return

    # Date given and never seen before: check format
    correct_format = False
    numbers = ori_date
    date = ori_date
    while not correct_format:
        try:
            # get year, month, day
            numbers = numbers.split("-")
            # Try to convert each field to int. If it does not work -> error in date format
            numbers_int = [int(n.strip()) for n in numbers]
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
            print("------COLLECTION DATE checking-----")
            numbers = input(f"Wrong format for collection date: {date}. \n"
                            "Please enter correct collection date in YYYY or "
                            "YYYY-MM or YYYY-MM-DD format:\n")
            date = numbers
    str_numbers = [str(n) for n in numbers]
    date_ok = "-".join(str_numbers)
    dates_list[date] = date_ok
    line["covv_collection_date"] = date_ok
    if date_ok != ori_date:
        logger_log.info(f"'Collection date' column: changed '{ori_date}' "
                        f"to '{date_ok}'.")


def check_gender(line, genders_list):
    """
    check gender: must be Male, Female or unknown
    """
    gender_checked = False
    ori_gender = line['covv_gender']
    gender = ori_gender
    while not gender_checked:
        if not gender or "unknown" in gender.lower():
            final_gender = "unknown"
            gender_checked = True
        elif gender == "Female" or gender == "Male":
            final_gender = gender
            gender_checked = True
        elif gender.lower() == "m":
            final_gender = "Male"
            gender_checked = True
        elif gender.lower() == "f":
            final_gender = "Female"
            gender_checked = True
        else:
            print("------GENDER checking-----")
            gender = input(f"Wrong format for gender: {gender}. \n"
                            "Please enter Male (m), Female (f) or unkown (u)\n")
    if final_gender != ori_gender:
        logger.info(f"'Gender' column: changed '{ori_gender}' to '{final_gender}'.")
          

if __name__ == '__main__':
    metadata = sys.argv[1]
    logger = utils.init_logger(f"{metadata}.log")
    logger = cure_metadata(metadata)
