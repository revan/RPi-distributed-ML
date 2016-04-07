from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('routing.html')

@app.route('/graph.viz')
def graphviz():
    return render_template('graph.viz')

@app.route('/topo.json')
def topo():
    return render_template('topo.json')

if __name__ == "__main__":
    app.run(debug=True)