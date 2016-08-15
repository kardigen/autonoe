# Autonoe
Python based script to sort photos by its date and eliminate duplicates using SHA1 digest

## Installing required packages

pip install -r requirements.txt

## Running

Autonoe works in 4 phases:
 - init database file - autonoe.db
 - scan target dir (optional) to build existing photos databse,
 - scan source diriectories to add input fies to databse
 - process files - this step will iterate over unprocessed input files and eventually copy nonduplicated files
 to target_dir/year/mounth/day
 
to get help run:

python autonoe/autonoe.py --help


 

