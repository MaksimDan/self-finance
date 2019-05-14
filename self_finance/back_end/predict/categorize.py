import logging
import pprint
from collections import defaultdict

import pandas as pd
from progressbar import ProgressBar
from tabulate import tabulate

from config.files import files
from self_finance.back_end.data import Data
from self_finance.back_end.predict.bank_classifier import BankClassifier
from self_finance.back_end.sqlite_helper import SqliteHelper
from self_finance.constants import Schema

logger = logging.getLogger(__name__)


class Categorize:
    def __init__(self):
        self.classifier = BankClassifier()
        self.model_df = Data.get_table_as_df(date_range=None)
        self.current_categories_dict = None
        assert self.model_df.shape[0] > 0, "No bank static was found."

    def cli_user_populate_missing_categories(self, auto_fill_with_model_suggestion=False):
        """
        obj: have the user manually update missing columns, and update the db accordingly.
        this is not used by the flask application itself. it is a command line utility
        """
        missing_cat_df = Data.get_missing_categories()
        if len(missing_cat_df) == 0:
            logger.info('No rows identified to categorize.')
            return

        model_c1 = self.classifier.get_model(Schema.BASE_MODEL_C1_NAME)
        model_c2 = self.classifier.get_model(Schema.BASE_MODEL_C2_NAME)
        user_c1_cats, user_c2_cats = [], []
        if not auto_fill_with_model_suggestion:
            print(">> Current Categories::")
            print(">> " + pprint.pformat(self.get_current_unique_categories(), indent=4))
            print(">> Note: press enter to take suggestion, or 'none' for no category", end='\n\n')

        bar = ProgressBar()
        for index in bar(range(missing_cat_df.shape[0])):
            row = missing_cat_df.iloc[index]
            print(">>\n" + tabulate(row.to_frame().T, headers='keys', tablefmt='psql'))
            suggestion_c1 = model_c1.predict(row[Data.get_missing_categories()].values) if model_c1 else None
            suggestion_c2 = model_c2.predict(row[Data.get_missing_categories()].values) if model_c2 else None

            category_c1, category_c2 = None, None
            if not auto_fill_with_model_suggestion:
                if suggestion_c1:
                    print(f">> Suggestion c1: {suggestion_c1}")
                category_c1 = input('>> Enter Expense super category: ').lower().strip()
                if suggestion_c2:
                    print(f">> Suggestion c2: {suggestion_c2}")
                category_c2 = input('>> Enter Expense secondary category: ').lower().strip()
                category_c1 = None if category_c1 == 'none' else category_c1
                category_c2 = None if category_c2 == 'none' else category_c2
                print('\n\n')

            user_c1_cats.append(category_c1 if bool(category_c1) or not suggestion_c1 else suggestion_c1)
            user_c2_cats.append(category_c2 if bool(category_c2) or not suggestion_c2 else suggestion_c2)

        pk_fields, cat_fields = Schema.get_pk_fields(), Schema.get_table_chase_y_fields()
        filled_cat_df = missing_cat_df[pk_fields]
        pd.options.mode.chained_assignment = None
        filled_cat_df[cat_fields[0]] = user_c1_cats
        filled_cat_df[cat_fields[1]] = user_c2_cats
        Data.update_missing_categories(filled_cat_df.to_dict('records'), pk_fields, cat_fields)

    def get_current_unique_categories(self):
        """
        obj: identify all the unique categories currently recognized by the user
        """
        if self.current_categories_dict:
            return self.current_categories_dict
        cat_fields = Schema.get_table_chase_y_fields()
        query = f"SELECT DISTINCT {','.join(cat_fields)}\n" \
            f"FROM {Schema.TABLE_NAME_CHASE_DEBIT}\n"
        _df_dict = SqliteHelper.execute_sqlite(query, files['base_db'], as_dataframe=True).to_dict('record')
        root_d = defaultdict(set)
        for d in _df_dict:
            root_d[d[cat_fields[0]]].add(d[cat_fields[1]])
        return root_d
