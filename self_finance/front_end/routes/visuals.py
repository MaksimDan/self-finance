import logging

from flask import render_template, request, flash

from self_finance.back_end.data import Data
from self_finance.back_end.date_range import DateRange
from self_finance.back_end.insights.image_registry import ImageRegistry
from self_finance.constants import Html
from self_finance.constants import Schema
from self_finance.constants import Visuals
from self_finance.front_end import app
from self_finance.front_end.routes._commons import valid_dr
from self_finance.front_end.routes.state import State

logger = logging.getLogger(__name__)


class VisualState(State):
    __all_plt_ids = ImageRegistry.get_all_plot_ids()
    __all_plt_ids_len = len(__all_plt_ids)

    plot_selections = dict(zip(__all_plt_ids, [True] * __all_plt_ids_len))

    @staticmethod
    def as_dict():
        return State.as_dict_helper(VisualState, Visuals, excluded={'df'})


def _partition_html_and_xml_docs(image_id_to_html_map):
    xml_docs = {k: v for k, v in image_id_to_html_map.items() if v.lstrip().startswith(Html.XML_DOC_STARTS_WITH)}
    html_docs = {k: v for k, v in image_id_to_html_map.items() if v.lstrip().startswith(Html.HTML_DOC_STARTS_WITH)}
    if len(image_id_to_html_map) != len(xml_docs) + len(html_docs):
        logging.debug('Visuals where not completely partitioned from their original group size.')
    return xml_docs, html_docs


def _standard_render():
    image_id_to_html = _get_html_from_ids()
    xml_and_html_docs = {k: v for k, v in image_id_to_html.items() if v is not None}
    xml_docs, html_docs = _partition_html_and_xml_docs(xml_and_html_docs)
    if not xml_and_html_docs or len(xml_and_html_docs) == 0:
        flash('No identified visuals to display', 'warning')
    else:
        plural = len(xml_and_html_docs) > 1
        flash(f'{len(xml_and_html_docs)} plot{"s" if plural else ""} {"have" if plural else "has"} been identified.',
              'info')
    return render_template("visuals.html", vis_html=list(html_docs.values()),
                           vis_xml=list(xml_docs.values()), **VisualState.as_dict())


def _get_html_from_ids():
    return {image_id: Data.get_most_recent_html_from_id(image_id) for image_id in VisualState.plot_selections.keys()
            if VisualState.plot_selections[image_id]}


@app.route('/visuals')
def visuals():
    return _standard_render()


@app.route('/visuals/redraw', methods=['POST'])
def visuals_redraw():
    if request.method == 'POST':
        form = request.form
        drs, dre = form['start_query_name'], form['end_query_name']
        if not valid_dr(drs, dre):
            return _standard_render()
        State.date_range_start, State.date_range_end = drs, dre

        # update which visuals to draw and redraw them
        requested_plots_to_draw = set(ImageRegistry.get_all_plot_ids()) & set(form.keys())
        _update_requested_plots_to_draw(set(requested_plots_to_draw))
        df = Data.get_table_as_df(DateRange(State.date_range_start, State.date_range_end),
                                  table_name=Schema.BANK_TB_NAME)
        if df is None or df.shape[0] == 0:
            flash(f'No data int table {Schema.BANK_TB_NAME} produce diagrams.', 'warning')
        else:
            ImageRegistry.plot_all(list(requested_plots_to_draw), df, drs, dre)
    return _standard_render()


def _update_requested_plots_to_draw(requested_plots_to_draw):
    for plt_id in VisualState.plot_selections.keys():
        if plt_id in requested_plots_to_draw:
            VisualState.plot_selections[plt_id] = True
        else:
            VisualState.plot_selections[plt_id] = False
