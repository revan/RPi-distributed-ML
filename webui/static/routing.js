$.get({url: "./graph.viz", async: false, success: function(data){document.body.innerHTML += Viz(data);}});

$('.node').each(function(index) {
    $(this).click(function() {
        var node = $("#" + this.id + "> title").text();
        alert("node " + node + " clicked");
    });
});