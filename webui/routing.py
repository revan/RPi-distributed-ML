import json
import gevent
from gevent import monkey
monkey.patch_all()
from flask import Flask, render_template, request, Response
app = Flask(__name__)

version = 0
topology = {i: [] for i in range(1, 17)}
classifier_errors = [[] for i in range(16)]

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
    if request.method == 'DELETE':
        classifier_errors = [[] for i in range(16)]
        return "OK"
    else:
        return Response(error_stream(), mimetype="text/event-stream")

@app.route('/classifier_error/<int:node>', methods=['POST'])
def add_error(node):
    global classifier_errors
    classifier_errors[node-1].append(float(request.form['value']))
    return "OK"

@app.route('/svm')
def svm():
    return render_template('svm.html')
