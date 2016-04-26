(function(){
	var ctx = $('#myChart');

	var myLineChart = new Chart(ctx, {
	    type: 'line',
	    data: {
	    	labels: [],
	    	datasets: [
	    	{
	    		label: "SVM Error",
	    		data: []
	    	}
	    	]
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
        	responsive: false
    	}
	});

    var source = new EventSource("/classifier_stream/");
    source.onmessage = function(msg) {
    	console.log(msg.data);
    	var newData = JSON.parse(msg.data);
    	myLineChart.data.datasets[0].data = newData;
    	myLineChart.data.labels = Array.apply(null, Array(newData.length)).map(function (_, i) {return i + 1;});
    	console.log(myLineChart.data);
    	myLineChart.update(5, true);
    };

})();