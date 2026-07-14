"""Local Handouts Manager — application entry point.

Thin by design: it builds the Flask app and registers the player and master
blueprints. All data logic lives in the `handouts` package.
"""

from flask import Flask

from handouts.routes_player import bp as player_bp
from handouts.routes_master import bp as master_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(player_bp)
    app.register_blueprint(master_bp)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
