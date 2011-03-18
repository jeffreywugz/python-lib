#!/usr/bin/python2
'''
tquery means txt query, which will be used to translate txt files to database tables,
 and then execute sql query on the database.
Usage: ./tquery.py <pat> <sql>
where <pat> will be used to:
 - indicate text file paths and database table names
 - specify database path
Examples:
vmstat 1 5|sed '1d'|sed 's/in/intr/' >vmstat.log && tquery.py vmstat.log 'select plot("-,+", rowid, intr) from _table'
'''

import sys, os, os.path
import re
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

class QueryErr(Exception):
    def __init__(self, msg, obj=None):
        Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "Query Exception: %s\n%s"%(self.msg, self.obj)

def safe_int(x, default=0):
    try:
        return int(x)
    except ValueError:
        return default
    
def list_slices(seq, *slices):
    return [seq[i] for i in slices]

def dict_slice(d, *keys):
    return [d.get(x) for x in keys]

def readlines(path):
    f = open(path)
    content = f.readlines()
    f.close()
    return content

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
    cols_scheme = map(lambda name,type: '%s %s'%(name, type), names, db_types)
    conn.execute('create table if not exists %s(%s)'%(table, ','.join(cols_scheme)))
    conn.executemany('insert or replace into %s(%s) values(%s)'%(table, ','.join(names), ','.join(['?']*len(names))), data)
    
    meta.set(table, 'done')
    conn.commit()
    return conn

class SqliteAgg:
    def __init__(self, **kw):
        self.kw = kw
        self.data = []

    def step(self, *values):
        self.data.append(values)

    def finalize(self):
        return None

def make_sqlite_agg_class(func):
    class SqliteAggClass(SqliteAgg):
        def __init__(self):
            SqliteAgg.__init__(self)

        def finalize(self):
            return func(self.data)
    return SqliteAggClass

SqliteStd = make_sqlite_agg_class(lambda data:np.std(np.transpose(data)[0]))
SqliteCorrcoef = make_sqlite_agg_class(lambda data:np.corrcoef(*np.transpose(data)[:2]))

def make_plot_func(func):
    def parse_matplot_spec(spec):
        spec = spec.split(',', 1)
        if len(spec) == 1: return spec[0], ''
        else: return spec

    def plot(data):
        if (not data) or (not data[-1]) : return None
        cols = np.transpose(data)
        spec, cols = cols[0][-1], cols[1:]
        path, args = parse_matplot_spec(spec)
        plt.figure()
        cols = [map(float, col) for col in cols]
        func(args, *cols)
        if (not path) or path == '-':
            plt.show()
        else:
            plt.savefig(path)
        return path
    return plot

def make_sqlite_plot_func(func):
    return make_sqlite_agg_class(make_plot_func(func))

def plot(args, x, y=None):
    if y == None:
        plt.plot(x, args)
    else:
        plt.plot(x, y, args)

def hist(args, x):
    plt.hist(x, bins=safe_int(args,10))
    
def scatter(args, x, y):
    hist2d = np.histogram2d(y, x, bins=safe_int(args,10))[0]
    plt.imshow(hist2d)

def corr(args, x, y):
    plt.ylim(0, 1)
    plt.xcorr(x, y, maxlags=safe_int(args, None))

def bar(args, *x):
    if not x: return None
    w = 0.8/len(x)
    colors = 'bgrcmy'
    groupX = np.array(range(len(x[0])))
    for i,col in enumerate(x):
        plt.bar(groupX+i*w, col, w, color=colors[i%len(colors)])
    
SqlitePlot = make_sqlite_plot_func(plot)
SqliteHist = make_sqlite_plot_func(hist)
SqliteScatter = make_sqlite_plot_func(scatter)
SqliteCorr = make_sqlite_plot_func(corr)
SqliteBar = make_sqlite_plot_func(bar)

def alphanum_key(key1):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def get_db(path, **collectors):
    conn = sqlite3.connect(path)
    sqlite3.enable_callback_tracebacks(True)
    conn.create_collation("alphanum", lambda x1,x2: cmp(alphanum_key(x1), alphanum_key(x2)))
    conn.create_aggregate("std", 1, SqliteStd)
    conn.create_aggregate("corrcoef", 2, SqliteCorrcoef)
    conn.create_aggregate("plot", 2, SqlitePlot)
    conn.create_aggregate("plot", 3, SqlitePlot)
    conn.create_aggregate("hist", 2, SqliteHist)
    conn.create_aggregate("corr", 3, SqliteCorr)
    conn.create_aggregate("scatter", 3, SqliteScatter)
    for i in range(2,32):
        conn.create_aggregate("bar", i, SqliteBar)
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
    print sql
    for cols in txt_db(pat).execute(sql):
        print '\t'.join(map(str, cols))
