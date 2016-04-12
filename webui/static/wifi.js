var width=4;
var height=4;
var num_nodes = 16;
var canvas_width = 600;
var canvas_height = 400;
var node_radius = 20;
var signal_radius = 100;

var init_page = function() {

    var nodes = [];
    var signals = [];
    var groups = [];
    var canvas = new fabric.Canvas('canvas');
    canvas.setHeight(canvas_height);
    canvas.setWidth(canvas_width);

    for (var i = 0; i < num_nodes; i++) {
        nodes.push(new fabric.Circle({
            radius: node_radius,
            fill: 'green',
            strokeWidth: 3,
            stroke: 'black',
            left: signal_radius - node_radius,
            top: signal_radius - node_radius
        }));
        signals.push(new fabric.Circle({
            radius: signal_radius,
            fill: 'rgba(51, 204, 255, 0.3)',
            left: 0,
            top: 0
        }));
        var label = new fabric.Text(i+1+'', {
            left: signal_radius - 0.5 * node_radius,
            top: signal_radius - 0.5 * node_radius,
            fontSize:30
        });

        groups.push(new fabric.Group([signals[i], nodes[i], label], {
            left: Math.floor((Math.random() * (canvas_width - 1.3 * signal_radius)) + 1 - 0.5 * signal_radius),
            top: Math.floor((Math.random() * (canvas_height - 1.3 * signal_radius)) + 1 - 0.5 * signal_radius)
        }));

        canvas.add(groups[i]);
    };

    $('#button-grid').unbind('click').click(function() {
        // edges = "";
        // for (var h = 0; h < height; h++) {
        //     for (var w = 0; w < width; w++) {
        //         if (w < width - 1) {
        //             addLinkToNetwork(h * height + w + 1, h * height + w + 2);
        //             edges += (h * height + w + 1) + "--" + (h * height + w + 2) + ";"
        //         }
        //         if (h < height - 1) {
        //             addLinkToNetwork(h * height + w + 1, (h + 1) * height + w + 1);
        //             edges += (h * height + w + 1) + "--" + ((h + 1) * height + w + 1) + ";";
        //         }
        //     }
        // }
        // updateGraph();
    });

    $('#button-complete').unbind('click').click(function() {
        // edges = "";
        // for (var i = 1; i < height * width; i++) {
        //     for (var k = i + 1; k <= height * width; k++) {
        //         addLinkToNetwork(i, k);
        //         edges += i + "--" + k + ";";
        //     }
        // }
        // updateGraph();
    });

    $('#button-save').unbind('click').click(function() {
        var network = {};

        for (var i = 1; i <= num_nodes; i++) {
            network[i] = [];
        }

        var distance = function(node1, node2) {
            return Math.sqrt(Math.pow(node1.top - node2.top, 2) + Math.pow(node1.left - node2.left, 2));
        };

        for (var i = 0; i < num_nodes; i++) {
            for (var k = 0; k < num_nodes; k++) {
                if (i != k && distance(groups[i], groups[k]) <= signal_radius) {
                    network[k+1].push(i+1);
                }
            }
        }

        var str = JSON.stringify(network);
        console.log(str);
        $.post('./topo.json', str, function() {
            alert('saved!');
            // document.body.innerHTML += "<h1>Saved!</h1>";
        });
    });
}

init_page();