
#pragma once

#include "stdafx.h"
#include <vector>


class ActiveRecordBase
{
public:
    static void SetDBConnect(CBaseDatabase *conn)
    {
        s_conn = conn;
    }

    ActiveRecordBase()
        : m_bNewRecord(TRUE)
    {
    }

    BOOL IsNewRecord()
    {
        return m_bNewRecord;
    }

    DWORD Save()
    {
        return IsNewRecord() ? CreateRecord() : UpdateRecord();
    }

    DWORD Delete()
    {
        return IsNewRecord() ? 0 : DeleteRecord();
    }

    virtual ~ActiveRecordBase()
    {
    }

protected:
    static CBaseDatabase *s_conn;

    BOOL m_bNewRecord;

    VOID SetLoadedRecord()
    {
        m_bNewRecord = FALSE;
    }

    virtual DWORD CreateRecord() = 0;
    virtual DWORD UpdateRecord() = 0;
    virtual DWORD DeleteRecord() = 0;

};

typedef enum {
    QUERY_ARG_DWORD = 1,
    QUERY_ARG_INT,
    QUERY_ARG_FLOAT,
    QUERY_ARG_BYTE,
    QUERY_ARG_STRING
} ActiveRecordQueryArgType;

struct ActiveRecordQueryArg
{
    ActiveRecordQueryArgType type;
    union {
        DWORD   dwVal;
        INT     nVal;
        FLOAT   fVal;
        BYTE    cVal;
        String  *pstrVal;
    };

    ActiveRecordQueryArg(ActiveRecordQueryArgType type)
    {
        this->type = type;
    }
};

typedef std::vector<ActiveRecordQueryArg *> ActiveRecordQueryArgs;
typedef ActiveRecordQueryArgs::iterator ActiveRecordQueryArgsIterator;


class ActiveRecordQuery
{
public:
    ActiveRecordQuery()
        : m_nLimit(100)
    {
    }

    ~ActiveRecordQuery()
    {
        RemoveAllCondArgs();
    }

    VOID AddArg(DWORD dwArg, INT nIndex = -1)
    {
        ActiveRecordQueryArg *arg = new ActiveRecordQueryArg(QUERY_ARG_DWORD);
        arg->dwVal = dwArg;
        AddArg(arg, nIndex);
    }

    VOID AddArg(INT nArg, INT nIndex = -1)
    {
        ActiveRecordQueryArg *arg = new ActiveRecordQueryArg(QUERY_ARG_INT);
        arg->nVal = nArg;
        AddArg(arg, nIndex);
    }

    VOID AddArg(FLOAT fArg, INT nIndex = -1)
    {
        ActiveRecordQueryArg *arg = new ActiveRecordQueryArg(QUERY_ARG_FLOAT);
        arg->fVal = fArg;
        AddArg(arg, nIndex);
    }

    VOID AddArg(BYTE cArg, INT nIndex = -1)
    {
        ActiveRecordQueryArg *arg = new ActiveRecordQueryArg(QUERY_ARG_BYTE);
        arg->cVal = cArg;
        AddArg(arg, nIndex);
    }

    VOID AddArg(LPCTSTR szArg, INT nIndex = -1)
    {
        ActiveRecordQueryArg *arg = new ActiveRecordQueryArg(QUERY_ARG_STRING);
        arg->pstrVal = new String(szArg);
        AddArg(arg, nIndex);
    }

    VOID RemoveCondArg(INT nIndex)
    {
        if (nIndex >= 0 && nIndex < m_args.size()) {
            m_args.erase(m_args.begin() + nIndex);
        }
    }

    VOID RemoveAllCondArgs()
    {
        ActiveRecordQueryArgsIterator it = m_args.begin();
        for (; it != m_args.end(); ++it) {
            if ((*it)->type == QUERY_ARG_STRING) {
                delete (*it)->pstrVal;
            }
            delete *it;
        }
        m_args.clear();
    }

    VOID OrderBy(LPCTSTR szOrderBy)
    {
        m_strOrderBy = szOrderBy;
    }

    VOID Where(LPCTSTR szCond)
    {
        m_strCond = szCond;
    }

    String GetQueryString() const;
    VOID BindArgs(CDBExecute *dbExec);

private:
    ActiveRecordQueryArgs m_args;
    DWORD m_nLimit;
    String m_strOrderBy;
    String m_strCond;

    VOID AddArg(ActiveRecordQueryArg *arg, INT nIndex)
    {
        if (nIndex >= 0) {
            RemoveCondArg(nIndex);
            m_args.insert(m_args.begin() + nIndex, arg);
        } else {
            m_args.push_back(arg);
        }
    }

};

