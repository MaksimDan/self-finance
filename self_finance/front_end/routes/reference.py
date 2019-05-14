from flask import render_template

from self_finance.front_end import app


def _standard_render():
    return render_template("reference.html")


@app.route('/reference')
def reference():
    return _standard_render()
