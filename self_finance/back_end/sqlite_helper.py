import logging
import os
import sqlite3
from numbers import Number

import pandas as pd

from config.files import ROOT

log = logging.getLogger(__name__)


class SqliteHelper:
    @staticmethod
    def execute_sqlite(q_str_or_file, db_path, delimiter=';', as_dataframe=False):
        """
        obj: entry point to execute sql either as a file or query string
        :param q_str_or_file: str - path of file to execute or the querie(s) themselves to execute
        :param db_path: str - database name
        :param delimiter: str - character that delimits individual sqlite queries
        :param as_dataframe: bool - whether or execute as a pandas dataframe
        :return: query executions
        """
        is_file = lambda s: (os.path.exists(s) or s.startswith(ROOT)) and s.endswith('.sql')
        if is_file(q_str_or_file):
            return SqliteHelper._execute_sql_from_file(filename=q_str_or_file, db_path=db_path,
                                                       delimiter=delimiter, as_dataframe=as_dataframe)
        else:
            return SqliteHelper._execute_sql_from_string(db_path=db_path, query_string=q_str_or_file,
                                                         delimiter=delimiter, as_dataframe=as_dataframe)

    @staticmethod
    def _execute_sql_from_file(**kwargs):
        """
        obj: execute sql string
        """
        with open(kwargs.get('filename'), 'r') as sqlite_file:
            query_string = sqlite_file.read()
            kwargs['query_string'] = query_string
            return SqliteHelper._execute_sql_from_string(**kwargs)

    @staticmethod
    def _execute_sql_from_string(**kwargs):
        """
        obj: execute sql string, kwargs taken from `execute_sql_from_file`
        """
        conn = sqlite3.connect(kwargs.get('db_path'))
        c = conn.cursor()

        # automatically handle multiple queries
        ret = []
        query_string = kwargs.get('query_string')
        # only delimit the query if specified to do so
        query_strings = query_string.split(kwargs.get('delimiter')) if kwargs.get('delimiter') else [query_string]

        # filter an invalid queries
        query_strings = [q for q in query_strings if q]

        for query_str in query_strings:
            # make a standard query, or store as dataframe
            if kwargs.get('as_dataframe'):
                _df = pd.read_sql_query(query_str, conn)
                ret.append(_df)
            else:
                query_result = c.execute(query_str)
                if query_result.rowcount > 0:
                    ret.append(query_result)

        conn.commit()
        conn.close()

        # gracefully handle returns
        return ret[0] if len(ret) == 1 else ret

    @staticmethod
    def frmt_sql_val(value):
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, Number):
            return value
        elif value is None:
            return "NULL"
