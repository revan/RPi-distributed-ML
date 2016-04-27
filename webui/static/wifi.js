var width=4;
var height=4;
var num_nodes = 16;
var canvas_width = 1500;
var canvas_height = 1000;
var spawn_width = 600;
var spawn_height = 400;
var node_radius = 20;
var signal_radius = 100;

var init_page = function() {

    var nodes = [];
    var signals = [];
    var groups = [];
    var target;
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
            fill: 'rgba(51, 204, 255, 0.1)',
            left: 0,
            top: 0,
        }));
        var label = new fabric.Text(i+1+'', {
            left: signal_radius - 0.5 * node_radius,
            top: signal_radius - 0.5 * node_radius,
            fontSize:30
        });

        groups.push(new fabric.Group([signals[i], nodes[i], label], {
            left: Math.floor((Math.random() * (spawn_width - 1.3 * signal_radius))),
            top: Math.floor((Math.random() * (spawn_height - 1.3 * signal_radius)))
        }));

        groups[i].hasControls = false;

        canvas.add(groups[i]);
    }

    target = new fabric.Rect({
        fill:'red',
        width: node_radius,
        height: node_radius,
        left: Math.floor((Math.random() * (spawn_width - 2 * signal_radius)) + 1),
        top: Math.floor((Math.random() * (spawn_height - 2 * signal_radius)) + 1)
    });
    target.hasControls = false;
    canvas.add(target);

    $('#button-save').unbind('click').click(function() {
        var i;
        var network = {};

        for (i = 1; i <= num_nodes; i++) {
            network[i+""] = [];
        }

        network.geo = {'target': [target.left, target.top]};

        var distance = function(node1, node2) {
            return Math.sqrt(Math.pow(node1.top - node2.top, 2) + Math.pow(node1.left - node2.left, 2));
        };

        for (i = 0; i < num_nodes; i++) {
            network.geo[(i+1)+""] = [groups[i].left + signal_radius, groups[i].top + signal_radius];
            for (var k = 0; k < num_nodes; k++) {
                if (i != k && distance(groups[i], groups[k]) <= signal_radius) {
                    network[(k+1)+""].push((i+1)+"");
                }
            }
        }

        network.from = (+$('#from').val())+"";

        var str = JSON.stringify(network);
        console.log(str);
        $.post('./topo.json', str, function() {
            $('#alert').html("<h1>Saved!</h1>");
        });
    });
};

init_page();