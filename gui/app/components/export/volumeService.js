angular.module('librarian')
    .factory('VolumeService', ['$interval', '$http', '$rootScope',
        function($interval, $http, $rootScope) {
            var volumePromise;
            var getVolumes = function() {
              $http({
                  method: 'GET',
                  url: '/export/scanvolumes'
              }).then(function (response) {
                $rootScope.volumes = response.data.volumes;
              });
            };

            var start = function() {
                volumePromise = $interval(getVolumes, 1000, 0);
            }

            var stop = function() {
              $interval.cancel(volumePromise);
            }

          return {
              start: start,
              stop: stop,
              getVolumes: getVolumes
          }
}]);

