import json
import gevent
from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template, request, Response
app = Flask(__name__)

version = 0
topology = {i: [] for i in range(1, 16)}
classifier_errors = []

@app.route('/')
def main():
    return render_template('wired.html')

@app.route('/wifi')
def wifi():
    return render_template('wifi.html')

@app.route('/topo.json', methods=['POST', 'GET'])
def topo():
    if request.method == 'POST':
        global topology
        global version
        topology = request.get_json(force=True)
        topology['version'] = version
        version += 1
        print(topology)

    return json.dumps(topology)

def error_stream():
    global classifier_errors
    while True:
        yield 'data: %s\n\n' % classifier_errors
        gevent.sleep(0.2)

@app.route('/classifier_stream/', methods=['GET', 'POST', 'DELETE'])
def class_stream():
    global classifier_errors
    if request.method == 'POST':
        classifier_errors.append(float(request.form['value']))
        return "OK"
    elif request.method == 'DELETE':
        classifier_errors = []
        return "OK"
    else:
        return Response(error_stream(), mimetype="text/event-stream")

@app.route('/svm')
def svm():
    return render_template('svm.html')
