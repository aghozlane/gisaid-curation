# Help for GISAID metadata curation process

## Requirements

Python3 with pip (pip3).


## How to get it?

	git clone git@github.com:asetGem/gisaid-curation.git
	cd gisaid-curation
	pip3 install requirements.py

to update, go to gisaid-curation, and type
	
	git pull

## How to use it

	./data_curation.py -f 'path to metadata xls file'

## Output

- `<metadatafile.xls>.changes.log`: all changes done in the metadata
- `<metadatafile.xls>.contact_sub.log`: changes done that lead to submitter contact. If sequence cannot be release, it is also written. Also, this soft does not check 'patient age' and 'authors' columns. Please check them by yourself
- `<metadatafile.xls>.virus_IDs.txt`: tsv file containing sequence IDs that have been modified. 1st column is original ID, 2nd is the new ID.
- `<metadatafile.xls>.curated.xls`: the new xls file, with curated metadata

