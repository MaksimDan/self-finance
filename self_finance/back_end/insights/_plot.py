import logging
import operator
from collections import Counter
from collections import defaultdict
from functools import reduce

import folium
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from folium.plugins import HeatMap

from config.files import files
from self_finance.back_end.data import Data
from self_finance.constants import BankSchema
from self_finance.constants import Visuals

logger = logging.getLogger(__name__)


class _PlotHelper:
    @staticmethod
    def cumsum_by_conditional_group(values, corresponding_categories):
        unique_groups = list(set(corresponding_categories))
        group_cumsum, group_curr_cumsum = defaultdict(list), defaultdict(int)
        for val, cat in zip(values, corresponding_categories):
            group_curr_cumsum[cat] += val
            for group in unique_groups:
                group_cumsum[group].append(group_curr_cumsum[group])
        return group_cumsum

    @staticmethod
    def cumsum_line_plot_by_group(main_df, fig, ax, hue, title, x=BankSchema.SCHEMA_BANK_DATE.name,
                                  y=BankSchema.SCHEMA_BANK_AMOUNT.name, ndate_labels=10):
        df_y, df_hue = list(main_df[y].values), list(main_df[hue].values)
        cumsum_hue = _PlotHelper.cumsum_by_conditional_group(df_y, df_hue)
        tmp_df = pd.DataFrame({y: reduce(lambda l1, l2: l1 + l2, cumsum_hue.values()),
                               hue: reduce(lambda l1, l2: l1 + l2,
                                           [[group] * len(values) for group, values in cumsum_hue.items()]),
                               x: list(main_df[x].values) * len(cumsum_hue)})

        # ensure x label for datetime is not overcrowded
        xloc = plt.MaxNLocator(ndate_labels)
        ax.xaxis.set_major_locator(xloc)
        sns.lineplot(x=x, y=y, hue=hue, data=tmp_df)
        fig.autofmt_xdate()
        plt.title(title)


class _Plot:
    """
    obj: all drawing / plot logic
    """
    plt.style.use('ggplot')
    sns.set_palette(sns.color_palette("bright"))
    sns.set_context("paper")

    @staticmethod
    def income_vs_expenses_over_time(df, **kwargs):
        """
        obj: how does income compare to my expenses over time?
        """
        plot_type, figsize, title = kwargs.get('plot_type', None), kwargs.get('figsize', None), \
                                    kwargs.get('title', None)

        fig, ax = plt.subplots(figsize=figsize)
        if plot_type == 'line':
            df_amount = list(df[BankSchema.SCHEMA_BANK_AMOUNT.name].values)
            df_type = list(df[BankSchema.SCHEMA_BANK_INC_OR_EXP.name].values)
            cum_sum_inc_or_exp = _PlotHelper.cumsum_by_conditional_group(df_amount, df_type)
            cum_sum_income, cum_sum_expense = cum_sum_inc_or_exp['income'], cum_sum_inc_or_exp['expense']
            cum_sum_profit = [inc - abs(exp) for inc, exp in zip(cum_sum_income, cum_sum_expense)]
            tmp_df = pd.DataFrame({BankSchema.SCHEMA_BANK_AMOUNT.name: cum_sum_expense + cum_sum_income + cum_sum_profit,
                                   'type': ['expense'] * len(cum_sum_expense) + ['income'] * len(cum_sum_income) +
                                           ['net'] * len(cum_sum_profit),
                                   BankSchema.SCHEMA_BANK_DATE.name: list(
                                       df[BankSchema.SCHEMA_BANK_DATE.name].values) * 3})
            # ensure x label for datetime is not overcrowded
            xloc = plt.MaxNLocator(10)
            ax.xaxis.set_major_locator(xloc)
            sns.lineplot(x=BankSchema.SCHEMA_BANK_DATE.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                         hue='type', data=tmp_df)
            fig.autofmt_xdate()
        elif plot_type == 'violin':
            sns.violinplot(x=BankSchema.SCHEMA_BANK_INC_OR_EXP.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                           hue=BankSchema.SCHEMA_BANK_INC_OR_EXP.name, data=df, showfliers=False)
        elif plot_type == 'bar':
            sns.barplot(x=BankSchema.SCHEMA_BANK_INC_OR_EXP.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                        data=df, estimator=np.sum)
        plt.title(title)
        return fig

    @staticmethod
    def _filter_df_by_n_highest_aggregates(df, key_column, agg_column=BankSchema.SCHEMA_BANK_AMOUNT.name, n=8):
        """
        obj: return a filtered dataframe allowing only the `n` highest elements in `column`
        to exist.
        """
        col_agg = defaultdict(float)
        for key, val in zip(df[key_column].values, df[agg_column].values):
            col_agg[key] += val
        sorted_col_agg_by_val = sorted(col_agg.items(), key=operator.itemgetter(1), reverse=True)
        allow_these_elms = [k for k, v in sorted_col_agg_by_val]
        allow_these_elms = allow_these_elms[:min(n, max(len(allow_these_elms) - 1, 0))]
        return df[df[key_column].isin(allow_these_elms)]

    @staticmethod
    def _filter_df_by_n_highest_frequency(df, key_column, n=8):
        col_freq = Counter(df[key_column].values)
        allow_these_elms = [k for k, f in col_freq.most_common(n)]
        return df[df[key_column].isin(allow_these_elms)]

    @staticmethod
    def _inc_or_exp_by_category(inc_or_exp, df, **kwargs):
        """
        obj: how does incomes and expenses change by category?
        """
        plot_type, figsize, title = kwargs.get('plot_type', None), kwargs.get('figsize', None), \
                                    kwargs.get('title', None)

        fig, ax = plt.subplots(figsize=figsize)
        df = df[df[BankSchema.SCHEMA_BANK_INC_OR_EXP.name] == inc_or_exp.lower()]
        if plot_type == 'line':
            df = _Plot._filter_df_by_n_highest_aggregates(df, BankSchema.SCHEMA_BANK_C1.name)
            _PlotHelper.cumsum_line_plot_by_group(df, fig, ax, BankSchema.SCHEMA_BANK_C1.name, 'Income by Category')
        elif plot_type == 'violin':
            df = _Plot._filter_df_by_n_highest_aggregates(df, BankSchema.SCHEMA_BANK_C1.name, n=4)
            sns.violinplot(x=BankSchema.SCHEMA_BANK_C1.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                           hue=BankSchema.SCHEMA_BANK_C2.name, data=df, showfliers=False)
        elif plot_type == 'bar':
            df = _Plot._filter_df_by_n_highest_aggregates(df, BankSchema.SCHEMA_BANK_C1.name, n=4)
            sns.barplot(x=BankSchema.SCHEMA_BANK_C1.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                        hue=BankSchema.SCHEMA_BANK_C2.name, data=df, estimator=np.sum)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.title(title)
        return fig

    @staticmethod
    def income_by_category(df, **kwargs):
        """
        obj: how does income change over time over time?
        """
        logging.info('Plotting income_by_category plot')
        return _Plot._inc_or_exp_by_category('income', df, **kwargs)

    @staticmethod
    def expenses_by_category(df, **kwargs):
        """
        obj: how does expenses change over time over time?
        """
        logging.info('Plotting expenses_by_category plot')
        return _Plot._inc_or_exp_by_category('expense', df, **kwargs)

    @staticmethod
    def transactional_frequency_over_time(df, **kwargs):
        """
        obj: how does the total count of transactions change over time?
        """
        logging.info('Plotting transactional_frequency_over_time plot')
        plot_type, figsize, title = kwargs.get('plot_type', None), kwargs.get('figsize', None), \
                                    kwargs.get('title', None)

        fig, ax = plt.subplots(figsize=figsize)
        tmp_const = 'count'
        df[tmp_const] = [1 for _ in range(0, df.shape[0])]
        if plot_type == 'line':
            df = _Plot._filter_df_by_n_highest_frequency(df, BankSchema.SCHEMA_BANK_C1.name)
            _PlotHelper.cumsum_line_plot_by_group(df, fig, ax, BankSchema.SCHEMA_BANK_C1.name, title, y=tmp_const)
        elif plot_type == 'bar':
            df = _Plot._filter_df_by_n_highest_frequency(df, BankSchema.SCHEMA_BANK_C1.name, 4)
            sns.barplot(x=BankSchema.SCHEMA_BANK_C1.name, y=tmp_const, hue=BankSchema.SCHEMA_BANK_C2.name, data=df,
                        estimator=np.sum)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.title(title)
        return fig

    @staticmethod
    def _inc_or_exp_by_month(inc_or_exp, df, **kwargs):
        plot_type, figsize, title = kwargs.get('plot_type', None), kwargs.get('figsize', None), \
                                    kwargs.get('title', None)
        fig, ax = plt.subplots(figsize=figsize)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        df = df[df[BankSchema.SCHEMA_BANK_INC_OR_EXP.name] == inc_or_exp.lower()]
        pd.options.mode.chained_assignment = None
        df[BankSchema.SCHEMA_BANK_DATE.name] = pd.to_datetime(df[BankSchema.SCHEMA_BANK_DATE.name])
        df.groupby(
            [BankSchema.SCHEMA_BANK_C1.name, pd.Grouper(key=BankSchema.SCHEMA_BANK_DATE.name, freq='M')]).count().reset_index()
        sns.barplot(x=BankSchema.SCHEMA_BANK_DATE.name, y=BankSchema.SCHEMA_BANK_AMOUNT.name,
                    hue=BankSchema.SCHEMA_BANK_C1.name, data=df, estimator=np.sum)
        xloc = plt.MaxNLocator(10)
        ax.xaxis.set_major_locator(xloc)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        fig.autofmt_xdate()
        plt.title(title)
        return fig

    @staticmethod
    def expenses_by_month(df, **kwargs):
        logging.info('Plotting expenses_by_month plot')
        return _Plot._inc_or_exp_by_month('expense', df, **kwargs)

    @staticmethod
    def income_by_month(df, **kwargs):
        logging.info('Plotting income_by_month plot')
        return _Plot._inc_or_exp_by_month('income', df, **kwargs)

    @staticmethod
    def spending_heatmap(date_range, db_path=files['base_db'], **kwargs):
        logging.info('Plotting spending_heatmap plot')
        hm_df = Data.get_heatmap_df(date_range, db_path)
        if hm_df is None:
            logging.warning('Query for heatmap dataframe returned as empty, ignoring plot.')
            return None
        hm_df = hm_df.dropna()
        hmap = folium.Map(zoom_start=6, location=Visuals.HM_START_LAT_LON)
        hm_wide = HeatMap(list(zip(hm_df[BankSchema.SCHEMA_LOCATION_LAT.name].values,
                                   hm_df[BankSchema.SCHEMA_LOCATION_LON.name].values,
                                   hm_df[BankSchema.SCHEMA_BANK_AMOUNT.name].values)),
                          min_opacity=0.2,
                          radius=17, blur=15,
                          max_zoom=1)
        hmap.add_child(hm_wide)
        return hmap.get_root().render()
