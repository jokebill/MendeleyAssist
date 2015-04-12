'''This module contains all exception classes:
    Error: base exception class
    |
    |--DbError: exception related to database
    |
    |--ProcError: exception related to procdure
'''
class Error(Exception):
    def __init__(self, msg):
        self.message = msg
        self.code = 1
    def __init__(self, code, msg):
        self.code = code
        self.message = msg
    def __str__(self):
        return repr(self.message)

class DbError(Error):
    def __init__(self, msg):
        Error.__init__(self,100,msg)

class InputError(Error):
    def __init__(self, msg):
        Error.__init__(self, 300, msg)

def main():
    try:
        raise DbError(1000)
    except Error as e:
        print "Received error with code:{0}".format(e.code)

if __name__=='__main__':
    main()
