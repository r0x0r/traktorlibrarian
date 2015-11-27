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


