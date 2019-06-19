import io
import logging
import os
import tempfile

import pandas as pd
from flask import render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename

from self_finance.back_end.data import Data
from self_finance.back_end.date_range import DateRange
from self_finance.back_end.insights.html_helper import HTMLHelper
from self_finance.constants import Data as ConstData
from self_finance.constants import Defaults
from self_finance.constants import BankSchema
from self_finance.constants import Schema
from self_finance.front_end import app
from self_finance.front_end.routes.commons import valid_dr
from self_finance.front_end.routes.insights import refresh_dynamic_insights
from self_finance.front_end.routes.insights import refresh_static_insights
from self_finance.front_end.routes.settings import invalidate_cache
from self_finance.front_end.routes.state import State

logger = logging.getLogger(__name__)


class DataState(State):
    order_by_column_name = BankSchema.SCHEMA_BANK_DATE.name
    order_by = Defaults.ORDER_BY_DEFAULT

    html_df = HTMLHelper.as_html_form_from_sql(
        BankSchema.BANK_TB_NAME, DateRange(State.date_range_start, State.date_range_end),
        order_by_column_name, order_by, table_id=ConstData.BANK_DATA_TABLE_ID)

    @staticmethod
    def as_dict():
        return State.as_dict_helper(DataState, ConstData)


def _standard_render():
    if not DataState.html_df or len(DataState.html_df) == 0:
        flash('No data was found in the database table.', 'warning')
    return render_template("data.html", data_table_id=ConstData.BANK_DATA_TABLE_ID, **DataState.as_dict())


@app.route('/data')
def data():
    return _standard_render()


def update_html_df():
    DataState.html_df = HTMLHelper.as_html_form_from_sql(
        BankSchema.BANK_TB_NAME, DateRange(State.date_range_start, State.date_range_end),
        DataState.order_by_column_name, DataState.order_by, table_id=ConstData.BANK_DATA_TABLE_ID)


@app.route('/data/data_query', methods=['POST', 'GET'])
def data_query():
    if request.method == 'POST':
        form = request.form

        # check validity of input queries
        obcn, o = form['order_by_column_name'], form['order']
        if obcn not in set(Schema.get_names(BankSchema.get_schema_table(BankSchema.BANK_TB_NAME))):
            flash(f'{obcn} is not a valid column name.', 'warning')
            return _standard_render()

        drs, dre = form['start_query_name'], form['end_query_name']
        if not valid_dr(drs, dre):
            return _standard_render()

        # update data range and order by states
        DataState.order_by_column_name, DataState.order_by = obcn, o
        State.date_range_start, State.date_range_end = drs, dre

        # combine everything together
        try:
            update_html_df()
        except KeyError:
            flash(f'Invalid column name {DataState.order_by_column_name}', 'danger')
            return _standard_render()
        flash(f'Data filtered between dates {State.date_range_start} and {State.date_range_end}.\n'
              f'{BankSchema.BANK_TB_NAME} table has had its order updated by '
              f'{DataState.order_by_column_name} {DataState.order_by}', 'info')
    return _standard_render()


@app.route('/data/upload', methods=['POST', 'GET'])
def data_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash(f'No file provided.', 'warning')
        else:
            f = request.files['file']
            fn = secure_filename(f.filename)
            if not f or not fn.endswith('.csv'):
                flash('Not an identified CSV file.', 'warning')
            else:
                try:
                    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
                    stream.seek(0)
                    input_df = pd.read_csv(stream, index_col=False)
                    # TODO - necessary?
                    # input_df = Data.cast_df_to_schema(input_df, Schema.BANK_TB_NAME)
                    Data.merge(input_df)
                    update_html_df()
                    # to ensure visuals and insights take in the most up to date information
                    invalidate_cache(flash=False)
                    refresh_dynamic_insights()
                    refresh_static_insights(ignore_clock=True)
                except IOError as e:
                    flash(f'Unable to parse file. {e}', 'warning')
                flash('Awesome! File processed successfully.', 'success')
    return _standard_render()


@app.route('/data/update', methods=['POST', 'GET'])
def data_update():
    if request.method == 'POST':
        form = request.form
        update_df = pd.read_html(form['hidden_post_name'], header=0, index_col=0, parse_dates=True)[0]
        update_df = Data.cast_df_to_schema(update_df, BankSchema.BANK_TB_NAME)
        Data.merge(update_df)
        update_html_df()
        invalidate_cache(flash=False)
        refresh_dynamic_insights()
        refresh_static_insights(ignore_clock=True)
        flash('Data updated with new csv.', 'info')
    return _standard_render()


@app.route('/data/truncate', methods=['POST', 'GET'])
def data_truncate():
    if request.method == 'POST':
        Data.truncate_all_tables()
        DataState.html_df = None
        invalidate_cache(flash=False)
        refresh_dynamic_insights()
        refresh_static_insights(ignore_clock=True)
        flash(f"{BankSchema.BANK_TB_NAME} table has been fully truncated from the base database.", 'info')
    return _standard_render()


@app.route('/data/download', methods=['POST', 'GET'])
def data_download():
    if request.method == 'POST':
        logger.info('Downloading bank data as csv file.')
        with tempfile.TemporaryDirectory() as tmpdir:
            dr = DateRange(State.date_range_start, State.date_range_end)
            bank_df = Data.get_table_as_df(dr, BankSchema.BANK_TB_NAME, DataState.order_by_column_name, DataState.order_by)
            if bank_df is None or bank_df.shape[0] == 0:
                flash(f'{BankSchema.BANK_TB_NAME} table is empty. Nothing to download.', 'warning')
                return _standard_render()
            bank_df.to_csv(os.path.join(tmpdir, ConstData.FILE_NAME_DOWNLOAD), index=False)
            return send_from_directory(directory=tmpdir, filename=ConstData.FILE_NAME_DOWNLOAD, as_attachment=True)
    return _standard_render()
