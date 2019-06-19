from os import environ


class Schema:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __dict__(self):
        return {self.name: self.type}

    @staticmethod
    def get_names(schema_list, sort=True):
        names = [schema.name for schema in schema_list]
        return sorted(names) if sort else names

    @staticmethod
    def get_types(schema_list):
        return [schema.type for schema in schema_list]


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
class BankSchema:
    # databases and tables
    BASE_DB_NAME = 'self_finance.db'

    _FULL_TB_NAME = 'full'
    BANK_TB_NAME = 'bank'
    LOCATION_TB_NAME = 'location'
    PAYMENT_META_TB_NAME = 'payment_meta'
    PLOT_CACHE_TB_NAME = 'plot_cache'

    # original table - untouched
    SCHEMA_FULL_ACCOUNT_ID = Schema('account_id', str)
    SCHEMA_FULL_ACCOUNT_OWNER = Schema('account_owner', str)
    SCHEMA_FULL_AMOUNT = Schema('amount', float)
    SCHEMA_FULL_CATEGORY = Schema('category', str)
    SCHEMA_FULL_CATEGORY_ID = Schema('category_id', int)
    SCHEMA_FULL_DATE = Schema('date', str)
    SCHEMA_FULL_ISO_CURRENCY_CODE = Schema('iso_currency_code', str)
    SCHEMA_FULL_LOCATION = Schema('location', str)
    SCHEMA_FULL_NAME = Schema('name', str)
    SCHEMA_FULL_PAYMENT_META = Schema('payment_meta', str)
    SCHEMA_FULL_PENDING = Schema('pending', bool)
    SCHEMA_FULL_PENDING_TRANSACTION_ID = Schema('pending_transaction_id', str)
    SCHEMA_FULL_TRANSACTION_ID = Schema('transaction_id', str)
    SCHEMA_FULL_TRANSACTION_TYPE = Schema('transaction_type', str)
    SCHEMA_FULL_UNOFFICIAL_CURRENCY_CODE = Schema('unofficial_currency_code', str)

    # main public table - after some preprocessing on full table
    SCHEMA_BANK_ACCOUNT_ID = Schema('account_id', str)
    SCHEMA_BANK_AMOUNT = Schema('amount', float)
    SCHEMA_BANK_C1 = Schema('c1', str)
    SCHEMA_BANK_C2 = Schema('c2', str)
    SCHEMA_BANK_C3 = Schema('c3', str)
    SCHEMA_BANK_DATE = Schema('date', str)
    SCHEMA_BANK_INC_OR_EXP = Schema('inc_or_exp', str)
    SCHEMA_BANK_NAME = Schema('name', str)
    SCHEMA_BANK_TRANSACTION_ID = Schema('transaction_id', str)

    # location index to main table
    SCHEMA_LOCATION_ADDRESS = Schema('address', str)
    SCHEMA_LOCATION_CITY = Schema('city', str)
    SCHEMA_LOCATION_LAT = Schema('lat', float)
    SCHEMA_LOCATION_LON = Schema('lon', float)
    SCHEMA_LOCATION_STATE = Schema('state', str)
    SCHEMA_LOCATION_STORE_NUMBER = Schema('store_number', int)
    SCHEMA_LOCATION_TRANSACTION_ID = Schema('transaction_id', int)
    SCHEMA_LOCATION_ZIP = Schema('zip', int)

    # payment meta index to public table
    SCHEMA_PAYMENT_META_BY_ORDER_OF = Schema('by_order_of', str)
    SCHEMA_PAYMENT_META_PAYEE = Schema('payee', str)
    SCHEMA_PAYMENT_META_PAYER = Schema('payer', str)
    SCHEMA_PAYMENT_META_PAYMENT_METHOD = Schema('payment_method', str)
    SCHEMA_PAYMENT_META_PAYMENT_PROCESSOR = Schema('payment_processor', str)
    SCHEMA_PAYMENT_META_PAYMENT_REFERENCE_NUMBER = Schema('reference_number', str)
    SCHEMA_PAYMENT_META_PPD_ID = Schema('ppd_id', int)
    SCHEMA_PAYMENT_META_REASON = Schema('reason', str)
    SCHEMA_PAYMENT_META_TRANSACTION_ID = Schema('transaction_id', int)

    # plot cache
    SCHEMA_PLOT_CACHE_END_DATE = Schema('end_date', str)
    SCHEMA_PLOT_CACHE_FULL_TITLE = Schema('full_title', str)
    SCHEMA_PLOT_CACHE_HTML = Schema('html', str)
    SCHEMA_PLOT_CACHE_LOOKUP_DATE = Schema('lookup_date', str)
    SCHEMA_PLOT_CACHE_START_DATE = Schema('start_date', str)
    _SCHEMA_PLOT_CACHE_TIMESTAMP = Schema('timestamp', str)

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
            BankSchema._FULL_TB_NAME: 'SCHEMA_FULL',
            BankSchema.LOCATION_TB_NAME: 'SCHEMA_LOCATION',
            BankSchema.PAYMENT_META_TB_NAME: 'SCHEMA_PAYMENT_META',
            BankSchema.BANK_TB_NAME: 'SCHEMA_BANK',
            BankSchema.PLOT_CACHE_TB_NAME: 'SCHEMA_PLOT_CACHE',
            'all_tables': 'TB_NAME'
        }[key]

    @staticmethod
    def get_schema_table(tb_name):
        """
        obj: return the schema object types for a table_id
        """
        return [v for k, v in BankSchema.__dict__.items() if k.startswith(BankSchema.__const_groups_get(tb_name))
                and not k.startswith('_')]

    @staticmethod
    def get_pk_fields(tb_name):
        if tb_name == BankSchema._FULL_TB_NAME or tb_name == BankSchema.BANK_TB_NAME:
            return [BankSchema.SCHEMA_BANK_DATE,
                    BankSchema.SCHEMA_BANK_AMOUNT,
                    BankSchema.SCHEMA_BANK_C1,
                    BankSchema.SCHEMA_BANK_C2,
                    BankSchema.SCHEMA_BANK_NAME]

    @staticmethod
    def get_all_table_names():
        return [v for k, v in BankSchema.__dict__.items()
                if BankSchema.__const_groups_get('all_tables') in k and not k.startswith('_')]

