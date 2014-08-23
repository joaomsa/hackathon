(function(){
    "use strict";

    var app = angular.module("boxepolitico", ['debounce']);

    app.value("api_token", "ArbNezEPBRPF");

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
                CandidateSrv.add(id);
                //CandidateSrv.add(id);
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
                console.log($scope.candidates);
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
                        cached[id] = {}
                        cached[id].id = id
                        cached[id].candidatura = data
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

}());
