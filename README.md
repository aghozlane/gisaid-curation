# Help for GISAID metadata curation process

**Disclaimer:** This software is distributed as it is. Please double-check the results.
If you encounter any bug/miss-correction, please put an issue on the github page, or send pull-requests!

**This soft does not check 'patient age' and 'authors' columns. Please check them by yourself**

## Requirements

Python3 with pip (pip3).


## How to get it?

Try to clone the repository using ssh: 

	git clone git@github.com:asetGem/gisaid-curation.git

If you did not put your ssh public key on github.com, use https:

	git clone https://github.com/asetGem/gisaid-curation.git

Then:

	cd gisaid-curation
	pip3 install --user -r requirements.txt

to update, go to your 'gisaid-curation' folder, and type
	
	git pull

## How to use it

	./data_curation.py -f 'path to metadata xls file'

## What it does

For each field, check if format is as expected (spaces in location, upper cases, 'unknown' in empty cells, 4,000x coverage format etc.). For fields like 'Location', 'Assembly' or 'Sequencing technology', it asks you to check that what is written is coherent. If not, give the correct value, and it will automatically change it. For example, we often see 'USA / Wyoming' instead of 'North America / USA / Wyoming'.



## Output

As an output of the script, you have the **currated xls file** that you can upload on the server. **warning** don't forget the sequence curation step before uploading, there might be some text to add to Comment and Symbol columns!

A file with what you have to **say to the submitter** (things that require 'Contact Submitter' in the guidelines). And if you can **release or not** the sequence:

- WARNING are for things to inform the submitter, but sequence can still be released.
- ERROR are for things to inform the submitter, but you need to hand him back the sequences.


More info:

- `<metadatafile.xls>.changes.log`: all changes done in the metadata
- `<metadatafile.xls>.contact_sub.log`: changes done that lead to submitter contact. If sequence cannot be released (ERROR), it is also written. Also, this soft does not check 'patient age' and 'authors' columns. Please check them by yourself.
- `<metadatafile.xls>.virus_IDs.txt`: tsv file containing sequence IDs that have been modified. 1st column is original ID, 2nd is the new ID.
- `<metadatafile.xls>.curated.xls`: the new xls file, with curated metadata

