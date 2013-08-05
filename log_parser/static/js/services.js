angular.module('sessionServices', ['ngResource']).
    factory('Session', function($resource) {
      return $resource('/view/sessions/.json', {}, {
        query: {method:'GET', params:{}, isArray:true}
      });
    });
