import datetime
import logging
import os

import dateparser
import pandas as pd
import plaid
from flask import jsonify
from flask import render_template, request, flash

from config.files import files
from self_finance.back_end.data import Data
from self_finance.constants import Schema
from self_finance.constants import App
from self_finance.front_end import app
from self_finance.front_end.routes.state import State
from self_finance.front_end.routes.data import update_html_df
from self_finance.front_end.routes.insights import refresh_static_insights
from self_finance.front_end.routes.insights import refresh_dynamic_insights


logger = logging.getLogger(__name__)


class BankState(State):
    PLAID_CLIENT_ID = os.environ[App.PLAID_CLIENT_ID_ENV_VAR_KEY]
    PLAID_PUBLIC_KEY = os.environ[App.PLAID_PUBLIC_KEY_ENV_VAR_KEY]
    PLAID_SECRET = os.environ[App.PLAID_SECRET_ENV_VAR_KEY]
    PLAID_ENV = 'development'
    PLAID_PRODUCTS = 'transactions'
    client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                          public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)
    access_token = None


def _standard_render():
    return render_template(
        'index.html',
        plaid_public_key=BankState.PLAID_PUBLIC_KEY,
        plaid_environment=BankState.PLAID_ENV,
        plaid_products=BankState.PLAID_PRODUCTS
    )


@app.route('/')
@app.route('/index')
def index():
    return _standard_render()


@app.route('/index/update_transactions', methods=['POST'])
def get_access_token_and_update_transaction_history():
    """
    obj: exchange token flow - exchange a Link public_token for an API access_token
    """
    if BankState.access_token is None:
        public_token = request.form['public_token']
        try:
            exchange_response = BankState.client.Item.public_token.exchange(public_token)
        except plaid.errors.PlaidError as e:
            flash(jsonify(format_error(e)), 'warning')
            return _standard_render()
        BankState.access_token = exchange_response['access_token']
    else:
        flash('Unable to obtain access token for data.', 'warning')
        return _standard_render()
    return update_transaction_history()


def update_transaction_history():
    mrtd_org = Data.get_most_recent_transaction_date(Schema.BANK_TB_NAME, files['base_db'])
    mrtd = Schema.DATE_FORMAT.format(dateparser.parse(mrtd_org).date()) if mrtd_org else Schema.DATE_FORMAT.format(
        datetime.date.min)

    # update on transactions only following the mrtd
    start_date, end_date = mrtd, Schema.DATE_FORMAT.format(datetime.datetime.now())
    full_df = get_transactions(start_date, end_date)

    # TODO - this stuff isn't getting flashed
    p1 = 'Successfully updated your bank to the latest transaction history.'
    p2 = '\nNo previous data was found in your database so your entire transactions history was applied.'
    p3 = f'\nFrom date {str(start_date)} to {str(end_date)}.'
    p4 = f'No new transactions have been found.'
    try:
        if full_df is None or full_df.shape[0] == 0:
            flash(p4, 'info')
            return _standard_render()
        logger.info(f'Merging transactions into {Schema.BANK_TB_NAME} database.')
        Data.merge(full_df, files['base_db'])
        if not mrtd_org:
            flash(p1 + p2, 'info')
        else:
            flash(p1 + p3, 'info')
    except Exception as e:
        flash(e, 'warning')

    # update data-state on /date end
    if full_df is not None and full_df.shape[0] > 0:
        # note: need to run from `as_html_form_from_sql` because of the
        # additional preprocessing that is handled in merge operation
        update_html_df()
        refresh_static_insights()
        refresh_dynamic_insights()
    return _standard_render()


def get_transactions(start_date, end_date):
    response = BankState.client.Transactions.get(BankState.access_token, start_date=start_date, end_date=end_date)
    transactions = response['transactions']

    # the transactions in the response are paginated, so make multiple calls while increasing the offset to
    # retrieve all transactions
    while len(transactions) < response['total_transactions']:
        response = BankState.client.Transactions.get(BankState.access_token, start_date=start_date, end_date=end_date,
                                                     offset=len(transactions)
                                                     )
        transactions.extend(response['transactions'])
    return pd.DataFrame.from_dict(transactions)


def format_error(e):
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type,
                      'error_message': e.message}}
