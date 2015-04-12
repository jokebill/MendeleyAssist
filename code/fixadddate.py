#!/usr/bin/env python
import logging
LOGLEVEL = logging.DEBUG
logging.basicConfig(level = LOGLEVEL,
        filename = 'fixadddate.log',
        filemode = 'w')

def main(dbfile, foldername):
    import sqlite3 as sql
    import os.path
    import numpy.random as nr
    import datetime
    import time
    
    if not os.path.isfile(dbfile):
        logging.ERROR('Incorrect database file')
    else:
        conn = sql.connect(dbfile)
    c = conn.cursor()
    cmdstr = '''SELECT id,name FROM Folders WHERE name = ?'''
    c.execute(cmdstr,(foldername,))
    fdid0 = c.fetchall()
    fdidall = []
    while fdid0:
        fdid1 = []
        for fdid in fdid0:
            c.execute("SELECT id,name FROM Folders WHERE parentId = ?",(fdid[0],))
            fdid1 = fdid1 + c.fetchall()
        fdidall = fdidall + fdid1
        fdid0 = fdid1[:]
    c.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='tmpfdid';")
    if c.fetchall():
        c.execute("DROP TABLE tmpfdid")

    c.execute("CREATE TABLE tmpfdid(id,name)")
    c.executemany("INSERT INTO tmpfdid(id,name) values (?,?)",fdidall)

    c.execute('''
SELECT
  Documents.id,
  SUBSTR(Documents.note,9,10) AS added_in_note
FROM tmpfdid INNER JOIN DocumentFolders ON
  DocumentFolders.folderId = tmpfdid.id
INNER JOIN Documents ON
  Documents.id = DocumentFolders.documentId
  ''')
    res = c.fetchall()
    idrec = [i[0] for i in res]
    addstr = [i[1] for i in res]
    unixtimes=[
        int(time.mktime(
            (datetime.datetime.strptime(str0,"%Y-%m-%d")+
             datetime.timedelta(0,nr.uniform(0,24*60*60))).timetuple()))
        for str0 in addstr
        ]
    print zip(idrec,unixtimes)
    c.executemany("UPDATE Documents SET added = ? WHERE id = ?",zip(unixtimes,idrec))
    
    conn.commit()
    c.execute("DROP TABLE tmpfdid")
    #c.execute("DROP TABLE tmpdoc")
    conn.close()

if __name__ == '__main__':
    import sys
    nin = len(sys.argv)
    if nin<>3:
        print nin
        print "fixadddate.py <MendeleyDatabase> <FolderToFix>"
        sys.exit(-1)
    dbfile=sys.argv[1]
    foldername=sys.argv[2]
    print dbfile
    print foldername

    main(dbfile, foldername)
