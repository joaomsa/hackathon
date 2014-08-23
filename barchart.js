var margin = {top: 20, right: 20, bottom: 30, left: 70},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;


var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], 0.1);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var y = d3.scale.linear()
    .range([height, 0]);

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .ticks(10,"$,");


var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("dilma_doacoes.json", function(error, data) {
    data.forEach(function (d) {
	if(d.montante == null)
	{d.montante = 0}
	d.montante = parseInt(d.montante)
    })
    
    data = data.sort(function (a,b) {
    	if (a.montante < b.montante)
    	    return 1;
    	if (a.montante > b.montante)
    	    return -1;
    	return 0;
    	})

    // set x and y limits
    x.domain(data.map(function(d) { return d.nome; }));
    y.domain([0, d3.max(data, function(d) { return d.montante; })]);

    // Draw y axis
    svg.append("g")
    	.attr("class", "y axis")
    	.call(yAxis)
    	.append("text")
    	// .attr("transform", "rotate(-90)")
    	// .attr("y", 6)
    	// .attr("dy", ".71em")
    	// .style("text-anchor", "end")
    	// .text("Montante");

    // Draw bars
    svg.selectAll(".bar")
	.data(data)
	.enter().append("rect")
	.attr("class", "bar")
	.attr("x", function(d) { return x(d.nome); })
	.attr("width", x.rangeBand())
	.attr("y", function(d) { return y(d.montante); })
	.attr("height", function(d) { return height - y(d.montante); });


    // Draw x axis
    svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + height + ")")
	.call(xAxis)
	.selectAll("text")
  	  .attr("transform", function (d) {
	      return "translate(-10,-10) rotate(-90)"
//	      return "translate(0,0) rotate(-90)"
	  })
	.style("text-anchor","start");
   
});

