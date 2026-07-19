from flask import Flask
from dotenv import load_dotenv
import os

from Controller.Routes import register_routes

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "terraprice-secret-key")
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
