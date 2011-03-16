#!/usr/bin/python2
'''
tquery means txt query, which will be used to txt files to database tables,
 and then execute sql query on the database.
Usage: ./tquery.py <pat> <sql>
where <pat> will be used to:
 - indicate text file paths and database table names
 - specify database path
Examples:
./tquery.py '$host.$app'
'''

import sys, os, os.path
import re
import sqlite3
from glob import glob

class QueryErr(Exception):
    def __init__(self, msg, obj=None):
        Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "Query Exception: %s\n%s"%(self.msg, self.obj)
    
def list_slices(seq, *slices):
    return [seq[i] for i in slices]

def dict_slice(d, *keys):
    return [d.get(x) for x in keys]

def readlines(path):
    with open(path) as f:
        return f.readlines()

def str2dict(template, str):
    def normalize(str):
        return re.sub('\$(\w+)', r'${\1:\w+}', str)
    def tore(str):
        return re.sub(r'\${(\w+):([^}]+)}', r'(?P<\1>\2)', str)
    rexp = '^%s$' % (tore(normalize(template)))
    match = re.match(rexp, str)
    if not match: return {}
    else: return dict(match.groupdict(), __self__=str)
    
def table_load(path):
    lines = [line.split() for line in readlines(path)]
    return lines[0], lines[1:]

def matrix_map(f, mat):
    return [map(f, row) for row in mat]
    
def table_query(path, *cols):
    header, data = table_load(path)
    if not cols: cols = header
    cols = [header.index(h) for c in cols]
    if any([c == -1 for c in cols]): raise QueryErr('no such cols', cols)
    return [list_slice(row, *cols) for row in data]

class KVTable:
    def __init__(self, conn, table='table0'):
        self.conn, self.table = conn, table

    def create_table(self):
        self.conn.execute('create table if not exists %s(k text,v text,primary key (k))'%(self.table))
        
    def get(self, k):
        self.create_table()
        v = list(self.conn.execute('select v from %s where k=?'%(self.table), (k,)))
        if v: return v[0][0]
        else: return None

    def set(self, k, v):
        self.create_table()
        self.conn.execute('insert or replace into %s(k,v) values(?,?)'%(self.table), (k,v))

def dump2db(conn, table, collector, default_type='float'):
    if not re.match('^\w+$', table): raise Exception('ill formed table name: %s'% table)
    def safe_float(x):
        try:
            return float(x)
        except TypeError,ValueError:
            return None
    def safe_int(x):
        try:
            return int(x)
        except TypeError,ValueError:
            return None
    type_map = dict(float='real',str='text',int='integer',bool='boolean')
    type_convertor = dict(float=safe_float, str=str, int=safe_int, bool=bool)
    meta = KVTable(conn)
    if meta.get(table) == 'done': return conn
    header,data = collector()
    names = [re.sub(':.*', '', h) for h in header]
    types = [re.sub('[^:]+:?', '', h, 1) or default_type for h in header]
    try:
        db_types = [type_map[t] for t in types]
    except Exception,e:
        raise QueryErr('no such type', types)
    data = [map(lambda type, cell: type_convertor[type](cell), types, row) for row in data]
    cols_scheme = map(lambda name,type: '%s %s'%(name, db_types), names, db_types)
    conn.execute('create table if not exists %s(%s)'%(table, ','.join(cols_scheme)))
    conn.executemany('insert or replace into %s(%s) values(%s)'%(table, ','.join(names), ','.join(['?']*len(names))), data)
    
    meta.set(table, 'done')
    conn.commit()
    return conn

def get_db(path, **collectors):
    conn = sqlite3.connect(path)
    [dump2db(conn, table, collector) for table,collector in collectors.items()]
    return conn

def txt_db(pat,default_type='float'):
    glob_pat, keys = re.sub('\$\w+', '*', pat), re.findall('\$(\w+)', pat)
    scheme = filter(lambda (p,d): d, [(p, str2dict(pat, p)) for p in glob(glob_pat)])
    def make_table_loader(p):
        def loader():
            return table_load(p)
        return loader
    collectors = [('_'.join(dict_slice(d, *keys)) or '_table', make_table_loader(p)) for p,d in scheme]
    def tables():
        return ['%s:str'%(k) for k in keys], [dict_slice(d, *keys) for p,d in scheme]
    if keys: collectors.append(('tables', tables))
    conn = get_db(pat+'.db', **dict(collectors))
    return conn

def _txt_db(path, table='_table', default_type='float'):
    return dump2db(sqlite3.connect(path+'.db'), table, lambda :table_load(path), default_type)

if __name__ == '__main__':
    pat = len(sys.argv) > 1 and sys.argv[1] or None
    sql = len(sys.argv) == 3 and sys.argv[2] or 'select * from tables'
    if not pat:
        print __doc__
        sys.exit()
    for cols in txt_db(pat).execute(sql):
        print '\t'.join(map(str, cols))
