angular.module('sessionServices', ['ngResource']).
    factory('Session', function($resource) {
      return $resource('/view/sessions/:active/.json', {active: 'false'});
    });
