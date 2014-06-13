'use strict';


// Declare app level module which depends on filters, and services
angular.module('cryptoApp', [
  'ngRoute',
  'chartjs-directive',
  'cryptoApp.filters',
  'cryptoApp.services',
  'cryptoApp.directives',
  'cryptoApp.controllers'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/', {templateUrl: 'partials/index.html', controller: 'IndexController'});
  $routeProvider.when('/level/:levelKey', {templateUrl: 'partials/level.html', controller: 'LevelController'});
  $routeProvider.when('/progress', {templateUrl: 'partials/progress.html', controller: 'ProgressController'});
  $routeProvider.otherwise({redirectTo: '/'});
}]);
