import os
import sys
import pymssql
import codegen


def write_file(filename, contents):
    if os.path.exists(filename):
        msg = 'file \'%s\' already exists, overwrite it (yes/no) ?'
        confirm = raw_input(msg % filename)
        if confirm != 'yes':
            return

    f = open(filename, 'wb')
    f.write(contents)
    f.close()
    print 'write file \'%s\' [ok]' % filename


config = {
    'server': r'127.0.0.1',
    'user': r'mydb',
    'passwd': r'mydb',
    'db': r'mydb'
}

args = sys.argv
if len(args) < 3:
    print 'usage: %s <table name> <class name>'
    print ''
    exit()

table_name = args[1]
class_name = args[2]

conn = pymssql.connect(server=config['server'],
                       user=config['user'],
                       password=config['passwd'],
                       database=config['db'])

gen = codegen.CRUDCodeGen(conn, table_name)
gen.set_class_name(class_name)

write_file('%sRecord.h' % class_name, gen.gen_record_header_code())
write_file('%s.h' % class_name, gen.gen_class_header_code())
write_file('%s.cpp' % class_name, gen.gen_class_source_code())


