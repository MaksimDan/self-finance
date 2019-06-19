import datetime
import logging
from math import nan
from collections import Counter

import pandas as pd

from config.files import files
from self_finance.back_end.data import Data
from self_finance.constants import BankSchema

logger = logging.getLogger(__name__)


class RawInsights:
    class Dynammic:
        @staticmethod
        def _agg_top_n_income_and_expense_categories(df, n):
            counter = Counter(list(df[BankSchema.SCHEMA_BANK_C1.name].values))
            return counter.most_common(n)

        @staticmethod
        def _top_n_categories(inc_or_exp, date_range, table_name, n, db_path):
            df = Data.get_table_as_df(date_range, table_name, db_path=db_path)
            if df is None or df.shape[0] == 0:
                return None
            df_filter = df[df[BankSchema.SCHEMA_BANK_INC_OR_EXP.name] == inc_or_exp]
            most_common_filter = RawInsights.Dynammic._agg_top_n_income_and_expense_categories(df_filter, n)
            return pd.DataFrame(most_common_filter, columns=['category', 'frequency'])

        @staticmethod
        def table_summary_statistics(table_name, date_range, db_path=files['base_db']):
            pd.options.html.border = 0
            summary_df = Data.get_table_as_df(date_range, table_name, db_path=db_path)
            if summary_df is None or summary_df.shape[0] == 0:
                logger.debug('Unable to instantiate summary statistics table. The database is probably empty.')
                return None
            else:
                return summary_df.describe()

        @staticmethod
        def get_top_n_income_categories(date_range, table_name, n=5, db_path=files['base_db']):
            return RawInsights.Dynammic._top_n_categories('income', date_range, table_name, n, db_path)

        @staticmethod
        def get_top_n_expense_categories(date_range, table_name, n=5, db_path=files['base_db']):
            return RawInsights.Dynammic._top_n_categories('expense', date_range, table_name, n, db_path)

    class Static:
        @staticmethod
        def _agg_income_and_expenses_by_month(df, month):
            sum_income, sum_expenses = 0, 0
            for index, row in df.iterrows():
                if row[BankSchema.SCHEMA_BANK_DATE.name].month == month:
                    if row[BankSchema.SCHEMA_BANK_AMOUNT.name] > 0:
                        sum_income += row[BankSchema.SCHEMA_BANK_AMOUNT.name]
                    else:
                        sum_expenses += row[BankSchema.SCHEMA_BANK_AMOUNT.name]
            return sum_income, sum_expenses

        @staticmethod
        def get_money_gain_and_spent_this_month_vs_last_month(date_range, table_name, _overide_month=None,
                                                              as_dataframe=False, db_path=files['base_db']):
            df = Data.get_table_as_df(date_range, table_name, db_path=db_path)
            if df is None or df.shape[0] == 0:
                return None
            df[BankSchema.SCHEMA_BANK_DATE.name] = pd.to_datetime(df[BankSchema.SCHEMA_BANK_DATE.name])
            this_month = _overide_month or datetime.date.today().month
            last_month = this_month - 1 or 12

            inc_this_month, exp_this_month = RawInsights.Static._agg_income_and_expenses_by_month(df, this_month)
            sum_income_last_month, exp_last_month = RawInsights.Static._agg_income_and_expenses_by_month(df, last_month)
            as_dict = {
                'inc_this_month': "{0:.2f}".format(inc_this_month),
                'exp_this_month': "{0:.2f}".format(exp_this_month),
                'inc_last_month': "{0:.2f}".format(sum_income_last_month),
                'exp_last_month': "{0:.2f}".format(exp_last_month)
            }
            if not as_dataframe:
                return as_dict
            else:
                # convert to a single row dataframe
                _temp_df = pd.DataFrame(list(as_dict.values())).T
                _temp_df.columns = list(as_dict.keys())
                return _temp_df

        @staticmethod
        def summarize_this_and_last_months_spending(date_range, table_name, db_path=files['base_db']):
            sum_dict = RawInsights.Static.get_money_gain_and_spent_this_month_vs_last_month(date_range, table_name,
                                                                                            db_path=db_path)
            if sum_dict is None:
                return None
            diff_income = float(sum_dict['inc_this_month']) - float(sum_dict['inc_this_month'])
            diff_expense = abs(float(sum_dict['exp_this_month'])) - abs(float(sum_dict['exp_last_month']))

            income_is_higher_this_month = diff_income > 0
            income_is_same_this_month = diff_income == 0
            expenses_are_lower_this_month = diff_expense < 0
            expenses_are_the_same_this_month = diff_expense == 0

            def try_div(a, b):
                try:
                    return a / b
                except ZeroDivisionError:
                    return nan

            if income_is_same_this_month:
                msg_income1 = 'the same'
                msg_income2 = 'remained the same'
            elif income_is_higher_this_month:
                msg_income1 = 'higher'
                increase_perc = try_div(float(sum_dict['inc_this_month']), float(sum_dict['inc_this_month']))
                increase_perc = "{0:.2f}".format(increase_perc)
                msg_income2 = f'increased by {increase_perc}x'
            else:
                msg_income1 = 'lower'
                dec_perc = try_div(float(sum_dict['inc_this_month']), float(sum_dict['inc_this_month']))
                dec_perc = "{0:.2f}".format(dec_perc)
                msg_income2 = f'decreased by {dec_perc}x'

            if expenses_are_the_same_this_month:
                msg_expense1 = 'the same'
                msg_expense2 = 'remained the same'
            elif expenses_are_lower_this_month:
                msg_expense1 = 'lower'
                dec_perc = try_div(abs(float(sum_dict['exp_last_month'])), abs(float(sum_dict['exp_this_month'])))
                dec_perc = "{0:.2f}".format(dec_perc)
                msg_expense2 = f'decreased by {dec_perc}x'
            else:
                msg_expense1 = 'higher'
                dec_perc = try_div(abs(float(sum_dict['exp_this_month'])), abs(float(sum_dict['exp_last_month'])))
                dec_perc = "{0:.2f}".format(dec_perc)
                msg_expense2 = f'increased by {dec_perc}x'

            summary = f"""
            Your income is {msg_income1} when compared to last month{' by $' + str(
                diff_income) if not income_is_same_this_month else ''}.
            And your expenses are {msg_expense1} when compared to last month{' by $' + "{0:.2f}".format(
                abs(diff_expense)) if not expenses_are_the_same_this_month else ''}.
            Your income has {msg_income2} and your expenses have {msg_expense2}.
            """
            summary = ' '.join(elm.strip() for elm in summary.split('\n'))
            return summary.strip()
