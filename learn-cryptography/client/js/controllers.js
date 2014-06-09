'use strict';

/* Controllers */

angular.module('cryptoApp.controllers', [])
  .controller('IndexController', ['$scope', function($scope) {
  }])
  .controller('LevelController', ['$scope', '$routeParams', '$http', function($scope, $routeParams, $http) {

    $http.get('level_data?level=' + $routeParams.levelKey).success(
      function(data) {
        $scope.level = data;
      }
    );

    $scope.includeUrls = {
      "texts": "partials/texts.html",
      "analysis": "partials/analysis.html",
      "decryptors": "partials/decryptors.html"
    };

    $scope.range = function(begin, end) {
      var result = [];
      for(var i = begin; i < end; i++) {
          result.push(i);
      }
      return result;
    };

    $scope.alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

  }]);
