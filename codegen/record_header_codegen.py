
import math
from string import Template
from helper import tpl

_HEADER_CODE = Template("""
#pragma once

// DB Table: ${table_name}

${declare_macros}

class ${record_class_name}
{
public:
${declare_fields}

    ${record_class_name}()
${init_fields}
    {
${fill_fields}
    }
${getters}
${setters}
};

""")

_DECLARE_MACRO = Template('#define ${name} ${val}')
_DECLARE_FIELD = Template('    ${type}${indent}${name}${declare_more};')
_INIT_FIELD = Template('        ${init_prefix} ${name}(${default_val})')
_FILL_FIELD = Template('       memset(${pointer}, 0, ${len});')
_GETTER_SQLTIME = Template("""
    SYSTEMTIME Get${col_name}()
    {
        SYSTEMTIME ${name};
        CHelper::SQLTimeToSystemTime(this->${name}, ${name});
        return ${name};
    }""")
_SETTER_SQLTIME = Template("""
    VOID Set${col_name}(SYSTEMTIME &${name})
    {
        CHelper::SystemTimeToSQLTime(${name}, this->${name});
    }""")
_SETTER_TCHAR = Template("""
    VOID Set${col_name}(LPCTSTR ${name})
    {
        if (${name}) {
            _tcscpy_s(this->${name}, ${size_field_name}, ${name});
        }
    }""")


class Generator:
    def __init__(self, schema):
        self.schema = schema

    def gen_code(self):
        schema = self.schema
        # macros
        declare_macros = []
        for macro in schema['macros']:
            declare_macros.append(tpl(_DECLARE_MACRO, macro))

        # fields
        max_len = 0
        for field in schema['fields']:
            l = len(field['type'])
            if l > max_len:
                max_len = l
        declare_fields = []
        init_fields = []
        getters = []
        setters = []
        init_prefix = ':'
        indent_len = int(math.ceil((max_len + 5) / 4) * 4)
        for field in schema['fields']:
            field_name = field['name']
            var = field.copy()
            var['indent'] = ' ' * (indent_len - len(field['type']))
            var['init_prefix'] = init_prefix
            declare_fields.append(tpl(_DECLARE_FIELD, var))
            if field['type'] == 'TCHAR':
                setters.append(tpl(_SETTER_TCHAR, field))
            if field['type'] == 'SQL_TIMESTAMP_STRUCT':
                setters.append(tpl(_SETTER_SQLTIME, field))
                getters.append(tpl(_GETTER_SQLTIME, field))
            if field_name not in schema['fill_fields']:
                init_fields.append(tpl(_INIT_FIELD, var))
                init_prefix = ','

        # fill fields
        fill_fields = []
        for field_name in schema['fill_fields']:
            field = schema['fill_fields'][field_name]
            fill = {}
            if field['type'] == 'TCHAR':
                fill['pointer'] = field_name
                fill['len'] = 'sizeof(TCHAR) * (%s + 1)' % field['macro']
            else:
                fill['pointer'] = '&' + field_name
                fill['len'] = 'sizeof(%s)' % field_name
            fill_fields.append(tpl(_FILL_FIELD, fill))

        code = tpl(_HEADER_CODE, {
            'table_name': schema['table_name'],
            'declare_macros': '\n'.join(declare_macros),
            'record_class_name': schema['record_class_name'],
            'declare_fields': '\n'.join(declare_fields),
            'init_fields': '\n'.join(init_fields),
            'fill_fields': '\n'.join(fill_fields),
            'getters': '\n'.join(getters),
            'setters': '\n'.join(setters),
        })

        return code


