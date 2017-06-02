

_FIELD_TYPE_BY_COL = {
    'int': 'DWORD',
    'nvarchar': 'TCHAR',
    'datetime': 'SQL_TIMESTAMP_STRUCT',
    'tinyint': 'BYTE'
}

_TYPE_PREFIX = {
    'DWORD': 'dw',
    'TCHAR': 'sz',
    'SQL_TIMESTAMP_STRUCT': 'st',
    'BYTE': 'c'
}


def get_field_by_col(col):
    col_name = col['COLUMN_NAME']
    col_type = col['TYPE_NAME']
    field = {}
    field['col_name'] = col_name
    field['col_type'] = col_type
    field['type'] = _FIELD_TYPE_BY_COL[col_type]
    field['type_prefix'] = _TYPE_PREFIX[field['type']]
    field['default_val'] = 0
    field['declare_more'] = ''
    field['name'] = field['type_prefix'] + col_name
    field['length'] = col['PRECISION']
    return field


def get_macro_name(name):
    macro = []
    index = 0
    for c in name:
        uc = c.upper()
        if c == uc and index > 0:
            macro.append('_')
        macro.append(uc)
        index = index + 1
    return ''.join(macro)


def get_pks_arg(schema):
    pks = []
    for pk_name in schema['pks']:
        field = schema['fields_map'][pk_name]
        pks.append('%s %s' % (field['type'], field['name']))
    return ', '.join(pks)


def tpl(tpl_contents, var={}):
    return tpl_contents.substitute(var)



