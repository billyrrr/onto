from flask import Flask
from view import TodoMediatorLc


TodoMediatorLc.start()

app = Flask(__name__)


@app.route('/', methods=('GET',))
def hello():
    return 'world'


