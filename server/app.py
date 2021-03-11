from flask import Flask

from src.server import server

# Init Flask application
app = Flask(__name__)
app.register_blueprint(server)

# Set flask app configurations
app.config['JSON_SORT_KEYS'] = False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
