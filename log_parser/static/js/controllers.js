var SessionListCtrl = function($scope, Session) {
  $scope.sessions = Session.query();
}
