import logging
import os
import re
import string
from csv import DictReader
from pathlib import Path

import pandas as pd
from faker import Faker

from self_finance.constants import Schema

logger = logging.getLogger(__name__)


class SelfReferentialDict(dict):
    """
    obj: this class is use to be able to reference a dictionary value via `{}`
    for example, 'new': hello+`{some_pre_existing_key}`
    """

    def __init__(self, *args, **kw):
        super(SelfReferentialDict, self).__init__(*args, **kw)
        self.itemlist = super(SelfReferentialDict, self).keys()
        self.fmt = string.Formatter()

    def __getitem__(self, item):
        return self.fmt.vformat(dict.__getitem__(self, item), {}, self)


class RegexDict(dict):
    """
    obj: match keys in a dictionary using a regex pattern
    """

    def __init__(self, *args, **kw):
        super(RegexDict, self).__init__(*args, **kw)
        self._d_items = super(RegexDict, self).items()
        self._d = {re.compile(k): v for k, v in self._d_items}

    def __getitem__(self, item):
        # return the first pattern match in the dictionary
        for pattern, v in self._d.items():
            if pattern.match(item):
                return v
        raise KeyError("No identified regex matching keys.")


def for_all_methods(decorator):
    """
    obj: apply a decorator for all methods of a class
    """

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def func_to_filename(func, params_dict, ext):
    """
    obj: convert function into a filename string with using the function as the primary dynamic signature,
    this requires the use to collect the locals() at the very first call of the function
    """

    def dict_to_fn(d):
        removed_noise = {k: v for k, v in d.items() if not k.startswith('__') and k != 'self'}
        return re.sub("[' {}()]", '', str(removed_noise)).replace(':', '-').replace(',', '_')

    return func.__name__ + f'_{dict_to_fn(params_dict)}' + f'.{ext}'


def rm_db():
    from config.files import files
    os.remove(files['base_db'])


def rm_rec(dir_path):
    for the_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, the_file)
        if os.path.isfile(file_path):
            os.unlink(file_path)


def strip_ext(path):
    """
    obj: remove the extension from the path name
    """
    return str(Path(path).with_suffix(''))


def anon_the_data(csv_path_in, csv_path_out, replacements=None):
    """
    obj: one time type of use function to anonymize bank test data
    """
    f = Faker()
    replace = replacements or {Schema.SCHEMA_BANK_ACCOUNT_ID.name: f.random_int(0, 3),
                               Schema.SCHEMA_BANK_AMOUNT.name: f.random_int(0, 10000),
                               Schema.SCHEMA_BANK_TRANSACTION_ID: f.random_int()}
    new_rows = []
    with open(csv_path_in, 'r') as fp:
        dr = DictReader(fp)
        for row in dr:
            new_row = {}
            for key in row.keys():
                new_row[key] = replace[key]() if key in replace.keys() else row[key]
            new_rows.append(new_row)
    pd.DataFrame(new_rows).to_csv(csv_path_out, index=False)


def strip_csv(csv_path_in, csv_path_out):
    new_rows = []
    with open(csv_path_in, 'r') as fp:
        dr = DictReader(fp)
        for row in dr:
            new_row = {}
            for old_key in row.keys():
                new_key = old_key.strip()
                new_row[new_key] = row[old_key].strip()
            new_rows.append(new_row)
    pd.DataFrame(new_rows).to_csv(csv_path_out, index=False)
