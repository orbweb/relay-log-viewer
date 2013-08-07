angular.module('sessions', ['sessionServices']).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/sessions', {controller: SessionListCtrl});
}]);
