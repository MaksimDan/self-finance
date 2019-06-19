import logging

from flask import render_template, request, flash

from self_finance.back_end.data import Data
from self_finance.front_end import app

logger = logging.getLogger(__name__)


def _standard_render():
    return render_template("settings.html")


@app.route('/settings')
def settings():
    return _standard_render()


@app.route('/settings/invalidate_cache', methods=['POST', 'GET'])
def invalidate_cache(flash_message=True):
    logging.info('Invalidating cache.')
    if request.method == 'POST':
        Data.invalidate_cache()
        if flash_message:
            flash('Cache was successfully invalidated.', 'info')
    return _standard_render()
