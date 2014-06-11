'use strict';

/* Controllers */

angular.module('cryptoApp.controllers', [])
  .controller('IndexController', ['$scope', function($scope) {
  }])
  .controller('LevelController', ['$scope', '$routeParams', '$http', function($scope, $routeParams, $http) {

    $http.get('level_data?level=' + $routeParams.levelKey).success(
      function(data) {
        $scope.level = data;
        // New level, default to not-yet-complete.
        $scope.level.success = false;
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

    $scope.rotate_decryptor = {"id":"rotate", "rotate": 1};
    // TODO use this in future:
    // $scope.decrytpros = [{'id':'rotate', 'data':{'rotate':1}}, {'id':'translate', 'data':{}}];
    $scope.decrypt = function(decryptor_model) {
      var data = {};
      data.level_key = $scope.level.key;
      data.text_key = $scope.level.text.key;
      var decryptor = {'id': 'rotate'};
      decryptor.key = {'rotate': decryptor_model.rotate};
      data.decryptor = decryptor;

      $http.post('decrypt_data', data).success(
          function(response_data) {
            // Update decrypted text tab
            $scope.level.text.cleartext = response_data.text;
            // Signal success or failure
            if (response_data.win) {
              $scope.level.success = response_data.win;
            }
          });
    };

  }]);
