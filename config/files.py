import os
from os.path import join

from self_finance import utils
from self_finance.constants import BankSchema


ROOT = os.getcwd()

dirs = utils.SelfReferentialDict({
    'static': join(ROOT, 'static'),
    'data_scratch': join('{static}', 'scratch'),
    'models': join('{static}', 'models'),
    'insights': join('{static}', 'insights'),
    'logs': join(ROOT, 'logs'),
    'template_folder': join(ROOT, os.path.join('self_finance', 'front_end', 'templates'))
})

files = utils.SelfReferentialDict({
    'log_config': join(ROOT, 'config', 'log.yml'),
    'base_db': join(ROOT, 'sql', BankSchema.BASE_DB_NAME),
    'create_db': join(ROOT, 'sql', 'create_db.sql'),
})

test_dirs = utils.SelfReferentialDict({
    'test': join(ROOT, '..'),
    'sql': join('{test}', 'sql'),
    'test_resources': join('{test}', 'resources')
})

test_files = utils.SelfReferentialDict({
    'bank_sample.csv': join(test_dirs['test_resources'], 'bank_sample.csv'),
    'locations_sample.csv': join(test_dirs['test_resources'], 'locations_sample.csv'),
    'payment_meta_sample.csv': join(test_dirs['test_resources'], 'payment_meta_sample.csv'),
    'full_sample.csv': join(test_dirs['test_resources'], 'full_sample.csv'),
    'transaction_response_dict.pickle': join(test_dirs['test_resources'], 'transaction_response_dict.pickle'),
    'create_db': join(test_dirs['sql'], 'create_db.sql'),
    'base_db': join(test_dirs['sql'], BankSchema.BASE_DB_NAME)
})
