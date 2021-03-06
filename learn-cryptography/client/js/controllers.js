'use strict';

/* Controllers */

var min = function(a, b) {
    if (a > b) {
        return b;
    }
    return a;
}

// Common words
var common_words = function(text) {
    text = text.replace(/[^\w\s]/g, '').toLowerCase().trim().split(/\s+/);
    var freqs = {};
    for ( var i = 0; i < text.length; i++ ) {
        freqs[text[i]] = (freqs[text[i]] || 0) + 1;
    }
    var tups = [];
    for (var k in freqs) {
        tups.push([k, freqs[k]]);
    }
    tups.sort(function(a, b) {return a[1] - b[1]});
    tups.reverse();
    var out = [];
    for (var i = 0; i < min(tups.length, 30); i++) {
        out.push(tups[i][0] + " (" + tups[i][1] + ")");
    }
    return out.join("\n");
};


var getFrequencies = function(text) {
  text = text.toLowerCase();
  var freqs = {};
  var maxFreq = 0;
  for ( var i = 0; i < text.length; i++ ) {
      if ('a' <= text[i] && text[i] <= 'z') {
          freqs[text[i]] = (freqs[text[i]] || 0) + 1;
          if (freqs[text[i]] > maxFreq) {
            maxFreq = freqs[text[i]];
          }
      }
  }
  console.log(freqs);
  var freqList = [];
  var aleph = "abcdefghijklmnopqrstuvwxyz".split("");
  var scale = 13/maxFreq;
  for (var i = 0; i < aleph.length; i++) {
    freqList.push(scale * freqs[aleph[i]]);
  }
  return freqList;
};

var fillCharts = function($scope) {
  $scope.textFreqChart.data.datasets[0].data = getFrequencies($scope.level.text.encrypted);
  $scope.textCommonWords = common_words($scope.level.text.encrypted);
};



angular.module('cryptoApp.controllers', [])
  .controller('MainController', ['$scope', '$http', function($scope, $http) {
    // Assume not signed in to start with
    $scope.user = {};
    $scope.user.is_signed_in = false;
    $http.get('/user_data').success(
      function(data) {
        $scope.user = data;
      });
  }])
  .controller('IndexController', ['$scope', function($scope) {
  }])
  .controller('ProgressController', ['$scope', '$http', function($scope, $http) {
    $http.get('/progress_data').success(
      function(data) {
        $scope.level_sequences = data;
      });
  }])
  .controller('LevelController', ['$scope', '$routeParams', '$http', function($scope, $routeParams, $http) {

    $http.get('level_data?level=' + $routeParams.levelKey).success(
      function(data) {
        $scope.level = data;
        // New level, default to not-yet-complete.
        $scope.level.success = false;
        fillCharts($scope);
      }
    );

    $scope.includeUrls = {
      "texts": "partials/texts.html",
      "analysis": "partials/analysis.html",
      "decryptors": "partials/decryptors.html"
    };

    $scope.encryptedTextTab = {'active':true};
    $scope.decryptedTextTab = {'active':false};

    $scope.range = function(begin, end) {
      var result = [];
      for(var i = begin; i < end; i++) {
          result.push(i);
      }
      return result;
    };

    $scope.alphabet = 'abcdefghijklmnopqrstuvwxyz'.split("");

    $scope.rotate_decryptor = {"id":"rotate", "key": {"rotate": 1}};
    $scope.translate_decryptor = {"id":"translate", "key":{}}
    for( var i = 0; i < $scope.alphabet.length; i++) {
      $scope.translate_decryptor.key[$scope.alphabet[i]] = "";
    }

    // TODO use this in future:
    // $scope.decrytpros = [{'id':'rotate', 'data':{'rotate':1}}, {'id':'translate', 'data':{}}];
    $scope.decrypt = function(decryptor_model) {
      var data = {};
      data.level_key = $scope.level.key;
      data.text_key = $scope.level.text.key;
      data.decryptor = decryptor_model;

      $http.post('decrypt_data', data).success(
          function(response_data) {
            // Update decrypted text tab
            $scope.level.text.cleartext = response_data.text;
            // Active decrypted text tab
            $scope.decryptedTextTab.active = true;
            // Signal success or failure
            if (response_data.win) {
              $scope.level.success = response_data.win;
            }
          });
    };

    var englishFreqData = {
      labels : $scope.alphabet,
      datasets : [{
        fillColor : "rgba(151,187,205,0.5)",
        strokeColor : "rgba(151,187,205,1)",
        data : [
           8.167,
           1.492,
           2.782,
           4.253,
           12.70,
           2.228,
           2.015,
           6.094,
           6.966,
           0.153,
           0.772,
           4.025,
           2.406,
           6.749,
           7.507,
           1.929,
           0.095,
           5.987,
           6.327,
           9.056,
           2.758,
           0.978,
           2.360,
           0.150,
           1.974,
           0.074
        ]
      }]
    }
    var options = {
        scaleShowLabels : false,
        scaleOverride: true,
        scaleSteps: 13,
        scaleStepWidth: 1,
        scaleStartValue: 0,
        barValueSpacing: 1
    };

    $scope.englishFreqChart = {
      options: options,
      data : englishFreqData
    };

    $scope.textFreqChart = {
      options: options,
      data : {
        labels: $scope.alphabet,
        datasets : [{
          fillColor : "rgba(151,187,205,0.5)",
          strokeColor : "rgba(151,187,205,1)",
          data : getFrequencies("")
        }]
      }
    };
  }]);
