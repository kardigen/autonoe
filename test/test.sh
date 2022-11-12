#!/bin/sh

# clean env
rm -f autonoe.db
rm -f test.log
rm -fr tmp
mkdir tmp

echo "=> Test initialize DB"
python3 ../autonoe/autonoe.py -i

if [ ! -f autonoe.db ]; then
    echo "ERROR: no autonoe.db file present"
    exit 2
fi
echo '=> OK'

echo "=> Test reading data/src/dates"
python3 ../autonoe/autonoe.py -s data/src/dates ".DS_Store" > test.log

RESULT=$(diff test.log expected_read_source_dates_1.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'

echo "=> Test reading existing data/src/dates"
python3 ../autonoe/autonoe.py -s data/src/dates ".DS_Store" > test.log

RESULT=$(diff test.log expected_read_source_dates_2.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'

echo "=> Test processing data/src/dates"
python3 ../autonoe/autonoe.py -p tmp > test.log
RESULT=$(diff test.log expected_process_dates.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi

find tmp > test.log
RESULT=$(diff test.log expected_target_dir.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'

echo "=> Test processed data/src/dates"
python3 ../autonoe/autonoe.py -p tmp > test.log
RESULT=$(diff test.log expected_processed.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'

echo "=> Test rebuild data/src/dates"
rm -f autonoe.db
python3 ../autonoe/autonoe.py -i

echo "... reading target"
python3 ../autonoe/autonoe.py -t tmp ".DS_Store" > test.log
RESULT=$(diff test.log expected_scan_target.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi

echo "... reading data/src/dates"
python3 ../autonoe/autonoe.py -s data/src/dates ".DS_Store" > test.log
RESULT=$(diff test.log expected_read_source_dates_1.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi

echo "... check processed data/src/dates"
python3 ../autonoe/autonoe.py -p tmp > test.log
RESULT=$(diff test.log expected_matched.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'

echo "=> Test reading data/src/formats"
python3 ../autonoe/autonoe.py -s data/src/formats ".DS_Store" > test.log

RESULT=$(diff test.log expected_read_source_formats.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'


echo "=> Test process data/src/formats"
python3 ../autonoe/autonoe.py -p tmp > test.log

RESULT=$(diff test.log expected_process_formats.log)
if [ -n "$RESULT" ]; then
    echo "ERROR: log differences detected"
    echo "$RESULT"
    exit 2
fi
echo '=> OK'