def getopts(logfile="mendeleyassist.log"):
    from optparse import OptionParser
    import logging

    p = OptionParser()
    p.add_option('-l', '--logging-level',
            dest = 'loglevel', default = 'info', 
            help = 'Logging level')
    p.add_option('-f', '--logging-file',
            dest = 'logfile', default = logfile,
            help = 'Logging file name')
    p.add_option('-r', '--reset',
            action = 'store_true', dest = 'reset',
            help = 'Reset the record for current platform')
    (opts, args) = p.parse_args()

    LOG_LEVELS = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG,
            }
    r={}
    r['loglevel'] = LOG_LEVELS.get(opts.loglevel, logging.NOTSET)
    r['logfile'] = opts.logfile
    r['reset'] = opts.reset

    #nin = len(args)
    #if nin<1:
        #r['pathdb'] = DefaultDb
    #else:
        #r['pathdb'] = args[0]

    logging.basicConfig(
            level = r['loglevel'],
            filename = r['logfile'],
            filemode = 'w',
            format = '%(asctime)s %(name)s-%(levelname)s: %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S')
    return r  

