from flask import Flask, send_from_directory, url_for, redirect

from .view.translator import translator

from .config.flask_config import config

from pathlib import Path


def create_app(config_name):
    app = Flask(__name__)

    # 設定 config
    app.config.from_object(config[config_name])

    @app.route('/')
    def index():
        # return 'success'
        return redirect(url_for('translator.index'))

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(Path("/").joinpath(app.root_path, 'static', 'img'), 'favicon.ico')

    # app.register_blueprint(index, url_prefix="/index")
    app.register_blueprint(translator, url_prefix="/translator")
    return app
