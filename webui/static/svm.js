(function(){
	var ctx = $('#myChart');

	var datasets = [];
	for (var i = 0; i< 16; i++) {
		datasets.push({
			label: 'Error Node ' + (i+1),
			data: []
		});
	}

	var myLineChart = new Chart(ctx, {
	    type: 'line',
	    data: {
	    	labels: [],
	    	datasets: datasets
	    },
	    options: {
	    	scales: {
	    		yAxes: [{
	    			ticks: {
	    				suggestedMin: 0,
	    				suggestedMax: 1
	    			}
	    		}]
	    	},
        	responsive: false,
        	legend: {
        		display: false
        	}
    	}
	});

    var source = new EventSource("/classifier_stream/");
    source.onmessage = function(msg) {
    	var newData = JSON.parse(msg.data);
    	var maxLen = 0;
    	for (var i = 0; i < 16; i++) {
    		myLineChart.data.datasets[i].data = newData[i];
    		if (maxLen < newData[i].length) {
    			maxLen = newData[i].length;
    		}
    	}
    	myLineChart.data.labels = Array.apply(null, Array(maxLen)).map(function (_, i) {return i + 1;});
    	console.log(myLineChart.data);
    	myLineChart.update(5, true);
    };

})();