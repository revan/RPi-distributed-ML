config = 'graph{layout=neato;splines=true;node [shape=box style=filled];1 [pos="1,4!"];2 [pos="2,4!"];3 [pos="3,4!"];4 [pos="4,4!"];5 [pos="1,3!"];6 [pos="2,3!"];7 [pos="3,3!"];8 [pos="4,3!"];9 [pos="1,2!"];10[pos="2,2!"];11[pos="3,2!"];12[pos="4,2!"];13[pos="1,1!"];14[pos="2,1!"];15[pos="3,1!"];16[pos="4,1!"];';
edges = "";

var updateGraph = function() {
    $("svg").remove();
    document.body.innerHTML += Viz(config + edges + "}");

    var first = null;
    $('.node').each(function(index) {
        $(this).click(function() {
            var node = $("#" + this.id + "> title").text();
            if (first == null) {
                first = node;
            } else {
                edges += first + "--" + node + ";";
                node = null;
                updateGraph();
            }
        });
    });
}

updateGraph();