
from string import Template
from helper import get_pks_arg, tpl

_SOURCE_CODE = Template("""
#include "${class_name}.h"

${class_name}::${class_name}()
{
}

${class_name}::~${class_name}()
{
}

${class_name} *${class_name}::Clone()
{
    ${class_name} *copy = new ${class_name}();
${clone_fields}
    copy->m_bNewRecord = m_bNewRecord;
    return copy;
}

${class_name} *${class_name}::FindOne(${pks_arg})
{
    CDBExecute exec(s_conn);
    ${class_name} *obj = new ${class_name}();
${bind_find_cols}
    obj->SetLoadedRecord();

    LPCTSTR sql = _T("SELECT * FROM ${table_name} WHERE ${pks_cond}");
${bind_find_pks_input}

    exec.Exec(sql);
    if (exec.Fetch())
    {
        return obj;
    }
    else
    {
        delete obj;
        return NULL;
    }
}

${class_name}Vector *${class_name}::Find(ActiveRecordQuery *query /* = NULL */)
{
    CDBExecute exec(s_conn);
    ${class_name} *obj = new ${class_name}();
${bind_find_cols}
    obj->SetLoadedRecord();

    String sql(_T("SELECT * FROM ${table_name}"));
    if (query) {
        sql += query->GetQueryString();
        query->BindArgs(&exec);
    }

    ${class_name}Vector *records = new ${class_name}Vector();
    exec.Exec(sql.c_str());
    while (exec.Fetch()) {
        records->items.push_back(obj->Clone());
    }
    delete obj;
    return records;
}

DWORD ${class_name}::CreateRecord()
{
    CDBExecute exec(s_conn);
    LPCTSTR sql = _T("INSERT INTO ${table_name} VALUES (${insert_vals})");
${bind_insert_input}

    if (!exec.Exec(sql))
    {
        return 0;
    }
    else
    {
        SetLoadedRecord();
        return 1;
    }
}

DWORD ${class_name}::UpdateRecord()
{
    CDBExecute exec(s_conn);
    DWORD dwRowCount = 0;
    LPCTSTR sql = _T("UPDATE ${table_name} SET ${update_vals} WHERE ${pks_cond} SELECT @@ROWCOUNT");
${bind_update_input}

    // update conds
${bind_pks_input}

    exec.BindCol(dwRowCount);
    exec.Exec(sql);
    if (exec.FetchRecordset())
    {
        exec.Fetch();
    }
    return dwRowCount;
}

DWORD ${class_name}::DeleteRecord()
{
    CDBExecute exec(s_conn);
    DWORD dwRowCount = 0;
    LPCTSTR sql = _T("DELETE FROM ${table_name} WHERE ${pks_cond} SELECT @@ROWCOUNT");
${bind_pks_input}

    exec.BindCol(dwRowCount);
    exec.Exec(sql);
    if (exec.FetchRecordset())
    {
        exec.Fetch();
    }
    return dwRowCount;
}

""")

_CLONE_FIELD = Template('    copy->${name} = ${name};')
_CLONE_TCHAR_FIELD = Template('    _tcscpy_s(copy->${name}, ${size_field_name}, ${name});')
_BIND_FIND_TCHAR_COL = Template('    exec.BindCol(obj->${name}, obj->${size_field_name});')
_BIND_FIND_COL = Template('    exec.BindCol(obj->${name});')
_BIND_FIND_PK_INPUT = Template('    exec.BindInput(${name});')
_BIND_INPUT = Template('    exec.BindInput(${name});')
_BIND_UPDATE_VAL = Template('${name} = ?')


def quote(name):
    return '\\"' + name + '\\"'


def get_pks_cond(schema):
    pks = []
    for pk_name in schema['pks']:
        pks.append('%s = ?' % quote(pk_name))
    return ' AND '.join(pks)


class Generator:
    def __init__(self, schema):
        self.schema = schema

    def gen_code(self):
        schema = self.schema

        clone_fields = []
        bind_find_cols = []
        for field in schema['fields']:
            if 'col_name' not in field:
                continue
            if field['type'] == 'TCHAR':
                bind_find_cols.append(tpl(_BIND_FIND_TCHAR_COL, field))
                clone_fields.append(tpl(_CLONE_TCHAR_FIELD, field))
            else:
                bind_find_cols.append(tpl(_BIND_FIND_COL, field))
                clone_fields.append(tpl(_CLONE_FIELD, field))

        bind_find_pks_input = []
        bind_pks_input = []
        for pk_name in schema['pks']:
            field = schema['fields_map'][pk_name]
            field_name = field['name']
            bind_find_pks_input.append(tpl(_BIND_FIND_PK_INPUT, {
                'name': field_name}))
            bind_pks_input.append(tpl(_BIND_INPUT, {
                'name': field_name}))

        insert_vals = []
        for col in schema['columns']:
            insert_vals.append('?')
        bind_insert_input = []
        bind_update_input = []
        bind_update_vals = []
        for field in schema['fields']:
            if 'col_name' not in field:
                continue
            col_name = field['col_name']
            code = tpl(_BIND_INPUT, {'name': field['name']})
            if col_name not in schema['pks']:
                bind_update_input.append(code)
                bind_update_vals.append(tpl(_BIND_UPDATE_VAL, {
                    'name': quote(col_name)}))
            bind_insert_input.append(code)

        return tpl(_SOURCE_CODE, {
            'table_name': quote(schema['table_name']),
            'class_name': schema['class_name'],
            'clone_fields': '\n'.join(clone_fields),
            'pks_arg': get_pks_arg(schema),
            'bind_find_cols': '\n'.join(bind_find_cols),
            'pks_cond': get_pks_cond(schema),
            'bind_find_pks_input': '\n'.join(bind_find_pks_input),
            'insert_vals': ', '.join(insert_vals),
            'bind_insert_input': '\n'.join(bind_insert_input),
            'update_vals': ', '.join(bind_update_vals),
            'bind_update_input': '\n'.join(bind_update_input),
            'bind_pks_input': '\n'.join(bind_pks_input)})


