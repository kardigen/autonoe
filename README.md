# Autonoe
Python based script to sort photos by its date and eliminate duplicates using SHA1 digest. 

## Installing required packages
**NOTE: Requires python3**
```
pip install -r requirements.txt
```

## Testing

```
cd test
./test.sh
```

## Running

Autonoe works in 4 phases:
 - init database file - autonoe.db
 - scan target dir (optional) to build existing photos database,
 - scan source diriectories to add input files to database
 - process files - this step will iterate over unprocessed input files and eventually copy nonduplicated files
 to target_dir/year/mounth/day
 
to get help run:

python3 autonoe/autonoe.py --help
