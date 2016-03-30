/*global $:false */
/*global angular:false */
/*global console:false */

angular.module('librarian', ['ngRoute'])

.config([
    '$routeProvider',

    function($routeProvider)  {

      $routeProvider
          .when('/clean/', {
              templateUrl: '../static/components/clean/clean.html',
              controller: 'CleanController'
          })
          .when('/export', {
              templateUrl: '../static/components/export/export.html',
              controller: 'ExportController'
          })
          .when('/', {
              templateUrl: '../static/components/landing/landing.html',
              controller: 'LandingController'
          });
    }
  ])

.controller('HeaderController', [
    '$scope',
    '$location',
    '$http',
    '$rootScope',
    '$route',

    function($scope, $location, $http, $rootScope, $route) {
      'use strict';

        $scope.goToHome = function() {
            $rootScope.$emit('home-event');

            if ($location.path() !== '/') {
                $location.path('/');
            }
        };

        $scope.selectLibrary = function() {
            $http({
              method: 'POST',
              url: '/choose/path',
              data: {
                traktor_check: true
              }
            }).then(function (response) {
              if(response.data.status == "ok") {
                  $rootScope.traktorDir = response.data.directory;
                  $route.reload();
              } else if (response.data.status == "error") {
                  $rootScope.$emit('error', response.data.message);
              }
            });
        }
    }
  ]);

angular.module('librarian')
    .controller('CleanController', ['$scope', '$rootScope', '$http', '$location',
        function ($scope, $rootScope, $http, $location) {
          'use strict';
          $scope.loading = true;

          $scope.remove = function() {
            $scope.removeButton = 'Removing';
            $scope.isProcessing = true;

            $http({
              method: 'GET',
              url: '/clean/confirm'
            }).then(function(response) {
              if(response.data.status == 'ok') {
                 $scope.backup = response.data.backup;
                 $scope.isDone = true;
              } else if(response.data.status == 'error') {
                 $rootScope.$emit('error', response.data.message);
                 $location.path('/');
              }
            });
          }

          $http({
              method: 'GET',
              url: '/clean'
          }).then(function(response) {
            if(response.data.status == 'ok') {
              $scope.dupCount = response.data.count;
              $scope.duplicates = response.data.duplicates;

              // Remove button initialization
              $scope.removeButton = 'Remove duplicates';
              $scope.isProcessing = false;

              $scope.loading = false;

            } else if(response.data.status == 'error') {
               $rootScope.$emit('error', response.data.message);
            }
          });

        }]);

angular.module('librarian')
    .directive('error', [
        '$rootScope',

        function ($rootScope) {
          'use strict';

            return {
                scope: {
                    message: '='
                },
                restrict: 'E',
                templateUrl: '/static/components/error/error.html',
                link: function($scope) {
                    var processError = function(error, message) {
                        $scope.visible = true;
                        $scope.message = message;
                    };

                    $scope.closeError = function () {
                        $scope.visible = false;
                    }

                    $rootScope.$on('error', processError);
                }
            };
        }
    ]);

angular.module('librarian')
    .controller('ExportController', [
        '$scope',
        '$http',
        '$interval',
        '$rootScope',
        '$location',
        '$timeout',
        'VolumeService',
        'StatusService',

        function ($scope, $http, $interval, $rootScope, $location, $timeout, VolumeService, StatusService) {
            'use strict';

            $scope.removeOrphans = false;
            $scope.selectedDriveIndex = -1;
            $scope.destination = "";

            $scope.messages = [];

            var processMessages = function (event, newMessages) {
                if (newMessages == 'end') {
                    $scope.isDone = true;
                    StatusService.stop();
                } else {
                    $scope.messages = $scope.messages.concat(newMessages);
                }
            };

            $scope.$watchCollection('messages', function(newCol, oldCol, scope) {
                $timeout(function () {
                    var message = $scope.messages.shift();
                    if (message) $scope.message = message;
                }, 100);
            });

            VolumeService.start();

            $scope.selectDrive = function(index) {
              $scope.selectedDriveIndex = index;
              $scope.destination = $scope.volumes[$scope.selectedDriveIndex];
            };

            $scope.toggleOrphans = function() {
            $scope.removeOrphans = !$scope.removeOrphans;
            }

            $scope.export = function() {
              $scope.isExporting = true;
              VolumeService.stop();

              $http({
                  method: 'POST',
                  url: '/export',
                  data: {
                      destination: $scope.destination,
                      remove_orphans: $scope.removeOrphans
                  }
              }).then(function (response) {
                  if (response.data.status === 'ok') {
                      StatusService.subscribe($scope, processMessages);
                      StatusService.start();
                  } else if(response.data.status == "error") {
                      $rootScope.$emit('error', response.data.message);
                  }
              });
            };

            var cancelExport = function() {
                return $http({
                    method: 'GET',
                    url: '/export/cancel'
                })
            }

            $scope.cancelExport = function () {
                StatusService.stop();

                cancelExport().then(function (response) {
                    if (response.data.status === 'ok') {
                        $scope.goToHome();
                    }
                });
            };

            $scope.goToHome = function() {
                if ($location.path() !== '/') {
                    $location.path('/');
                }
            };

            $rootScope.$on('home-event', function() {
                StatusService.stop();
                VolumeService.stop();
                cancelExport();
            });

        }
    ]);



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


'use strict';

angular.module('librarian')
    .controller('LandingController', [
      '$scope',
      '$route',
      '$rootScope',
      '$http',
      '$location',
      'VolumeService',

      function ($scope, $route, $rootScope, $http, $location, VolumeService) {
          $rootScope.isLanding = true;

          $scope.goTo = function(link) {
            $http({
                  method: 'GET',
                  url: '/check/traktor',
            }).then(function (response) {
                if(response.data.status == 'ok') {
                    $rootScope.isLanding = false;
                    $location.path(link);
                } else if (response.data.status == 'error') {
                    $rootScope.$emit('error', response.data.message);
                }
            });

          }

          var initialize = function() {
              VolumeService.getVolumes();
              $http({
                  method: 'GET',
                  url: '/init',
              }).then(function (data) {
              });
          }

          initialize();
    }]);



angular.module('librarian')
    .directive('loader', function () {
      'use strict';

        return {
            scope: {
                message: '='
            },
            restrict: 'E',
            templateUrl: '/static/components/loader/loader.html',
            link: function($scope) {
            }
        };
    });
