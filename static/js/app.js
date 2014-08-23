(function(){
    "use strict";

    var app = angular.module("boxepolitico", ['debounce']);

    app.controller('SearchCtrl', [ "$scope", "$http",
        function($scope, $http){
            $scope.query = "";

            $scope.watch("query", function(val){
                console.log(val);
            });
        }
    ]);
}());
