import datetime
import logging
from io import StringIO
from threading import BoundedSemaphore
from threading import Lock
from threading import Thread

from self_finance.back_end.date_range import DateRange
from self_finance.back_end.insights._plot import _Plot
from self_finance.back_end.plot_cache import PlotCache
from self_finance.constants import BankSchema
from self_finance.constants import Visuals

logger = logging.getLogger(__name__)


class ImageRegistry:
    """
    obj: interaction class that maps human friendly string and parameters
    to Plot
    """
    __global_lock = Lock()
    _plot_interface = {
        'Income vs Expenses Over Time': {
            'func': _Plot.income_vs_expenses_over_time,
            'supported_plots': {'line', 'bar', 'violin'},
            'figsize': (11, 8)
        },
        'Income by Category': {
            'func': _Plot.income_by_category,
            'supported_plots': {'line', 'bar', 'violin'},
            'figsize': (11, 5)
        },
        'Expenses by Category': {
            'func': _Plot.expenses_by_category,
            'supported_plots': {'line', 'bar', 'violin'},
            'figsize': (11, 5)
        },
        'Frequency of Transactions by Category': {
            'func': _Plot.transactional_frequency_over_time,
            'supported_plots': {'line', 'bar'},
            'figsize': (11, 5)
        },
        'Income by Month': {
            'func': _Plot.income_by_month,
            'supported_plots': {'bar'},
            'figsize': (11, 5)
        },
        'Expenses by Month': {
            'func': _Plot.expenses_by_month,
            'supported_plots': {'bar'},
            'figsize': (11, 5)
        },
        'Spending Heatmap': {
            'func': _Plot.spending_heatmap,
        }
    }

    @staticmethod
    def _get_plot_interface_keys():
        return ImageRegistry._plot_interface.keys()

    @staticmethod
    def get_supported_plots(plot_key):
        try:
            return ImageRegistry._plot_interface[plot_key]['supported_plots']
        except KeyError:
            return None

    @staticmethod
    def get_plot_func(plot_key):
        try:
            return ImageRegistry._plot_interface[plot_key]['func']
        except KeyError:
            return None

    @staticmethod
    def get_plot_figsize(plot_key):
        try:
            return ImageRegistry._plot_interface[plot_key]['figsize']
        except KeyError:
            return None

    @staticmethod
    def get_all_plot_ids():
        plot_ids = []
        for plt_basis in ImageRegistry._get_plot_interface_keys():
            support_plot_types = ImageRegistry.get_supported_plots(plt_basis)
            # logic in place to support plots that don't have types like bar, violin, etc
            if support_plot_types:
                for plt_type in support_plot_types:
                    plot_ids.append(ImageRegistry._make_plot_key_title(plt_basis, plt_type))
            else:
                plot_ids.append(plt_basis)
        return sorted(plot_ids)

    @staticmethod
    def plot_all(plot_ids, df, start_date, end_date):
        threads = []
        df = df.sort_values(by=BankSchema.SCHEMA_BANK_DATE.name)
        semaphor_pool = BoundedSemaphore(value=Visuals.PLOT_MAX_THREADS)
        logging.info(f'Beginning plotting using {Visuals.PLOT_MAX_THREADS} threads.')
        for plt_id in plot_ids:
            semaphor_pool.acquire()
            t = Thread(target=ImageRegistry._plot, args=(plt_id, start_date, end_date, df))
            threads.append(t)
            t.start()
            semaphor_pool.release()
        # wait for all of them to finish
        for x in threads:
            x.join()

    @staticmethod
    def _plot(plt_id, start_date, end_date, df):
        # the logic here is put in place also handle the case when we want to plot heat map
        plot_branch = [s.strip() for s in plt_id.split('-')]
        is_matplotlib = len(plot_branch) == 2
        if is_matplotlib:
            plot_basis, plot_type = plot_branch
            plot_type = plot_type.lower()
            ImageRegistry.__plot(plot_basis, start_date, end_date, plot_type, df)
        else:
            plot_basis = plot_branch[0].strip()
            ImageRegistry.__plot(plot_basis, start_date, end_date)

    @staticmethod
    def __plot(plot_basis, start_date, end_date, plot_type=None, df=None):
        # check if we've plotted this same plot in the past before
        kwargs = {}
        now = datetime.datetime.now().strftime(BankSchema.DATE_FORMAT2)
        title = ImageRegistry._make_plot_key_title(plot_basis, plot_type)
        plot_cache_result = PlotCache.hit(title, start_date, end_date, now)
        if plot_cache_result is None:
            logging.info(f'Plot cache miss for plot: {title}, replotting.')
            if plot_type and plot_type not in ImageRegistry.get_supported_plots(plot_basis):
                raise KeyError(f"Provided plot type {plot_type} is not supported.")
            kwargs['plot_type'] = plot_type
            kwargs['title'] = title
            kwargs['figsize'] = ImageRegistry.get_plot_figsize(plot_basis)
            with ImageRegistry.__global_lock:
                if df is not None:
                    fig_or_html = ImageRegistry.get_plot_func(plot_basis)(df, **kwargs)
                else:
                    # heatmap
                    fig_or_html = ImageRegistry.get_plot_func(plot_basis)(DateRange(start_date, end_date), **kwargs)
            # is figure
            if fig_or_html is not None and not isinstance(fig_or_html, str):
                stream_reader = StringIO()
                fig_or_html.savefig(stream_reader, format='svg', bbox_inches='tight')
                stream_reader.seek(0)
                html = stream_reader.getvalue()
                PlotCache.add_cache_miss(title, start_date, end_date, now, html)
            elif fig_or_html is None:
                logging.warning(f'Ignoring plot for {plot_basis}.')
            else:
                # heat-map plot
                PlotCache.add_cache_miss(title, start_date, end_date, now, fig_or_html)
        else:
            logging.info(f'Plot cache hit for plot: {title}, ignoring replotting.')

    @staticmethod
    def _make_plot_key_title(plot_basis, plot_type):
        if plot_type is None:
            return plot_basis
        else:
            return f"{plot_basis} - {plot_type.capitalize()}"
