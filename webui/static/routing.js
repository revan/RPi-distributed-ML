var edges = "";
var width=4;
var height=4;
var network = {};
for (var i = 1; i <= width * height; i++) {
    network[i] = [];
}

var updateGraph = function() {    
    var config = 'graph{layout=neato;splines=true;node [shape=box style=filled];';

    $("svg").remove();

    var i = 1;
    var nodes = "";
    for (var h = height - 1; h >= 0; h--) {
        for (var w = 0; w < width; w++) {
            nodes += i++ + ' [pos="' + w + ',' + h + '!"];';
        }
    }

    document.body.innerHTML += Viz(config + nodes + edges + "}");

    var addLinkToNetwork = function(node1, node2) {
        network[node1].push(+node2);
        network[node2].push(+node1);
    };

    var first = null;
    $('.node').each(function(index) {
        $(this).click(function() {
            var node = $("#" + this.id + "> title").text();
            if (first === null) {
                first = node;
            } else {
                addLinkToNetwork(first, node);
                edges += first + "--" + node + ";";
                node = null;
                updateGraph();
            }
        });
    });

    $('#button-grid').unbind('click').click(function() {
        edges = "";
        for (var h = 0; h < height; h++) {
            for (var w = 0; w < width; w++) {
                if (w < width - 1) {
                    addLinkToNetwork(h * height + w + 1, h * height + w + 2);
                    edges += (h * height + w + 1) + "--" + (h * height + w + 2) + ";";
                }
                if (h < height - 1) {
                    addLinkToNetwork(h * height + w + 1, (h + 1) * height + w + 1);
                    edges += (h * height + w + 1) + "--" + ((h + 1) * height + w + 1) + ";";
                }
            }
        }
        updateGraph();
    });

    $('#button-complete').unbind('click').click(function() {
        edges = "";
        for (var i = 1; i < height * width; i++) {
            for (var k = i + 1; k <= height * width; k++) {
                addLinkToNetwork(i, k);
                edges += i + "--" + k + ";";
            }
        }
        updateGraph();
    });

    $('#button-save').unbind('click').click(function() {
        network.from = +$('#from').val();
        network.to = +$('#to').val();

        var str = JSON.stringify(network);
        console.log(str);
        $.post('./topo.json', str, function() {
            document.body.innerHTML += "<h1>Saved!</h1>";
        });
    });
};

updateGraph();