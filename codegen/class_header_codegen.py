
from string import Template
from helper import get_pks_arg, tpl

_HEADER_CODE = Template("""

#pragma once

#include "ActiveRecordBase.h"
#include "${record_class_name}.h"

class ${class_name};

typedef std::vector<${class_name}*> ${class_name}VectorInner;
typedef ${class_name}VectorInner::iterator ${class_name}Iterator;

class ${class_name}Vector;

class ${class_name} : public ${record_class_name}, public ActiveRecordBase
{
public:
    ${class_name}();
    virtual ~${class_name}();

    ${class_name} *Clone();

    static LPCTSTR GetTableName()
    {
        return _T("${table_name}");
    }

    static ${class_name} *FindOne($pks_arg);
    static ${class_name}Vector *Find(ActiveRecordQuery *query = NULL);

protected:
    virtual DWORD CreateRecord();
    virtual DWORD UpdateRecord();
    virtual DWORD DeleteRecord();

};


class ${class_name}Vector
{
public:
    ~${class_name}Vector()
    {
        ${class_name}Iterator it = items.begin();
        for (; it != items.end(); ++it) {
            delete *it;
        }
    }

    ${class_name}VectorInner items;
};

""")


class Generator:
    def __init__(self, schema):
        self.schema = schema

    def gen_code(self):
        vars = self.schema.copy()
        vars['pks_arg'] = get_pks_arg(self.schema)
        return tpl(_HEADER_CODE, vars)


