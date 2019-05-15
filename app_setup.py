import os
from logging.config import dictConfig

import yaml

from config.files import dirs, files
from self_finance.back_end.data import Data


class _Init:
    @staticmethod
    def logger():
        with open(files['log_config'], 'r') as log_yml:
            yml_dict = yaml.load(log_yml)
            dictConfig(yml_dict)

    @staticmethod
    def db():
        Data.create_base_db()

    @staticmethod
    def paths():
        # create all required directories if not existing
        for k in dirs.keys():
            os.makedirs(dirs[k], exist_ok=True)


def init_all():
    _Init.logger()
    _Init.paths()
    _Init.db()


def run_app():
    import threading
    import webbrowser

    from self_finance.constants import App
    from self_finance.front_end import app

    init_all()
    app.logger.info(f'Beginning {App.APPLICATION_NAME} application.')
    threading.Timer(App.TIME_WAIT_OPEN_BROWSER_SECONDS, lambda: webbrowser.open(App.LOCAL_HOST)).start()
    app.run(port=App.PORT, debug=False)
