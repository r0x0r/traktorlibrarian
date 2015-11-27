angular.module('librarian')
    .factory('StatusService', ['$interval', '$http', '$rootScope',
        function($interval, $http, $rootScope) {
            var statusUpdatePromise;
            var getExportStatus = function() {
              $http({
                  method: 'GET',
                  url: '/export/status'
              }).then(function (response) {
                  if (response.data.status === 'ok') {
                      $rootScope.$emit('status-event', response.data.messages);
                  } else if (response.data.status === 'end') {
                      $rootScope.$emit('status-event', 'end');
                  }
              });
            };

            var start = function() {
                statusUpdatePromise = $interval(getExportStatus, 1000, 0);
            };

            var stop = function() {
                $interval.cancel(statusUpdatePromise);
            };

            var subscribe = function(scope, callback) {
                var handler = $rootScope.$on('status-event', callback);
                scope.$on('$destroy', handler);
            };

            return {
              start: start,
              stop: stop,
              subscribe: subscribe
            }
}]);

