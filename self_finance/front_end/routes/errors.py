from flask import render_template

from self_finance.front_end import app


@app.errorhandler(404)
def not_found_error(error):
    return render_template('./errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('./errors/500.html'), 500


@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template('./errors/405.html'), 405
