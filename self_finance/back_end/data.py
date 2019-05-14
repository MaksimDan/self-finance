import logging
import re
import sqlite3

import dateparser
import pandas as pd
from pandas.io.json import json_normalize

from config.files import files
from self_finance.back_end.sqlite_helper import SqliteHelper
from self_finance.constants import Schema

logger = logging.getLogger(__name__)


class Data:
    @staticmethod
    def _column_preprocessing_pt1(df):
        """
        obj: rename dataframe columns to contain only lower case alpha numeric characters,
        everything else is otherwise replaced with '_'
        """
        org_column_names = df.columns.values
        new_column_names = [re.sub('[^0-9a-zA-Z]+', '_', c_n.lower().strip()) for c_n in org_column_names]
        df = df.rename(index=str, columns=dict(zip(org_column_names, new_column_names)))
        return df

    @staticmethod
    def _column_preprocessing_pt2(df):
        """
        obj: when a new table comes in, preprocess the columns that are generally not
        changed by the user, such as converting the date column into a standard readable format
        """
        df[Schema.SCHEMA_BANK_DATE.name] = df.apply(
            lambda row: dateparser.parse(row[Schema.SCHEMA_BANK_DATE.name]).date(), axis=1)
        df[Schema.SCHEMA_BANK_INC_OR_EXP.name] = df.apply(lambda row: 'expense' if
        row[Schema.SCHEMA_BANK_AMOUNT.name] < 0 else 'income', axis=1)

        # add additional columns if they are missing
        # note the caveat - when the dataframe source comes from a csv, it needs to be reevaluated
        list_categories = [eval(elm) if isinstance(elm, str) else elm for elm in
                           list(df[Schema.SCHEMA_FULL_CATEGORY.name])]

        def add_category_col_to_db(cat_name, cat_index):
            df[cat_name] = [c[cat_index] if cat_index < len(c) else None for c in list_categories]

        cat_cols = [Schema.SCHEMA_BANK_C1.name, Schema.SCHEMA_BANK_C2.name, Schema.SCHEMA_BANK_C3.name]
        for cat_name, i in zip(cat_cols, range(len(cat_cols))):
            add_category_col_to_db(cat_name, i)
        return df

    @staticmethod
    def preprocess_data(df):
        df = Data._column_preprocessing_pt1(df)
        df = Data._column_preprocessing_pt2(df)
        df_bank = df[Schema.get_names(Schema.get_schema_table(Schema.BANK_TB_NAME))]
        return df_bank

    @staticmethod
    def merge(csv_path_or_df, db_name=files['base_db']):
        """
        obj: inner join chase csv expenses with current database, updating it in the process
        """
        # read static and add additional columns to match schema
        tmp_df = pd.read_csv(csv_path_or_df, index_col=False) if isinstance(csv_path_or_df, str) else csv_path_or_df

        # grab other sub-tables
        def eval_json_and_add_transaction_id(column_pull):
            data_column = list(tmp_df[column_pull])
            data_column_evaled = [eval(d) if isinstance(d, str) else d for d in data_column]
            df = json_normalize(data_column_evaled)
            df[Schema.SCHEMA_BANK_TRANSACTION_ID.name] = tmp_df[Schema.SCHEMA_BANK_TRANSACTION_ID.name]
            return df

        # if this is an update for example, the user will be working with the the public table
        # with no mention of location or meta table information
        locations_df, payment_meta_df, bank_df = None, None, None
        if Schema.SCHEMA_FULL_LOCATION.name in tmp_df.columns.values:
            locations_df = eval_json_and_add_transaction_id(Schema.SCHEMA_FULL_LOCATION.name)
        if Schema.SCHEMA_FULL_PAYMENT_META.name in tmp_df.columns.values:
            payment_meta_df = eval_json_and_add_transaction_id(Schema.SCHEMA_FULL_PAYMENT_META.name)
        # preprocess the date only on the condition that the schema match the original full schema (from plaid api)
        if set(Schema.get_names(Schema.get_schema_table(Schema._FULL_TB_NAME))) - set(tmp_df.columns.values) == set():
            bank_df = Data.preprocess_data(tmp_df)
        else:
            # otherwise this is an update operatation
            bank_df = tmp_df
        # merge the static and close the connection
        tmp_tb_id = '__tmp'
        conn = None
        inline_tb_names = [Schema.LOCATION_TB_NAME, Schema.PAYMENT_META_TB_NAME, Schema.BANK_TB_NAME]
        for df, tb_name in zip([locations_df, payment_meta_df, bank_df], inline_tb_names):
            if df is not None and df.shape[0] > 0:
                column_order = Schema.get_names(Schema.get_schema_table(tb_name))
                df = df[column_order]
                columns_schema = ', '.join(column_order)
                conn = sqlite3.connect(db_name)
                df.to_sql(tmp_tb_id, con=conn, if_exists='replace', index=False)
                # rearrange columns to match schema
                merge_query = f'INSERT OR REPLACE INTO {tb_name} ({columns_schema})\n' \
                    f'SELECT * FROM {tmp_tb_id}'
                conn.execute(merge_query)
                conn.commit()
        if conn:
            conn.close()

    @staticmethod
    def create_base_db():
        """
        obj: create standard base database
        """
        SqliteHelper.execute_sqlite(files['create_db'], files['base_db'])

    @staticmethod
    def truncate(table_name):
        """
        obj: drop table in database
        """
        query = f"DELETE FROM {table_name};"
        SqliteHelper.execute_sqlite(query, files['base_db'])

    @staticmethod
    def truncate_all_tables():
        for table in Schema.get_all_table_names():
            Data.truncate(table)

    @staticmethod
    def get_table_as_df(date_range, table_name, order_by_col_name=Schema.SCHEMA_BANK_DATE.name,
                        order='DESC', db_path=files['base_db']):
        """
        obj: a common request for the application. get a table from base db using two high
        level parameters
        """
        query_select = f"SELECT * FROM {table_name}\n"
        query_where = f"WHERE DATE({Schema.SCHEMA_BANK_DATE.name}) BETWEEN " \
            f"'{date_range.start}' AND '{date_range.end}'\n" if date_range else ''
        query_order = f"ORDER BY {order_by_col_name} {order}" if order else ''
        query = query_select + query_where + query_order

        # this is useful in the scenario of not breaking down the app if there
        # is no database to begin with (static initializers in /front_end/routes.py)
        try:
            return SqliteHelper.execute_sqlite(query, db_path, as_dataframe=True)
        except Exception:
            return None

    @staticmethod
    def get_missing_categories(as_dataframe=True):
        """
        obj: identify unlabeled data
        """
        query = f"SELECT * FROM {Schema.BANK_TB_NAME}\n" \
            f"WHERE {Schema.SCHEMA_BANK_C1.name} IS NULL OR {Schema.SCHEMA_BANK_C2.name}=''"
        return SqliteHelper.execute_sqlite(query, files['base_db'], as_dataframe=as_dataframe)

    @staticmethod
    def update_missing_categories(filled_list_dict, cat_ids, pk_ids):
        """
        obj: build a query to update the missing categories in the database
        """

        def start():
            query = f"UPDATE {Schema.BANK_TB_NAME}\n"
            query += "SET "
            return query

        def middle(d, column_ids):
            return ', '.join(f"{col_name}={SqliteHelper.frmt_sql_val(d[col_name])}"
                             for col_name in column_ids)

        def end(d, column_ids):
            query = '\nWHERE\n'
            query += ' AND '.join(f"{col_name}={SqliteHelper.frmt_sql_val(d[col_name])}"
                                  for col_name in column_ids)
            return query + ';\n'

        all_queries = ''.join(start() + middle(d, pk_ids) + end(d, cat_ids) for d in filled_list_dict)
        SqliteHelper.execute_sqlite(all_queries, files['base_db'])

    @staticmethod
    def get_most_recent_transaction_date(tb_name, db_path):
        sql_query = f"SELECT {Schema.SCHEMA_BANK_DATE.name} FROM {tb_name}" \
            f" ORDER BY DATE({Schema.SCHEMA_BANK_DATE.name}) DESC LIMIT 1"
        df = SqliteHelper.execute_sqlite(sql_query, db_path, as_dataframe=True)
        # empty table - no most recent transaction
        if df.shape[0] != 1:
            return None
        return df[Schema.SCHEMA_BANK_DATE.name][0]

    @staticmethod
    def get_most_recent_html_from_id(image_id, db_path=files['base_db']):
        sql_query = f"SELECT {Schema.SCHEMA_PLOT_CACHE_HTML.name} FROM {Schema.PLOT_CACHE_TB_NAME}" \
            f" WHERE {Schema.SCHEMA_PLOT_CACHE_FULL_TITLE.name}='{image_id}'" \
            f" ORDER BY {Schema._SCHEMA_PLOT_CACHE_TIMESTAMP.name} DESC LIMIT 1"
        df = SqliteHelper.execute_sqlite(sql_query, db_path, as_dataframe=True)
        return None if df is None or df.shape[0] <= 0 else df[Schema.SCHEMA_PLOT_CACHE_HTML.name][0]

    @staticmethod
    def get_heatmap_df(date_range, db_path=files['base_db']):
        sql_query = f"""
        SELECT {Schema.SCHEMA_LOCATION_LON.name}, {Schema.SCHEMA_LOCATION_LAT.name}, {Schema.SCHEMA_BANK_AMOUNT.name}
        FROM {Schema.BANK_TB_NAME} INNER JOIN {Schema.LOCATION_TB_NAME} ON {Schema.BANK_TB_NAME}.{Schema.SCHEMA_BANK_TRANSACTION_ID.name}
        WHERE DATE({Schema.SCHEMA_BANK_DATE.name}) BETWEEN '{date_range.start}' AND '{date_range.end}'
        """
        df = SqliteHelper.execute_sqlite(sql_query, db_path, as_dataframe=True)
        return None if df is None or df.shape[0] <= 0 else df

    @staticmethod
    def invalidate_cache(db_path=files['base_db']):
        logging.info('Invalidating plot cache by clearing contents.')
        sql_query = f"""
        DELETE FROM {Schema.PLOT_CACHE_TB_NAME};
        """
        SqliteHelper.execute_sqlite(sql_query, db_path)

    @staticmethod
    def cast_df_to_schema(df, table_id):
        column_to_type_map = {sch.name: sch.type for sch in Schema.get_schema_table(table_id)}
        return df.astype(column_to_type_map)
