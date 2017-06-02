
# gen code for:
# - Table Record C++ header file
# - C++ Class header file
# - C++ Class source file


from helper import get_field_by_col, get_macro_name

import record_header_codegen
import class_header_codegen
import class_source_codegen


class CRUDCodeGen:
    def __init__(self, conn, table_name, class_name=None):
        self.conn = conn
        self.schema = {}
        self.schema['table_name'] = table_name
        if class_name is None:
            class_name = table_name
        self.set_class_name(class_name)

        self._query_schema()
        self._query_pks()
        self._parse_columns()

    def set_class_name(self, class_name, record_class_name=None):
        self.schema['class_name'] = class_name
        if record_class_name is None:
            record_class_name = class_name + 'Record'
        self.schema['record_class_name'] = record_class_name

    def gen_record_header_code(self):
        generator = record_header_codegen.Generator(self.schema)
        return generator.gen_code()

    def gen_class_header_code(self):
        generator = class_header_codegen.Generator(self.schema)
        return generator.gen_code()

    def gen_class_source_code(self):
        generator = class_source_codegen.Generator(self.schema)
        return generator.gen_code()

    def _query_schema(self):
        sql = 'sp_columns "%s"' % self.schema['table_name']
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(sql)
        self.schema['columns'] = []
        self.schema['columns_map'] = {}
        for col in cursor:
            self.schema['columns'].append(col)
            self.schema['columns_map'][col['COLUMN_NAME']] = col

    def _query_pks(self):
        sql = 'sp_primary_keys_rowset "%s"' % self.schema['table_name']
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(sql)
        self.schema['pks'] = []
        for pk in cursor:
            self.schema['pks'].append(pk['COLUMN_NAME'])

    def _parse_columns(self):
        self.schema['fields'] = []
        self.schema['fill_fields'] = {}
        self.schema['macros'] = []
        for col in self.schema['columns']:
            field = get_field_by_col(col)
            field_name = field['name']
            self.schema['fields'].append(field)
            if field['type'] == 'TCHAR':
                self._parse_tchar_field(field)
                self.schema['fill_fields'][field_name] = field
            elif field['type'] == 'SQL_TIMESTAMP_STRUCT':
                self.schema['fill_fields'][field_name] = field
        self.schema['fields_map'] = {}
        for field in self.schema['fields']:
            if 'col_name' in field:
                self.schema['fields_map'][field['col_name']] = field

    def _parse_tchar_field(self, field):
        col_name = field['col_name']
        m_name = get_macro_name(self.schema['table_name'] + col_name) + '_LEN'
        size_field_name = 'n' + col_name
        field['size_field_name'] = size_field_name
        field['macro'] = m_name
        field['declare_more'] = '[%s + 1]' % m_name
        macro = {
            'name': m_name,
            'val': field['length'],
        }
        size_field = {
            'type': 'SQLLEN',
            'type_prefix': 'n',
            'name': size_field_name,
            'default_val': '%s + 1' % m_name,
            'declare_more': '',
        }
        self.schema['fields'].append(size_field)
        self.schema['macros'].append(macro)


