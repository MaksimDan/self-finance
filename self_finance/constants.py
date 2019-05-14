from os import environ


class _Schema:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __dict__(self):
        return {self.name: self.type}


class _Flash:
    def __init__(self, msg, type):
        self.msg = msg
        self.type = type


class App:
    APPLICATION_NAME = 'self-finance'
    SECRET_KEY = environ.get('SECRET_KEY') or '@#$%DSNA)(*S#EBDASJK'
    PORT = 5001
    LOCAL_HOST = f'http://localhost:{PORT}'
    TIME_WAIT_OPEN_BROWSER_SECONDS = 2
    PLAID_CLIENT_ID_ENV_VAR_KEY = 'PLAID_CLIENT_ID'
    PLAID_PUBLIC_KEY_ENV_VAR_KEY = 'PLAID_PUBLIC_KEY'
    PLAID_SECRET_ENV_VAR_KEY = 'PLAID_SECRET'


class Defaults:
    DATE_RANGE_START_DEFAULT = '5 months ago'
    DATE_RANGE_END_DEFAULT = 'today'
    ORDER_BY_DEFAULT = 'DESC'


class Flash:
    DATE_RANGE_FILTER_KEY_ERROR = _Flash('One or both date ranges were invalid.', 'warning')


class Visuals:
    HM_START_LAT_LON = [36.778259, -119.417931]
    PLOT_MAX_THREADS = 10


class Data:
    FILE_NAME_DOWNLOAD = 'bank_data.csv'
    BANK_DATA_TABLE_ID = 'bank_data_df'


class Insights:
    # 15 days -- TODO - this is hard hack between it assumes the interview of the static plots (which are 1 months time)
    STATIC_TIME_CACHE_REFRESH_MINUTES = 1 * 60 * 60 * 24 * 15

    BANK_SUMMARY_TABLE_ID = 'bank_summary_df'
    TOP_INC_TABLE_ID = 'top_inc_df'
    TOP_EXP_TABLE_ID = 'top_exp_df'
    SPENDING_VS_LAST_MONTH_TABLE_ID = 'spending_vs_last_month_df'
    INSIGHT_TABLE_CLASS = 'insight_table'


class Html:
    HTML_DOC_STARTS_WITH = '<!DOCTYPE html>'
    XML_DOC_STARTS_WITH = '<?xml'
    # for bootstrap
    BANK_DATA_TABLE_BS_CLASSES = ['table', 'table-responsive-sm', 'table-hover']


# note: _ prefix schema elements are hidden explicitly because they are auto fields such as auto increment
class Schema:
    # databases and tables
    BASE_DB_NAME = 'self_finance.db'

    _FULL_TB_NAME = 'full'
    BANK_TB_NAME = 'bank'
    LOCATION_TB_NAME = 'location'
    PAYMENT_META_TB_NAME = 'payment_meta'
    PLOT_CACHE_TB_NAME = 'plot_cache'

    # original table - untouched
    SCHEMA_FULL_ACCOUNT_ID = _Schema('account_id', str)
    SCHEMA_FULL_ACCOUNT_OWNER = _Schema('account_owner', str)
    SCHEMA_FULL_AMOUNT = _Schema('amount', float)
    SCHEMA_FULL_CATEGORY = _Schema('category', str)
    SCHEMA_FULL_CATEGORY_ID = _Schema('category_id', int)
    SCHEMA_FULL_DATE = _Schema('date', str)
    SCHEMA_FULL_ISO_CURRENCY_CODE = _Schema('iso_currency_code', str)
    SCHEMA_FULL_LOCATION = _Schema('location', str)
    SCHEMA_FULL_NAME = _Schema('name', str)
    SCHEMA_FULL_PAYMENT_META = _Schema('payment_meta', str)
    SCHEMA_FULL_PENDING = _Schema('pending', bool)
    SCHEMA_FULL_PENDING_TRANSACTION_ID = _Schema('pending_transaction_id', str)
    SCHEMA_FULL_TRANSACTION_ID = _Schema('transaction_id', str)
    SCHEMA_FULL_TRANSACTION_TYPE = _Schema('transaction_type', str)
    SCHEMA_FULL_UNOFFICIAL_CURRENCY_CODE = _Schema('unofficial_currency_code', str)

    # main public table - after some preprocessing on full table
    SCHEMA_BANK_ACCOUNT_ID = _Schema('account_id', str)
    SCHEMA_BANK_AMOUNT = _Schema('amount', float)
    SCHEMA_BANK_C1 = _Schema('c1', str)
    SCHEMA_BANK_C2 = _Schema('c2', str)
    SCHEMA_BANK_C3 = _Schema('c3', str)
    SCHEMA_BANK_DATE = _Schema('date', str)
    SCHEMA_BANK_INC_OR_EXP = _Schema('inc_or_exp', str)
    SCHEMA_BANK_NAME = _Schema('name', str)
    SCHEMA_BANK_TRANSACTION_ID = _Schema('transaction_id', str)

    # location index to main table
    SCHEMA_LOCATION_ADDRESS = _Schema('address', str)
    SCHEMA_LOCATION_CITY = _Schema('city', str)
    SCHEMA_LOCATION_LAT = _Schema('lat', float)
    SCHEMA_LOCATION_LON = _Schema('lon', float)
    SCHEMA_LOCATION_STATE = _Schema('state', str)
    SCHEMA_LOCATION_STORE_NUMBER = _Schema('store_number', int)
    SCHEMA_LOCATION_TRANSACTION_ID = _Schema('transaction_id', int)
    SCHEMA_LOCATION_ZIP = _Schema('zip', int)

    # payment meta index to public table
    SCHEMA_PAYMENT_META_BY_ORDER_OF = _Schema('by_order_of', str)
    SCHEMA_PAYMENT_META_PAYEE = _Schema('payee', str)
    SCHEMA_PAYMENT_META_PAYER = _Schema('payer', str)
    SCHEMA_PAYMENT_META_PAYMENT_METHOD = _Schema('payment_method', str)
    SCHEMA_PAYMENT_META_PAYMENT_PROCESSOR = _Schema('payment_processor', str)
    SCHEMA_PAYMENT_META_PAYMENT_REFERENCE_NUMBER = _Schema('reference_number', str)
    SCHEMA_PAYMENT_META_PPD_ID = _Schema('ppd_id', int)
    SCHEMA_PAYMENT_META_REASON = _Schema('reason', str)
    SCHEMA_PAYMENT_META_TRANSACTION_ID = _Schema('transaction_id', int)

    # plot cache
    SCHEMA_PLOT_CACHE_END_DATE = _Schema('end_date', str)
    SCHEMA_PLOT_CACHE_FULL_TITLE = _Schema('full_title', str)
    SCHEMA_PLOT_CACHE_HTML = _Schema('html', str)
    SCHEMA_PLOT_CACHE_LOOKUP_DATE = _Schema('lookup_date', str)
    SCHEMA_PLOT_CACHE_START_DATE = _Schema('start_date', str)
    _SCHEMA_PLOT_CACHE_TIMESTAMP = _Schema('timestamp', str)

    # misc
    # note - this date format is nessessary for datetime to be able to parse
    DATE_FORMAT = "{:%Y-%m-%d}"
    DATE_FORMAT2 = "%Y-%m-%d"

    @staticmethod
    def __const_groups_get(key):
        """
        obj: return group of static constants in this class that are a product of a common string pattern
        """
        return {
            Schema._FULL_TB_NAME: 'SCHEMA_FULL',
            Schema.LOCATION_TB_NAME: 'SCHEMA_LOCATION',
            Schema.PAYMENT_META_TB_NAME: 'SCHEMA_PAYMENT_META',
            Schema.BANK_TB_NAME: 'SCHEMA_BANK',
            Schema.PLOT_CACHE_TB_NAME: 'SCHEMA_PLOT_CACHE',
            'all_tables': 'TB_NAME'
        }[key]

    @staticmethod
    def get_schema_table(tb_name):
        """
        obj: return the schema object types for a table_id
        """
        return [v for k, v in Schema.__dict__.items() if k.startswith(Schema.__const_groups_get(tb_name))
                and not k.startswith('_')]

    @staticmethod
    def get_names(schema_list, sort=True):
        names = [schema.name for schema in schema_list]
        return sorted(names) if sort else names

    @staticmethod
    def get_types(schema_list):
        return [schema.type for schema in schema_list]

    @staticmethod
    def get_pk_fields(tb_name):
        if tb_name == Schema._FULL_TB_NAME or tb_name == Schema.BANK_TB_NAME:
            return [Schema.SCHEMA_BANK_DATE,
                    Schema.SCHEMA_BANK_AMOUNT,
                    Schema.SCHEMA_BANK_C1,
                    Schema.SCHEMA_BANK_C2,
                    Schema.SCHEMA_BANK_NAME]

    @staticmethod
    def get_all_table_names():
        return [v for k, v in Schema.__dict__.items()
                if Schema.__const_groups_get('all_tables') in k and not k.startswith('_')]
