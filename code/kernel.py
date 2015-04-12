#!/usr/bin/env python
'''This module provides kernal functions to assist the Mendeley Desktop software'''
import logging
import os
from ErrorClass import *
import sqlite3 as sql
from opts import getopts

def sysinfo():
    '''
A function to get the uuid, mac address, system name, system version,
user name.
'''
    global SysInfo
    import platform, getpass, hashlib
    from uuid import getnode
    
    log = baselog.getChild('sysinfo')
    sysname = platform.system()
    sysver = platform.release()
    username = getpass.getuser()
    macadd = '{0:012X}'.format(getnode())
    macadd = ':'.join([macadd[i:i+2] for i in range(0,len(macadd),2)])

    idstr = "{0} {1} {2} {3}".format(macadd,sysname,sysver,username)
    hashid = hashlib.md5(idstr).hexdigest()
    SysInfo["hash"]=hashid
    SysInfo["mac"]=macadd
    SysInfo["sys"]=sysname
    SysInfo["ver"]=sysver
    SysInfo["user"]=username

    log.debug('''-----sys info-------
    %s''', dictdisp(SysInfo))
    return idstr

def fixpath(setpath=None, dbreset=False):
    global MedInfo
    log = baselog.getChild('fixpath')
    log.debug('%s',PathDb)
    if not PathDb:
        errmsg = "PathDb uninitialized"
        print errmsg
        log.error(errmsg)
        raise DbError(errmsg)
    try:
        conn = sql.connect(PathDb)
    except sql.Error as e:
        errmsg = 'Failed to connect to database : {0}'.format(e.message)
        print errmsg
        log.error(errmsg)
        raise DbError(errmsg)
    conn.row_factory = sql.Row
    c = conn.cursor()
    cmdstr='''
    SELECT * FROM Paths
    WHERE hash=?'''
    try:
        c.execute(cmdstr,(SysInfo['hash'],))
    except sql.Error as e:
        errmsg = 'Sqlite engine error: {0}'.format(e.message)
        print errmsg
        log.error(errmsg)
        conn.close()
        raise DbError(errmsg)
    res=c.fetchone()
    if not res or dbreset:
        ## New system detected
        if not hasattr(setpath, '__call__'):
            errmsg = 'Argument setpath should be a function'
            print errmsg
            log.error(errmsg)
            conn.close()
            raise InputError(errmsg)
        for k,v in setpath().iteritems():
            MedInfo[k]=v
        MedInfo['refpath']=path2uri(MedInfo['refpath'])
        log.debug('''-----returned Mendeley Info-----
        {0}'''.format(dictdisp(MedInfo)))
        ## Write mendeley information to database
        cmdstr='''
            INSERT OR REPLACE INTO Paths
                (hash,mac,sys,ver,user,
                 dbfile,refpath,progfile)
            VALUES (?,?,?,?,?,?,?,?)
            '''
        try:
            c.execute(cmdstr,(
                    SysInfo["hash"],SysInfo["mac"],SysInfo["sys"],
                    SysInfo["ver"],SysInfo["user"],MedInfo["dbfile"],
                    MedInfo["refpath"],MedInfo["progfile"]))
        except sql.Error as e:
            errmsg="Error writing path infomation to PathDb: {0}".format(e.message)
            print errmsg
            log.error(errmsg)
            conn.close()
            raise DbError(errmsg)
        conn.commit()
    else:
        ## Get mendeley information from database
        for k in MedInfo.iterkeys():
            MedInfo[k]=res[k]
    conn.close()

    ## fix attachment paths in Mendeley database
    try:
        conn = sql.connect(MedInfo['dbfile'])
    except sql.Error as e:
        errmsg='Error connecting to Mendeley database.'
        print errmsg
        log.error(errmsg)
        raise DbError(errmsg)
    
    c=conn.cursor()
    try:
        c.execute("SELECT hash,localUrl FROM Files")
    except sql.Error as e:
        errmsg='Error read Files table from Mendeley database: {0}'.format(e.message)
        print errmsg
        log.error(errmsg)
        raise DbError(e.message)
    res = c.fetchall()
    if res:
        resfix = [(MedInfo['refpath']+r[1][r[1].rfind('/'):],r[0]) for r in res]
        c.executemany('''
            UPDATE Files
            SET localUrl = ?
            WHERE hash = ?;''',
            resfix)
        log.debug('First row in fixed path: %s',resfix[0])
        conn.commit()

    ## fix organiser path in mendeley database
    try:
        refpath_p = uri2path(MedInfo['refpath'])
        log.debug('Reference path for organiser is : %s',refpath_p)
        c.execute('''
            UPDATE Settings
            SET value = ?
            WHERE key = 'Organiser/OrganiserLocation';''',
            (refpath_p,))
    except sql.Error as e:
        errmsg='Error update Organiser path for Mendeley: {0}'.format(e.message)
        print errmsg
        log.error(errmsg)
        raise DbError(errmsg)
    conn.commit()
    conn.close()

    ## Run Mendeley
    if SysInfo["sys"]!="Darwin":
        import subprocess
        subprocess.call(MedInfo['progfile'])

def dictdisp(d=None):
    r=""
    if isinstance(d, dict):
        for k,v in d.iteritems():
            r=r+'\t{0}:\t{1}\n'.format(k,v)
    r=r[:-1]
    return r

def setMendeleyData():
    info = MedInfo.copy()
    print "This is a new platform: \n"
    print dictdisp(SysInfo)
    info['dbfile'] = raw_input("Type the database path: ")
    info['refpath'] = raw_input("Type the real reference folder path: ")    
    info['progfile'] = raw_input("Type type program file path: ")
    return info

def moveDownloaded():
    import platform
    log = __base_logger__.getChild('moveDownloaded')
    if platform.system() == 'Windows':
        import shutil
        srcdir = os.path.join(os.path.split(__info__.dbfile)[0],'Downloaded')
        src = os.listdir(srcdir)
        dst = __info__.refpath[len('file:///'):].replace('/','\\')
        if len(src) > 0:
            for f in src:
                shutil.move(os.path.join(srcdir,f),dst)
            log.info("%d files have been moved from Downloaded folder to Reference folder.",len(src))

def path2uri(path):
    from urllib import quote
    import re
    if path.find('file://') == 0:
        return path
    else:
        pathsplit = re.split(r"[/\\]+",path)
        if '' in pathsplit:
            pathsplit.remove('')
        uricomp=[quote(x,safe=':')
                for x in pathsplit]
        uricomp.insert(0,"file://")
        return '/'.join(uricomp)

def uri2path(uri):
    import platform, os.path, re
    from urllib import unquote
    cursys = platform.system()
    header = 'file://'
    if uri.find(header)== 0:
        uri=uri[len(header):]
    uricomp = [unquote(x)
            for x in re.split(r"[/\\]+",uri)]
    if '' in uricomp:
        uricomp.remove('')
    if cursys <> "Windows":
        uricomp.insert(0,'')
    return os.path.sep.join(uricomp)

class FixDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
             raise KeyError("Immutable dict")
        dict.__setitem__(self, key, value)

SupportSystems = ('Windows','Linux','Darwin')
baselog = None
SysInfo = FixDict(hash=None,mac=None,sys=None,ver=None,user=None)
MedInfo = FixDict(dbfile=None,refpath=None,progfile=None)
PathDb = None

def init():
    global baselog,SysInfo,PathDb
    baselog = logging.getLogger("kernel")
    ## for debug only
    ## end debug only
    sysinfo()
    ProgDir = os.path.sep.join(os.getcwd().split(os.path.sep)[:-1])
    PathDb = os.path.join(ProgDir,'res','MendeleyPaths.sqlite')

def main():
    global logger

    opts=getopts()
    init()
    fixpath(setMendeleyData,opts['reset'])

if __name__ == '__main__':
    main()
else:
    init()
