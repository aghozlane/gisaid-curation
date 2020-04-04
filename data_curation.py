#!/usr/bin/env python3
# coding: utf-8

import sys

import pandas as pd



def cure_metadata(file_in):
    """
    file_in in xls format
    """
    md = pd.read_excel(file_in, sheet_name=1, header=0, dtype=str)
    # Empty cells -> put empty string
    md = md.fillna("")
    print(md.dtypes)
    # print(md["covv_passage"].head(n=13))
    # print(md["submitter"])
    for index, line in md.iterrows():
        # Skip 2nd header line
        if "filename" in line["fn"]:
            continue
        # check_virus_name(line)
        check_details(line)
        check_date(line)

        # print(line)
        # break
    # print(md["covv_passage"].head(n=13))


def check_details(line):
    """
    line = pandas.core.series.Series
    """
    details = line["covv_passage"]
    if not details:
        line["covv_passage"] = "unknown"
    else:
        line["covv_passage"] = details.capitalize()


def check_date(line):
    """
    line = pandas.core.series.Series
    """
    date = line["covv_collection_date"]
    print(date)
    if not date:
        line["covv_collection_date"] = "unknown"
        return
    numbers = date.split("-")
    for number in numbers:
        int(number)
        # try:
        #     int(number)
        # except:
        #     print()

    return

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
