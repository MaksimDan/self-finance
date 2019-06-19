import time

from flask import render_template, request

from self_finance.back_end.date_range import DateRange
from self_finance.back_end.insights.html_helper import HTMLHelper
from self_finance.back_end.insights.raw_insights import RawInsights
from self_finance.constants import Insights
from self_finance.constants import BankSchema
from self_finance.front_end import app
from self_finance.front_end.routes.commons import valid_dr
from self_finance.front_end.routes.state import State


class InsightState(State):
    html_bank_summary = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.table_summary_statistics(
        BankSchema.BANK_TB_NAME,
        DateRange(State.date_range_start, State.date_range_end)),
        Insights.BANK_SUMMARY_TABLE_ID, replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    html_top_inc_cat = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.get_top_n_income_categories(
        DateRange(State.date_range_start, State.date_range_end),
        BankSchema.BANK_TB_NAME), Insights.TOP_INC_TABLE_ID,
        replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    html_top_exp_cat = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.get_top_n_expense_categories(
        DateRange(State.date_range_start, State.date_range_end),
        BankSchema.BANK_TB_NAME), Insights.TOP_EXP_TABLE_ID,
        replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    _static_clock = time.time()
    html_inc_and_exp_this_month_vs_last_month_summary = HTMLHelper.as_html_form_from_df(
        RawInsights.Static.get_money_gain_and_spent_this_month_vs_last_month(
            DateRange(State.date_range_start, State.date_range_end),
            BankSchema.BANK_TB_NAME, as_dataframe=True), Insights.SPENDING_VS_LAST_MONTH_TABLE_ID,
        replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    html_inc_and_exp_this_month_vs_last_month_summary_as_str = RawInsights.Static. \
        summarize_this_and_last_months_spending(
        DateRange(State.date_range_start, State.date_range_end), BankSchema.BANK_TB_NAME)
    spending_vs_last_month_pid = 'spending_vs_last_month_p'

    @staticmethod
    def as_dict():
        return State.as_dict_helper(InsightState, Insights)

    @staticmethod
    def get_clock():
        return InsightState._static_clock

    @staticmethod
    def set_clock(clock):
        InsightState._static_clock = clock


def refresh_static_insights(ignore_clock=False):
    now = time.time()
    passed_minutes = now - InsightState.get_clock()
    # refresh only if a significant time has passed
    if ignore_clock or passed_minutes <= Insights.STATIC_TIME_CACHE_REFRESH_MINUTES:
        InsightState.html_inc_and_exp_this_month_vs_last_month_summary = HTMLHelper.as_html_form_from_df(
            RawInsights.Static.get_money_gain_and_spent_this_month_vs_last_month(
                DateRange(State.date_range_start, State.date_range_end),
                BankSchema.BANK_TB_NAME, as_dataframe=True), Insights.SPENDING_VS_LAST_MONTH_TABLE_ID,
            replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

        InsightState.html_inc_and_exp_this_month_vs_last_month_summary_as_str = RawInsights.Static. \
            summarize_this_and_last_months_spending(
            DateRange(State.date_range_start, State.date_range_end),
            BankSchema.BANK_TB_NAME)
        # refresh the clock for next look up period
        InsightState.set_clock(time.time())


def refresh_dynamic_insights():
    InsightState.html_bank_summary = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.table_summary_statistics(
        BankSchema.BANK_TB_NAME,
        DateRange(State.date_range_start, State.date_range_end)),
        Insights.BANK_SUMMARY_TABLE_ID, replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    InsightState.html_top_inc_cat = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.get_top_n_income_categories(
        DateRange(State.date_range_start, State.date_range_end),
        BankSchema.BANK_TB_NAME), Insights.TOP_INC_TABLE_ID,
        replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)

    InsightState.html_top_exp_cat = HTMLHelper.as_html_form_from_df(RawInsights.Dynammic.get_top_n_expense_categories(
        DateRange(State.date_range_start, State.date_range_end),
        BankSchema.BANK_TB_NAME), Insights.TOP_EXP_TABLE_ID,
        replace_default_data_frame_class_with=Insights.INSIGHT_TABLE_CLASS)


def _standard_render():
    refresh_static_insights()
    return render_template("insights.html", **InsightState.as_dict())


@app.route('/insights')
def insights():
    return _standard_render()


@app.route('/insights/dynamic', methods=['POST', 'GET'])
def insights_dynamic():
    if request.method == 'POST':
        form = request.form
        drs, dre = form['start_query_name'], form['end_query_name']
        if not valid_dr(drs, dre):
            return _standard_render()
        State.date_range_start, State.date_range_end = drs, dre
        refresh_dynamic_insights()
    return _standard_render()
