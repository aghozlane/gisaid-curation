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

import logging
logger = logging.getLogger("gisaid_curation.metadata")

from gisaid_curation import utils


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
    genders_list = {}
    covs_list = {}
    orilab_list = {}
    orilabaddress_list = {}
    sublab_list = {}
    sublabaddress_list = {}
    assembly_list = {}
    seqtechno_list = {}
    authors_list = {}
    vnames_list = []  # list of virus names
    
    # Sometimes, assembly method was incremented by a bad "Excell fill down" by the user. Hence,
    # it will always ask if method is ok (as these are different methods each time)
    # Curator can skip this column
    skip_assembly = False
    # same as for assembly method
    skip_seqtechno = False

    # Read input xls file
    md = pd.read_excel(file_in, sheet_name=1, header=0, dtype=str)
    instructions = pd.read_excel(file_in, sheet_name=0, header=0, dtype=str)


    # Empty cells
    md = md.fillna("")
    corresp_file = f"{file_in}.virus_IDs.txt"
    # create empty file to put curated metadata
    open(corresp_file, "w").close()
    # Check all fields, line by line
    for index, line in md.iterrows():
        # Skip 2nd header line
        if "filename" in line["fn"]:
            continue
        # Check covv_type. 
        check_type(line)
        # Check location field
        check_location(line, locations_list)
        print("")
        # Check virus names
        check_vnames(line, vnames_list, countries, corresp_file)
        print("")
        # Check dates
        check_date(line, dates_list)
        # Check passage history/details column
        check_column(line, "covv_passage", details_list, capital=True)
        print("")
        # Check host
        check_column(line, "covv_host", hosts_list, capital=True)
        # Check gender
        check_gender(line, genders_list)
        # Check originating and submitting lab and address
        # If not given, contact submitter and DO NOT release
        check_mandatory_field(line, "covv_orig_lab", orilab_list, alert=True)
        check_mandatory_field(line, "covv_orig_lab_addr", orilabaddress_list, alert=True)
        check_mandatory_field(line, "covv_subm_lab", sublab_list, alert=True)
        check_mandatory_field(line, "covv_subm_lab_addr", sublabaddress_list, alert=True)
        check_mandatory_field(line, "covv_authors", authors_list, 
                              alert=True, user_check=True)
        # Check sequence information. If not given, contact submitter, but release
        if not skip_assembly:
            # Sometimes, assembly method was incremented by a bad "Excell fill down" by the user. Hence,
            # it will always ask if method is ok (as these are different methods each time)
            # Curator can skip this column
            skip_assembly = check_mandatory_field(line, "covv_assembly_method", assembly_list, 
                                                  alert=False, user_check=True)
        if not skip_seqtechno:
            # same as for assembly_method
            skip_seqtechno = check_mandatory_field(line, "covv_seq_technology", seqtechno_list, 
                                                   alert=False, user_check=True)
        # Check coverage
        check_coverage(line, covs_list)

    logger.error("TO CURATOR: check 'Patient age'.")

    # Save as xls
    writer = pd.ExcelWriter(f"{file_in}.curated.xls") 
    instructions.to_excel(writer, sheet_name='instructions', index=False)
    md.to_excel(writer, sheet_name='Submissions', index=False)
    writer.save()


def check_type(line):
    """
    type must always be 'betacoronavirus'

    Parameters
    ----------
    line: pandas.core.series.Series
        line currently checked
    """
    vtype = line["covv_type"]
    if vtype != "betacoronavirus":
        logger.info(f"Type changed from '{vtype}' to 'betacoronavirus'.")
        line["covv_type"] = "betacoronavirus"


def check_location(line, locations):
    """
    Check Location column

    line = pandas.core.series.Series
    locations -> dict {prev_loc: new_loc}
    """
    write_warning = True
    ori_location = line["covv_location"]
    location = ori_location
    location_ok = False
    while not location_ok:
        # If we already saw this field, and it was valid, just skip checking this time
        if location in locations:
            location = locations[location]
            line["covv_location"] = location
            locations[ori_location] = location
            location_ok = True
            return
        # If never seen before, check format
        else:
            # Separate by continent, country, region
            sep = location.strip().split("/")
            # Keep only each field without accent, non-utf8 characters, and no trailing spaces
            sep = [unidecode.unidecode(f.strip()) for f in sep]
            formatted_sep = checked_location_format(sep, location, locations)
            location = " / ".join(formatted_sep)
            # If we removed accents, inform curator and ask for approval
            if location != ori_location:
                print("------LOCATION checking-----")
                print(f"{ori_location} was changed to {location}.")
                write_warning = False
            # If warning comes from a change, the 'LOCATION checking' flag was
            # already printed.
            # If not (just asking user confirmation), print 'LOCATION checking' here
            if write_warning:
                print("------LOCATION checking-----")
            # If it is a location we never saw before, ask user to validate
            answer = input(f"Is location '{location}' ok? ([Y]/n)")
            # If answer not yes/no, re-ask question
            while answer.lower() not in ["yes", "y", "no", "n", ""]:
                answer = input(f"Is location '{location}' ok? ([Y]/n)")
            # if answer is no, ask user for new text for location
            if answer.lower() in ["n", "no"]:
                answer = input("Please enter correct location, in "
                               "format 'Continent / Country [/ Region]'\n")
                location = answer
            elif not answer or answer.lower() in ["y", "yes"]:
                location_ok = True

    # If location was changed, inform curator.
    # If it was changed exactly as before, no need to write it
    if ori_location != location:
        logger.info(f"'Location' column: changed '{ori_location}' to '{location}'.")

    line["covv_location"] = location
    locations[ori_location] = location


def checked_location_format(sep, location, locations):
    """
    Check if Location is in expected format: Continent / Country / Region

    location -> str
    locations -> dict {prev_loc: new_loc}
    """
    new_sep = sep
    # Check that location has at least continent, and at most 3 fields
    # If not, ask user for location field
    while len(new_sep) < 2:
        print("------LOCATION checking-----")
        print(f"Wrong format for location: {location}")
        answer = input("Please enter correct location, in "
                       "format 'Continent / Country [/ Region / others]'\n") 
        new_sep = answer.strip().split("/")
        new_sep = [f.strip().capitalize() for f in new_sep]
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
    final_vname = checked_vname_format(vname, location, countries)
    if final_vname not in vnames_list:
        vnames_list.append(final_vname)
    # Log if we changed something
    if orig_vname != final_vname:
        with open(corresp_file, "a") as cf:
            cf.write("\t".join([orig_vname, final_vname]) + "\n")
        logger.warning(f"Changed sequence name '{orig_vname}' to '{final_vname}'. "
                        "Sequence can be released.")

    line["covv_virus_name"] = final_vname


def checked_vname_format(vname, location, countries):
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
    if fields[1].upper() not in location.upper():
        # Country not in location, but already seen before -> replace as it 
        # has been replaced before
        if fields[1].lower() in countries:
            country = countries[fields[1]]
        # Country not in location and never seen before: try to fix it
        else:
            country = location.split("/")[1].strip()
            print("------VIRUS NAME checking-----")
            print(f"'{vname}' is not a valid virus name. It should follow this format: "
                   "hCoV-19/Country/Identifier/2020. Here, 'Country' field does not correspond "
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
    First letter must be uppercase, others lowercase.
    if details/history, ask curator to confirm. Sometimes, it is written like 'clinical sample'.
    Should be replaced by 'Original (clinical sample)'

    line = pandas.core.series.Series
    column : str, header of column to check
    column_list : dict {ori_text:new_text}

    Works for 
    - passage details/history
    - host
    """
    text_ok = False
    column_text = line[column]
    seq = line["covv_virus_name"]

    final_column_text = column_text
    while not text_ok:
        # If we already saw this field, and it was valid, just skip checking this time
        if column_text.lower() in column_list:
            final_column_text = column_list[column_text.lower()]
            text_ok = True
        # If empty or UNKNOWN: put 'unknown'
        elif not column_text or column_text.lower() == "unknown":
            final_column_text = "unknown"
            column_list[column_text] = "unknown"
            text_ok = True
        else:
            # If column is covv_passage, we will ask user to confirm. If he confirms,
            # answer ok will be True. Otherwise, False -> recheck
            # Ask to check if cov_passage:
            answer_ok = True  # Did the curator answer yes, or a new text
            if column == "covv_passage":
                print("------PASSAGE DETAILS/HISTORY checking-----")
                answer = input(f"Is '{column_text}' ok for 'Passage details/history'? "
                                "It should start with Original or Vero. Y/new_text:\n" )
                # If user answered yes, we keep what we already have
                if not answer or answer.lower() in ["y", "yes", ""]:
                    final_column_text = column_text
                # If answer is a new string (not 'no'), this is the new text
                # User should not answer 'no', but let's check
                elif answer and answer.lower() not in ["no", "n"]:
                    final_column_text = answer
                else:
                    answer_ok = False
                # If he answered no, will be asked again
            # If user confirmed or gave new text, format text and release
            if answer_ok:
                # Put first letter in upper case if asked
                if capital:
                    final_column_text = final_column_text.capitalize()
                # Remove accents
                final_column_text = unidecode.unidecode(final_column_text)
                text_ok = True

    if not final_column_text in column_list:
        column_list[column_text.lower()] = final_column_text
    if final_column_text != column_text:
        logger.info(f"For {seq}, '{column}' column: changed '{column_text}' to '{final_column_text}'.")
        # Update information
        line[column] = final_column_text


def check_mandatory_field(line, column, column_list, alert=False, user_check=False):
    """
    For a mandatory field, check that there is something in it. If not, ask submitter 
    to fill it.

    Works for:
    - originating lab
    - address originating lab
    - submitting lab
    - address submitting lab
    - assembly
    - seq techno

    alert: true: if info empty, or curator says that it is not ok:
                 curator must contact submitter AND NO release
           false: if info empty, or curator says that it is not ok:
                  contact submitter but can release
    column: header of column
    line: whole line
    column_list: {text: new_text} for each 'text' already seen and checked

    return bool: if column will be skipped after or not

    """
    text = line[column]
    seq = line["covv_virus_name"]

    new_text = text

    # Checkpoint 1:
    # already seen and checked
    if text in column_list:
        new_text = column_list[text]
        line[column] = new_text
        return False

    # Checkpoint 2:
    # If new text is empty, or filled with unknown, and it is the first time we are 
    # in this case (did not end with first check point), write warning, or error according to 
    # 'alert' flag
    if not new_text or new_text.lower() == "unknown":
        if alert:
            logger.error(f"For {seq}, '{column}' is unknown. "
                          "Ask submitter to give this information. NO RELEASE")
            new_text = "unknown"
        else:
            logger.warning(f"{seq} has no {column} text. Filled to unknown. "
                           "Inform submitter he could give this information. Can be released.")
            new_text = "unknown"

    # Checkpoint 3:
    # If there is something (not unknown), ask user_check = True
    # Ask user if this text is ok or not 
    if new_text != "unknown" and user_check:
        text_ok = False
        while not text_ok:
            print(f"\n------{column.upper()} checking-----")
            answer = input(f"For seq '{seq}', is '{new_text}' fine for column {column}? Answers:"
                            " 'Y' to accept this text (default)\n"
                            "<new_value>: text to put instead of current one\n"
                            "'s': to skip this column in all sequences, and check "
                            "it yourself after).\n")
            # user asks to ignore this column starting from this line
            if answer.lower() in ['s', 'skip']:
                return True
            # User did entered a value:
            # if not yes and not no, new_text = new_value
            elif answer.lower() not in ['y', 'yes', '', 'n', 'no']:
                new_text = answer
                text_ok = True
            # if user said yes -> keep new_text, and text_ok = True
            elif answer.lower() in ['y', 'yes', '']:
                text_ok = True
            # if user said no, nothing changes (keep new_text, and text_ok still False)

    # Remove accents
    new_text = unidecode.unidecode(new_text)
    if text != new_text:
        logger.info(f"For sequence {seq}, '{column}' column: changed '{text}' to '{new_text}'.")
        # Update information
    column_list[text] = new_text
    line[column] = new_text
    return False


def check_date(line, dates_list):
    """
    line = pandas.core.series.Series
    """
    # Save original field to write changes if there are
    ori_date = line["covv_collection_date"].strip() 
    new_date = ori_date
    # Try to convert date to string, if it was in date format in excel
    try:
        # if complete date: written as 2020-03-01 00:00:00
        # if YYYY-MM -> written as is, so no need to change
        if "00:00:00" in new_date:
            new_date = str(pd.to_datetime(ori_date, yearfirst=True).strftime("%Y-%m-%d"))
    # If not able to convert, date is already a string, so stay as it is, and it will be checked as a string
    except:
        pass
    new_date = unidecode.unidecode(new_date)
    seq = line["covv_virus_name"]
    # If we already saw and checked this, reuse what has been done
    if new_date in dates_list:
        line["covv_collection_date"] = dates_list[new_date]
    # If no date given, put unknown (empty field is 'NA filled up')
    if not new_date or new_date.lower() == "unknown":
        line["covv_collection_date"] = "unknown"
        dates_list[new_date] = "unknown"
        return

    # Date given and never seen before: check format
    correct_format = False
    numbers = new_date
    date = new_date
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
            numbers = input(f"For sequence {seq}, wrong format for collection date: {date}. \n"
                            "Please enter correct collection date in YYYY or "
                            "YYYY-MM or YYYY-MM-DD format:\n")
            new_date = numbers
    str_numbers = [str(n) for n in numbers]
    date_ok = "-".join(str_numbers)
    dates_list[ori_date] = date_ok
    line["covv_collection_date"] = date_ok
    if date_ok != ori_date:
        logger.info(f"'Collection date' column: changed '{ori_date}' to '{date_ok}'.")


def check_gender(line, genders_list):
    """
    check gender: must be Male, Female or unknown
    """
    gender_checked = False
    ori_gender = line['covv_gender']
    seq = line["covv_virus_name"]
    gender = ori_gender
    if gender in genders_list:
        line['covv_gender'] = genders_list[gender]
        return
    while not gender_checked:
        if not gender or "unknown" in gender.lower() or "u" in gender.lower():
            final_gender = "unknown"
            gender_checked = True
        elif gender == "Female" or gender == "Male":
            final_gender = gender
            gender_checked = True
        elif gender.lower() in ["m", "male"]:
            final_gender = "Male"
            gender_checked = True
        elif gender.lower() in ["f", "female"]:
            final_gender = "Female"
            gender_checked = True
        else:
            print("------GENDER checking-----")
            gender = input(f"For {seq}, wrong format for gender: {gender}. \n"
                            "Please enter Male (m), Female (f) or unkown (u)\n")
    if final_gender != ori_gender:
        logger.info(f"For {seq}, 'Gender' column: changed '{ori_gender}' to '{final_gender}'.")
    line['covv_gender'] = final_gender
    genders_list[ori_gender] = final_gender
          

def check_coverage(line, cov_list):
    """
    Check coverage format: 
    * ',' if > 1000
    * lower 'x' after the number

    If not given: unknown, contact submitter but release
    """
    cov_ok = False
    ori_cov = line["covv_coverage"]  # keep original value
    seq = line["covv_virus_name"]
    cov = ori_cov

    if ori_cov in cov_list:
        cov = cov_list[ori_cov]
        cov_ok = True

    while not cov_ok:
        # If empty, fill with unknown and contact submitter
        if not cov or cov.lower() == "unknown":
            cov = "unknown"
            cov_ok = True
        # First, keep only coverage number (no 'x')
        else:
            cov = cov.lower().strip().split('x')[0]
            # try to convert to int.
            try:
                int_cov = int(cov.replace(",", ""))
                cov = str(f"{int_cov:,}x")
                cov_ok = True
            except ValueError as e:
                print("------COVERAGE checking-----")
                cov = input(f"Given coverage ({cov}) for {seq} is not an int. "
                             "Please provide an int value for coverage. "
                             "If coverage is unkown, type 'U' (default):\n")
                if cov == "u":
                    cov = "unknown"

    # If there was something in coverage but it was changed, log it
    # If it was empty, we just replaced by unknown. Already logged.
    if ori_cov != cov and ori_cov:
        logger.warning(f"For {seq} 'Coverage' column: changed '{ori_cov}' to "
                       f"'{cov}'. Sequence can be released")
    elif not ori_cov:
        logger.warning(f"For {seq}, coverage not given. Filled with unknown "
                        "(Sequence can be released)")
    cov_list[ori_cov] = cov
    line["covv_coverage"] = cov


if __name__ == '__main__':
    parsed = utils.make_parser(sys.argv[1:])
    metadata = parsed.xls_file
    logger = utils.init_logger(metadata, "gisaid_curation")
    cure_metadata(metadata)
