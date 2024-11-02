from flask import Flask, request

app = Flask(__name__)

@app.get('/home')
def hello():
    return "hello world"

@app.post('/test')
def template():
    return f'hi {request.json["name"]}'

