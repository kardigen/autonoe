#!/usr/bin/env python

import getopt, sys, os, os.path, time, sqlite3, hashlib, datetime, time, exifread, subprocess, locale, re
from os.path import join

DB_NAME = "autonoe.db"

HOME_DIR = os.getcwd()
date_pattern1 = re.compile(r"\d\d\d\d:\d\d:\d\d")
date_pattern2 = re.compile(r"\d\d\d\d/\d\d/\d\d")
date_pattern3 = re.compile(r"\d\d\d\d\\\d\d\\\d\d")
def initDb():
    print('initializing DB...')
    try:
        db = sqlite3.connect(DB_NAME)
        c = db.cursor()
        
        try:
            c.execute('''DROP TABLE sources''')
            c.execute('''DROP TABLE targets''')
        except:
            pass
        
        c.execute('''CREATE TABLE sources (id integer PRIMARY KEY, source_path text, date text, date_type text, hash text, status text)''')
        c.execute('''CREATE TABLE targets (id integer PRIMARY KEY, target_path text, source_path text, date text, date_type text, hash text, status text)''')
        c.execute('''CREATE INDEX IF NOT EXISTS target_hash_idx on targets (hash)''')
        c.execute('''CREATE INDEX IF NOT EXISTS source_hash_idx on sources (hash)''')
        
        db.commit()
        db.close()
        print('Done.')
    except:
        print('ERROR - init paths table')
        raise
    
def parseDate(aFile,path):
    tags = exifread.process_file(aFile)
    date = str(tags['EXIF DateTimeOriginal']).split()[0] if ('EXIF DateTimeOriginal' in tags) else None
    if(date is not None):
        date_type = 'EXIF'
        if(not date_pattern1.match(date)):
            if( date_pattern2.match(date)):
                date = date.replace('/',":")
            elif( date_pattern3.match(date)):
                date = date.replace('\\',":")
    
    if (date is None):
        date = time.strftime('%Y:%m:%d',time.localtime(os.path.getctime(path)))
        date_type = 'file time'
    return [date,date_type]


def getFileHash(aFile):
    hasher = hashlib.sha512()
    while True:
        r = aFile.read(4096)
        if not len(r):
            break
        hasher.update(r)
    return hasher.hexdigest()
        
def scanSourceFiles(sourcePath):
    print('Scaning source directory: '+ repr(sourcePath[0]) )
    excludes = r'' + (re.escape(sourcePath[1]) if len(sourcePath) > 1 else '$')
    print ('exclude ' + excludes)
    try:
        db = sqlite3.connect(DB_NAME)
        for root, dirs, files in os.walk(sourcePath[0]): # Walk directory tree
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            files[:] = [f for f in files if not re.match(excludes, f)]
            for f in files:
                path = join(root, f)
                if not os.path.isfile(path):
                    continue
                
                print('## Scanning: ' + repr(path))
                aFile = open(path, 'rb')
                try:                 
                    parsedDate = parseDate(aFile,path)
                    fileHash = getFileHash(aFile)
                except:
                    print('ERROR parsing - skipping - file: ' + repr(path))
                    continue
                finally:
                    aFile.close()
                    
                #print 'source: ' + path + ' date: ' + str(parsedDate[0]) + ' hash: ' + fileHash
                result = db.execute("SELECT * FROM sources WHERE hash = '%s'" % (fileHash))
                records = result.fetchall()
                if(len(records) == 0):
                    #print "INSERT INTO sources VALUES (NULL,'%s','%s','%s','%s','source_scan')" % (path,parsedDate[0],parsedDate[1],fileHash)
                    db.execute("INSERT INTO sources VALUES (NULL,'%s','%s','%s','%s','source_scan')" % (path,parsedDate[0],parsedDate[1],fileHash))
                    print('++ Added: ' + repr(path))
                else:
                    existsAlready = False
                    for record in records:
                        if( repr(record[1]) == repr(path) and repr(record[2]) == repr(parsedDate[0]) and repr(record[3]) == repr(parsedDate[1])):
                            #print 'source duplication found: ' + path + " - no action"
                            existsAlready = True
                            break
                    if(not existsAlready):
                        #print "INSERT INTO sources VALUES (NULL,'%s','%s','%s','%s','source_scan')" % (path,parsedDate[0],parsedDate[1],fileHash)
                        db.execute("INSERT INTO sources VALUES (NULL,'%s','%s','%s','%s','source_scan')" % (path,parsedDate[0],parsedDate[1],fileHash))
                        print('++ Added: ' + repr(path))
                    else:
                        print('## Already exists: ' + repr(path))
            db.commit()    
                
        
        print('Scaning source directory: '+ repr(sourcePath[0]) + ' done.')
    except:
        print('ERROR - CRITICAL ERROR')
        raise
    finally:
        db.close()
    
def scanTargetFiles(targetPath):
    print('Scaning target directory: '+ repr(targetPath[0]) )
    excludes = r'' + (re.escape(targetPath[1]) if len(targetPath) > 1 else '$')
    try:
        db = sqlite3.connect(DB_NAME)
        #clean targets
        try:
            db.execute('''DROP TABLE targets''')
        except:
            pass
        db.execute('''CREATE TABLE targets (id integer PRIMARY KEY, target_path text, source_path text, date text, date_type text, hash text, status text)''')
        db.commit()
        
        # Walk directory tree
        for root, dirs, files in os.walk(targetPath[0]):
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            files[:] = [f for f in files if not re.match(excludes, f)]
            for f in files:
                path = join(root, f)
                if not os.path.isfile(path):
                    continue
                
                print ('## Scanning: ' + repr(path))
                aFile = open(path, 'rb')                
                parsedDate = parseDate(aFile,path)
                fileHash = getFileHash(aFile)
                aFile.close()
                
                db.execute("INSERT INTO targets VALUES (NULL,'%s','%s','%s','%s','%s','target_scan')" % (path,path,parsedDate[0],parsedDate[1],fileHash))
            db.commit()
        print('Scaning target directory: '+repr( targetPath[0] ) + ' done.')
    except:
        print('ERROR')
        raise
    finally:
        db.close()
    
def processSourceFiles(targetPath):
    print('Processing files to target directory: '+ repr( targetPath[0] ))
    try:
        
        db = sqlite3.connect(DB_NAME)
        result = db.execute("SELECT * FROM sources WHERE status = 'source_scan'")
        for record in result:
            #print "SELECT * FROM targets WHERE hash = '%s'" % (record[4])
            targetWithHash = db.execute("SELECT * FROM targets WHERE hash = '%s'" % (record[4]))
            targetWithHashResults = targetWithHash.fetchall()
            dateSplited = record[2].split(':')
            if len(dateSplited) < 3:
                dateSplited = record[2].split('/')
            srcFile = record[1] if repr(record[1][0]) == repr(u'/') else HOME_DIR +"/" + record[1] 
            # print(dateSplited)
            targetPathFull = targetPath[0] + '/' + dateSplited[0] + "/" + dateSplited[1] + "/" + dateSplited[2] + "/"
            targetDir = targetPathFull if repr(targetPathFull[0]) == repr(u'/') else HOME_DIR + "/" + targetPathFull
            
            if(len(targetWithHashResults) == 0):
                try:
                    os.makedirs(targetDir)
                except:
                    pass
                
                print ("++ Copy new file: cp -p -n " + repr(record[1]) + " " + repr(targetPathFull))
                cpResult = subprocess.call(['cp','-p','-n',srcFile,targetDir ])
                if(cpResult == 0):
                    #print "INSERT INTO targets VALUES (NULL,'%s','%s','%s','%s','%s','coppied')" % (targetPathFull,record[1],record[2],record[3],record[4])
                    db.execute("INSERT INTO targets VALUES (NULL,'%s','%s','%s','%s','%s','coppied')" % (targetPathFull,record[1],record[2],record[3],record[4]))
                    #print "UPDATE sources SET status = 'coppied' WHERE id = " + str(record[0])
                    db.execute("UPDATE sources SET status = 'coppied' WHERE id = " + str(record[0]))
                else:
                    print ( "ERROR copy new: cp -p -n " + repr(srcFile) + " " + repr(targetDir))
            else:
                for targetRecord in targetWithHashResults:
                    #check if dates are equal
                    if targetRecord[3] == record[2] and targetRecord[4] == record[3]:
                        #print "UPDATE sources SET status = 'dupplicated' WHERE id = " + str(record[0])
                        db.execute("UPDATE sources SET status = 'dupplicated' WHERE id = " + str(record[0]))
                        print ("== Source file matches existing file: " + srcFile + " == " + targetRecord[2])
                        continue
                    else:
                        try:
                            os.makedirs(targetDir)
                        except:
                            pass
                        
                        print ("++ Copy different file: cp -p -n " + repr(srcFile) + " " + repr(targetDir))
                        cpResult = subprocess.call(['cp','-p','-n',srcFile  ,targetDir ])
                        if(cpResult == 0):
                            #print "INSERT INTO targets VALUES (NULL,'%s','%s','%s','%s','%s','coppied')" % (targetPathFull,record[1],record[2],record[3],record[4])
                            db.execute("INSERT INTO targets VALUES (NULL,'%s','%s','%s','%s','%s','coppied')" % (targetPathFull,record[1],record[2],record[3],record[4]))
                            #print "UPDATE sources SET status = 'coppied' WHERE id = " + str(record[0])
                            db.execute("UPDATE sources SET status = 'coppied' WHERE id = " + str(record[0]))
                        else:
                            print ("ERROR copy different dates: cp -p -n " + repr(srcFile) + " " + repr(targetDir))
        
        db.commit()
        print('Processing files done.')
    except:
        print('ERROR')
        raise
    finally:
        db.close()
        
def usage():
	print('usage: python autonoe ?option?')
	print("  available options:")
	print("    [-i | --init-db] - initialize database autonoe.db file in current directory - it will remove all the data if db exists")
	print("    [-t | --scan-target <target_dir_path> <excludes>] - scan target directory to build target files index, excludes is optional parameter to exclude some names of folders and files")
	print("    [-s | --scan-source <source_dir_path> <excludes>] - scan source directory to build source file queue, excludes is optional parameter to exclude some names of folders and files")
	print("    [-p | --process <target_dir_path>] - process sources and targets and copy new files and update existing")
	

def main(argv):
    locale.setlocale(locale.LC_ALL, '')
    print ("locale: " + str(locale.getlocale()))
    try:
        opts,args = getopt.getopt(argv,"histp",["help","init-db","scan-source","scan-target","process"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    if(len(opts) == 0):
        usage()
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-i", "--init-db"):
            initDb()
        elif opt in ("-s", "--scan-source"):
            scanSourceFiles(args)
        elif opt in ("-t", "--scan-target"):
            scanTargetFiles(args)
        elif opt in ("-p", "--process"):
            processSourceFiles(args)
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
