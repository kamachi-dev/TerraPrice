from flask import Flask
from Model.account import *
from Model.dataset import *

app = Flask(__name__)

with app.app_context():
    app.create_all()

@app.route('/account', methods=['POST'])
def account():
    pass

@app.route('/dataset', methods=['GET'])
def dataset():
    pass

@app.route('/addRecord', methods=['GET'])
def add_record():
    pass