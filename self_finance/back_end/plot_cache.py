from config.files import files
from self_finance.back_end.sqlite_helper import SqliteHelper
from self_finance.constants import Schema


class PlotCache:
    @staticmethod
    def hit(full_title, start_date, end_date, lookup_date, db_path=files['base_db']):
        """
        obj: return the html if it was previously plotted today --
             - keys: plot name, data range, lookup date
        """
        sql_query = f"SELECT {Schema.SCHEMA_PLOT_CACHE_HTML.name} FROM {Schema.PLOT_CACHE_TB_NAME}" \
            f" WHERE {Schema.SCHEMA_PLOT_CACHE_FULL_TITLE.name}='{full_title}' AND" \
            f" {Schema.SCHEMA_PLOT_CACHE_START_DATE.name}='{start_date}' AND" \
            f" {Schema.SCHEMA_PLOT_CACHE_END_DATE.name}='{end_date}' AND " \
            f" {Schema.SCHEMA_PLOT_CACHE_LOOKUP_DATE.name}='{lookup_date}'"
        sql_result = SqliteHelper.execute_sqlite(sql_query, db_path, as_dataframe=True)
        if sql_result is not None and sql_result.shape[0] > 0:
            return sql_result[Schema.SCHEMA_PLOT_CACHE_HTML.name].values[0]
        else:
            return None

    @staticmethod
    def add_cache_miss(full_title, start_date, end_date, lookup_date, html, db_path=files['base_db']):
        schema = ', '.join(Schema.get_names(Schema.get_schema_table(Schema.PLOT_CACHE_TB_NAME)))
        # a single quote within a sqlite query is escaped with double quotes
        html = html.replace("'", "''")
        # note: insert into because the logic flow guarantees that value combination will be unique
        sql_query = f"INSERT INTO {Schema.PLOT_CACHE_TB_NAME} ({schema})" \
            f" VALUES ('{end_date}', '{full_title}', '{html}', '{lookup_date}', '{start_date}')"
        # note that delimiter is None because the string field html itself could have ';'
        SqliteHelper.execute_sqlite(sql_query, db_path, delimiter=None)
