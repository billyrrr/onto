from flask import Flask
from flask_jsonrpc import JSONRPC

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)

from view import TodoMediator

TodoMediator.start(app=app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


