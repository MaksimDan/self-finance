import logging
import re

from self_finance.back_end.data import Data
from self_finance.constants import Data as ConstData
from self_finance.constants import Html

logger = logging.getLogger(__name__)


class HTMLHelper:
    _TABLE_CELL_TAG = '<td>'
    _TABLE_CELL_EDITABLE_TAG = "<td contenteditable='true'>"

    @staticmethod
    def _make_html_table_editable(html_df):
        return html_df.replace(HTMLHelper._TABLE_CELL_TAG,
                               HTMLHelper._TABLE_CELL_EDITABLE_TAG)

    @staticmethod
    def as_html_form_from_sql(table_name, date_range, order_by_col_name, order, table_id=None,
                              replace_default_data_frame_class_with=None):
        rddfcw = replace_default_data_frame_class_with
        df = Data.get_table_as_df(date_range, table_name, order_by_col_name, order)
        if df is None or df.shape[0] == 0:
            return None
        return HTMLHelper.as_html_form_from_df(df, table_id, make_editable=True,
                                               replace_default_data_frame_class_with=rddfcw)

    # TODO - kind of bad thing to but the style directly in here, its a poor assumption - should put in css
    @staticmethod
    def as_html_form_from_df(df, table_id=None, make_editable=False, replace_default_data_frame_class_with=None):
        if df is None or df.shape[0] == 0:
            return None
        rddfcw = replace_default_data_frame_class_with
        # hack to remove dataframe class that does not get replaced and add custom styling
        default_html = df.to_html(classes=Html.BANK_DATA_TABLE_BS_CLASSES, table_id=table_id, border=0)
        html_updated = re.sub(f'id="{ConstData.BANK_DATA_TABLE_ID}"',
                              f'id="{ConstData.BANK_DATA_TABLE_ID}" style="table-layout: fixed;"', default_html)
        html_updated = html_updated.replace('class="dataframe ', f'class="{rddfcw} ') if rddfcw else html_updated
        return html_updated if not make_editable else HTMLHelper._make_html_table_editable(html_updated)
