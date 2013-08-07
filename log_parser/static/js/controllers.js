var SessionListCtrl = function($scope, Session, $location) {
  $scope.pred = '-start_time';
  $scope.reverse = false;
  $scope.sessions = Session.query();
  $scope.getActive = function(state) {
    var state = state || $scope.active;
    $scope.sessions = Session.query({active: state});
  };
};
