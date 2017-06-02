
#include "ActiveRecordBase.h"

CBaseDatabase *ActiveRecordBase::s_conn = NULL;

String ActiveRecordQuery::GetQueryString() const
{
    // [WHERE] [ORDER BY]
    String str;
    if (m_strCond.length()) {
        str = _T(" WHERE ") + m_strCond;
    }
    if (m_strOrderBy.length()) {
        str += _T(" ORDER BY ") + m_strOrderBy;
    }
    return str;
}

VOID ActiveRecordQuery::BindArgs(CDBExecute *dbExec)
{
    ActiveRecordQueryArgsIterator it = m_args.begin();
    ActiveRecordQueryArg *arg;
    for (; it != m_args.end(); ++it) {
        arg = *it;
        switch (arg->type) {
            case QUERY_ARG_DWORD:
                dbExec->BindInput(arg->dwVal);
                break;

            case QUERY_ARG_INT:
                dbExec->BindInput(arg->nVal);
                break;

            case QUERY_ARG_FLOAT:
                //dbExec->BindInput(arg->fVal);
                dbExec->BindParameter(SQL_PARAM_INPUT, SQL_C_FLOAT, SQL_FLOAT, &arg->fVal);
                break;

            case QUERY_ARG_BYTE:
                dbExec->BindInput(arg->cVal);
                break;

            case QUERY_ARG_STRING:
                dbExec->BindInput(arg->pstrVal->c_str());
        }
    }
}
