(function(){
    "use strict";

    var app = angular.module("boxepolitico", ['debounce']);

    app.controller("SearchCtrl", [ "$scope", "$http", "CandidateSrv",
        function($scope, $http, CandidateSrv){
            $scope.name = "";
            $scope.candidates = [];

            $scope.$watch("name", function(val){
                $http.get("/search", {
                    params: {'nome': val}
                }).success(function(data, status, headers, config, statusText){
                    $scope.candidates = data;
                }).error(function(data, status, headers, config, statusText){
                    console.log(status, statusText);
                });
            });

            $scope.select = function(id){
                if (!CandidateSrv.isSelected(id))
                    CandidateSrv.add(id);
            }
        }
    ]);

    app.controller("VsCtrl", ["$scope", "$rootScope", "CandidateSrv",
        function($scope, $rootScope, CandidateSrv){
            $scope.candidates = []; 

            $rootScope.$on("candidate.changed", function(){
                $scope.candidates = CandidateSrv.candidates;
            });

            $scope.$watch('candidates', function(){
                setTimeout(function(){
                    for (var i = 0; i < $scope.candidates.length; i++){
                        plotData("votenaweb_" + $scope.candidates[i].id, 
                                $scope.candidates[i].projeto.up, 
                                $scope.candidates[i].projeto.down)
                    }
                }, 100);
                setTimeout(function(){
                    for (var i = 0; i < $scope.candidates.length; i++){
                        drawDonations("donations_" + $scope.candidates[i].id, 
                            $scope.candidates[i].id )
                    }
                }, 100);
            }, true);
        }
    ]);

    app.service('CandidateSrv', [ '$rootScope', '$http',
        function($rootScope, $http){
            var that = this;

            var cached = {}
            var selected = []

            that.candidates = selected;

            that.isSelected = function(id){
                for (var i = 0; i < selected.length; i++){
                    if (selected[i].id === id)
                        return true;
                }
                return false;
            };

            var actuallyAdd = function(data){
                    selected.push(data);
                    $rootScope.$emit('candidate.changed');
            };

            that.add = function(id){
                if (that.isSelected(id))
                    return;

                if (cached[id] !== undefined){
                    actuallyAdd(cached[id]);
                } else {
                    $http.get("/candidatura", {
                        params: {'id': id}
                    }).success(function(data, status, headers, config, statusText){
                        cached[id] = data
                        cached[id].id = id
                        actuallyAdd(cached[id]);
                    }).error(function(data, status, headers, config, statusText){
                        console.log(status, statusText);
                    });
                }
            };

            that.remove = function(id){
                if (!that.isSelected(id))
                    return;

                for (var i = 0; i < selected.length; i++){
                    if (selected[i].id === id){
                        selected.splice(i, 1);
                        $rootScope.$emit('candidate.changed');
                        return;
                    }
                }
            };
        }
    ]);

    function plotData(canvas_id, up_vote, down_vote) {
        var canvas;
        var ctx;
        var lastend = 0;
        var myTotal = down_vote + up_vote;

        canvas = document.getElementById(canvas_id);
        ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var myData = [up_vote, down_vote];
        var myColor = ["rgb(154, 191, 114)","#D95B43"];

        for (var i = 0; i < myData.length; i++) {
            ctx.fillStyle = myColor[i];
            ctx.beginPath();
            ctx.moveTo(200,150);
            ctx.arc(200,150,150,lastend,lastend+
                (Math.PI*2*(myData[i]/myTotal)),false);
                ctx.lineTo(200,150);
                ctx.fill();
                lastend += Math.PI*2*(myData[i]/myTotal);
        }

        ctx.fillStyle = "white";
        ctx.font = "20px Helvetica";
        if(up_vote > down_vote) ctx.fillText((up_vote/myTotal * 100 | 0) + " %", 180, 230);
        else ctx.fillText((down_vote/myTotal * 100 | 0) + " %", 180, 80);
    }

    function drawDonations(div_id, id){
        var margin = {top: 20, right: 20, bottom: 30, left: 70},
            width = 400 - margin.left - margin.right,
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


        var svg = d3.select("#" + div_id).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var drawUpdate = function(data){
        };
        d3.json(id + ".json", function(error, data) {
            console.log(svg);
            data.forEach(function (d) {
            if(d.montante == null)
            {d.montante = 0}
            d.montante = parseInt(d.montante) // / 1000
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
        //        return "translate(0,0) rotate(-90)"
            })
            .style("text-anchor","start");
        
        });
    }

}());
