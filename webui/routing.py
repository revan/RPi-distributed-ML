import json
from flask import Flask, render_template, request, send_file
app = Flask(__name__)

topology = {i: [] for i in range(1, 16)}

@app.route('/')
def main():
    return render_template('routing.html')

@app.route('/wifi')
def wifi():
    return render_template('wifi.html')

@app.route('/graph.viz')
def graphviz():
    return render_template('graph.viz')

@app.route('/topo.json', methods=['POST', 'GET'])
def topo():
    if request.method == 'POST':
        global topology
        topology = request.get_json(force=True)
        print(topology)

    return json.dumps(topology)

if __name__ == "__main__":
    app.run(debug=True)