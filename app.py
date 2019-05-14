import threading
import webbrowser

from app_setup import init_all
from self_finance.constants import App
from self_finance.front_end import app

if __name__ == "__main__":
    init_all()
    app.logger.info(f'Beginning {App.APPLICATION_NAME} application.')
    threading.Timer(App.TIME_WAIT_OPEN_BROWSER_SECONDS, lambda: webbrowser.open(App.LOCAL_HOST)).start()
    app.run(port=App.PORT, debug=False)
